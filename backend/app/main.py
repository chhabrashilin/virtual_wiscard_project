"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.routers import auth, cards, services, admin, blockchain, wallet, tickets
from app.database import get_db, engine, Base, ensure_schema
from app import models  # noqa: F401  (ensures models are registered on Base)
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Virtual Wiscard API",
    description="Digital student ID system for UW-Madison with Blockchain & Apple Wallet",
    version="2.0.0"
)

# CORS middleware for frontend access - now using environment variables
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://frontend:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(services.router)
app.include_router(admin.router)
app.include_router(blockchain.router)
app.include_router(wallet.router)
app.include_router(tickets.router)

@app.on_event("startup")
def on_startup():
    """Create tables on startup so the API works even if init_db.py wasn't run."""
    Base.metadata.create_all(bind=engine)
    ensure_schema(engine)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Virtual Wiscard API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "JWT Authentication",
            "Virtual Student ID Cards",
            "QR Code Generation + Verifier",
            "Dining Dollars, Wiscard Cash & Meal Swipes",
            "Wisc Print",
            "Permission-based Door/Building Access",
            "Madison Metro Transit Pass",
            "Athletic & Event Ticketing",
            "Lost-card Freeze",
            "Blockchain/NFT Integration",
            "Apple Wallet Pass Generation",
            "Transaction History",
            "Admin Dashboard"
        ]
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Enhanced health check endpoint."""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

