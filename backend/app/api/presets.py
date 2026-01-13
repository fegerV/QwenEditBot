from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from redis_client import redis_client
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.PresetResponse])
def get_presets(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get all presets, optionally filtered by category"""
    try:
        query = db.query(models.Preset)
        if category:
            query = query.filter(models.Preset.category == category)
        presets = query.order_by(models.Preset.order).all()
        return presets
    except Exception as e:
        logger.error(f"Error getting presets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting presets: {str(e)}"
        )

@router.get("/{preset_id}", response_model=schemas.PresetResponse)
def get_preset(preset_id: int, db: Session = Depends(get_db)):
    """Get a specific preset"""
    try:
        preset = db.query(models.Preset).filter(models.Preset.id == preset_id).first()
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preset not found"
            )
        return preset
    except Exception as e:
        logger.error(f"Error getting preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting preset: {str(e)}"
        )

@router.post("/", response_model=schemas.PresetResponse, status_code=status.HTTP_201_CREATED)
def create_preset(preset: schemas.PresetCreate, db: Session = Depends(get_db)):
    """Create a new preset (Admin only)"""
    try:
        new_preset = models.Preset(**preset.model_dump())
        db.add(new_preset)
        db.commit()
        db.refresh(new_preset)
        logger.info(f"Preset created: {new_preset.id}")
        return new_preset
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating preset: {str(e)}"
        )

@router.put("/{preset_id}", response_model=schemas.PresetResponse)
def update_preset(preset_id: int, preset: schemas.PresetCreate, db: Session = Depends(get_db)):
    """Update a preset (Admin only)"""
    try:
        db_preset = db.query(models.Preset).filter(models.Preset.id == preset_id).first()
        if not db_preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preset not found"
            )
        
        for key, value in preset.model_dump().items():
            setattr(db_preset, key, value)
        
        db.commit()
        db.refresh(db_preset)
        logger.info(f"Preset updated: {db_preset.id}")
        return db_preset
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating preset: {str(e)}"
        )

@router.delete("/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(preset_id: int, db: Session = Depends(get_db)):
    """Delete a preset (Admin only)"""
    try:
        preset = db.query(models.Preset).filter(models.Preset.id == preset_id).first()
        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preset not found"
            )
        
        db.delete(preset)
        db.commit()
        logger.info(f"Preset deleted: {preset_id}")
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting preset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting preset: {str(e)}"
        )