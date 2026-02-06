"""
Database connection and session management
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from .models import create_db_engine, init_db, get_session_maker

# Initialize engine and session
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session_local():
    """Get or create session maker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = get_session_maker()
    return _SessionLocal


def init_database():
    """Initialize the database (create tables)."""
    init_db()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints.
    Yields a database session and ensures cleanup.
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Use this for non-FastAPI code.
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
