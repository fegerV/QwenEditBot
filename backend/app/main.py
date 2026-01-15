from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import HTTPException, status
from .config import settings, ensure_directories
from .database import engine, Base, SessionLocal, seed_presets_if_empty
from .api import users, presets, jobs, balance, telegram, payments, webhooks
from . import models
from .services.scheduler import WeeklyBonusScheduler
from redis_client import redis_client
import logging
import os
from pathlib import Path
import asyncio

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

# Run database migrations
def run_migrations():
    logger.info("Running database migrations...")
    try:
        import subprocess
        result = subprocess.run([
            "alembic", "upgrade", "head"
        ], cwd=".", capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Database migrations applied successfully")
        else:
            logger.error(f"Failed to apply migrations: {result.stderr}")
    except Exception as e:
        logger.exception(f"Error running migrations: {e}")

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
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

# Global scheduler instance
scheduler: WeeklyBonusScheduler = None

@app.on_event("startup")
async def on_startup():
    # Run migrations first
    try:
        run_migrations()
    except Exception as e:
        logger.exception("Error during migrations on startup")

    # Ensure required directories exist (create at startup to avoid import side-effects)
    try:
        ensure_directories()
        logger.info("Ensured required directories exist")
    except Exception:
        logger.exception("Failed to ensure directories")

    # Create tables only in development to avoid masking migration problems
    try:
        if os.getenv('APP_ENV', 'production').lower() == 'development':
            create_tables()
        else:
            logger.info('Skipping Base.metadata.create_all() in non-development environment')
    except Exception:
        logger.exception("Failed to create tables via metadata.create_all")

    # Connect to Redis
    try:
        await redis_client.connect()
        logger.info("Connected to Redis successfully")
    except Exception:
        logger.exception("Failed to connect to Redis - continuing startup without Redis")
        # don't re-raise; allow app to start without Redis

    # Seed presets if database is empty - run in thread to avoid blocking event loop
    db = SessionLocal()
    try:
        try:
            await asyncio.to_thread(seed_presets_if_empty, db)
            logger.info("Presets initialization completed")
        except Exception:
            logger.exception("Failed to seed presets")
    finally:
        db.close()

    # Start weekly bonus scheduler
    global scheduler
    try:
        scheduler = WeeklyBonusScheduler(SessionLocal)
        await scheduler.start()
    except Exception:
        logger.exception("Failed to start WeeklyBonusScheduler")
        scheduler = None

    logger.info("QwenEditBot Backend started successfully")

@app.on_event("shutdown")
async def on_shutdown():
    # Stop weekly bonus scheduler
    global scheduler
    if scheduler:
        try:
            await scheduler.stop()
        except Exception:
            logger.exception("Error stopping scheduler")

    # Close Redis connection
    try:
        await redis_client.close()
        logger.info("Redis connection closed")
    except Exception:
        logger.exception("Error closing Redis connection")

    logger.info("QwenEditBot Backend shutdown complete")

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

        # Resolve to absolute path
        if not file_path_obj.is_absolute():
            file_path_obj = (Path.cwd() / file_path_obj).resolve()
        else:
            file_path_obj = file_path_obj.resolve()

        # Build list of allowed directories (resolve them)
        allowed_dirs = []
        for allowed_dir in (
            getattr(settings, 'COMFY_INPUT_DIR', None),
            getattr(settings, 'COMFY_OUTPUT_DIR', None),
            getattr(settings, 'UPLOADS_DIR', None),
            './results'
        ):
            if not allowed_dir:
                continue
            allowed_dirs.append(Path(allowed_dir).resolve())

        # Security check - ensure requested file is inside one of the allowed directories
        is_allowed = False
        for d in allowed_dirs:
            try:
                if file_path_obj.is_relative_to(d):
                    is_allowed = True
                    break
            except Exception:
                # For Python versions without is_relative_to, fallback to manual check
                try:
                    if str(d) == str(file_path_obj) or str(file_path_obj).startswith(str(d) + os.sep):
                        is_allowed = True
                        break
                except Exception:
                    continue

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

        return FileResponse(str(file_path_obj))

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )