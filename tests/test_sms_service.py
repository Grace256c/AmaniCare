"""SMS service tests."""

from __future__ import annotations

import httpx
import pytest

from app.core.config import get_settings
from app.services.sms_service import AfricaTalkingSMSService


@pytest.mark.asyncio
async def test_send_sms_uses_africas_talking_when_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """The SMS service should post to Africa's Talking when credentials are present."""
    get_settings.cache_clear()
    monkeypatch.setenv("AFRICAS_TALKING_USERNAME", "demo")
    monkeypatch.setenv("AFRICAS_TALKING_API_KEY", "demo-key")
    monkeypatch.setenv("AFRICAS_TALKING_SENDER_ID", "MAMACARE")

    requests: list[dict[str, object]] = []

    class FakeAsyncClient:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.kwargs = kwargs

        async def __aenter__(self) -> "FakeAsyncClient":
            return self

        async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
            return False

        async def post(self, url: str, data: dict[str, object], auth: tuple[str, str] | None = None) -> httpx.Response:
            requests.append({"url": url, "data": data, "auth": auth})
            return httpx.Response(200, json={"SMSMessageData": {"Recipients": [{"status": "Success"}]}})

    monkeypatch.setattr("app.services.sms_service.httpx.AsyncClient", FakeAsyncClient)

    service = AfricaTalkingSMSService()
    result = await service.send_sms("+256700000000", "Hello MamaCare")

    assert result is True
    assert requests[0]["url"] == get_settings().africas_talking_sms_url
    assert requests[0]["data"]["to"] == "+256700000000"
    assert requests[0]["data"]["message"] == "Hello MamaCare"
    assert requests[0]["data"]["from"] == "MAMACARE"
    assert requests[0]["auth"] == ("demo", "demo-key")
