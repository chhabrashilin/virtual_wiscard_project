"""
Authentication utilities for JWT tokens and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration - now from environment variables
DEFAULT_SECRET_KEY = "virtual-wiscard-secret-key-change-in-production"
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

# Fail fast in production if the secret was never configured. In development we
# allow the default but warn loudly so it is obvious in the logs.
if SECRET_KEY == DEFAULT_SECRET_KEY:
    if ENVIRONMENT == "production":
        raise RuntimeError(
            "SECRET_KEY must be set in production. Generate one with: "
            "python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    print(
        "[WARNING] Using the default development SECRET_KEY. "
        "Set SECRET_KEY in your environment before deploying."
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, netid: str, password: str):
    """Authenticate a user by netid and password."""
    user = db.query(User).filter(User.netid == netid).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    if not user.is_active:
        return False
    return user

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        netid: str = payload.get("sub")
        if netid is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.netid == netid).first()
    if user is None:
        raise credentials_exception

    # Check if card is expired. expiration_date is a DateTime, so compare against
    # a datetime (not a date) to avoid a TypeError that would 500 every request.
    if user.expiration_date and user.expiration_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your WisCard has expired. Please contact administration."
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact administration."
        )

    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current user and verify admin status."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

