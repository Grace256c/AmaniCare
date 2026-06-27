"""Africa's Talking SMS integration service."""

from __future__ import annotations

import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.user import User
from app.repositories.sms_message_repository import SMSMessageRepository
from app.repositories.user_repository import UserRepository


class AfricaTalkingSMSService:
    """Send SMS messages through Africa's Talking."""

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.settings = get_settings()
        self.db = db
        self.sms_repo = SMSMessageRepository(db) if db is not None else None
        self.user_repo = UserRepository(db) if db is not None else None

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        *,
        template_name: str | None = None,
        user_id: int | None = None,
        dedupe_key: str | None = None,
    ) -> bool:
        """Send an SMS to a phone number and return success status."""
        if self.db is not None and self.user_repo is not None and self.sms_repo is not None:
            user = await self.user_repo.get_by_phone(phone_number)
            if user is None:
                logger.warning("Skipping SMS for unknown user {}", phone_number)
                return False

            if template_name and await self.sms_repo.has_recent_message(
                user_id=user.id,
                template_name=template_name,
            ):
                logger.info("Skipping duplicate SMS for {} using {}", phone_number, template_name)
                return False

        if not self.settings.africas_talking_username or not self.settings.africas_talking_api_key:
            logger.warning("Africa's Talking credentials are not configured; skipping SMS send")
            return False

        if self.db is not None and self.sms_repo is not None:
            log_entry = await self.sms_repo.log_message(
                phone_number=phone_number,
                message_body=message,
                user_id=user_id,
                template_name=template_name,
                status="pending",
            )
        else:
            log_entry = None

        payload = {
            "username": self.settings.africas_talking_username,
            "to": phone_number,
            "message": message,
        }
        if self.settings.africas_talking_sender_id:
            payload["from"] = self.settings.africas_talking_sender_id

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.settings.africas_talking_sms_url,
                    data=payload,
                    auth=(self.settings.africas_talking_username, self.settings.africas_talking_api_key),
                )
                if response.status_code >= 400:
                    logger.error(
                        "Africa's Talking SMS send failed with status {}: {}",
                        response.status_code,
                        response.text,
                    )
                    if log_entry is not None:
                        await self.sms_repo.update(log_entry, status="failed", error_message=response.text)
                    return False
        except httpx.HTTPError as exc:
            logger.exception("Africa's Talking SMS send failed: {}", exc)
            if log_entry is not None:
                await self.sms_repo.update(log_entry, status="failed", error_message=str(exc))
            return False

        if log_entry is not None and self.sms_repo is not None:
            await self.sms_repo.update(log_entry, status="sent")

        logger.info("Africa's Talking SMS sent to {}", phone_number)
        return True
