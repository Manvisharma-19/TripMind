"""
Database connection setup.
Uses SQLite by default so you can run this locally with zero setup;
swap DATABASE_URL to a Postgres URL (e.g. Neon/Supabase) for deployment.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tripmind.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency - yields a DB session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()