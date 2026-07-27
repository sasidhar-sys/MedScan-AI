"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Audit Log Model

Author: Sasidhar A
"""

import enum

from sqlalchemy import Column, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class AuditAction(str, enum.Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    UPLOAD = "UPLOAD"
    AI_PREDICTION = "AI_PREDICTION"
    REPORT_GENERATED = "REPORT_GENERATED"


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action = Column(
        Enum(AuditAction),
        nullable=False,
        index=True,
    )

    resource_type = Column(
        String(100),
        nullable=False,
    )

    resource_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    ip_address = Column(
        String(45),
        nullable=True,
    )

    user_agent = Column(
        Text,
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="audit_logs",
    )

    def __repr__(self):
        return (
            f"<AuditLog("
            f"action='{self.action.value}', "
            f"resource='{self.resource_type}'"
            f")>"
        )
