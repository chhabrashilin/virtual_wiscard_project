"""
Virtual card endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Balance
from app.utils import generate_access_token, generate_qr_code_data

router = APIRouter(prefix="/api/cards", tags=["cards"])

@router.get("/my-card")
def get_my_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's virtual card information."""
    # Get all balances
    balances = db.query(Balance).filter(Balance.user_id == current_user.id).all()
    balance_dict = {b.service_type: b.balance for b in balances}
    
    return {
        "id": current_user.id,
        "netid": current_user.netid,
        "full_name": current_user.full_name,
        "student_id": current_user.student_id,
        "email": current_user.email,
        "photo_url": current_user.photo_url,
        "is_active": current_user.is_active,
        "expiration_date": current_user.expiration_date.isoformat(),
        "balances": balance_dict
    }

@router.post("/generate-qr")
def generate_qr_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a temporary QR code token for scanning."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    access_token = generate_access_token(db, current_user.id, expires_minutes=5)
    qr_image = generate_qr_code_data(access_token.token)
    
    return {
        "token": access_token.token,
        "expires_at": access_token.expires_at.isoformat(),
        "qr_code": qr_image
    }

@router.get("/balances")
def get_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all service balances for current user."""
    balances = db.query(Balance).filter(Balance.user_id == current_user.id).all()
    return {
        "balances": [
            {
                "service_type": b.service_type,
                "balance": b.balance,
                "last_updated": b.last_updated.isoformat()
            }
            for b in balances
        ]
    }

