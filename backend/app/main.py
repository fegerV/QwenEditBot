from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import HTTPException, status
from .config import settings
from .database import engine, Base
from .api import users, presets, jobs, balance, telegram, payments, webhooks
from .services.scheduler import WeeklyBonusScheduler
from . import models
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
def create_tables():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

# Create FastAPI app
app = FastAPI(
    title="QwenEditBot Backend",
    description="Backend API for QwenEditBot with ComfyUI integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(presets.router, prefix="/api/presets", tags=["presets"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(balance.router, prefix="/api/balance", tags=["balance"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])

weekly_bonus_scheduler = WeeklyBonusScheduler()


@app.on_event("startup")
async def on_startup():
    create_tables()
    weekly_bonus_scheduler.start()
    logger.info("QwenEditBot Backend started successfully")


@app.on_event("shutdown")
def on_shutdown():
    weekly_bonus_scheduler.shutdown()

@app.get("/")
def read_root():
    return {"message": "QwenEditBot Backend is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/file/{file_path:path}")
async def download_file(file_path: str):
    """Download file from server"""
    try:
        file_path_obj = Path(file_path)
        
        # Security check - only allow files within certain directories
        allowed_dirs = [
            settings.COMFY_INPUT_DIR,
            settings.COMFY_OUTPUT_DIR,
            "./results"
        ]
        
        # Check if file is in allowed directory
        is_allowed = False
        for allowed_dir in allowed_dirs:
            allowed_dir_path = Path(allowed_dir)
            if allowed_dir_path in file_path_obj.parents or str(file_path_obj).startswith(str(allowed_dir_path)):
                is_allowed = True
                break
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this file is not allowed"
            )
        
        if not file_path_obj.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        return FileResponse(file_path)
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )