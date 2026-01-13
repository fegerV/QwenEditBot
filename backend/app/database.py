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

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
async def get_presets_by_category(db: Session, category: str):
    """Get all presets for a category"""
    from .models import Preset
    return db.query(Preset).filter(
        Preset.category == category
    ).order_by(Preset.order).all()

async def get_preset(db: Session, preset_id: int):
    """Get preset by ID"""
    from .models import Preset
    return db.query(Preset).filter(Preset.id == preset_id).first()

async def get_all_presets(db: Session):
    """Get all presets"""
    from .models import Preset
    return db.query(Preset).order_by(Preset.order).all()

async def create_preset(db: Session, preset_data: dict):
    """Create new preset"""
    from .models import Preset
    db_preset = Preset(**preset_data)
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return db_preset

async def seed_presets_if_empty(db: Session):
    """Seed database with default presets if empty"""
    from .models import Preset
    
    count = db.query(Preset).count()
    if count > 0:
        logger.info(f"Database already contains {count} presets. Skipping seed.")
        return
    
    presets_data = [
        # Art Styles
        {"category": "styles", "name": "Oil Painting", "icon": "🖌", "prompt": "Convert the image into an oil painting style with visible brush strokes, rich colors, and a classical artistic feel, while preserving the original composition.", "order": 1},
        {"category": "styles", "name": "Watercolor", "icon": "💧", "prompt": "Convert the image into a watercolor painting with soft edges, light color bleeding, and a hand-painted artistic look, preserving the main details.", "order": 2},
        {"category": "styles", "name": "Pencil Sketch", "icon": "✏️", "prompt": "Transform the image into a detailed pencil sketch with clear linework and shading, like a hand-drawn illustration.", "order": 3},
        {"category": "styles", "name": "Ink Drawing", "icon": "🖋", "prompt": "Convert the image into an ink drawing with bold black outlines, high contrast, and a clean hand-drawn style.", "order": 4},
        
        # Portraits
        {"category": "portrait", "name": "Studio Portrait", "icon": "📸", "prompt": "Enhance the image into a professional studio portrait with soft lighting, realistic skin texture, and natural colors, preserving facial identity.", "order": 1},
        {"category": "portrait", "name": "Cinematic Portrait", "icon": "🎬", "prompt": "Convert the portrait into a cinematic style with dramatic lighting, shallow depth of field, and a movie-like atmosphere, while keeping the person's identity.", "order": 2},
        {"category": "portrait", "name": "Artistic Portrait", "icon": "🧑‍🎨", "prompt": "Create an artistic portrait with expressive lighting and painterly details, preserving facial features and overall composition.", "order": 3},
        
        # Products
        {"category": "product", "name": "E-commerce", "icon": "🛒", "prompt": "Transform the image into a clean professional product photo with neutral background, even lighting, and sharp details suitable for an online store.", "order": 1},
        {"category": "product", "name": "Premium Product", "icon": "🌟", "prompt": "Enhance the product image with dramatic lighting, glossy reflections, and a premium advertising look, keeping the product shape unchanged.", "order": 2},
        
        # Lighting
        {"category": "lighting", "name": "Soft Light", "icon": "🌞", "prompt": "Adjust the image to have soft, natural lighting with smooth shadows and a warm, pleasant atmosphere.", "order": 1},
        {"category": "lighting", "name": "Dark Mood", "icon": "🌙", "prompt": "Create a dark and moody atmosphere with low-key lighting, deep shadows, and cinematic contrast.", "order": 2},
        {"category": "lighting", "name": "Golden Hour", "icon": "🌅", "prompt": "Apply golden hour lighting with warm tones, soft highlights, and a sunset-like atmosphere.", "order": 3},
        
        # Animation
        {"category": "animation", "name": "Comic Book", "icon": "💥", "prompt": "Convert the image into a comic book style with bold outlines, flat colors, and a graphic illustrated look.", "order": 1},
        {"category": "animation", "name": "Anime", "icon": "🇯🇵", "prompt": "Transform the image into an anime style illustration with clean lines, expressive features, and vibrant colors.", "order": 2},
        {"category": "animation", "name": "Cartoon", "icon": "🧸", "prompt": "Convert the image into a cartoon style with simplified shapes, bright colors, and a playful illustrated look.", "order": 3},
        
        # Enhancement
        {"category": "enhancement", "name": "Improve Quality", "icon": "✨", "prompt": "Improve image quality by enhancing details, colors, and lighting while keeping the original style and composition unchanged.", "order": 1},
    ]
    
    for preset_data in presets_data:
        preset = Preset(
            **preset_data,
            price=30.0,
            workflow_type="qwen_edit_2511"
        )
        db.add(preset)
    
    db.commit()
    logger.info(f"Added {len(presets_data)} presets to database")

logger.info(f"Database connected: {settings.DATABASE_URL}")