"""Repository for health event persistence."""

import json
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health_event import HealthEvent


class HealthEventRepository:
    """Persist and fetch health events for a user."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        user_id: int,
        event_type: str,
        event_date: date,
        metadata: dict | None = None,
    ) -> HealthEvent:
        event = HealthEvent(
            user_id=user_id,
            event_type=event_type,
            event_date=event_date,
            metadata_json=json.dumps(metadata or {}, default=str),
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def list_for_user(self, user_id: int) -> list[HealthEvent]:
        result = await self.db.execute(
            select(HealthEvent)
            .where(HealthEvent.user_id == user_id)
            .order_by(HealthEvent.event_date.desc())
        )
        return list(result.scalars().all())
