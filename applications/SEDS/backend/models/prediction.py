"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Prediction Model

Author: Sasidhar A
"""

import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class PredictionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Prediction(BaseModel):
    __tablename__ = "predictions"

    uploaded_image_id = Column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_images.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    predicted_class = Column(
        String(100),
        nullable=False,
    )

    confidence_score = Column(
        Float,
        nullable=False,
    )

    risk_level = Column(
        Enum(RiskLevel),
        nullable=False,
    )

    model_name = Column(
        String(150),
        nullable=False,
    )

    model_version = Column(
        String(50),
        nullable=False,
    )

    inference_time_ms = Column(
        Integer,
        nullable=True,
    )

    gradcam_path = Column(
        String(500),
        nullable=True,
    )

    explanation = Column(
        Text,
        nullable=True,
    )

    prediction_status = Column(
        Enum(PredictionStatus),
        default=PredictionStatus.PENDING,
        nullable=False,
    )

    uploaded_image = relationship(
        "UploadedImage",
        back_populates="predictions",
    )

    report = relationship(
        "AIReport",
        back_populates="prediction",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<Prediction("
            f"class='{self.predicted_class}', "
            f"confidence={self.confidence_score:.2f}"
            f")>"
        )
