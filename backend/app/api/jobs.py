from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from ..config import settings
from ..services.balance import check_balance, deduct_balance, refund_balance
import logging
import os
from pathlib import Path
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/create", response_model=schemas.JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    user_id: int,
    preset_id: Optional[int] = None,
    prompt: Optional[str] = None,
    workflow_type: Optional[str] = "standard",
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Create a new job"""
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check balance
        if not check_balance(user_id, settings.EDIT_COST, db):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient balance. Required: {settings.EDIT_COST}, Available: {user.balance}"
            )
        
        # Get preset prompt and workflow_type if preset_id is provided
        job_prompt = prompt
        if preset_id:
            preset = db.query(models.Preset).filter(models.Preset.id == preset_id).first()
            if not preset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Preset not found"
                )
            job_prompt = preset.prompt
            workflow_type = preset.workflow_type or "standard"
        
        # Save uploaded image
        input_dir = Path(settings.COMFY_INPUT_DIR)
        input_dir.mkdir(parents=True, exist_ok=True)
        
        file_ext = image_file.filename.split('.')[-1]
        image_filename = f"input_{uuid.uuid4().hex}.{file_ext}"
        image_path = input_dir / image_filename
        
        # Save the file
        with open(image_path, "wb") as buffer:
            buffer.write(await image_file.read())
        
        # Create job
        new_job = models.Job(
            user_id=user_id,
            image_path=str(image_path),
            prompt=job_prompt,
            status=schemas.JobStatus.queued
        )
        
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Deduct balance
        deduct_balance(user_id, settings.EDIT_COST, f"Job creation: {new_job.id}", db)
        
        logger.info(f"Job created: {new_job.id}")
        return new_job
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating job: {e}")
        # Refund balance if job creation failed
        if 'user' in locals():
            refund_balance(user.user_id, settings.EDIT_COST, f"Job creation failed: {str(e)}", db)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating job: {str(e)}"
        )

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job status"""
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return job
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting job: {str(e)}"
        )

@router.get("/", response_model=List[schemas.JobResponse])
def get_jobs(
    status: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get jobs with optional status filter"""
    try:
        query = db.query(models.Job)
        
        if status:
            query = query.filter(models.Job.status == status)
        
        jobs = query.order_by(models.Job.created_at.asc()).limit(limit).all()
        return jobs
    except Exception as e:
        logger.error(f"Error getting jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting jobs: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[schemas.JobResponse])
def get_user_jobs(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get user's jobs with pagination"""
    try:
        jobs = db.query(models.Job).filter(models.Job.user_id == user_id)
        jobs = jobs.offset(skip).limit(limit).order_by(models.Job.created_at.desc()).all()
        return jobs
    except Exception as e:
        logger.error(f"Error getting user jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user jobs: {str(e)}"
        )

@router.put("/{job_id}", response_model=schemas.JobResponse)
def update_job_status(
    job_id: int,
    job_update: schemas.JobUpdate,
    db: Session = Depends(get_db)
):
    """Update job status (Worker only)"""
    try:
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Update job status
        job.status = job_update.status
        job.result_path = job_update.result_path
        job.error = job_update.error

        # Update retry count if provided
        if job_update.retry_count is not None:
            job.retry_count = job_update.retry_count
        
        db.commit()
        db.refresh(job)
        
        logger.info(f"Job updated: {job_id}, status: {job_update.status}")
        return job
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating job: {str(e)}"
        )