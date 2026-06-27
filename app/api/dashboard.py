"""Analytics endpoints for the women’s health platform."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.reminder import Reminder, ReminderType
from app.models.sms_message import SMSMessage
from app.models.user import LifeStage, User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    """Return lightweight health-platform analytics for the dashboard."""
    registered_users = await db.scalar(select(func.count()).select_from(User))
    active_users = await db.scalar(
        select(func.count())
        .select_from(User)
        .where(User.last_sms_sent_at.is_not(None))
    )
    sms_sent = await db.scalar(
        select(func.count()).select_from(SMSMessage).where(SMSMessage.status == "sent")
    )
    reminders_sent = await db.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.status == "sent")
    )
    reminders_delivered = await db.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.status == "delivered")
    )
    ai_advice_requests = await db.scalar(
        select(func.count()).select_from(SMSMessage).where(SMSMessage.template_name == "advice_followup")
    )
    menstrual_users = await db.scalar(
        select(func.count()).select_from(User).where(User.life_stage == LifeStage.REGULAR)
    )
    pregnancy_users = await db.scalar(
        select(func.count()).select_from(User).where(User.life_stage == LifeStage.PREGNANT)
    )
    postpartum_users = await db.scalar(
        select(func.count()).select_from(User).where(User.life_stage == LifeStage.POSTPARTUM)
    )
    menopause_users = await db.scalar(
        select(func.count()).select_from(User).where(User.life_stage.in_([LifeStage.PERIMENOPAUSE, LifeStage.MENOPAUSE]))
    )

    return {
        "registered_users": int(registered_users or 0),
        "active_users": int(active_users or 0),
        "sms_sent": int(sms_sent or 0),
        "reminders_sent": int(reminders_sent or 0),
        "reminders_delivered": int(reminders_delivered or 0),
        "ai_requests": int(ai_advice_requests or 0),
        "menstrual_users": int(menstrual_users or 0),
        "pregnancy_users": int(pregnancy_users or 0),
        "postpartum_users": int(postpartum_users or 0),
        "menopause_users": int(menopause_users or 0),
    }
