"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Core Database Module

Creates the SQLAlchemy engine and session management.

Author: Sasidhar A
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings


DATABASE_URL = settings.DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    """
    FastAPI dependency.

    Returns a database session.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
