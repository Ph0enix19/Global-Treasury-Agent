"""Service health endpoint."""

import os

from fastapi import APIRouter

from app.models.schemas import HealthResponse


router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check() -> HealthResponse:
    demo_mode = os.getenv("DEMO_MODE", "true").lower() != "false"
    return HealthResponse(
        status="ok",
        service="Treasurer.ai",
        mode="demo" if demo_mode else "configured",
    )
