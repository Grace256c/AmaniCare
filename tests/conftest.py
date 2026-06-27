"""Pytest configuration and shared fixtures."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Force test database before importing app modules.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from app.core.database import AsyncSessionLocal, Base, engine, get_db
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Create fresh tables before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client with overridden database dependency."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
