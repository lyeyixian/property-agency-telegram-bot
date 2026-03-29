"""Tests for the bot application setup."""

from unittest.mock import MagicMock, patch

import pytest

from app.bot import build_application


class TestBuildApplication:
    def test_raises_runtime_error_when_token_missing(self, monkeypatch):
        """build_application() raises RuntimeError when TELEGRAM_BOT_TOKEN is not set."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
            build_application()

    def test_raises_runtime_error_when_token_empty(self, monkeypatch):
        """build_application() raises RuntimeError when TELEGRAM_BOT_TOKEN is empty."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "")
        with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN"):
            build_application()

    def test_returns_application_with_handlers_when_token_set(self, monkeypatch):
        """build_application() returns a configured Application when token is provided."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token-for-testing")

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.updater.return_value = mock_builder
        mock_builder.build.return_value = mock_app

        with patch("app.bot.Application") as mock_application_class:
            mock_application_class.builder.return_value = mock_builder
            result = build_application()

        assert result is mock_app
        mock_application_class.builder.assert_called_once()
        mock_builder.token.assert_called_once_with("fake-token-for-testing")
        mock_builder.updater.assert_called_once_with(None)
        assert mock_app.add_handler.call_count == 5
