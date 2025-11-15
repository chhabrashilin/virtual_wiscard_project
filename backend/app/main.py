"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, cards, services, admin

app = FastAPI(
    title="Virtual Wiscard API",
    description="Digital student ID system for UW-Madison",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(services.router)
app.include_router(admin.router)

@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Virtual Wiscard API", "status": "running"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

