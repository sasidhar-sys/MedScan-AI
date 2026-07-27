"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Doctor Model

Author: Sasidhar A
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class Doctor(BaseModel):
    __tablename__ = "doctors"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    medical_license_number = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    specialization = Column(
        String(150),
        nullable=False,
    )

    hospital_name = Column(
        String(255),
        nullable=False,
    )

    department = Column(
        String(150),
        nullable=True,
    )

    years_of_experience = Column(
        Integer,
        nullable=False,
        default=0,
    )

    qualification = Column(
        String(255),
        nullable=True,
    )

    profile_photo = Column(
        String(500),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="doctor_profile",
        uselist=False,
    )

    patients = relationship(
        "Patient",
        back_populates="doctor",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Doctor("
            f"license='{self.medical_license_number}', "
            f"specialization='{self.specialization}'"
            f")>"
        )
