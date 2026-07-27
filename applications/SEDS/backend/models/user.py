"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
User Model

Author: Sasidhar A
"""

import enum

from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"
    RESEARCHER = "RESEARCHER"


class User(BaseModel):
    __tablename__ = "users"

    full_name = Column(String(150), nullable=False)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.DOCTOR,
    )

    phone = Column(
        String(20),
        nullable=True,
    )

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_superuser = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    doctor_profile = relationship(
        "Doctor",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<User("
            f"email='{self.email}', "
            f"role='{self.role.value}'"
            f")>"
        )
