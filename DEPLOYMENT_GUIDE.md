# QwenEditBot Deployment Guide

This document describes the deployment process for the QwenEditBot system with Redis-based job queuing.

## Architecture Overview

The system consists of:
- **Backend**: FastAPI application handling API requests and database operations
- **Worker**: Processes image editing jobs using ComfyUI
- **Redis**: Job queue management
- **ComfyUI**: Image processing backend
- **Database**: SQLite for persistent storage

## Prerequisites

- Python 3.9+
- Redis server
- ComfyUI installation
- Windows environment (as per requirements)

## Directory Structure

```
C:\qweneditbot\
├── backend/           # FastAPI + aiogram
│   ├── app/
│   ├── requirements.txt
│   └── main.py
├── worker/            # Обработка очереди
├── data/
│   ├── uploads/
│   ├── outputs/
│   └── redis/
├── ComfyUI/           # Уже стоит
└── workflows/         # JSON workflow для Qwen
```

## Installation Steps

### 1. Install Dependencies

```bash
# Backend
cd C:\qweneditbot\backend
pip install -r requirements.txt

# Worker
cd C:\qweneditbot\worker
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` files in both backend and worker directories:

#### Backend .env
```
BOT_TOKEN=your_bot_token_here
COMFYUI_URL=http://127.0.0.1:8188
COMFY_INPUT_DIR=C:/ComfyUI/input
DATABASE_URL=sqlite:///./qwen.db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_JOB_QUEUE_KEY=qwenedit:job_queue
REDIS_RESULT_TTL=3600
```

#### Worker .env
```
BOT_TOKEN=your_bot_token_here
BACKEND_API_URL=http://localhost:8000
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_INPUT_DIR=C:/ComfyUI/input
COMFYUI_OUTPUT_DIR=C:/ComfyUI/output
RESULTS_DIR=./results
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_JOB_QUEUE_KEY=qwenedit:job_queue
REDIS_RESULT_TTL=3600
```

### 3. Set Up Redis

Start Redis server:
```bash
redis-server
```

### 4. Start Services

Open separate terminals and start each service:

#### Terminal 1: ComfyUI (already running)
```bash
cd C:\ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

#### Terminal 2: Backend
```bash
cd C:\qweneditbot\backend
uvicorn app.main:app --host 0.0.0 --port 8000
```

#### Terminal 3: Worker
```bash
cd C:\qweneditbot\worker
python run.py
```

#### Terminal 4: Ngrok (for webhook tunneling)
```bash
ngrok http 8000
```

#### Telegram Webhook Setup
Once ngrok provides you with the public URL (e.g., `https://xxxx-xx-xxx-xxx-xx.ngrok-free.app`), use it to set up the Telegram webhook:

```bash
# Replace YOUR_BOT_TOKEN with your actual bot token
# Replace NGROK_URL with the URL provided by ngrok
curl -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=NGROK_URL/api/telegram/webhook"
```

To verify the webhook was set correctly:
```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/getWebhookInfo"
```

## Redis Configuration

The system uses Redis for job queue management with the following configuration:
- Queue key: `qwenedit:job_queue`
- Result TTL: 1 hour (3600 seconds)
- Default Redis database: 0

## Job Processing Flow

1. User uploads image and sends prompt via Telegram bot
2. Backend creates job record in database and adds job to Redis queue
3. Worker polls Redis queue for new jobs
4. Worker processes job using ComfyUI
5. Result is stored and sent back to user

## Testing

To verify the system is working:

1. Check backend health: `GET http://localhost:8000/health`
2. Verify Redis connectivity in logs
3. Submit a test job through the bot interface
4. Monitor worker logs for job processing

## Troubleshooting

### Common Issues

- **Redis Connection**: Ensure Redis server is running and credentials are correct
- **ComfyUI Connection**: Verify ComfyUI is accessible at configured URL
- **File Permissions**: Ensure proper permissions for data directories

### Logs

- Backend logs: Console output from uvicorn
- Worker logs: Console output from worker
- Redis logs: From Redis server console

## Scaling Considerations

- Multiple workers can connect to the same Redis queue
- Redis can be configured with persistence for durability
- Database connection pooling can be implemented for high loads