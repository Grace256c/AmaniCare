"""Reminder scheduling tests."""

import pytest
from httpx import AsyncClient


REGISTER_PAYLOAD = {
    "phone_number": "+256700000003",
    "name": "Linda",
    "age": 35,
    "life_stage": "Perimenopause",
    "language": "English",
}


@pytest.mark.asyncio
async def test_schedule_reminder(client: AsyncClient) -> None:
    """POST /api/reminders should schedule a mock reminder."""
    await client.post("/api/users/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/reminders",
        json={
            "phone_number": REGISTER_PAYLOAD["phone_number"],
            "type": "period",
            "next_date": "2026-07-15",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "period"
    assert data["next_date"] == "2026-07-15"


@pytest.mark.asyncio
async def test_list_reminders(client: AsyncClient) -> None:
    """GET /api/reminders/{phone_number} should list scheduled reminders."""
    await client.post("/api/users/register", json=REGISTER_PAYLOAD)
    await client.post(
        "/api/reminders",
        json={
            "phone_number": REGISTER_PAYLOAD["phone_number"],
            "type": "menopause_wellness",
            "next_date": "2026-08-01",
        },
    )

    response = await client.get(f"/api/reminders/{REGISTER_PAYLOAD['phone_number']}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["reminders"]) == 1
