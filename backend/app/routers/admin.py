"""
Admin dashboard endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_admin_user
from app.models import User, Balance, AccessLog, AccessToken
from app.auth import get_password_hash
from datetime import datetime, timedelta

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
    expiration = datetime.fromisoformat(user_data.expiration_date.replace('Z', '+00:00'))
    
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

