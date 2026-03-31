# Copilot Instructions

## Application Overview

This is a **Python Telegram bot** built for a **Malaysian property agency** to assist agents with their daily business processes. It is built with **FastAPI** (as the webhook server) and **python-telegram-bot** (for handling Telegram bot commands), and is deployable to **GCP Cloud Run**.

The bot receives Telegram updates via a webhook endpoint (`POST /webhook`) and routes commands to the appropriate handlers in `app/handlers.py`.

For detailed architecture and design decisions, see [`docs/architecture.md`](../docs/architecture.md).  
For application context and development guidelines, see [`AGENTS.md`](../AGENTS.md).

---

## Development Workflow

### TDD — Red → Green → Refactor

This project follows Test-Driven Development (TDD). Before writing any production code:

1. **Red** – Write a failing test that describes the desired behaviour.
2. **Green** – Write the minimal production code to make the test pass.
3. **Refactor** – Clean up the code while keeping all tests green.

Never skip the Red step. Every new feature or bug fix must start with a test.

### Before Committing

Always run the following three steps **in order** and ensure all pass before committing:

```bash
# 1. Format code
uv run ruff format .

# 2. Lint code
uv run ruff check .

# 3. Run tests
uv run pytest
```

If any step fails, fix the issues before committing. Do **not** commit failing tests, lint errors, or unformatted code.

### Updating Context Files

When making changes that affect the application's architecture, features, commands, dependencies, or development conventions, update the relevant context files to keep them accurate:

- [`docs/architecture.md`](../docs/architecture.md) — update when changing architecture, deployment, data flow, or tech stack decisions.
- [`AGENTS.md`](../AGENTS.md) — update when adding commands, changing project structure, or modifying development workflows.

---

## Key Conventions

- **Dependency management**: Use `uv` — add packages with `uv add <package>` and dev tools with `uv add --dev <package>`.
- **Formatting & linting**: Use `ruff` (configured in `pyproject.toml`) for both formatting (`ruff format`) and linting (`ruff check`).
- **Testing**: Use `pytest` with `asyncio_mode = "auto"`. Tests live in `tests/` and mirror the `app/` module structure.
- **Environment variables**: `TELEGRAM_BOT_TOKEN` (required) and `WEBHOOK_SECRET_TOKEN` (optional but recommended for security) must be set before running the bot.
- **Handler pattern**: Each Telegram slash command maps to an `async def` function in `app/handlers.py` that accepts `(update: Update, context: ContextTypes.DEFAULT_TYPE)` and is registered in `app/bot.py`.
- **Malaysia context**: The agency is based in Malaysia — use MYR (Malaysian Ringgit, RM) for property prices, Malaysian English, and local market conventions.
