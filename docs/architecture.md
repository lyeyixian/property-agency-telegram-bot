# Architecture

## Overview

This is a **Telegram bot** for a Malaysian property agency, built to assist agents with their daily business operations. It uses a **webhook-based architecture**: Telegram pushes updates to the bot's HTTP endpoint, rather than the bot polling Telegram's servers.

```
Telegram  ──HTTPS POST──►  FastAPI (/webhook)  ──►  python-telegram-bot handlers
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Web framework | FastAPI | 0.135.2 | HTTP server hosting the `/webhook` endpoint |
| ASGI server | Uvicorn | 0.42.0 | Serves the FastAPI app in production |
| Telegram library | python-telegram-bot | 22.7 | Telegram Bot API client and update dispatcher |
| Language | Python | ≥ 3.14 | Application runtime |
| Dependency manager | uv | — | Dependency resolution, virtual environment, and script running |
| Containerisation | Docker | — | Consistent build and runtime environment |
| Cloud platform | GCP Cloud Run | — | Serverless container hosting |
| Linter / Formatter | Ruff | 0.9.0 | Code style enforcement |
| Test framework | pytest + pytest-asyncio | 9.0.2 / 1.3.0 | Unit and integration tests |

---

## Architectural Decisions

### ADR-001: Webhook over Polling

**Decision**: Use Telegram's webhook delivery instead of long-polling.

**Reason**: The bot is deployed on GCP Cloud Run, which scales to zero when idle. Long-polling requires a persistent process; webhooks allow the container to be cold-started on demand and handle only active traffic, reducing cost.

**Consequence**: The application must expose a public HTTPS endpoint. Locally, a tunnel tool (e.g. ngrok) is required to forward Telegram's HTTPS calls to `localhost`.

---

### ADR-002: FastAPI as the Webhook Server

**Decision**: Use FastAPI instead of the built-in webhook support from `python-telegram-bot`.

**Reason**: FastAPI provides a clean, testable HTTP layer with standard middleware, health-check endpoints, and dependency injection — all of which are useful for production deployments. Using `updater=None` in the `Application` builder disables the built-in polling/webhook runner.

**Consequence**: The FastAPI `lifespan` context manager is responsible for calling `bot_app.initialize()` and `bot_app.shutdown()` at startup and shutdown.

---

### ADR-003: Singleton Bot Application

**Decision**: The `python-telegram-bot` `Application` instance is created once and stored in `app.main._bot_app`, accessed via `get_bot_app()`.

**Reason**: The `Application` object holds an HTTPX async client and handler registry. Re-creating it on every request would be expensive and incorrect.

**Consequence**: Tests must reset `_bot_app = None` between runs to avoid state leakage between test cases.

---

### ADR-004: Webhook Secret Token

**Decision**: If `WEBHOOK_SECRET_TOKEN` is set in the environment, the `/webhook` endpoint enforces it by checking the `X-Telegram-Bot-Api-Secret-Token` header using a timing-safe comparison.

**Reason**: Without a secret token, any party that discovers the webhook URL can send arbitrary payloads to the bot. The secret is sent by Telegram on every update when configured via `setWebhook`.

**Consequence**: In development without a secret token configured, all requests to `/webhook` are accepted without authentication checks.

---

### ADR-005: TDD Development Approach

**Decision**: All new features and bug fixes must follow the Red → Green → Refactor TDD cycle.

**Reason**: The property agency workflow will grow over time. TDD ensures each behaviour is explicitly specified, regression-proofed, and documented through tests before code is written.

**Consequence**: No production code may be added without a corresponding failing test written first.

---

## Data Flow

### Incoming Telegram Update

```
1. User sends a command (e.g. /listings) to the Telegram bot.
2. Telegram POSTs the update as JSON to https://<host>/webhook.
3. FastAPI's /webhook handler validates the X-Telegram-Bot-Api-Secret-Token header.
4. The JSON body is deserialised into a telegram.Update object via Update.de_json().
5. The Update is passed to bot_app.process_update(), which dispatches to the
   matching CommandHandler registered in app/bot.py.
6. The handler function in app/handlers.py sends a reply via the Telegram Bot API.
```

### Application Lifecycle

```
FastAPI startup  →  lifespan()  →  bot_app.initialize()
FastAPI shutdown →  lifespan()  →  bot_app.shutdown()
```

---

## Directory Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI app, lifespan, /health, /webhook endpoints
│   ├── bot.py          # Builds the python-telegram-bot Application; registers handlers
│   └── handlers.py     # Async handler functions for each slash command
├── tests/
│   ├── __init__.py
│   ├── test_bot.py        # Tests for build_application()
│   ├── test_handlers.py   # Tests for each command handler function
│   └── test_main.py       # Tests for FastAPI endpoints (health, webhook, auth)
├── docs/
│   ├── agents.md          # AI agent context and development guide
│   └── architecture.md    # This file
├── .github/
│   ├── agents/            # Custom Copilot agent definitions
│   │   └── issues-planner.agent.md
│   ├── workflows/
│   │   └── codeql.yml
│   └── copilot-instructions.md
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

---

## Deployment

The application is containerised via a multi-stage `Dockerfile`:

1. **Builder stage** — installs dependencies with `uv sync --frozen --no-dev` into `.venv`.
2. **Runtime stage** — copies the `.venv` and `app/` source into a slim Python image.
3. GCP Cloud Run serves the container, injecting `PORT` (defaults to `8080`).

The webhook URL must be registered with Telegram after each deployment using the `setWebhook` API call.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Token issued by [@BotFather](https://t.me/BotFather) for the bot. |
| `WEBHOOK_SECRET_TOKEN` | No | Secret used to validate that webhook requests originate from Telegram. |
