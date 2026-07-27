"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Backend Configuration

Author: Sasidhar A
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings.
    Automatically loads values from the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =====================================================
    # COMPANY & PRODUCT
    # =====================================================

    COMPANY_NAME: str = Field(default="MedScan AI")
    PROJECT_NAME: str = Field(default="Smart Esophageal Diagnosis System")
    PROJECT_SHORT_NAME: str = Field(default="SEDS")
    PROJECT_VERSION: str = Field(default="1.0.0")

    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # =====================================================
    # SERVER
    # =====================================================

    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL: str = Field(default="postgresql://postgres:changeme@localhost:5432/seds_db")

    # =====================================================
    # JWT
    # =====================================================

    SECRET_KEY: str = Field(default="CHANGE_THIS_TO_A_RANDOM_64_CHARACTER_SECRET")

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # =====================================================
    # MODEL PATHS
    # =====================================================

    ENDOSCOPY_MODEL: str = "models/endoscopy/weights/endoscopy_best.pth"

    BIOPSY_MODEL: str = "models/biopsy/weights/biopsy_best.pth"

    CLINICAL_MODEL: str = "models/clinical/weights/clinical_best.pkl"

    FUSION_MODEL: str = "models/fusion/weights/fusion_best.pth"

    # =====================================================
    # DATASET PATHS
    # =====================================================

    ENDOSCOPY_DATASET: str = "datasets/endoscopy"

    BIOPSY_DATASET: str = "datasets/biopsy"

    CLINICAL_DATASET: str = "datasets/clinical"

    # =====================================================
    # STORAGE
    # =====================================================

    UPLOAD_FOLDER: str = "uploads"

    REPORT_FOLDER: str = "reports"

    LOG_FOLDER: str = "logs"

    MAX_UPLOAD_SIZE_MB: int = 100

    # =====================================================
    # EXPLAINABILITY
    # =====================================================

    ENABLE_GRADCAM: bool = True

    ENABLE_SCORECAM: bool = True

    ENABLE_SHAP: bool = True

    # =====================================================
    # CHATBOT
    # =====================================================

    GEMINI_API_KEY: str = ""

    VECTOR_DB: str = "vector_db"

    # =====================================================
    # LOGGING
    # =====================================================

    LOG_LEVEL: str = "INFO"

    # =====================================================
    # CORS
    # =====================================================

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        """
        Returns allowed origins as a list.
        """
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """
    Returns a singleton Settings instance.
    """
    return Settings()


settings = get_settings()
