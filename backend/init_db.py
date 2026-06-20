"""
Initialize database with dummy student accounts.
"""
from datetime import datetime, timedelta
import os
import secrets
from app.database import engine, SessionLocal, ensure_schema
from app.models import (
    Base, User, Balance, AccessLog,
    MealPlan, AccessPermission, TransitPass, Ticket,
)
from app.auth import get_password_hash


def _avatar(name: str) -> str:
    """Deterministic placeholder avatar so the card never looks empty."""
    seed = name.replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={seed}&background=C5050C&color=fff&size=256"


def _seed_history(db, user_id: int):
    """Seed a handful of realistic access logs so history/analytics aren't empty."""
    now = datetime.utcnow()
    sample = [
        ("dining", "payment_8.75", "Gordon Avenue Market", 2),
        ("library", "checkout", "College Library", 26),
        ("residence", "door_access", "Sellery Hall", 30),
        ("dining", "payment_12.50", "Rheta's Market", 50),
        ("print", "print_job", "College Library", 73),
    ]
    for service_type, action, location, hours_ago in sample:
        db.add(AccessLog(
            user_id=user_id,
            service_type=service_type,
            action=action,
            success=True,
            location=location,
            created_at=now - timedelta(hours=hours_ago),
        ))

# Ensure data directory exists
if os.getenv("DATABASE_URL", "").startswith("sqlite:///./data/"):
    os.makedirs("data", exist_ok=True)

def init_database():
    """Create tables and populate with dummy data."""
    # Create all tables and apply lightweight column migrations
    Base.metadata.create_all(bind=engine)
    ensure_schema(engine)
    
    db = SessionLocal()
    
    try:
        # Check if users already exist
        if db.query(User).count() > 0:
            print("Database already initialized.")
            return
        
        # Create admin user
        admin = User(
            netid="admin",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
            student_id="ADMIN001",
            email="admin@wisc.edu",
            photo_url="",
            is_admin=True,
            is_active=True,
            expiration_date=datetime.utcnow() + timedelta(days=365)
        )
        db.add(admin)
        
        # Create dummy students
        students = [
            {
                "netid": "jdoe",
                "password": "password123",
                "full_name": "John Doe",
                "student_id": "12345678",
                "email": "jdoe@wisc.edu",
                "dining_balance": 150.50,
                "print_balance": 25.00,
                "wiscard_cash": 80.00,
                "meal_plan": ("Unlimited", 120),
                "residence": ("sellery_hall", "Sellery Residence Hall"),
                "ticket": ("Badgers vs. Gophers", "Camp Randall Stadium", "Section O, Row 12"),
            },
            {
                "netid": "jsmith",
                "password": "password123",
                "full_name": "Jane Smith",
                "student_id": "87654321",
                "email": "jsmith@wisc.edu",
                "dining_balance": 75.25,
                "print_balance": 10.50,
                "wiscard_cash": 42.50,
                "meal_plan": ("Flex 14", 56),
                "residence": ("witte_hall", "Witte Residence Hall"),
                "ticket": ("Men's Basketball vs. Purdue", "Kohl Center", "Section 116, Row C"),
            },
            {
                "netid": "bwilliams",
                "password": "password123",
                "full_name": "Bob Williams",
                "student_id": "11223344",
                "email": "bwilliams@wisc.edu",
                "dining_balance": 200.00,
                "print_balance": 5.00,
                "wiscard_cash": 15.75,
                "meal_plan": ("Block 80", 31),
                "residence": ("chadbourne_hall", "Chadbourne Residence Hall"),
                "ticket": None,
            }
        ]
        
        for student_data in students:
            user = User(
                netid=student_data["netid"],
                password_hash=get_password_hash(student_data["password"]),
                full_name=student_data["full_name"],
                student_id=student_data["student_id"],
                email=student_data["email"],
                photo_url=_avatar(student_data["full_name"]),
                is_admin=False,
                is_active=True,
                is_frozen=False,
                expiration_date=datetime.utcnow() + timedelta(days=365)
            )
            db.add(user)
            db.flush()  # Get user ID
            
            # Stored-value accounts
            db.add(Balance(user_id=user.id, service_type="dining", balance=student_data["dining_balance"]))
            db.add(Balance(user_id=user.id, service_type="print", balance=student_data["print_balance"]))
            db.add(Balance(user_id=user.id, service_type="wiscard_cash", balance=student_data["wiscard_cash"]))

            # Meal-plan swipes
            plan_name, swipes = student_data["meal_plan"]
            db.add(MealPlan(user_id=user.id, plan_name=plan_name, swipes_remaining=swipes))

            # Door/building access: everyone gets RecWell + their residence hall
            db.add(AccessPermission(
                user_id=user.id, resource_key="recwell", resource_name="RecWell (Nick & Bakke)"
            ))
            res_key, res_name = student_data["residence"]
            db.add(AccessPermission(user_id=user.id, resource_key=res_key, resource_name=res_name))

            # Transit (bus pass)
            db.add(TransitPass(
                user_id=user.id,
                status="active",
                semester="Fall 2026",
                valid_until=datetime.utcnow() + timedelta(days=180),
            ))

            # Sample event ticket
            if student_data["ticket"]:
                event_name, venue, seat = student_data["ticket"]
                db.add(Ticket(
                    user_id=user.id,
                    code=secrets.token_urlsafe(16),
                    event_name=event_name,
                    event_date=datetime.utcnow() + timedelta(days=14),
                    venue=venue,
                    seat=seat,
                    status="valid",
                ))

            # Seed some activity history
            _seed_history(db, user.id)
        
        db.commit()
        print("Database initialized successfully!")
        print("\nTest accounts created:")
        print("Admin: netid='admin', password='admin123'")
        print("Students: netid='jdoe'/'jsmith'/'bwilliams', password='password123'")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

