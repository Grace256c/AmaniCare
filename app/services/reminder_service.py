"""Mock reminder scheduling service."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_phone_number
from app.models.reminder import Reminder, ReminderType
from app.repositories.reminder_repository import ReminderRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reminder import ReminderCreate
from app.services.sms_service import AfricaTalkingSMSService
from datetime import date, datetime, timedelta


def _parse_date(value: date | str | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


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
        self.sms_service = AfricaTalkingSMSService()
        self.db = db

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
            "Reminder scheduled: {} ({}) on {}",
            phone,
            reminder_type.value,
            data.next_date,
        )
        message = (
            f"MamaCare reminder: {reminder_type.value.replace('_', ' ')} is due on {data.next_date}."
        )
        await self.sms_service.send_sms(phone, message)
        return reminder

    async def list_for_phone(self, phone_number: str) -> list[Reminder]:
        """Return all reminders for a phone number."""
        phone = validate_phone_number(phone_number)
        return await self.reminder_repo.list_by_phone(phone)

    async def generate_reminders_for_user(self, user: object) -> list[Reminder]:
        """Create reminders based on user's life stage and stored dates.

        Returns list of created Reminder objects.
        """
        created: list[Reminder] = []

        async def add_if_missing(reminder_type: ReminderType, next_date: date) -> None:
            existing = await self.reminder_repo.get_existing(
                user_id=user.id,
                phone_number=user.phone_number,
                reminder_type=reminder_type,
                next_date=next_date,
            )
            if existing is not None:
                return

            reminder = await self.reminder_repo.create(
                user_id=user.id,
                phone_number=user.phone_number,
                reminder_type=reminder_type,
                next_date=next_date,
            )
            created.append(reminder)

        # Menstrual health and fertility
        last_period = _parse_date(getattr(user, "last_period_date", None))
        cycle_length = getattr(user, "cycle_length", None) or 28

        if last_period:
            next_period = last_period + timedelta(days=cycle_length)
            fertile_day = last_period + timedelta(days=cycle_length - 14)
            fertile_start = fertile_day - timedelta(days=5)
            fertile_end = fertile_day + timedelta(days=1)

            # 3 days before expected period
            await add_if_missing(ReminderType.PERIOD_DUE, next_period - timedelta(days=3))
            # on expected period date
            await add_if_missing(ReminderType.PERIOD, next_period)
            # 2 days before fertile window
            await add_if_missing(ReminderType.FERTILE_WINDOW, fertile_start - timedelta(days=2))

        # Trying to conceive
        life_stage = getattr(user, "life_stage", None)
        if life_stage in {"TryingToConceive", getattr(life_stage, "value", None)} and last_period:
            fertile_day = last_period + timedelta(days=cycle_length - 14)
            fertile_start = fertile_day - timedelta(days=5)
            # Fertile window starts tomorrow
            await add_if_missing(ReminderType.FERTILE_WINDOW, fertile_start + timedelta(days=1))
            # Ovulation reminder
            await add_if_missing(ReminderType.OVULATION, fertile_day)

        # Pregnancy
        conception = _parse_date(getattr(user, "conception_date", None))
        if conception:
            # estimated due date
            edd = conception + timedelta(days=280)
            # week reminders
            weeks = [12, 20, 28, 36]
            for w in weeks:
                await add_if_missing(ReminderType.ANC_VISIT, conception + timedelta(weeks=w))

        # Postpartum
        delivery = _parse_date(getattr(user, "delivery_date", None))
        if delivery:
            await add_if_missing(ReminderType.POSTNATAL_CHECK, delivery + timedelta(weeks=1))
            await add_if_missing(ReminderType.POSTNATAL_CHECK, delivery + timedelta(weeks=2))
            await add_if_missing(ReminderType.POSTNATAL_CHECK, delivery + timedelta(weeks=6))

        # Menopause/perimenopause weekly wellness
        if life_stage in {"Perimenopause", "Menopause", getattr(life_stage, "value", None)}:
            await add_if_missing(
                ReminderType.WEEKLY_WELLNESS,
                datetime.utcnow().date() + timedelta(days=7),
            )

        return created
