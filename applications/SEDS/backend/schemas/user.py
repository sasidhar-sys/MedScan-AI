"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
User Pydantic Schemas

Author: Sasidhar A
"""

from uuid import UUID
from pydantic import BaseModel, EmailStr
from backend.models.user import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.DOCTOR
    phone: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    phone: str | None = None
    is_verified: bool
    is_superuser: bool

    model_config = {
        "from_attributes": True
    }
