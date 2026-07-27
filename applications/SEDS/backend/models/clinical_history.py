"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Clinical History Model

Author: Sasidhar A
"""

from sqlalchemy import Boolean, Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class ClinicalHistory(BaseModel):
    __tablename__ = "clinical_histories"

    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    chief_complaint = Column(
        Text,
        nullable=True,
    )

    symptoms = Column(
        Text,
        nullable=True,
    )

    medical_history = Column(
        Text,
        nullable=True,
    )

    surgical_history = Column(
        Text,
        nullable=True,
    )

    family_history = Column(
        Text,
        nullable=True,
    )

    allergies = Column(
        Text,
        nullable=True,
    )

    current_medications = Column(
        Text,
        nullable=True,
    )

    smoking_history = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    alcohol_history = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    patient = relationship(
        "Patient",
        back_populates="clinical_history",
        uselist=False,
    )

    def __repr__(self):
        return f"<ClinicalHistory(patient_id='{self.patient_id}')>"
