"""
Virtual card endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Balance, AccessLog, MealPlan, AccessPermission, TransitPass
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

    meal_plan = db.query(MealPlan).filter(MealPlan.user_id == current_user.id).first()
    transit = db.query(TransitPass).filter(TransitPass.user_id == current_user.id).first()
    permissions = db.query(AccessPermission).filter(
        AccessPermission.user_id == current_user.id
    ).all()

    return {
        "id": current_user.id,
        "netid": current_user.netid,
        "full_name": current_user.full_name,
        "student_id": current_user.student_id,
        "email": current_user.email,
        "photo_url": current_user.photo_url,
        "is_active": current_user.is_active,
        "is_frozen": current_user.is_frozen,
        "expiration_date": current_user.expiration_date.isoformat(),
        "balances": balance_dict,
        "meal_plan": {
            "plan_name": meal_plan.plan_name,
            "swipes_remaining": meal_plan.swipes_remaining,
        } if meal_plan else None,
        "transit_pass": {
            "status": transit.status,
            "semester": transit.semester,
            "valid_until": (transit.valid_until.isoformat() + "Z") if transit and transit.valid_until else None,
        } if transit else None,
        "permissions": [
            {"resource_key": p.resource_key, "resource_name": p.resource_name}
            for p in permissions
        ],
    }


@router.post("/freeze")
def freeze_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Student-initiated freeze (e.g. lost card). Blocks all scans until unfrozen."""
    current_user.is_frozen = True
    db.commit()
    return {"success": True, "is_frozen": True, "message": "Your card is frozen."}


@router.post("/unfreeze")
def unfreeze_card(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverse a student-initiated freeze."""
    current_user.is_frozen = False
    db.commit()
    return {"success": True, "is_frozen": False, "message": "Your card is active again."}


@router.post("/generate-qr")
def generate_qr_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a temporary QR code token for scanning."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    if current_user.is_frozen:
        raise HTTPException(status_code=403, detail="Your card is frozen. Unfreeze it to generate a code.")
    
    access_token = generate_access_token(db, current_user.id, expires_minutes=5)
    qr_image = generate_qr_code_data(access_token.token)
    
    return {
        "token": access_token.token,
        # expires_at is stored as naive UTC; mark it as UTC ("Z") so the browser
        # does not misinterpret it as local time (which broke the countdown timer).
        "expires_at": access_token.expires_at.isoformat() + "Z",
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

@router.get("/transaction-history")
def get_transaction_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get transaction history for current user."""
    logs = db.query(AccessLog).filter(
        AccessLog.user_id == current_user.id
    ).order_by(AccessLog.created_at.desc()).limit(limit).all()

    return {
        "transactions": [
            {
                "id": log.id,
                "service_type": log.service_type,
                "action": log.action,
                "success": log.success,
                "location": log.location,
                # Mark naive UTC timestamps as UTC so the browser renders them
                # in the user's local time correctly.
                "created_at": log.created_at.isoformat() + "Z"
            }
            for log in logs
        ]
    }

