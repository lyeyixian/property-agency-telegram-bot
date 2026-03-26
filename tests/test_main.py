"""Tests for the FastAPI application."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

_SECRET = "test-secret-token"


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


def _make_mock_bot():
    """Return a mock Telegram bot application."""
    mock_bot = MagicMock()
    mock_bot.initialize = AsyncMock()
    mock_bot.shutdown = AsyncMock()
    mock_bot.process_update = AsyncMock()
    mock_bot.bot = MagicMock()
    mock_bot.bot.defaults = None  # prevents tzinfo MagicMock breaking Update.de_json
    return mock_bot


@pytest.fixture()
def client(monkeypatch):
    """Return a TestClient with the bot application mocked out and a webhook secret set."""
    monkeypatch.setenv("WEBHOOK_SECRET_TOKEN", _SECRET)

    mock_bot = _make_mock_bot()

    import app.main as main_module

    # Reset the singleton so lifespan calls get_bot_app() → our mock.
    main_module._bot_app = None

    with patch("app.main.get_bot_app", return_value=mock_bot):
        with TestClient(main_module.app, raise_server_exceptions=True) as c:
            yield c, mock_bot

    # Clean up singleton after the test.
    main_module._bot_app = None


@pytest.fixture()
def client_no_secret(monkeypatch):
    """Return a TestClient with the bot application mocked out and no webhook secret."""
    monkeypatch.delenv("WEBHOOK_SECRET_TOKEN", raising=False)

    mock_bot = _make_mock_bot()

    import app.main as main_module

    # Reset the singleton and module-level secret token.
    main_module._bot_app = None
    main_module._webhook_secret_token = None

    with patch("app.main.get_bot_app", return_value=mock_bot):
        with TestClient(main_module.app, raise_server_exceptions=True) as c:
            yield c, mock_bot

    # Restore state after test.
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
        response = c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        assert response.status_code == 200

    def test_webhook_processes_start_command(self, client):
        c, mock_bot = client
        payload = _make_update("/start")
        c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_help_command(self, client):
        c, mock_bot = client
        payload = _make_update("/help")
        c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_listings_command(self, client):
        c, mock_bot = client
        payload = _make_update("/listings")
        c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_contact_command(self, client):
        c, mock_bot = client
        payload = _make_update("/contact")
        c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        mock_bot.process_update.assert_called_once()

    def test_webhook_processes_about_command(self, client):
        c, mock_bot = client
        payload = _make_update("/about")
        c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        mock_bot.process_update.assert_called_once()

    def test_webhook_missing_secret_token_returns_401(self, client):
        c, mock_bot = client
        payload = _make_update("/start")
        response = c.post("/webhook", json=payload)
        assert response.status_code == 401
        mock_bot.process_update.assert_not_called()

    def test_webhook_invalid_secret_token_returns_403(self, client):
        c, mock_bot = client
        payload = _make_update("/start")
        response = c.post(
            "/webhook",
            json=payload,
            headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-token"},
        )
        assert response.status_code == 403
        mock_bot.process_update.assert_not_called()

    def test_webhook_invalid_json_returns_400(self, client):
        c, mock_bot = client
        response = c.post(
            "/webhook",
            content=b"not-valid-json",
            headers={
                "Content-Type": "application/json",
                "X-Telegram-Bot-Api-Secret-Token": _SECRET,
            },
        )
        assert response.status_code == 400
        mock_bot.process_update.assert_not_called()

    def test_webhook_non_dict_json_returns_400(self, client):
        c, mock_bot = client
        response = c.post(
            "/webhook",
            json=[1, 2, 3],
            headers={"X-Telegram-Bot-Api-Secret-Token": _SECRET},
        )
        assert response.status_code == 400
        mock_bot.process_update.assert_not_called()

    def test_webhook_no_secret_configured_accepts_all_requests(self, client_no_secret):
        c, mock_bot = client_no_secret
        payload = _make_update("/start")
        response = c.post("/webhook", json=payload)
        assert response.status_code == 200
        mock_bot.process_update.assert_called_once()


class TestGetBotApp:
    def test_get_bot_app_returns_singleton(self, monkeypatch):
        """get_bot_app() should return the same instance on repeated calls."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")

        import app.main as main_module

        main_module._bot_app = None
        try:
            with patch("app.main.build_application") as mock_build:
                mock_build.return_value = MagicMock()
                first = main_module.get_bot_app()
                second = main_module.get_bot_app()
                assert first is second
                mock_build.assert_called_once()
        finally:
            main_module._bot_app = None
