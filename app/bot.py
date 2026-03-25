"""Telegram bot application setup."""
import os

from telegram.ext import Application, CommandHandler

from app.handlers import about, contact, help_command, listings, start


def build_application() -> Application:
    """Build and configure the Telegram bot application."""
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    app = Application.builder().token(token).updater(None).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("listings", listings))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("about", about))

    return app
