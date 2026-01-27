from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import List, Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False  # Set to True for debugging SQL queries
)

# Create a configured "Session" class (SQLAlchemy 2.x style)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)

# Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Preset database functions
def get_presets_by_category(db: Session, category: str):
    """Get all presets for a category"""
    from .models import Preset
    return db.query(Preset).filter(
        Preset.category == category
    ).order_by(Preset.order_index).all()

def get_preset(db: Session, preset_id: int):
    """Get preset by ID"""
    from .models import Preset
    return db.query(Preset).filter(Preset.id == preset_id).first()

def get_all_presets(db: Session):
    """Get all presets"""
    from .models import Preset
    return db.query(Preset).order_by(Preset.order_index).all()

def create_preset(db: Session, preset_data: dict):
    """Create new preset"""
    from .models import Preset
    db_preset = Preset(**preset_data)
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return db_preset

def seed_presets_if_empty(db: Session) -> int:
    """Seed database with default presets if empty.
    
    NOTE: This function is deprecated. All presets are now defined in bot/handlers/menu.py.
    This function is kept for backward compatibility but does nothing.
    
    Returns 0 (no presets inserted).
    """
    logger.info("seed_presets_if_empty() called but presets are now in menu.py. Skipping database seed.")
    return 0

logger.info(f"Database connected: {settings.DATABASE_URL}")