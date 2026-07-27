"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Patient Model

Author: Sasidhar A
"""

import enum
from datetime import date

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Patient(BaseModel):
    __tablename__ = "patients"

    doctor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    patient_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name = Column(
        String(100),
        nullable=False,
    )

    last_name = Column(
        String(100),
        nullable=False,
    )

    gender = Column(
        Enum(Gender),
        nullable=False,
    )

    date_of_birth = Column(
        Date,
        nullable=False,
    )

    age = Column(
        Integer,
        nullable=False,
    )

    phone = Column(
        String(20),
        nullable=True,
    )

    email = Column(
        String(255),
        nullable=True,
    )

    address = Column(
        String(500),
        nullable=True,
    )

    blood_group = Column(
        String(5),
        nullable=True,
    )

    emergency_contact_name = Column(
        String(150),
        nullable=True,
    )

    emergency_contact_phone = Column(
        String(20),
        nullable=True,
    )

    doctor = relationship(
        "Doctor",
        back_populates="patients",
    )

    clinical_history = relationship(
        "ClinicalHistory",
        back_populates="patient",
        uselist=False,
        cascade="all, delete-orphan",
    )

    uploaded_images = relationship(
        "UploadedImage",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Patient("
            f"id='{self.patient_id}', "
            f"name='{self.first_name} {self.last_name}'"
            f")>"
        )
