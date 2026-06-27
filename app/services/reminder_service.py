"""Mock reminder scheduling service."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_phone_number
from app.models.reminder import Reminder, ReminderType
from app.repositories.reminder_repository import ReminderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reminder import ReminderCreate


class ReminderService:
    """Schedules mock SMS reminders for registered users."""

    TYPE_MAP = {
        "period": ReminderType.PERIOD,
        "medication": ReminderType.MEDICATION,
        "pregnancy_checkin": ReminderType.PREGNANCY_CHECKIN,
        "menopause_wellness": ReminderType.MENOPAUSE_WELLNESS,
    }

    def __init__(self, db: AsyncSession) -> None:
        self.reminder_repo = ReminderRepository(db)
        self.user_repo = UserRepository(db)

    async def schedule(self, data: ReminderCreate) -> Reminder:
        """
        Schedule a mock reminder for a registered user.

        Raises:
            ValueError: When the user is not found.
        """
        phone = validate_phone_number(data.phone_number)
        user = await self.user_repo.get_by_phone(phone)
        if not user:
            raise ValueError("User not found. Register before scheduling reminders.")

        reminder_type = self.TYPE_MAP[data.type.value]
        reminder = await self.reminder_repo.create(
            user_id=user.id,
            phone_number=phone,
            reminder_type=reminder_type,
            next_date=data.next_date,
        )
        logger.info(
            "Mock reminder scheduled: {} ({}) on {}",
            phone,
            reminder_type.value,
            data.next_date,
        )
        return reminder

    async def list_for_phone(self, phone_number: str) -> list[Reminder]:
        """Return all reminders for a phone number."""
        phone = validate_phone_number(phone_number)
        return await self.reminder_repo.list_by_phone(phone)
