"""Telegram bot application setup."""
import os

from telegram.ext import Application, CommandHandler

from app.handlers import about, contact, help_command, listings, start


def build_application() -> Application:
    """Build and configure the Telegram bot application."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Environment variable TELEGRAM_BOT_TOKEN is not set. "
            "Please set TELEGRAM_BOT_TOKEN before starting the Telegram bot application."
        )
    app = Application.builder().token(token).updater(None).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("listings", listings))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("about", about))

    return app
