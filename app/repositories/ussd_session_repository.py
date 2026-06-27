"""USSD session data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import USSDFlow, USSDSession


class USSDSessionRepository:
    """Repository for USSD session state management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_session_id(self, session_id: str) -> USSDSession | None:
        """Fetch session state by Africa's Talking session ID."""
        result = await self.db.execute(
            select(USSDSession).where(USSDSession.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        session_id: str,
        phone_number: str,
        flow: USSDFlow = USSDFlow.MAIN,
    ) -> USSDSession:
        """Create a new USSD session."""
        session = USSDSession(
            session_id=session_id,
            phone_number=phone_number,
            flow=flow,
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def update(self, session: USSDSession, **fields: object) -> USSDSession:
        """Update session fields."""
        for key, value in fields.items():
            if hasattr(session, key):
                setattr(session, key, value)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def delete(self, session: USSDSession) -> None:
        """Remove a completed USSD session."""
        await self.db.delete(session)
        await self.db.flush()
