"""
Database models for Virtual Wiscard system.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """Student user model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    netid = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    student_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    photo_url = Column(String, default="")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    expiration_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    balances = relationship("Balance", back_populates="user", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="user", cascade="all, delete-orphan")

class Balance(Base):
    """Service balance model (dining, etc.)."""
    __tablename__ = "balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_type = Column(String, nullable=False)  # 'dining', 'print', etc.
    balance = Column(Float, default=0.0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="balances")

class AccessToken(Base):
    """Temporary QR/NFC access tokens."""
    __tablename__ = "access_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_revoked = Column(Boolean, default=False)

class AccessLog(Base):
    """Log of access attempts and service usage."""
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_type = Column(String, nullable=False)  # 'dining', 'library', 'residence', etc.
    action = Column(String, nullable=False)  # 'entry', 'checkout', 'payment', etc.
    timestamp = Column(DateTime, server_default=func.now())
    success = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="access_logs")

