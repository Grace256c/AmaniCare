"""Health event routes for longitudinal health tracking."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.health_event_repository import HealthEventRepository
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/health-events", tags=["Health Events"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_health_event(payload: dict, db: AsyncSession = Depends(get_db)) -> dict:
    """Create a new health event for an existing user."""
    phone_number = payload.get("phone_number")
    event_type = payload.get("event_type")
    event_date = payload.get("event_date")
    metadata = payload.get("metadata") or {}

    if not phone_number or not event_type or not event_date:
        raise HTTPException(status_code=400, detail="phone_number, event_type, and event_date are required")

    if isinstance(event_date, str):
        event_date = date.fromisoformat(event_date)

    user_repo = UserRepository(db)
    user = await user_repo.get_by_phone(phone_number)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    repo = HealthEventRepository(db)
    event = await repo.create(
        user_id=user.id,
        event_type=event_type,
        event_date=event_date,
        metadata=metadata,
    )
    return {
        "id": event.id,
        "event_type": event.event_type,
        "event_date": event.event_date.isoformat(),
        "metadata": metadata,
    }
