"""Tests for the Telegram bot command handlers."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.handlers import about, contact, help_command, listings, start


def _make_update():
    """Return a minimal mock Update with a message that records reply_text calls."""
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    return update


def _make_context():
    """Return a minimal mock ContextTypes.DEFAULT_TYPE."""
    return MagicMock()


class TestStartHandler:
    async def test_replies_with_welcome_message(self):
        update = _make_update()
        await start(update, _make_context())
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
        assert "Welcome" in text
        assert "/help" in text

    async def test_does_not_specify_parse_mode(self):
        update = _make_update()
        await start(update, _make_context())
        call_kwargs = update.message.reply_text.call_args[1]
        assert "parse_mode" not in call_kwargs


class TestHelpHandler:
    async def test_replies_with_help_message(self):
        update = _make_update()
        await help_command(update, _make_context())
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
        assert "/start" in text
        assert "/help" in text
        assert "/listings" in text
        assert "/contact" in text
        assert "/about" in text

    async def test_uses_markdown_parse_mode(self):
        update = _make_update()
        await help_command(update, _make_context())
        call_kwargs = update.message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "Markdown"


class TestListingsHandler:
    async def test_replies_with_listings_message(self):
        update = _make_update()
        await listings(update, _make_context())
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
        assert "listings" in text.lower()

    async def test_uses_markdown_parse_mode(self):
        update = _make_update()
        await listings(update, _make_context())
        call_kwargs = update.message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "Markdown"


class TestContactHandler:
    async def test_replies_with_contact_message(self):
        update = _make_update()
        await contact(update, _make_context())
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
        assert "contact" in text.lower()

    async def test_uses_markdown_parse_mode(self):
        update = _make_update()
        await contact(update, _make_context())
        call_kwargs = update.message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "Markdown"


class TestAboutHandler:
    async def test_replies_with_about_message(self):
        update = _make_update()
        await about(update, _make_context())
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        text = call_args[0][0] if call_args[0] else call_args[1].get("text", "")
        assert "about" in text.lower() or "agency" in text.lower()

    async def test_uses_markdown_parse_mode(self):
        update = _make_update()
        await about(update, _make_context())
        call_kwargs = update.message.reply_text.call_args[1]
        assert call_kwargs.get("parse_mode") == "Markdown"
