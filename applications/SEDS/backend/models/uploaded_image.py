"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Uploaded Medical Image Model

Author: Sasidhar A
"""

import enum

from sqlalchemy import BigInteger, Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class ImageModality(str, enum.Enum):
    ENDOSCOPY = "ENDOSCOPY"
    BIOPSY = "BIOPSY"
    CT = "CT"
    MRI = "MRI"
    PET_CT = "PET_CT"


class UploadStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UploadedImage(BaseModel):
    __tablename__ = "uploaded_images"

    patient_id = Column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    modality = Column(
        Enum(ImageModality),
        nullable=False,
    )

    original_filename = Column(
        String(255),
        nullable=False,
    )

    stored_filename = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    mime_type = Column(
        String(100),
        nullable=False,
    )

    file_size = Column(
        BigInteger,
        nullable=True,
    )

    upload_status = Column(
        Enum(UploadStatus),
        default=UploadStatus.UPLOADED,
        nullable=False,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    patient = relationship(
        "Patient",
        back_populates="uploaded_images",
    )

    predictions = relationship(
        "Prediction",
        back_populates="uploaded_image",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<UploadedImage("
            f"modality='{self.modality.value}', "
            f"file='{self.original_filename}'"
            f")>"
        )
