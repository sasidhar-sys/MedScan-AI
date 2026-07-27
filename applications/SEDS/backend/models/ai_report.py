"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
AI Report Model

Author: Sasidhar A
"""

import enum

from sqlalchemy import Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class ReportStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"
    ARCHIVED = "ARCHIVED"


class AIReport(BaseModel):
    __tablename__ = "ai_reports"

    prediction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    report_title = Column(
        String(255),
        nullable=False,
    )

    summary = Column(
        Text,
        nullable=False,
    )

    findings = Column(
        Text,
        nullable=True,
    )

    recommendations = Column(
        Text,
        nullable=True,
    )

    disclaimer = Column(
        Text,
        nullable=False,
        default=(
            "This AI-generated report is intended to assist healthcare "
            "professionals and should not replace clinical judgment."
        ),
    )

    report_pdf_path = Column(
        String(500),
        nullable=True,
    )

    report_status = Column(
        Enum(ReportStatus),
        default=ReportStatus.DRAFT,
        nullable=False,
    )

    prediction = relationship(
        "Prediction",
        back_populates="report",
        uselist=False,
    )

    def __repr__(self):
        return (
            f"<AIReport("
            f"title='{self.report_title}', "
            f"status='{self.report_status.value}'"
            f")>"
        )
