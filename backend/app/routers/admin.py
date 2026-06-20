"""
Admin dashboard endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, validator
from app.database import get_db
from app.auth import get_current_admin_user
from app.models import (
    User, Balance, AccessLog, AccessToken,
    MealPlan, AccessPermission, TransitPass, Ticket,
)
from app.auth import get_password_hash
from datetime import datetime, timedelta
from typing import Optional
import secrets

router = APIRouter(prefix="/api/admin", tags=["admin"])

class UserCreate(BaseModel):
    """User creation model."""
    netid: str
    password: str
    full_name: str
    student_id: str
    email: str
    photo_url: str = ""
    is_admin: bool = False
    expiration_date: str

class BalanceUpdate(BaseModel):
    """Balance update model."""
    user_id: int
    service_type: str
    balance: float

    @validator('balance')
    def validate_balance(cls, v):
        if v < 0:
            raise ValueError('Balance cannot be negative')
        return round(v, 2)

@router.get("/users")
def get_all_users(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)."""
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": u.id,
                "netid": u.netid,
                "full_name": u.full_name,
                "student_id": u.student_id,
                "email": u.email,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "expiration_date": u.expiration_date.isoformat()
            }
            for u in users
        ]
    }

@router.post("/users")
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)."""
    # Check if netid already exists
    existing = db.query(User).filter(User.netid == user_data.netid).first()
    if existing:
        raise HTTPException(status_code=400, detail="NetID already exists")
    
    # Parse expiration date
    try:
        expiration = datetime.fromisoformat(user_data.expiration_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid expiration_date. Use ISO format, e.g. 2026-01-15T00:00:00Z"
        )
    
    new_user = User(
        netid=user_data.netid,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        student_id=user_data.student_id,
        email=user_data.email,
        photo_url=user_data.photo_url,
        is_admin=user_data.is_admin,
        expiration_date=expiration
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "id": new_user.id,
        "netid": new_user.netid,
        "full_name": new_user.full_name,
        "message": "User created successfully"
    }

@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle user active status (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"success": True, "is_active": user.is_active}

@router.post("/balances")
def update_balance(
    balance_data: BalanceUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user balance (admin only)."""
    balance = db.query(Balance).filter(
        Balance.user_id == balance_data.user_id,
        Balance.service_type == balance_data.service_type
    ).first()
    
    if balance:
        balance.balance = balance_data.balance
    else:
        balance = Balance(
            user_id=balance_data.user_id,
            service_type=balance_data.service_type,
            balance=balance_data.balance
        )
        db.add(balance)
    
    db.commit()
    return {"success": True, "balance": balance.balance}

@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_logs = db.query(AccessLog).count()
    
    # Service usage stats
    service_stats = db.query(
        AccessLog.service_type,
        func.count(AccessLog.id).label("count")
    ).group_by(AccessLog.service_type).all()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_access_logs": total_logs,
        "service_usage": {stat.service_type: stat.count for stat in service_stats}
    }

@router.post("/revoke-token")
def revoke_token(
    token: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke an access token (admin only)."""
    access_token = db.query(AccessToken).filter(AccessToken.token == token).first()
    if not access_token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    access_token.is_revoked = True
    db.commit()
    
    return {"success": True, "message": "Token revoked"}


# --------------------------------------------------------------------------- #
# Door/building access permissions
# --------------------------------------------------------------------------- #

class PermissionGrant(BaseModel):
    user_id: int
    resource_key: str
    resource_name: str


@router.post("/permissions")
def grant_permission(
    data: PermissionGrant,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Grant a user access to a door/building/resource (idempotent)."""
    if not db.query(User).filter(User.id == data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    existing = db.query(AccessPermission).filter(
        AccessPermission.user_id == data.user_id,
        AccessPermission.resource_key == data.resource_key,
    ).first()
    if existing:
        existing.resource_name = data.resource_name
    else:
        db.add(AccessPermission(
            user_id=data.user_id,
            resource_key=data.resource_key,
            resource_name=data.resource_name,
        ))
    db.commit()
    return {"success": True}


@router.post("/permissions/revoke")
def revoke_permission(
    data: PermissionGrant,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke a user's access to a resource."""
    perm = db.query(AccessPermission).filter(
        AccessPermission.user_id == data.user_id,
        AccessPermission.resource_key == data.resource_key,
    ).first()
    if perm:
        db.delete(perm)
        db.commit()
    return {"success": True}


# --------------------------------------------------------------------------- #
# Meal-plan swipes
# --------------------------------------------------------------------------- #

class MealPlanUpdate(BaseModel):
    user_id: int
    plan_name: str = "Flex"
    swipes_remaining: int

    @validator('swipes_remaining')
    def non_negative(cls, v):
        if v < 0:
            raise ValueError('swipes_remaining cannot be negative')
        return v


@router.post("/meal-swipes")
def set_meal_swipes(
    data: MealPlanUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create or update a user's meal plan."""
    if not db.query(User).filter(User.id == data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    plan = db.query(MealPlan).filter(MealPlan.user_id == data.user_id).first()
    if plan:
        plan.plan_name = data.plan_name
        plan.swipes_remaining = data.swipes_remaining
    else:
        db.add(MealPlan(
            user_id=data.user_id,
            plan_name=data.plan_name,
            swipes_remaining=data.swipes_remaining,
        ))
    db.commit()
    return {"success": True, "swipes_remaining": data.swipes_remaining}


# --------------------------------------------------------------------------- #
# Transit pass
# --------------------------------------------------------------------------- #

class TransitUpdate(BaseModel):
    user_id: int
    status: str = "active"
    semester: str = ""
    valid_until: Optional[str] = None


@router.post("/transit")
def set_transit_pass(
    data: TransitUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create or update a user's transit (bus pass) eligibility."""
    if not db.query(User).filter(User.id == data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    valid_until = None
    if data.valid_until:
        try:
            valid_until = datetime.fromisoformat(data.valid_until.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid valid_until date")

    transit = db.query(TransitPass).filter(TransitPass.user_id == data.user_id).first()
    if transit:
        transit.status = data.status
        transit.semester = data.semester
        transit.valid_until = valid_until
    else:
        db.add(TransitPass(
            user_id=data.user_id,
            status=data.status,
            semester=data.semester,
            valid_until=valid_until,
        ))
    db.commit()
    return {"success": True, "status": data.status}


# --------------------------------------------------------------------------- #
# Event ticketing
# --------------------------------------------------------------------------- #

class TicketCreate(BaseModel):
    user_id: int
    event_name: str
    event_date: Optional[str] = None
    venue: str = ""
    seat: Optional[str] = None


@router.post("/tickets")
def issue_ticket(
    data: TicketCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Issue an event ticket to a user."""
    if not db.query(User).filter(User.id == data.user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    event_date = None
    if data.event_date:
        try:
            event_date = datetime.fromisoformat(data.event_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid event_date")

    ticket = Ticket(
        user_id=data.user_id,
        code=secrets.token_urlsafe(16),
        event_name=data.event_name,
        event_date=event_date,
        venue=data.venue,
        seat=data.seat,
        status="valid",
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return {"success": True, "ticket_id": ticket.id, "code": ticket.code}

