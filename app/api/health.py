"""Health check API routes."""

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(status="ok")
