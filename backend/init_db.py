"""
Initialize database with dummy student accounts.
"""
from datetime import datetime, timedelta
import os
from app.database import engine, SessionLocal
from app.models import Base, User, Balance
from app.auth import get_password_hash

# Ensure data directory exists
if os.getenv("DATABASE_URL", "").startswith("sqlite:///./data/"):
    os.makedirs("data", exist_ok=True)

def init_database():
    """Create tables and populate with dummy data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
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
                "photo_url": "",
                "dining_balance": 150.50
            },
            {
                "netid": "jsmith",
                "password": "password123",
                "full_name": "Jane Smith",
                "student_id": "87654321",
                "email": "jsmith@wisc.edu",
                "photo_url": "",
                "dining_balance": 75.25
            },
            {
                "netid": "bwilliams",
                "password": "password123",
                "full_name": "Bob Williams",
                "student_id": "11223344",
                "email": "bwilliams@wisc.edu",
                "photo_url": "",
                "dining_balance": 200.00
            }
        ]
        
        for student_data in students:
            user = User(
                netid=student_data["netid"],
                password_hash=get_password_hash(student_data["password"]),
                full_name=student_data["full_name"],
                student_id=student_data["student_id"],
                email=student_data["email"],
                photo_url=student_data["photo_url"],
                is_admin=False,
                is_active=True,
                expiration_date=datetime.utcnow() + timedelta(days=365)
            )
            db.add(user)
            db.flush()  # Get user ID
            
            # Add dining balance
            balance = Balance(
                user_id=user.id,
                service_type="dining",
                balance=student_data["dining_balance"]
            )
            db.add(balance)
        
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

