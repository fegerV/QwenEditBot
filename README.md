# QwenEditBot - Complete AI Image Editing Solution

A complete Telegram bot for AI-powered image editing using ComfyUI, featuring a modern FastAPI backend and a user-friendly Telegram interface.

## 🎨 Architecture Overview

The project consists of four main components:
- **Backend (Phase 1)**: FastAPI REST API with database, job queue, ComfyUI integration, and payment system
- **Bot (Phase 2)**: Telegram bot built with aiogram 3.x for user interaction
- **Worker (Phase 3)**: Async worker process with job queue and GPU management
- **Payments (Phase 4)**: YuKassa integration with SBP support and weekly bonus system

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- ComfyUI installed and running
- Telegram bot token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/fegerV/QwenEditBot
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
COMFY_INPUT_DIR = "C:/ComfyUI/ComfyUI/input/bot"
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
BACKEND_URL = http://localhost:8000
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
COMFYUI_INPUT_DIR=C:/ComfyUI/ComfyUI/input/bot
COMFYUI_OUTPUT_DIR=C:/ComfyUI/ComfyUI/output/bot

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

### ✅ Payment System (Phase 4 - Complete)
- YuKassa integration for payments (SBP, cards)
- Payment creation and confirmation URLs
- Webhook handling for payment status updates
- Payment history for users
- Weekly bonus system (automatic +10 points on Friday 20:00 UTC)
- Telegram notifications for payments and bonuses
- Refund payment type for balance recovery
- Full payment lifecycle management
- HMAC-SHA256 signature verification for webhooks

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

## 💳 Payment Configuration (Phase 4)

### YuKassa Setup

1. Register at [YooKassa](https://yookassa.ru)
2. Create a shop and obtain credentials:
   - `SHOP_ID`: Your shop ID
   - `API_KEY`: From the developer panel
   - `WEBHOOK_SECRET`: For webhook signature verification

3. Configure webhooks in YooKassa dashboard:
   - URL: `https://your-backend.com/api/webhooks/yukassa`
   - Events: `payment.succeeded`, `payment.failed`, `payment.canceled`

### Environment Variables

Add to `backend/.env`:

```env
# YuKassa Configuration
YUKASSA_SHOP_ID="your_shop_id"
YUKASSA_API_KEY="live_your_api_key"
YUKASSA_WEBHOOK_SECRET="your_webhook_secret"

# Payment Settings
PAYMENT_MIN_AMOUNT=1           # Minimum amount in rubles
PAYMENT_MAX_AMOUNT=10000       # Maximum amount in rubles
PAYMENT_RETURN_URL="https://t.me/YourBotUsername"
POINTS_PER_RUBLE=100          # 1 ruble = 100 points

# Weekly Bonus Configuration
WEEKLY_BONUS_ENABLED=true
WEEKLY_BONUS_AMOUNT=10         # Points to give each user
WEEKLY_BONUS_DAY=4            # 0=Monday, 4=Friday
WEEKLY_BONUS_TIME="20:00"     # HH:MM UTC
```

## 🔐 Безопасность платежей

- ✅ Все webhook'и от YuKassa проверяются по HMAC-SHA256 подписи
- ✅ Поддельные платежи автоматически отклоняются (401 Unauthorized)
- ✅ Все платежи логируются для аудита
- ✅ YuKassa API ключи хранятся в переменных окружения (не в коде)

### Payment Flow

1. User selects "➕ Пополнить" in bot
2. Chooses amount (100₽, 250₽, 500₽, 1000₽, or custom)
3. User selects payment method (Card or SBP)
4. Backend creates payment in YuKassa with the selected method
5. Bot sends payment link to user
6. User pays via SBP/card
7. YuKassa sends webhook to backend
8. Backend verifies signature and updates payment status
9. Balance is credited automatically
10. User receives Telegram notification

### Weekly Bonus

Every Friday at 20:00 UTC:
- All registered users receive +10 points
- Telegram notification sent to each user
- Payment recorded as "weekly_bonus" type
- Configurable amount and schedule

### Payment History

Users can view:
- All their payments (top-ups, bonuses, refunds)
- Payment status (pending, succeeded, failed, cancelled)
- Payment type (payment, weekly_bonus, refund)
- Timestamp and amount

## 🧪 API Testing

Use the Swagger UI at `http://localhost:8000/docs` to test all endpoints.

### Payment API Examples

**Create payment:**
```bash
curl -X POST "http://localhost:8000/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": 100, "payment_method": "sbp"}'
```

**Get payment status:**
```bash
curl -X GET "http://localhost:8000/api/payments/1"
```

**Get payment history:**
```bash
curl -X GET "http://localhost:8000/api/payments/user/1?limit=10"
```

## 🔮 Future Phases

All phases are now complete! The system is production-ready.

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

## 🤖 Настройка BotFather

Для корректной работы всех команд бота необходимо настроить его в Telegram через BotFather.

### 📋 Быстрая настройка

1. **Автоматическая настройка (рекомендуется):**
   ```bash
   # Linux/Mac
   cd bot
   chmod +x setup_botfather.sh
   ./setup_botfather.sh
   
   # Windows
   cd bot
   .\setup_botfather.ps1
   ```

2. **Ручная настройка:**
   - Откройте файл `bot/BOTFATHER_SETUP.txt`
   - Следуйте пошаговой инструкции

### 📚 Документация

- **Подробная инструкция:** `bot/SETUP_INSTRUCTIONS.md`
- **Пошаговая настройка:** `bot/BOTFATHER_SETUP.txt`
- **Автоматические скрипты:**
  - `bot/setup_botfather.sh` (Linux/Mac)
  - `bot/setup_botfather.ps1` (Windows)

### ✅ Что настраивается

- **Команды бота:** `/start`, `/help`, `/menu`, `/balance`, `/cancel`
- **Описание бота:** Текст в профиле бота
- **Информация о боте:** Краткое описание функций
- **Приватность:** Режим приватности для работы в группах

### 🔧 Команды после настройки

После настройки BotFather пользователи смогут:
- Видеть список команд при вводе `/`
- Получать подсказки по командам
- Легко навигировать по функциям бота

### 📖 Подробная документация

Полную информацию о настройке и возможностях BotFather смотрите в файле `bot/SETUP_INSTRUCTIONS.md`.
