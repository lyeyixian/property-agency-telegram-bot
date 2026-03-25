"""Tests for the FastAPI application."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_update(command: str) -> dict:
    """Return a minimal Telegram Update payload for a slash command."""
    return {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "date": 1700000000,  # 2023-11-14 22:13:20 UTC
            "chat": {"id": 123, "type": "private"},
            "from": {"id": 456, "is_bot": False, "first_name": "Test"},
            "text": command,
            "entities": [{"offset": 0, "length": len(command), "type": "bot_command"}],
        },
    }


@pytest.fixture()
def client():
    """Return a TestClient with the bot application mocked out."""
    mock_bot = MagicMock()
    mock_bot.initialize = AsyncMock()
    mock_bot.shutdown = AsyncMock()
    mock_bot.process_update = AsyncMock()
    mock_bot.bot = MagicMock()
    mock_bot.bot.defaults = None  # prevents tzinfo MagicMock breaking Update.de_json

    import app.main as main_module

    # Reset the singleton so lifespan calls get_bot_app() → our mock.
    main_module._bot_app = None

    with patch("app.main.get_bot_app", return_value=mock_bot):
        with TestClient(main_module.app, raise_server_exceptions=True) as c:
            yield c, mock_bot

    # Clean up singleton after the test.
    main_module._bot_app = None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        c, _ = client
        response = c.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestWebhookEndpoint:
    def test_webhook_returns_200(self, client):
        c, _ = client
        payload = _make_update("/start")
        response = c.post("/webhook", json=payload)
        assert response.status_code == 200

    def test_webhook_processes_start_command(self, client):
        c, mock_bot = client
        payload = _make_update("/start")
        c.post("/webhook", json=payload)
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_help_command(self, client):
        c, mock_bot = client
        payload = _make_update("/help")
        c.post("/webhook", json=payload)
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_listings_command(self, client):
        c, mock_bot = client
        payload = _make_update("/listings")
        c.post("/webhook", json=payload)
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_contact_command(self, client):
        c, mock_bot = client
        payload = _make_update("/contact")
        c.post("/webhook", json=payload)
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_about_command(self, client):
        c, mock_bot = client
        payload = _make_update("/about")
        c.post("/webhook", json=payload)
        mock_bot.process_update.assert_called_once()
