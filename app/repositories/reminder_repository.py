"""Reminder data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder, ReminderType


class ReminderRepository:
    """Repository for reminder CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        user_id: int,
        phone_number: str,
        reminder_type: ReminderType,
        next_date,
    ) -> Reminder:
        """Schedule a new reminder."""
        reminder = Reminder(
            user_id=user_id,
            phone_number=phone_number,
            reminder_type=reminder_type,
            next_date=next_date,
        )
        self.db.add(reminder)
        await self.db.flush()
        await self.db.refresh(reminder)
        return reminder

    async def list_by_phone(self, phone_number: str) -> list[Reminder]:
        """Return all reminders for a phone number."""
        result = await self.db.execute(
            select(Reminder)
            .where(Reminder.phone_number == phone_number)
            .order_by(Reminder.next_date.asc())
        )
        return list(result.scalars().all())
