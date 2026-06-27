"""User data access layer."""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import LifeStage, User
from app.models.reproductive_profile import ReproductiveProfile


def _normalize_date(value: object | None) -> date | None:
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value))


class UserRepository:
    """Repository for User CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_phone(self, phone_number: str) -> User | None:
        """Fetch a user by phone number."""
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        phone_number: str,
        name: str,
        age: int,
        life_stage: LifeStage,
        language: str = "English",
        sms_opt_in: bool = False,
        preferred_language: str = "English",
        sms_opt_out_at: object | None = None,
        last_sms_sent_at: object | None = None,
        full_name: str | None = None,
        date_of_birth: object | None = None,
        district: str | None = None,
        country: str | None = None,
        voice_opt_in: bool = False,
        whatsapp_opt_in: bool = False,
        preferred_contact_time: str | None = None,
        blood_group: str | None = None,
        allergies: str | None = None,
        chronic_conditions: str | None = None,
        medications: str | None = None,
        disabilities: str | None = None,
        menarche_age: int | None = None,
        currently_menstruating: bool | None = None,
        cycle_regular: bool | None = None,
        average_cycle_length: int | None = None,
        average_period_length: int | None = None,
        contraception_method: str | None = None,
        trying_to_conceive: bool | None = None,
        menopause_status: str | None = None,
        pregnancy_history_count: int | None = None,
        miscarriage_history_count: int | None = None,
        c_section_history_count: int | None = None,
        age_at_first_period: int | None = None,
        symptom_patterns: str | None = None,
        last_period_date: object | None = None,
        cycle_length: int | None = None,
        conception_date: object | None = None,
        estimated_due_date: object | None = None,
        pregnancy_week: int | None = None,
        gestational_age: int | None = None,
        trimester: str | None = None,
        delivery_date: object | None = None,
        delivery_type: str | None = None,
        breastfeeding_status: str | None = None,
        symptom_preferences: str | None = None,
        hot_flashes: bool | None = None,
        sleep_changes: bool | None = None,
        mood_changes: bool | None = None,
        bone_health: bool | None = None,
        night_sweats: bool | None = None,
        menopause_preferences: str | None = None,
    ) -> User:
        """Create a new user record."""
        user = User(
            phone_number=phone_number,
            name=name,
            age=age,
            life_stage=life_stage,
            language=language,
            sms_opt_in=sms_opt_in,
            preferred_language=preferred_language,
            sms_opt_out_at=sms_opt_out_at,
            last_sms_sent_at=last_sms_sent_at,
            full_name=full_name,
            date_of_birth=_normalize_date(date_of_birth),
            district=district,
            country=country,
            voice_opt_in=voice_opt_in,
            whatsapp_opt_in=whatsapp_opt_in,
            preferred_contact_time=preferred_contact_time,
            blood_group=blood_group,
            allergies=allergies,
            chronic_conditions=chronic_conditions,
            medications=medications,
            disabilities=disabilities,
            menarche_age=menarche_age,
            currently_menstruating=currently_menstruating,
            cycle_regular=cycle_regular,
            average_cycle_length=average_cycle_length,
            average_period_length=average_period_length,
            contraception_method=contraception_method,
            trying_to_conceive=trying_to_conceive,
            menopause_status=menopause_status,
            pregnancy_history_count=pregnancy_history_count,
            miscarriage_history_count=miscarriage_history_count,
            c_section_history_count=c_section_history_count,
            age_at_first_period=age_at_first_period,
            symptom_patterns=symptom_patterns,
            last_period_date=_normalize_date(last_period_date),
            cycle_length=cycle_length,
            conception_date=_normalize_date(conception_date),
            estimated_due_date=_normalize_date(estimated_due_date),
            pregnancy_week=pregnancy_week,
            gestational_age=gestational_age,
            trimester=trimester,
            delivery_date=_normalize_date(delivery_date),
            delivery_type=delivery_type,
            breastfeeding_status=breastfeeding_status,
            symptom_preferences=symptom_preferences,
            hot_flashes=hot_flashes,
            sleep_changes=sleep_changes,
            mood_changes=mood_changes,
            bone_health=bone_health,
            night_sweats=night_sweats,
            menopause_preferences=menopause_preferences,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        # Auto-create reproductive profile
        profile = ReproductiveProfile(user_id=user.id)
        self.db.add(profile)
        await self.db.flush()
        await self.db.refresh(profile)
        user.reproductive_profile_id = profile.id

        return user

    async def update(self, user: User, **fields: object) -> User:
        """Update mutable user fields and sync to reproductive profile if present."""
        reproductive_fields = {
            "menarche_age", "currently_menstruating", "cycle_regular", "average_cycle_length",
            "average_period_length", "contraception_method", "trying_to_conceive",
            "menopause_status", "pregnancy_history_count", "miscarriage_history_count",
            "c_section_history_count", "age_at_first_period", "symptom_patterns",
            "last_period_date", "cycle_length", "conception_date", "estimated_due_date",
            "pregnancy_week", "gestational_age", "trimester", "delivery_date",
            "delivery_type", "breastfeeding_status", "symptom_preferences",
            "hot_flashes", "sleep_changes", "mood_changes", "bone_health",
            "night_sweats", "menopause_preferences",
        }

        profile_updates = {}
        for key, value in fields.items():
            if value is None or not hasattr(user, key):
                continue
            if key in reproductive_fields:
                if key in {"date_of_birth", "conception_date", "estimated_due_date", "delivery_date", "last_period_date"}:
                    profile_updates[key] = _normalize_date(value)
                    setattr(user, key, _normalize_date(value))
                else:
                    profile_updates[key] = value
                    setattr(user, key, value)
            else:
                if key in {"date_of_birth", "last_period_date", "conception_date", "estimated_due_date", "delivery_date"}:
                    setattr(user, key, _normalize_date(value))
                else:
                    setattr(user, key, value)

        await self.db.flush()
        await self.db.refresh(user)

        # Sync reproductive updates to profile if it exists
        if profile_updates and user.reproductive_profile_id:
            from app.repositories.reproductive_profile_repository import ReproductiveProfileRepository
            profile_repo = ReproductiveProfileRepository(self.db)
            profile = await profile_repo.get_by_user_id(user.id)
            if profile:
                await profile_repo.update(profile, **profile_updates)

        return user
