"""
Service integration endpoints (dining, library, residence, etc.).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from datetime import datetime
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Balance, AccessLog, MealPlan, TransitPass, AccessPermission
from app.utils import validate_access_token

router = APIRouter(prefix="/api/services", tags=["services"])

class ServiceAccessRequest(BaseModel):
    """Request model for service access."""
    token: str
    service_type: str
    action: str = "entry"
    location: str | None = None
    resource: str | None = None  # resource_key for permission-based door access


def _deny(db, user, request, reason):
    """Log a failed access attempt and raise 403."""
    db.add(AccessLog(
        user_id=user.id,
        service_type=request.service_type,
        action=request.action,
        success=False,
        location=request.location or request.resource,
    ))
    db.commit()
    raise HTTPException(status_code=403, detail=reason)


@router.post("/access")
def access_service(
    request: ServiceAccessRequest,
    db: Session = Depends(get_db)
):
    """Validate access token and grant service access (for scanning)."""
    user = validate_access_token(db, request.token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    resource_name = None

    # Permission-based door/building access (RecWell, labs, residence, etc.)
    if request.resource:
        permission = db.query(AccessPermission).filter(
            AccessPermission.user_id == user.id,
            AccessPermission.resource_key == request.resource,
        ).first()
        if not permission:
            _deny(db, user, request, f"No access permission for '{request.resource}'")
        resource_name = permission.resource_name

    # Transit (Madison Metro) tap requires an active bus pass
    if request.service_type == "transit":
        transit = db.query(TransitPass).filter(TransitPass.user_id == user.id).first()
        active = (
            transit is not None
            and transit.status == "active"
            and (transit.valid_until is None or transit.valid_until > datetime.utcnow())
        )
        if not active:
            _deny(db, user, request, "No active transit pass")

    # Log successful access
    log = AccessLog(
        user_id=user.id,
        service_type=request.service_type,
        action=request.action,
        success=True,
        location=request.location or resource_name,
    )
    db.add(log)
    db.commit()

    return {
        "success": True,
        "user": {
            "full_name": user.full_name,
            "student_id": user.student_id,
            "netid": user.netid
        },
        "service_type": request.service_type,
        "action": request.action,
        "resource_name": resource_name,
    }

@router.post("/dining/check-balance")
def check_dining_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check dining hall balance."""
    balance = db.query(Balance).filter(
        Balance.user_id == current_user.id,
        Balance.service_type == "dining"
    ).first()
    
    if not balance:
        balance = Balance(user_id=current_user.id, service_type="dining", balance=0.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)
    
    return {"service_type": "dining", "balance": balance.balance}

class DiningUseRequest(BaseModel):
    """Request model for using dining balance."""
    amount: float

    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount is positive and within limits."""
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 100:
            raise ValueError('Amount exceeds maximum transaction limit of $100')
        return round(v, 2)  # Round to 2 decimal places

@router.post("/dining/use")
def use_dining_balance(
    request: DiningUseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use dining balance (simulate payment)."""
    amount = request.amount

    try:
        balance = db.query(Balance).filter(
            Balance.user_id == current_user.id,
            Balance.service_type == "dining"
        ).first()

        if not balance:
            raise HTTPException(status_code=404, detail="Dining balance not found")

        if balance.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Deduct balance and create log in same transaction
        balance.balance -= amount

        log = AccessLog(
            user_id=current_user.id,
            service_type="dining",
            action=f"payment_{amount}",
            success=True
        )
        db.add(log)
        db.commit()

        return {"success": True, "new_balance": balance.balance, "amount_charged": amount}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")

@router.post("/library/checkout")
def library_checkout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate library checkout validation."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    log = AccessLog(
        user_id=current_user.id,
        service_type="library",
        action="checkout",
        success=True
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": "Library checkout validated"}

@router.post("/residence/access")
def residence_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate residence hall door access."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    log = AccessLog(
        user_id=current_user.id,
        service_type="residence",
        action="door_access",
        success=True
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "message": "Residence hall access granted"}


@router.post("/print/check-balance")
def check_print_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check Wisc Print (printing) balance."""
    balance = db.query(Balance).filter(
        Balance.user_id == current_user.id,
        Balance.service_type == "print"
    ).first()

    if not balance:
        balance = Balance(user_id=current_user.id, service_type="print", balance=0.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)

    return {"service_type": "print", "balance": balance.balance}


class PrintUseRequest(BaseModel):
    """Request model for spending print balance."""
    amount: float

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 100:
            raise ValueError('Amount exceeds maximum transaction limit of $100')
        return round(v, 2)


@router.post("/print/use")
def use_print_balance(
    request: PrintUseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Spend print balance (simulate a print job)."""
    amount = request.amount

    try:
        balance = db.query(Balance).filter(
            Balance.user_id == current_user.id,
            Balance.service_type == "print"
        ).first()

        if not balance:
            raise HTTPException(status_code=404, detail="Print balance not found")

        if balance.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        balance.balance -= amount

        log = AccessLog(
            user_id=current_user.id,
            service_type="print",
            action=f"print_job_{amount}",
            success=True
        )
        db.add(log)
        db.commit()

        return {"success": True, "new_balance": balance.balance, "amount_charged": amount}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")


# --------------------------------------------------------------------------- #
# Wiscard Cash — a unified stored-value account usable at many vendors
# (vending, laundry, bookstore, off-campus partners).
# --------------------------------------------------------------------------- #

@router.post("/wiscard-cash/check-balance")
def check_wiscard_cash(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check the unified Wiscard Cash balance."""
    balance = db.query(Balance).filter(
        Balance.user_id == current_user.id,
        Balance.service_type == "wiscard_cash"
    ).first()
    if not balance:
        balance = Balance(user_id=current_user.id, service_type="wiscard_cash", balance=0.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)
    return {"service_type": "wiscard_cash", "balance": balance.balance}


class WiscardCashUseRequest(BaseModel):
    """Spend Wiscard Cash at a vendor."""
    amount: float
    vendor: str = "Campus Vendor"

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 500:
            raise ValueError('Amount exceeds maximum transaction limit of $500')
        return round(v, 2)


@router.post("/wiscard-cash/use")
def use_wiscard_cash(
    request: WiscardCashUseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Spend Wiscard Cash at a vendor (vending, laundry, bookstore, etc.)."""
    try:
        balance = db.query(Balance).filter(
            Balance.user_id == current_user.id,
            Balance.service_type == "wiscard_cash"
        ).first()
        if not balance:
            raise HTTPException(status_code=404, detail="Wiscard Cash account not found")
        if balance.balance < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        balance.balance -= request.amount
        db.add(AccessLog(
            user_id=current_user.id,
            service_type="wiscard_cash",
            action=f"purchase_{request.amount}",
            success=True,
            location=request.vendor,
        ))
        db.commit()
        return {
            "success": True,
            "new_balance": balance.balance,
            "amount_charged": request.amount,
            "vendor": request.vendor,
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")


# --------------------------------------------------------------------------- #
# Meal-plan swipes (a count of meals, distinct from dining dollars)
# --------------------------------------------------------------------------- #

@router.get("/dining/swipes")
def get_meal_swipes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get remaining meal-plan swipes."""
    plan = db.query(MealPlan).filter(MealPlan.user_id == current_user.id).first()
    if not plan:
        return {"plan_name": None, "swipes_remaining": 0}
    return {"plan_name": plan.plan_name, "swipes_remaining": plan.swipes_remaining}


@router.post("/dining/swipe")
def use_meal_swipe(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use one meal-plan swipe at a dining hall."""
    try:
        plan = db.query(MealPlan).filter(MealPlan.user_id == current_user.id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="No meal plan on file")
        if plan.swipes_remaining <= 0:
            raise HTTPException(status_code=400, detail="No meal swipes remaining")

        plan.swipes_remaining -= 1
        db.add(AccessLog(
            user_id=current_user.id,
            service_type="dining",
            action="meal_swipe",
            success=True,
        ))
        db.commit()
        return {"success": True, "swipes_remaining": plan.swipes_remaining}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transaction failed: {str(e)}")


# --------------------------------------------------------------------------- #
# Transit (Madison Metro bus pass)
# --------------------------------------------------------------------------- #

@router.get("/transit/pass")
def get_transit_pass(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the student's transit (bus pass) status."""
    transit = db.query(TransitPass).filter(TransitPass.user_id == current_user.id).first()
    if not transit:
        return {"status": "inactive", "semester": "", "valid_until": None}
    return {
        "status": transit.status,
        "semester": transit.semester,
        "valid_until": (transit.valid_until.isoformat() + "Z") if transit.valid_until else None,
    }


# --------------------------------------------------------------------------- #
# Door/building access permissions (read-only, for the student's own card)
# --------------------------------------------------------------------------- #

@router.get("/access-permissions")
def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List the doors/buildings the current student can access."""
    perms = db.query(AccessPermission).filter(
        AccessPermission.user_id == current_user.id
    ).all()
    return {
        "permissions": [
            {"resource_key": p.resource_key, "resource_name": p.resource_name}
            for p in perms
        ]
    }

