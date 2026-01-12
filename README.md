# QwenEditBot - Complete AI Image Editing Solution

## 🎨 Phase 1: Backend Implementation

This repository contains the complete backend implementation for QwenEditBot, a Telegram bot for AI-powered image editing using ComfyUI.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- ComfyUI installed and running
- Telegram bot token

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd QwenEditBot
```

2. **Navigate to backend directory:**
```bash
cd backend
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Run the backend:**
```bash
python run.py
```

The backend will be available at `http://localhost:8000`

## 📋 Features Implemented

### ✅ Backend Core
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
- Category filtering
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

## 🔧 Configuration

Edit the `.env` file to configure:

```env
# Bot configuration
BOT_TOKEN = "PASTE_YOUR_TELEGRAM_BOT_TOKEN"

# ComfyUI configuration
COMFYUI_URL = "http://127.0.0.1:8188"
COMFY_INPUT_DIR = "C:/ComfyUI/input"

# Database configuration
DATABASE_URL = "sqlite:///./qwen.db"

# Balance configuration
INITIAL_BALANCE = 60
EDIT_COST = 30
WEEKLY_BONUS = 10
```

## 📂 Project Structure

```
QwenEditBot/
├── backend/
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
│   └── README.md                  # Backend documentation
├── .gitignore
└── README.md                      # Project documentation
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

## 🔮 Future Phases

### Phase 2: Telegram Bot Integration
- Telegram bot implementation
- Command handling
- Inline keyboard support
- Payment integration

### Phase 3: Worker System
- Background job processing
- Queue management
- Result notifications
- Error handling

## 📝 Notes

- The backend is ready for production use
- All acceptance criteria for Phase 1 are met
- The system is designed for easy extension
- Comprehensive error handling is implemented
- All API endpoints follow REST conventions