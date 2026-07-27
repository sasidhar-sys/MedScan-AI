"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Base ORM Model

Author: Sasidhar A
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from backend.core.database import Base


class BaseModel(Base):
    """
    Abstract base model containing common columns across all database tables.
    """

    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )
