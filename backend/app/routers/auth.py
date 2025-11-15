"""
Authentication endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    user: dict

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint - accepts netid as username."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect netid or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.netid}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "netid": user.netid,
            "full_name": user.full_name,
            "student_id": user.student_id,
            "email": user.email,
            "photo_url": user.photo_url,
            "is_admin": user.is_admin
        }
    }

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": current_user.id,
        "netid": current_user.netid,
        "full_name": current_user.full_name,
        "student_id": current_user.student_id,
        "email": current_user.email,
        "photo_url": current_user.photo_url,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "expiration_date": current_user.expiration_date.isoformat()
    }

