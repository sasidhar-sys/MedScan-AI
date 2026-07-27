"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Main FastAPI Application

Author: Sasidhar A
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SEDS Backend Started")
    yield
    logger.info("SEDS Backend Shutting down...")


app = FastAPI(
    title="Smart Esophageal Diagnosis System (SEDS)",
    description="AI-powered Clinical Decision Support System for Early Esophageal Cancer Detection.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "company": settings.COMPANY_NAME,
        "project": settings.PROJECT_NAME,
        "short_name": settings.PROJECT_SHORT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_SHORT_NAME,
    }
