# QwenEditBot Backend

FastAPI backend for QwenEditBot with ComfyUI integration, user management, balance system, presets, and job queue.

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone <repository-url>
cd QwenEditBot/backend
```

### 2. Create .env file
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
- `BOT_TOKEN`: Your Telegram bot token
- `COMFYUI_URL`: URL to your ComfyUI instance
- `COMFY_INPUT_DIR`: Directory where ComfyUI expects input images
- `DATABASE_URL`: SQLite database URL

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the backend
```bash
python run.py
```

The backend will start on `http://localhost:8000`

### 5. Access API documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📋 API Endpoints

### Users
- `POST /api/users/register` - Register new user
- `GET /api/users/{user_id}` - Get user info
- `GET /api/users/{user_id}/balance` - Get user balance

### Balance
- `GET /api/balance/{user_id}` - Get balance
- `POST /api/balance/{user_id}/check` - Check sufficient balance
- `POST /api/balance/{user_id}/deduct` - Deduct points
- `POST /api/balance/{user_id}/refund` - Refund points
- `POST /api/balance/{user_id}/add` - Add points (admin)

### Presets
- `GET /api/presets` - List all presets
- `GET /api/presets/{preset_id}` - Get specific preset
- `POST /api/presets` - Create preset (admin)
- `PUT /api/presets/{preset_id}` - Update preset (admin)
- `DELETE /api/presets/{preset_id}` - Delete preset (admin)

### Jobs
- `POST /api/jobs/create` - Create new job
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs/user/{user_id}` - List user jobs
- `PUT /api/jobs/{job_id}` - Update job status (worker)

### Telegram
- `POST /api/telegram/webhook` - Telegram webhook

## 🧪 Testing with cURL

### Register a user
```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": 123456, "username": "testuser"}'
```

### Get user info
```bash
curl -X GET "http://localhost:8000/api/users/1"
```

### Check balance
```bash
curl -X POST "http://localhost:8000/api/balance/1/check" \
  -H "Content-Type: application/json" \
  -d '{"required_points": 30}'
```

### Create a job
```bash
curl -X POST "http://localhost:8000/api/jobs/create?user_id=1&preset_id=1" \
  -H "Content-Type: multipart/form-data" \
  -F "image_file=@test_image.jpg"
```

## 📦 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app
│   ├── config.py              # Configuration
│   ├── database.py            # Database setup
│   ├── models.py              # ORM models
│   ├── schemas.py             # Pydantic models
│   ├── api/                  # API endpoints
│   ├── services/              # Business logic
│   └── utils/                 # Utilities
├── .env.example
├── requirements.txt
└── run.py
```

## 🔧 Configuration

Edit `.env` file to configure:
- Database connection
- ComfyUI integration
- Telegram bot token
- Payment gateways
- Balance settings

## 🐳 Docker (Future)

Docker support will be added in future phases.

## 🤖 ComfyUI Integration

The backend integrates with ComfyUI for image processing:
- Uploads images to ComfyUI input directory
- Sends prompts to ComfyUI API
- Retrieves processed results

## 💰 Balance System

- Users start with 60 points
- Each edit costs 30 points
- Weekly bonus of 10 points
- Admin can add/refund points

## 📝 Notes

- CORS is enabled for all origins
- SQLite database is used by default
- All API endpoints are documented with Swagger
- Error handling with proper HTTP status codes