"""FastAPI application for the Property Agency Telegram Bot.

Telegram sends webhook updates to the /webhook endpoint.
The bot processes commands and replies via the Telegram API.
"""
import logging
import os
import secrets
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from telegram import Update

from app.bot import build_application

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_bot_app = None
_webhook_secret_token = os.getenv("WEBHOOK_SECRET_TOKEN")


def get_bot_app():
    """Return the singleton Telegram bot application."""
    global _bot_app
    if _bot_app is None:
        _bot_app = build_application()
    return _bot_app


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manage Telegram bot application lifecycle."""
    bot_app = get_bot_app()
    await bot_app.initialize()
    logger.info("Telegram bot application initialized.")
    yield
    await bot_app.shutdown()
    logger.info("Telegram bot application shut down.")


app = FastAPI(title="Property Agency Telegram Bot", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    """Health-check endpoint used by Cloud Run."""
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request) -> Response:
    """Receive and process a Telegram webhook update."""
    if _webhook_secret_token:
        incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if incoming is None:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)
        if not secrets.compare_digest(incoming, _webhook_secret_token):
            return Response(status_code=status.HTTP_403_FORBIDDEN)

    try:
        data = await request.json()
    except ValueError:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    if not isinstance(data, dict):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    bot_app = get_bot_app()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return Response(status_code=status.HTTP_200_OK)
