"""Simple analytics endpoints for demo purposes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.user import User, LifeStage
from app.models.reminder import Reminder, ReminderType
from app.models.sms_message import SMSMessage

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    res = {}
    q = await db.execute(select(func.count()).select_from(User))
    res["registered_users"] = q.scalar_one()

    q = await db.execute(select(func.count()).select_from(SMSMessage))
    res["sms_sent"] = q.scalar_one()

    # AI advice requests are not tracked; reuse sms_messages with template
    q = await db.execute(select(func.count()).select_from(SMSMessage).where(SMSMessage.template_name == "advice_followup"))
    res["ai_advice_requests"] = q.scalar_one()

    # reminders by type
    for t, key in [(ReminderType.PERIOD, "period_support_requests"), (ReminderType.PREGNANCY_CHECKIN, "pregnancy_support_requests"), (ReminderType.MENOPAUSE_WELLNESS, "menopause_support_requests")]:
        q = await db.execute(select(func.count()).select_from(Reminder).where(Reminder.reminder_type == t))
        res[key] = q.scalar_one()

    return res
"""Simple dashboard stats API for hackathon demos."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.reminder import Reminder, ReminderType
from app.models.sms_message import SMSMessage
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)) -> dict[str, int]:
    """Return simple stats for the frontend demo."""
    registered_users = await db.scalar(select(func.count()).select_from(User))
    sms_sent = await db.scalar(
        select(func.count()).select_from(SMSMessage).where(SMSMessage.status == "sent")
    )
    ai_advice_requests = await db.scalar(
        select(func.count()).select_from(SMSMessage).where(SMSMessage.template_name == "advice_follow_up")
    )
    period_support_requests = await db.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.reminder_type == ReminderType.PERIOD)
    )
    pregnancy_support_requests = await db.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.reminder_type == ReminderType.PREGNANCY_CHECKIN)
    )
    menopause_support_requests = await db.scalar(
        select(func.count()).select_from(Reminder).where(Reminder.reminder_type == ReminderType.MENOPAUSE_WELLNESS)
    )

    return {
        "registered_users": int(registered_users or 0),
        "sms_sent": int(sms_sent or 0),
        "ai_advice_requests": int(ai_advice_requests or 0),
        "period_support_requests": int(period_support_requests or 0),
        "pregnancy_support_requests": int(pregnancy_support_requests or 0),
        "menopause_support_requests": int(menopause_support_requests or 0),
    }
