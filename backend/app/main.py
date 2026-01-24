from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import HTTPException, status
from .config import settings, ensure_directories
from .database import engine, Base, SessionLocal, seed_presets_if_empty
from .api import users, presets, jobs, balance, telegram, payments, webhooks, promocodes
from . import models
from .services.scheduler import WeeklyBonusScheduler
from redis_client import redis_client
from sqlalchemy import text
import logging
import os
from pathlib import Path
import asyncio
import sys

# Configure logging with file output
log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(log_directory, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_directory, 'backend_startup.log'), encoding='utf-8'),
        logging.FileHandler(os.path.join(log_directory, 'backend_runtime.log'), encoding='utf-8')
    ]
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
app.include_router(promocodes.router, prefix="/api/promocodes", tags=["promocodes"])

# Global scheduler instance
scheduler: WeeklyBonusScheduler = None

@app.on_event("startup")
async def on_startup():
    logger.info("="*60)
    logger.info("STARTING QwenEditBot Backend")
    logger.info("="*60)
    
    startup_errors = []
    
    # Pre-flight: Check environment
    logger.info("[1/7] Checking environment...")
    try:
        env = os.getenv('APP_ENV', 'production')
        logger.info(f"APP_ENV: {env}")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Python Executable: {sys.executable}")
    except Exception as e:
        logger.error(f"Environment check failed: {e}")
        startup_errors.append(f"Environment: {e}")
    
    # Step 1: Run migrations
    logger.info("[2/7] Running database migrations...")
    try:
        run_migrations()
        logger.info("[OK] Migrations completed")
    except Exception as e:
        logger.error(f"[ERROR] Migration failed: {e}")
        logger.exception("Migration error details")
        startup_errors.append(f"Migration: {str(e)[:100]}")
    
    # Step 2: Ensure required directories
    logger.info("[3/7] Creating required directories...")
    try:
        ensure_directories()
        logger.info("[OK] Directories ensured")
    except Exception as e:
        logger.error(f"[ERROR] Directory creation failed: {e}")
        logger.exception("Directory error details")
        startup_errors.append(f"Directories: {str(e)[:100]}")
    
    # Step 3: Test database connection
    logger.info("[4/7] Testing database connection...")
    db_test_session = None
    try:
        db_test_session = SessionLocal()
        result = db_test_session.execute(text("SELECT 1"))
        result.scalar()
        logger.info("[OK] Database connection successful")
        
        # Test if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"[OK] Found {len(tables)} tables in database: {tables[:5]}{'...' if len(tables) > 5 else ''}")
    except Exception as e:
        logger.error(f"[ERROR] Database connection failed: {e}")
        logger.exception("Database error details")
        startup_errors.append(f"Database: {str(e)[:100]}")
    finally:
        if db_test_session:
            db_test_session.close()
    
    # Step 4: Create tables (development only)
    logger.info("[5/7] Creating tables (if development)...")
    try:
        if os.getenv('APP_ENV', 'production').lower() == 'development':
            logger.info("Creating tables via metadata.create_all()...")
            create_tables()
            logger.info("[OK] Tables created")
        else:
            logger.info("Skipping Base.metadata.create_all() in production")
    except Exception as e:
        logger.error(f"[ERROR] Table creation failed: {e}")
        logger.exception("Table creation error details")
        startup_errors.append(f"Tables: {str(e)[:100]}")
    
    # Step 5: Seed presets
    logger.info("[6/7] Seeding presets...")
    db = SessionLocal()
    try:
        await asyncio.to_thread(seed_presets_if_empty, db)
        logger.info("[OK] Presets initialization completed")
    except Exception as e:
        logger.error(f"[ERROR] Preset seeding failed: {e}")
        logger.exception("Preset seeding error details")
        startup_errors.append(f"Presets: {str(e)[:100]}")
    finally:
        db.close()
    
    # Step 6: Connect to Redis (non-critical)
    logger.info("[7/7] Connecting to Redis...")
    try:
        await redis_client.connect()
        logger.info("[OK] Redis connected successfully")
    except Exception as e:
        logger.warning(f"[WARN] Redis connection failed (non-critical): {e}")
        # Don't add to startup_errors - this is non-critical
    
    # Step 7: Start scheduler (non-critical)
    logger.info("Starting WeeklyBonusScheduler...")
    global scheduler
    try:
        scheduler = WeeklyBonusScheduler(SessionLocal)
        await scheduler.start()
        logger.info("[OK] Scheduler started")
    except Exception as e:
        logger.warning(f"[WARN] Scheduler failed to start (non-critical): {e}")
        logger.exception("Scheduler error details (non-critical)")
        scheduler = None
        # Don't add to startup_errors - this is non-critical
    
    # Final status
    logger.info("="*60)
    if startup_errors:
        logger.error("BACKEND STARTUP COMPLETED WITH ERRORS:")
        for i, error in enumerate(startup_errors, 1):
            logger.error(f"  {i}. {error}")
        logger.warning("Backend started but some components may not work correctly")
    else:
        logger.info("[OK] BACKEND STARTUP COMPLETED SUCCESSFULLY")
    logger.info("="*60)

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