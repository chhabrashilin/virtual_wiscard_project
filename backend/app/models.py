"""
Database models for Virtual Wiscard system.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index
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
    is_frozen = Column(Boolean, default=False)  # student-initiated lost-card freeze
    expiration_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    balances = relationship("Balance", back_populates="user", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="user", cascade="all, delete-orphan")
    access_tokens = relationship("AccessToken", back_populates="user", cascade="all, delete-orphan")
    meal_plan = relationship("MealPlan", back_populates="user", uselist=False, cascade="all, delete-orphan")
    permissions = relationship("AccessPermission", back_populates="user", cascade="all, delete-orphan")
    transit_pass = relationship("TransitPass", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")

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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    is_revoked = Column(Boolean, default=False)

    user = relationship("User", back_populates="access_tokens")

class AccessLog(Base):
    """Log of access attempts and service usage."""
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    service_type = Column(String, nullable=False, index=True)  # 'dining', 'library', 'residence', etc.
    action = Column(String, nullable=False)  # 'entry', 'checkout', 'payment', etc.
    created_at = Column(DateTime, server_default=func.now(), index=True)  # Renamed from timestamp for consistency
    success = Column(Boolean, default=True)
    location = Column(String, nullable=True)  # Optional location field

    user = relationship("User", back_populates="access_logs")

    # Composite index for common query pattern
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_service_created', 'service_type', 'created_at'),
    )


class MealPlan(Base):
    """Meal-plan swipes (a count of meals, distinct from dining dollars)."""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    plan_name = Column(String, default="Flex")
    swipes_remaining = Column(Integer, default=0)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="meal_plan")


class AccessPermission(Base):
    """A grant allowing a user through a specific door/building/resource."""
    __tablename__ = "access_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_key = Column(String, nullable=False)   # e.g. 'recwell', 'sellery_hall'
    resource_name = Column(String, nullable=False)  # human label
    granted_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="permissions")

    __table_args__ = (
        Index('idx_user_resource', 'user_id', 'resource_key', unique=True),
    )


class TransitPass(Base):
    """Madison Metro bus-pass eligibility tied to the Wiscard."""
    __tablename__ = "transit_passes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    status = Column(String, default="active")  # 'active' | 'inactive'
    semester = Column(String, default="")
    valid_until = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="transit_pass")


class Ticket(Base):
    """An athletic/event ticket issued to a student, validated at the gate."""
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    event_name = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=True)
    venue = Column(String, default="")
    seat = Column(String, nullable=True)
    status = Column(String, default="valid")  # 'valid' | 'used' | 'void'
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="tickets")

