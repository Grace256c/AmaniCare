"""Regression tests for the SMS MVP features."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sms_test_endpoint_accepts_payload(client: AsyncClient) -> None:
    """The demo SMS endpoint should accept a phone number and message."""
    response = await client.post(
        "/api/sms/test",
        json={"phone_number": "+256700000000", "message": "Hello MamaCare"},
    )
    assert response.status_code == 200
    assert response.json()["success"] in {True, False}


@pytest.mark.asyncio
async def test_dashboard_stats_endpoint_returns_shape(client: AsyncClient) -> None:
    """The dashboard stats endpoint should return the expected demo metrics."""
    response = await client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "registered_users",
        "sms_sent",
        "ai_advice_requests",
        "period_support_requests",
        "pregnancy_support_requests",
        "menopause_support_requests",
    }
