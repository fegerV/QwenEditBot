from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .api import users, presets, jobs, balance, telegram
from . import models
import logging

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
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])

@app.on_event("startup")
def on_startup():
    create_tables()
    logger.info("QwenEditBot Backend started successfully")

@app.get("/")
def read_root():
    return {"message": "QwenEditBot Backend is running", "status": "ok"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}