# property-agency-telegram-bot

A simple Telegram chatbot for property agency workflows, built with **FastAPI** and deployable to **GCP Cloud Run**.

---

## Architecture

```
Telegram  ──webhook──►  FastAPI (/webhook)  ──►  python-telegram-bot handlers
```

Telegram sends every incoming update (message / command) as an HTTP POST to your webhook URL. FastAPI receives it, deserialises it, and delegates to the appropriate command handler which replies via the Telegram Bot API.

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | List available commands |
| `/listings` | Browse placeholder property listings |
| `/contact` | Agent contact information |
| `/about` | About the agency |

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A Telegram bot token — create one via [@BotFather](https://t.me/BotFather)
- (For local webhook testing) [ngrok](https://ngrok.com/) or a similar tunnel tool

---

## Running Locally with Docker

### 1. Clone the repository

```bash
git clone https://github.com/lyeyixian/property-agency-telegram-bot.git
cd property-agency-telegram-bot
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and set your bot token and webhook secret:

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
WEBHOOK_SECRET_TOKEN=your-webhook-secret-token-here
```

### 3. Build and start the container

```bash
docker compose up --build
```

The server starts on **http://localhost:8080**.

You can verify it is healthy:

```bash
curl http://localhost:8080/health
# {"status":"ok"}
```

### 4. Expose your local server to Telegram (webhook)

Telegram requires an **HTTPS** URL to deliver updates. Use ngrok to create a tunnel:

```bash
ngrok http 8080
```

Copy the `https://` forwarding URL (e.g. `https://abc123.ngrok.io`).

### 5. Register the webhook with Telegram

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://abc123.ngrok.io/webhook", "secret_token": "your-webhook-secret-token-here"}'
```

Telegram will now forward all bot updates to your local server. Open the bot in Telegram and try `/start`.

---

## Running Tests

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Sync the virtual environment (creates `.venv` automatically):

```bash
uv sync
```

Run the test suite:

```bash
uv run pytest
```

---

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI app & webhook endpoint
│   ├── bot.py         # Telegram Application setup
│   └── handlers.py    # Slash-command handler functions
├── tests/
│   ├── __init__.py
│   └── test_main.py   # Pytest tests
├── .env.example       # Template for required environment variables
├── docker-compose.yml # Local Docker testing
├── Dockerfile         # Production image (GCP Cloud Run)
├── pyproject.toml     # Project metadata, dependencies, and tool config
└── uv.lock            # Locked dependency versions
```

---

## Deploying to GCP Cloud Run

1. **Build and push the image**

   ```bash
   gcloud builds submit --tag gcr.io/<PROJECT_ID>/property-agency-bot
   ```

2. **Deploy**

   ```bash
   gcloud run deploy property-agency-bot \
     --image gcr.io/<PROJECT_ID>/property-agency-bot \
     --platform managed \
     --region <REGION> \
     --allow-unauthenticated \
     --set-env-vars TELEGRAM_BOT_TOKEN=<YOUR_TOKEN>,WEBHOOK_SECRET_TOKEN=<YOUR_WEBHOOK_SECRET_TOKEN>
   ```

3. **Register the webhook** (replace with your Cloud Run URL)

   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://<CLOUD_RUN_URL>/webhook", "secret_token": "<YOUR_WEBHOOK_SECRET_TOKEN>"}'
   ```
