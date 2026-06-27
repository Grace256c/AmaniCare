"""Mock reminder scheduling API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.reminder import ReminderCreate, ReminderListResponse, ReminderResponse
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])


def get_reminder_service(db: AsyncSession = Depends(get_db)) -> ReminderService:
    """Dependency injection for ReminderService."""
    return ReminderService(db)


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def schedule_reminder(
    payload: ReminderCreate,
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderResponse:
    """Schedule a mock SMS reminder for a registered user."""
    try:
        reminder = await service.schedule(payload)
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(exc).lower()
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return ReminderResponse.model_validate(reminder)


@router.get("/{phone_number}", response_model=ReminderListResponse)
async def list_reminders(
    phone_number: str,
    service: ReminderService = Depends(get_reminder_service),
) -> ReminderListResponse:
    """List all scheduled reminders for a user."""
    try:
        reminders = await service.list_for_phone(phone_number)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ReminderListResponse(
        phone_number=phone_number,
        reminders=[ReminderResponse.model_validate(r) for r in reminders],
    )
