"""Repository for SMS message logging and deduplication."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sms_message import SMSMessage


class SMSMessageRepository:
    """Persist SMS events and find recent duplicates."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log_message(
        self,
        *,
        phone_number: str,
        message_body: str,
        direction: str = "outbound",
        user_id: int | None = None,
        template_name: str | None = None,
        status: str = "pending",
        provider_message_id: str | None = None,
        attempt_count: int = 1,
        error_message: str | None = None,
    ) -> SMSMessage:
        """Create a message log entry."""
        message = SMSMessage(
            user_id=user_id,
            phone_number=phone_number,
            direction=direction,
            template_name=template_name,
            message_body=message_body,
            status=status,
            provider_message_id=provider_message_id,
            attempt_count=attempt_count,
            error_message=error_message,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def update(self, message: SMSMessage, **fields: object) -> SMSMessage:
        """Update an SMS message record."""
        for key, value in fields.items():
            if hasattr(message, key):
                setattr(message, key, value)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def has_recent_message(
        self,
        *,
        user_id: int | None,
        template_name: str | None,
        within_hours: int = 24,
    ) -> bool:
        """Return True when the same user/template combination was used recently."""
        if user_id is None or template_name is None:
            return False

        cutoff = datetime.utcnow() - timedelta(hours=within_hours)
        result = await self.db.execute(
            select(SMSMessage).where(
                SMSMessage.user_id == user_id,
                SMSMessage.template_name == template_name,
                SMSMessage.created_at >= cutoff,
            )
        )
        return result.scalar_one_or_none() is not None
