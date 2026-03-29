# AI Agent Context Guide

This document gives AI coding agents (GitHub Copilot, Copilot Workspace, etc.) the context they need to contribute effectively to this project.

---

## What This Application Does

This is a **Telegram bot** built for a **Malaysian property agency**. It helps property agents with their daily business operations by providing a conversational interface over Telegram. Clients and agents interact with the bot using slash commands.

**Current commands:**

| Command | Description |
|---------|-------------|
| `/start` | Welcome message introducing the bot |
| `/help` | Lists all available commands |
| `/listings` | Shows available property listings |
| `/contact` | Displays agent contact details |
| `/about` | Describes the agency |

The bot is deployed on **GCP Cloud Run** and receives Telegram updates via a **webhook** endpoint (`POST /webhook`) served by **FastAPI**.

For full architectural details, see [`docs/architecture.md`](architecture.md).

---

## Technology Stack

- **Language**: Python ≥ 3.14
- **Web framework**: FastAPI
- **Telegram library**: python-telegram-bot
- **Dependency manager**: uv (use `uv run` to execute commands in the venv)
- **Linter / Formatter**: Ruff
- **Test framework**: pytest with pytest-asyncio (`asyncio_mode = "auto"`)
- **Container**: Docker (multi-stage build)
- **Cloud**: GCP Cloud Run

---

## Development Commands

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable lint issues
uv run ruff check --fix .

# Run tests
uv run pytest

# Run a single test file
uv run pytest tests/test_handlers.py

# Run tests verbosely
uv run pytest -v
```

> ⚠️ Always run **format → lint → tests** in that order before committing.

---

## TDD Development Workflow

This project follows **Test-Driven Development** using the Red → Green → Refactor cycle:

1. **Red** — Write a failing test that specifies the desired behaviour. Run it and confirm it fails.
2. **Green** — Write the minimum production code needed to make the test pass. Run tests and confirm they pass.
3. **Refactor** — Improve code quality (naming, structure, readability) without changing behaviour. Run tests again to confirm nothing broke.

**Never write production code without a failing test first.**

### Example: Adding a new `/valuation` command

```python
# tests/test_handlers.py  (Step 1 — Red)
class TestValuationHandler:
    async def test_replies_with_valuation_message(self):
        update = _make_update()
        await valuation(update, _make_context())
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "valuation" in text.lower()
```

Run `uv run pytest` → test fails (Red). Then implement `valuation` in `app/handlers.py` and register it in `app/bot.py` (Green). Clean up (Refactor). Run formatter, linter, and tests before committing.

---

## Adding a New Command

1. Write a failing test in `tests/test_handlers.py` (Red).
2. Add the handler function in `app/handlers.py` following the existing pattern:
   ```python
   async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       """Handle the /my_command command."""
       await update.message.reply_text("Your message here", parse_mode="Markdown")
   ```
3. Import and register it in `app/bot.py`:
   ```python
   from app.handlers import ..., my_command
   app.add_handler(CommandHandler("my_command", my_command))
   ```
4. Add a corresponding test to `test_bot.py` updating the expected handler count.
5. Update this file (`docs/agents.md`) and the command table in `README.md`.
6. Run format, lint, and tests. Commit only when all pass.

---

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py         # FastAPI app, lifespan, health check, webhook endpoint
│   ├── bot.py          # Builds Application, registers CommandHandlers
│   └── handlers.py     # Async functions handling each slash command
├── tests/
│   ├── __init__.py
│   ├── test_bot.py        # Tests for build_application()
│   ├── test_handlers.py   # Tests for each command handler
│   └── test_main.py       # Tests for FastAPI endpoints and auth
├── docs/
│   ├── agents.md          # This file — AI agent context guide
│   └── architecture.md    # Architecture and design decisions
├── .github/
│   ├── agents/            # Custom Copilot agent definitions
│   ├── workflows/
│   └── copilot-instructions.md
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

---

## Code Conventions

- **Malaysia context**: Prices in MYR (RM), Malaysian English, local address formats and market conventions.
- **Handler signature**: All handlers are `async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None`.
- **Parse mode**: Use `parse_mode="Markdown"` for rich text responses; plain text for simple messages.
- **Environment variables**: Loaded at module import time via `python-dotenv`. Access with `os.getenv()`.
- **Singleton pattern**: `app.main._bot_app` holds the single `Application` instance; access it via `get_bot_app()`. Reset to `None` in tests to prevent state leakage.
- **No direct `git push`**: Always go through PR review.

---

## Keeping Context Files Updated

When making changes, keep these files accurate:

| Change type | Files to update |
|-------------|----------------|
| New command or feature | `docs/agents.md` (command table, guide), `README.md` (command table) |
| Architecture change | `docs/architecture.md` (ADRs, data flow, stack table) |
| New dependency | `docs/architecture.md` (stack table), `pyproject.toml` |
| New dev convention | `.github/copilot-instructions.md`, `docs/agents.md` |
| Structural/directory change | All context files that reference the directory tree |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from [@BotFather](https://t.me/BotFather). |
| `WEBHOOK_SECRET_TOKEN` | Recommended | Validates that `/webhook` requests come from Telegram. |
