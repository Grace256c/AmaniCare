"""AI health advice API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.advice import AdviceRequest, AdviceResponse
from app.services.deepseek_service import DeepseekService
from app.services.registration_service import RegistrationService

router = APIRouter(prefix="/api/advice", tags=["Advice"])


def get_registration_service(db: AsyncSession = Depends(get_db)) -> RegistrationService:
    """Dependency injection for RegistrationService."""
    return RegistrationService(db)


def get_deepseek_service() -> DeepseekService:
    """Dependency injection for DeepseekService."""
    return DeepseekService()


@router.post("", response_model=AdviceResponse)
async def ask_advice(
    payload: AdviceRequest,
    registration_service: RegistrationService = Depends(get_registration_service),
    deepseek_service: DeepseekService = Depends(get_deepseek_service),
) -> AdviceResponse:
    """Generate personalized health advice using Deepseek AI."""
    try:
        user = await registration_service.get_user(payload.phone_number)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please register first.",
        )

    try:
        advice = await deepseek_service.generate_advice(user, payload.question)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate advice from AI service",
        ) from exc

    return AdviceResponse(question=payload.question, advice=advice)
