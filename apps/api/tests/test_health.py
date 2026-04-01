from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from src.ai.lm_studio_client import LMStudioError, LMStudioErrorKind
from src.main import app


@pytest.mark.asyncio
async def test_health_returns_ok():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "galley-api"
    assert data["db"] == "ok"


@pytest.mark.asyncio
async def test_health_degraded_when_db_unreachable():
    with patch("src.routes.health._db_ok", return_value=False):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["db"] == "unreachable"


@pytest.mark.asyncio
async def test_ai_health_disabled():
    with patch("src.routes.health.settings") as mock_settings:
        mock_settings.lm_studio_enabled = False
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/health/ai")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ai_enabled"] is False
    assert payload["reachable"] is None
    assert payload["model"] is None
    assert payload["error"] is None


@pytest.mark.asyncio
async def test_ai_health_reachable():
    mock_client = MagicMock()
    mock_client.check_availability.return_value = (True, None)

    with patch("src.routes.health.settings") as mock_settings, \
         patch("src.routes.health.LMStudioClient", return_value=mock_client):
        mock_settings.lm_studio_enabled = True
        mock_settings.lm_studio_base_url = "http://localhost:1234/v1"
        mock_settings.lm_studio_model = "Qwen/Qwen2.5-7B-Instruct"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/health/ai")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ai_enabled"] is True
    assert payload["reachable"] is True
    assert payload["model"] == "Qwen/Qwen2.5-7B-Instruct"
    assert payload["error"] is None


@pytest.mark.asyncio
async def test_ai_health_unreachable():
    mock_client = MagicMock()
    mock_client.check_availability.return_value = (
        False,
        LMStudioError(LMStudioErrorKind.unavailable, "Connection refused"),
    )

    with patch("src.routes.health.settings") as mock_settings, \
         patch("src.routes.health.LMStudioClient", return_value=mock_client):
        mock_settings.lm_studio_enabled = True
        mock_settings.lm_studio_base_url = "http://localhost:1234/v1"
        mock_settings.lm_studio_model = ""

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/health/ai")

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["ai_enabled"] is True
    assert payload["reachable"] is False
    assert payload["model"] is None
    assert payload["error"] == "Connection refused"
