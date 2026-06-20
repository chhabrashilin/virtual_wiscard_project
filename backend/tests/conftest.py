"""
Shared pytest fixtures: an isolated in-memory database, seeded users, a TestClient
with the get_db dependency overridden, and a helper to fetch auth tokens.
"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import get_password_hash
from app.database import Base, get_db
from app.main import app
from app.models import (
    Balance, User, MealPlan, AccessPermission, TransitPass, Ticket,
)

# A single shared in-memory SQLite database for the whole test session.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _seed(db):
    """Create one admin and one student (with balances)."""
    admin = User(
        netid="admin",
        password_hash=get_password_hash("admin123"),
        full_name="Admin User",
        student_id="ADMIN001",
        email="admin@wisc.edu",
        is_admin=True,
        is_active=True,
        expiration_date=datetime.utcnow() + timedelta(days=365),
    )
    student = User(
        netid="jdoe",
        password_hash=get_password_hash("password123"),
        full_name="John Doe",
        student_id="12345678",
        email="jdoe@wisc.edu",
        is_admin=False,
        is_active=True,
        expiration_date=datetime.utcnow() + timedelta(days=365),
    )
    db.add_all([admin, student])
    db.flush()
    db.add(Balance(user_id=student.id, service_type="dining", balance=50.0))
    db.add(Balance(user_id=student.id, service_type="print", balance=10.0))
    db.add(Balance(user_id=student.id, service_type="wiscard_cash", balance=40.0))
    db.add(MealPlan(user_id=student.id, plan_name="Flex", swipes_remaining=3))
    db.add(AccessPermission(
        user_id=student.id, resource_key="recwell", resource_name="RecWell"
    ))
    db.add(TransitPass(
        user_id=student.id, status="active", semester="Fall 2026",
        valid_until=datetime.utcnow() + timedelta(days=120),
    ))
    db.add(Ticket(
        user_id=student.id, code="TEST-TICKET-CODE", event_name="Badgers vs. Gophers",
        venue="Camp Randall", seat="Section O", status="valid",
    ))
    db.commit()


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _seed(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_header(client):
    def _login(netid: str, password: str) -> dict:
        resp = client.post(
            "/api/auth/login",
            data={"username": netid, "password": password},
        )
        assert resp.status_code == 200, resp.text
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login
