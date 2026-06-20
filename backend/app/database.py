"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./virtual_wiscard.db")

# Ensure data directory exists for Docker
if DATABASE_URL.startswith("sqlite:///./data/"):
    os.makedirs("data", exist_ok=True)

SQLALCHEMY_DATABASE_URL = DATABASE_URL

# check_same_thread is a SQLite-only argument. Passing it to other drivers
# (e.g. PostgreSQL) raises a TypeError, so apply it conditionally.
connect_args = (
    {"check_same_thread": False}
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Columns added after the initial schema. create_all() creates new *tables* but
# never alters existing ones, so we add missing columns here. This is a minimal
# stand-in for a full migration tool (Alembic); it only runs for SQLite, where
# new dev databases are common and ALTER TABLE ADD COLUMN is safe.
_ADDED_COLUMNS = {
    "users": [("is_frozen", "BOOLEAN DEFAULT 0")],
}


def ensure_schema(target_engine=engine):
    """Idempotently add any columns introduced after the initial schema."""
    if target_engine.url.get_backend_name() != "sqlite":
        return
    inspector = inspect(target_engine)
    existing_tables = inspector.get_table_names()
    for table, columns in _ADDED_COLUMNS.items():
        if table not in existing_tables:
            continue
        present = {c["name"] for c in inspector.get_columns(table)}
        for name, ddl in columns:
            if name not in present:
                with target_engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))

