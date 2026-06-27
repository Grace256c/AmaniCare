"""Reminder data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder, ReminderType


class ReminderRepository:
    """Repository for reminder CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_existing(
        self,
        *,
        user_id: int,
        phone_number: str,
        reminder_type: ReminderType,
        next_date,
    ) -> Reminder | None:
        """Return an existing reminder matching the same key, if present."""
        result = await self.db.execute(
            select(Reminder).where(
                Reminder.user_id == user_id,
                Reminder.phone_number == phone_number,
                Reminder.reminder_type == reminder_type,
                Reminder.next_date == next_date,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: int,
        phone_number: str,
        reminder_type: ReminderType,
        next_date,
    ) -> Reminder:
        """Schedule a new reminder or return an existing one for the same key."""
        existing_reminder = await self.get_existing(
            user_id=user_id,
            phone_number=phone_number,
            reminder_type=reminder_type,
            next_date=next_date,
        )
        if existing_reminder is not None:
            return existing_reminder

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
