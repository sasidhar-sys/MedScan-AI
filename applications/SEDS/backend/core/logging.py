"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Logging Configuration

Author: Sasidhar A
"""

from pathlib import Path
import sys

from loguru import logger

from backend.core.config import settings


LOG_DIR = Path(settings.LOG_FOLDER)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove()

# Console Logger
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    colorize=True,
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "{message}",
)

# Application Log
logger.add(
    LOG_DIR / "app.log",
    level="INFO",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    enqueue=True,
)

# Error Log
logger.add(
    LOG_DIR / "error.log",
    level="ERROR",
    rotation="10 MB",
    retention="60 days",
    compression="zip",
    enqueue=True,
)

__all__ = ["logger"]
