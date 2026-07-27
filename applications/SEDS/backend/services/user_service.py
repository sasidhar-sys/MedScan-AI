"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
User Business Logic Service

Author: Sasidhar A
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.utils.password import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user record by email address.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user record with hashed password.
    """
    existing_user = get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    hashed = hash_password(user_in.password)
    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        password_hash=hashed,
        role=user_in.role,
        phone=user_in.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
