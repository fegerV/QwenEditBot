# QwenEditBot - Complete AI Image Editing Solution

A complete Telegram bot for AI-powered image editing using ComfyUI, featuring a modern FastAPI backend and a user-friendly Telegram interface.

## 🎨 Architecture Overview

The project consists of two main components:
- **Backend (Phase 1)**: FastAPI REST API with database, job queue, and ComfyUI integration
- **Bot (Phase 2)**: Telegram bot built with aiogram 3.x for user interaction

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- ComfyUI installed and running
- Telegram bot token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd QwenEditBot
```

2. **Backend Setup:**
```bash
cd backend
cp .env.example .env
# Edit backend/.env with your configuration
pip install -r requirements.txt
python run.py
```

The backend will be available at `http://localhost:8000`

3. **Bot Setup (in a new terminal):**
```bash
cd bot
cp .env.example .env
# Edit bot/.env with your BOT_TOKEN
pip install -r requirements.txt
python run.py
```

The bot will start and connect to the backend API.

4. **Worker Setup (in another terminal):**
```bash
cd worker
cp .env.example .env
# Edit worker/.env with your configuration
pip install -r requirements.txt
python run.py
```

The worker will start processing jobs from the queue and sending results to users.

### Quick Start Guide

1. Start the backend server (it runs on port 8000)
2. Start the bot (it will connect to the backend)
3. Open Telegram and interact with your bot using `/start`
4. Upload photos and select editing options

## 📋 Features Implemented

### ✅ Backend Core (Phase 1)
- FastAPI application with proper CORS configuration
- SQLite database with SQLAlchemy ORM
- Complete API documentation with Swagger UI
- Structured logging

### ✅ User Management
- User registration with initial balance
- User information retrieval
- Balance tracking

### ✅ Preset System
- CRUD operations for presets
- Category filtering (Styles, Lighting, Design)
- Admin-only creation/editing

### ✅ Job Queue
- Job creation with image upload
- Balance deduction on job creation
- Job status tracking
- Result retrieval

### ✅ Balance System
- Balance checking
- Point deduction
- Refund functionality
- Admin balance management

### ✅ ComfyUI Integration
- REST client for ComfyUI API
- Image upload to ComfyUI
- Prompt submission
- Status checking
- Result retrieval

### ✅ Telegram Bot (Phase 2)
- Modern bot built with aiogram 3.x
- FSM (Finite State Machine) for user flow management
- Main menu with ReplyKeyboard
- Inline keyboards for navigation
- Preset selection by category
- Custom prompt support
- Photo upload and processing
- Balance checking before job creation
- Complete error handling
- Full integration with backend API

### ✅ Worker System (Phase 3)
- Async worker process with job queue
- GPU lock mechanism (file-based)
- Job status management (queued → processing → completed/failed)
- ComfyUI integration with workflow processing
- Automatic retry with exponential backoff (5s, 10s, 20s)
- Result delivery to Telegram users
- Error handling with balance refunds
- Complete logging and monitoring
- Configurable polling intervals
- Graceful shutdown handling

## 🔧 Configuration

### Backend Configuration (backend/.env)
```env
# Bot configuration
BOT_TOKEN = "your_telegram_bot_token_here"

# ComfyUI configuration
COMFYUI_URL = "http://127.0.0.1:8188"
COMFY_INPUT_DIR = "C:/ComfyUI/input"
COMFYUI_TIMEOUT = 300

# Database configuration
DATABASE_URL = "sqlite:///./qwen.db"

# Balance configuration
INITIAL_BALANCE = 60
EDIT_COST = 30
WEEKLY_BONUS = 10

# Payment configuration (optional)
YUKASSA_SHOP_ID = ""
YUKASSA_API_KEY = ""

# Security
SECRET_KEY = "dev-secret-key-change-in-production"
```

### Bot Configuration (bot/.env)
```env
# Telegram Bot Token
BOT_TOKEN = your_telegram_bot_token_here

# Backend API URL
BACKEND_API_URL = http://localhost:8000
BACKEND_API_TIMEOUT = 30

# Telegram Webhook (optional, for production)
TELEGRAM_WEBHOOK_URL =

# Balance Configuration
INITIAL_BALANCE = 60
EDIT_COST = 30
```

### Worker Configuration (worker/.env)
```env
# Backend API
BACKEND_API_URL=http://localhost:8000
BACKEND_API_TIMEOUT=60

# ComfyUI
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_TIMEOUT=300
COMFYUI_POLL_INTERVAL=0.5
COMFYUI_INPUT_DIR=C:/ComfyUI/input
COMFYUI_OUTPUT_DIR=C:/ComfyUI/output

# Telegram
BOT_TOKEN=your_bot_token_here
TELEGRAM_API_URL=https://api.telegram.org

# Worker
WORKER_POLLING_INTERVAL=2
WORKER_GPU_LOCK_TIMEOUT=30
WORKER_LOG_LEVEL=INFO

# Retry
MAX_RETRIES=3
RETRY_DELAYS=5,10,20

# Results
RESULTS_DIR=./results
```

## 📖 Additional Documentation

- **Backend Documentation**: See `backend/README.md` for API details
- **Bot Documentation**: See `bot/BOT_README.md` for Telegram bot specifics

## 📂 Project Structure

```
QwenEditBot/
├── backend/                       # Phase 1 - Backend API
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI application
│   │   ├── config.py              # Configuration
│   │   ├── database.py            # Database setup
│   │   ├── models.py              # ORM models
│   │   ├── schemas.py             # Pydantic models
│   │   ├── api/                  # API endpoints
│   │   │   ├── users.py           # User endpoints
│   │   │   ├── presets.py         # Preset endpoints
│   │   │   ├── jobs.py            # Job endpoints
│   │   │   ├── balance.py         # Balance endpoints
│   │   │   └── telegram.py        # Telegram webhook
│   │   ├── services/              # Business logic
│   │   │   ├── comfyui.py         # ComfyUI client
│   │   │   └── balance.py         # Balance logic
│   │   └── utils/                 # Utilities
│   ├── .env.example               # Environment template
│   ├── requirements.txt           # Dependencies
│   └── run.py                     # Backend entry point
│
├── bot/                           # Phase 2 - Telegram Bot
│   ├── __init__.py
│   ├── main.py                    # Bot application
│   ├── config.py                  # Bot configuration
│   ├── states.py                  # FSM states
│   ├── keyboards.py               # Keyboards
│   ├── utils.py                   # Utility functions
│   ├── handlers/                  # Event handlers
│   │   ├── __init__.py
│   │   ├── start.py               # /start and commands
│   │   ├── menu.py                # Main menu
│   │   ├── presets.py             # Preset selection
│   │   ├── custom_prompt.py       # Custom prompts
│   │   ├── image_upload.py        # Image handling
│   │   ├── balance.py             # Balance management
│   │   └── help.py                # Help system
│   ├── services/
│   │   ├── __init__.py
│   │   └── api_client.py          # Backend API client
│   ├── .env.example               # Environment template
│   ├── requirements.txt           # Dependencies
│   └── run.py                     # Bot entry point
│
├── worker/                        # Phase 3 - Worker System
│   ├── __init__.py
│   ├── main.py                    # Worker application
│   ├── config.py                  # Worker configuration
│   ├── run.py                     # Worker entry point
│   ├── gpu/
│   │   ├── __init__.py
│   │   └── lock.py                 # GPU lock mechanism
│   ├── queue/
│   │   ├── __init__.py
│   │   ├── job_queue.py            # Job queue management
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── image_editor.py         # Image processing
│   │   └── result_handler.py       # Result delivery
│   ├── retry/
│   │   ├── __init__.py
│   │   └── strategy.py             # Retry logic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── backend_client.py       # Backend API client
│   │   ├── comfyui_client.py       # ComfyUI client
│   │   └── telegram_client.py      # Telegram client
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py               # Logging utilities
│   ├── .env.example               # Environment template
│   └── requirements.txt           # Dependencies
│
├── .gitignore
└── README.md                      # This file
```

## 🧪 API Testing

Use the Swagger UI at `http://localhost:8000/docs` to test all endpoints interactively.

### Example cURL commands:

**Register user:**
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456, "username": "testuser"}'
```

**Create job:**
```bash
curl -X POST "http://localhost:8000/api/jobs/create?user_id=1&preset_id=1" \
  -H "Content-Type: multipart/form-data" \
  -F "image_file=@test_image.jpg"
```

## ✅ Completed Phases

### ✅ Worker System (Phase 3 - Complete)
- Background job processing with asyncio
- Job queue management with polling
- GPU lock mechanism (file-based)
- Real-time result notifications to users
- ComfyUI task execution monitoring
- Automatic retry with exponential backoff
- Result delivery to Telegram
- Error handling and balance refunds
- Complete logging and monitoring

## 🔮 Future Phases

### Phase 4: Payment Integration (Final)
- SBP (Система быстрых платежей) integration
- Bank card payments via Yukassa
- Payment confirmation and validation
- Automatic balance top-up
- Payment history and receipts
- Webhook for payment notifications

## 📝 Notes

### Backend (Phase 1)
- The backend is ready for production use
- All acceptance criteria are met
- The system is designed for easy extension
- Comprehensive error handling is implemented
- All API endpoints follow REST conventions

### Bot (Phase 2)
- Complete FSM implementation for user flow management
- Full integration with backend API
- Graceful error handling and user feedback
- Ready for webhook deployment (currently using polling)
- Modular design for easy extension
- Comprehensive logging for debugging

### Development
- Uses polling mode for local development
- Backend and bot can run independently
- Proper separation of concerns
- Type hints throughout the codebase
- Async/await pattern for optimal performance