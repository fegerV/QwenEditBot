# QwenEditBot - Telegram Bot (Phase 2)

## 📋 Overview

This is the Telegram bot implementation for QwenEditBot, built with aiogram 3.x. It provides a user-friendly interface for the AI image editing service.

## 🚀 Quick Start

### Prerequisites

1. **Backend API must be running:**
   ```bash
   cd backend
   python run.py
   ```

2. **Install bot dependencies:**
   ```bash
   cd bot
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your BOT_TOKEN
   ```

4. **Run the bot:**
   ```bash
   python run.py
   ```

## 📂 Project Structure

```
bot/
├── __init__.py
├── main.py                 # Bot application entry point
├── config.py               # Configuration management
├── states.py               # FSM state definitions
├── keyboards.py            # Inline and Reply keyboards
├── utils.py                # Utility functions
├── run.py                  # Bot launcher
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── handlers/               # Event handlers
│   ├── __init__.py
│   ├── start.py           # /start, /help, /menu commands
│   ├── menu.py            # Main menu navigation
│   ├── presets.py         # Preset selection
│   ├── custom_prompt.py   # Custom prompt handling
│   ├── image_upload.py    # Photo upload and processing
│   ├── balance.py         # Balance management
│   └── help.py           # Help system
└── services/              # External services
    ├── __init__.py
    └── api_client.py      # Backend API client
```

## 🎯 User Flow

1. **User starts bot** (`/start`)
   - Bot registers user in backend (if not exists)
   - User receives 60 points bonus
   - Main menu is displayed

2. **User selects editing option:**
   - Choose from presets (Styles, Lighting, Design)
   - OR write custom prompt
   - Upload photo
   - Photo is sent to backend for processing

3. **Backend processes:**
   - Checks user balance (requires 30 points)
   - Creates job in queue
   - Processes image with ComfyUI (Phase 3)
   - Returns result to user (Phase 3)

## 🔧 Configuration

### Environment Variables (.env)

```env
BOT_TOKEN=your_telegram_bot_token_here
BACKEND_URL=http://localhost:8000
BACKEND_API_TIMEOUT=30
TELEGRAM_WEBHOOK_URL=
INITIAL_BALANCE=60
EDIT_COST=30
```

`BACKEND_API_URL` is also supported for backward compatibility.

## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and register user |
| `/help` | Show help information |
| `/menu` | Return to main menu |
| `/balance` | Show current balance |

## 🎨 Main Menu

The bot provides a main menu with the following options:

```
🎨 Редактировать фото
🧩 Стили
💡 Освещение
🖼 Оформление
✍️ Свой промпт
💰 Баланс
➕ Пополнить
ℹ️ Помощь
```

## 🔄 FSM States

The bot uses Finite State Machine (FSM) to manage user interaction:

- `main_menu` - User is at main menu
- `select_preset_category` - Selecting preset category
- `select_preset` - Selecting specific preset
- `awaiting_image_for_preset` - Waiting for image upload (preset flow)
- `awaiting_custom_prompt` - Waiting for custom prompt text
- `awaiting_image_for_custom` - Waiting for image upload (custom prompt flow)
- `awaiting_payment` - In payment menu
- `processing_job` - Job is being processed

## 🔌 API Integration

The bot communicates with the backend API through `BackendAPIClient`:

- `register_user()` - Register new user
- `get_user()` - Get user information
- `get_balance()` - Get user balance
- `check_balance()` - Check if user has enough balance
- `get_presets()` - Get presets (optionally by category)
- `create_job()` - Create new job with image upload
- `get_job_status()` - Get job status
- `get_user_jobs()` - Get user's jobs

## 🧪 Testing

### Test Import
```bash
python test_bot_import.py
```

### Manual Testing
1. Start backend API
2. Start bot
3. Open Telegram and interact with bot
4. Test all features:
   - `/start` command
   - Navigate through menu
   - Select presets
   - Upload photos
   - Check balance

## 📝 Notes

- **Polling Mode**: Bot uses polling for local development
- **Error Handling**: All handlers have try-catch blocks with logging
- **User Feedback**: Users receive clear messages for errors and success states
- **Logging**: Comprehensive logging for debugging
- **Type Hints**: All functions have type annotations

## 🔮 Future Enhancements (Phase 3 & 4)

- **Phase 3**: Worker system for background job processing
- **Phase 4**: Payment integration (SBP, cards)
- **Real-time notifications**: Send results when ready
- **Webhook mode**: For production deployment
- **Admin panel**: Manage presets and users

## 🐛 Troubleshooting

### Bot won't start
- Check if BOT_TOKEN is set in `.env`
- Check if backend API is running on `http://localhost:8000`
- Check bot logs for errors

### Can't upload photos
- Check if backend API is accessible
- Check if ComfyUI input directory exists
- Check file permissions

### Balance issues
- Check if user is registered in backend
- Check database for user balance
- Check balance deduction logic in backend

## 📞 Support

For issues or questions:
- Check backend logs
- Check bot logs
- Review API documentation at `http://localhost:8000/docs`
