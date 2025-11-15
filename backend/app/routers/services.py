"""
Service integration endpoints (dining, library, residence, etc.).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Balance, AccessLog
from app.utils import validate_access_token

router = APIRouter(prefix="/api/services", tags=["services"])

class ServiceAccessRequest(BaseModel):
    """Request model for service access."""
    token: str
    service_type: str
    action: str = "entry"

@router.post("/access")
def access_service(
    request: ServiceAccessRequest,
    db: Session = Depends(get_db)
):
    """Validate access token and grant service access (for scanning)."""
    user = validate_access_token(db, request.token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Log access attempt
    log = AccessLog(
        user_id=user.id,
        service_type=request.service_type,
        action=request.action,
        success=True
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
        "action": request.action
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

@router.post("/dining/use")
def use_dining_balance(
    request: DiningUseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use dining balance (simulate payment)."""
    amount = request.amount
    balance = db.query(Balance).filter(
        Balance.user_id == current_user.id,
        Balance.service_type == "dining"
    ).first()
    
    if not balance:
        raise HTTPException(status_code=404, detail="Dining balance not found")
    
    if balance.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    balance.balance -= amount
    db.commit()
    
    # Log transaction
    log = AccessLog(
        user_id=current_user.id,
        service_type="dining",
        action=f"payment_{amount}",
        success=True
    )
    db.add(log)
    db.commit()
    
    return {"success": True, "new_balance": balance.balance}

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

