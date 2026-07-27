import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.models import (
    BaseModel,
    User,
    UserRole,
    Doctor,
    Patient,
    Gender,
    ClinicalHistory,
    UploadedImage,
    ImageModality,
    UploadStatus,
    Prediction,
    PredictionStatus,
    RiskLevel,
    AIReport,
    ReportStatus,
    AuditLog,
    AuditAction,
)

models = [User, Doctor, Patient, ClinicalHistory, UploadedImage, Prediction, AIReport, AuditLog]

print("All Models Successfully Loaded! ✅\n")
for m in models:
    print(f"Table: {m.__tablename__:<20} -> {m}")
