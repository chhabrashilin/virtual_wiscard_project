"""
Utility functions for QR code generation and token management.
"""
import secrets
import qrcode
import io
import base64
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import AccessToken, User

def generate_qr_code_data(token: str) -> str:
    """Generate QR code image as base64 string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def generate_access_token(db: Session, user_id: int, expires_minutes: int = 5) -> AccessToken:
    """Generate a temporary access token for QR/NFC scanning."""
    # Generate secure random token
    token = secrets.token_urlsafe(32)
    
    # Create token record
    access_token = AccessToken(
        user_id=user_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
        is_revoked=False
    )
    db.add(access_token)
    db.commit()
    db.refresh(access_token)
    return access_token

def validate_access_token(db: Session, token: str) -> User:
    """Validate an access token and return the associated user."""
    access_token = db.query(AccessToken).filter(
        AccessToken.token == token,
        AccessToken.is_revoked == False,
        AccessToken.expires_at > datetime.utcnow()
    ).first()
    
    if not access_token:
        return None
    
    user = db.query(User).filter(User.id == access_token.user_id).first()
    if not user or not user.is_active or user.is_frozen:
        return None
    
    return user

