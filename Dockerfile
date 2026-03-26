# ---- build stage ----
FROM python:3.14.0-slim-bookworm AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /uvx /usr/local/bin/

# Copy dependency files and install into an isolated venv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---- runtime stage ----
FROM python:3.14.0-slim-bookworm

WORKDIR /app

# Copy uv binary and the pre-built virtual environment
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /uvx /usr/local/bin/
COPY --from=builder /app/.venv /app/.venv

COPY app/ ./app/

# Cloud Run injects PORT; default to 8080
ENV PORT=8080
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE ${PORT}

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
