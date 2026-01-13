import logging
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from worker.redis_client import redis_client
from worker.config import settings
from worker.services.backend_client import BackendAPIClient

logger = logging.getLogger(__name__)


class Job(BaseModel):
    """Job model for worker"""
    id: int
    user_id: int
    image_path: str
    prompt: str
    status: str
    result_path: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime


class JobQueue:
    """Job queue (now uses Redis)"""

    def __init__(self):
        self.backend_client = BackendAPIClient()

    async def get_pending_jobs(self, limit: int = 1) -> List[Job]:
        """
        Get jobs with status='queued'
        """
        try:
            jobs_data = await redis_client.get_pending_jobs(limit=limit)
            jobs = []
            for job_data in jobs_data:
                # Convert Redis job data to Job model
                job = Job(
                    id=job_data['id'],
                    user_id=job_data['user_id'],
                    image_path=job_data['image_path'],
                    prompt=job_data['prompt'],
                    status=job_data['status'],
                    created_at=datetime.fromisoformat(job_data['created_at']) if job_data.get('created_at') else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(job_data['updated_at']) if job_data.get('updated_at') else datetime.utcnow()
                )
                jobs.append(job)
                
            logger.debug(f"Found {len(jobs)} pending jobs from Redis")
            return jobs
        except Exception as e:
            logger.error(f"Error getting pending jobs from Redis: {e}")
            # Fallback to API
            try:
                jobs_data = await self.backend_client.get_pending_jobs(limit=limit)
                jobs = [Job(**job_data) for job_data in jobs_data]
                logger.debug(f"Fallback: Found {len(jobs)} pending jobs from API")
                return jobs
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return []

    async def update_job_status(self, job_id: int, status: str, **kwargs) -> bool:
        """
        Update job status
        kwargs: result_path, error, retry_count
        """
        try:
            # Update in Redis
            success = await redis_client.update_job_status(job_id, status, **kwargs)
            if success:
                logger.debug(f"Job {job_id} status updated to {status} in Redis")
            
            # Also update via API for consistency
            update_data = {"status": status}
            update_data.update(kwargs)
            
            job = await self.backend_client.update_job(job_id, update_data)
            logger.debug(f"Job {job_id} status updated to {status} via API")
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id} status: {e}")
            return False

    async def get_job(self, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        try:
            # Try to get from Redis first
            # For now, we'll get from API as Redis doesn't store full job details
            job_data = await self.backend_client.get_job(job_id)
            if job_data:
                return Job(**job_data)
            return None
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            return None

    async def refund_balance(self, user_id: int, amount: int, reason: str) -> bool:
        """Refund balance to user"""
        try:
            success = await self.backend_client.refund_balance(user_id, amount, reason)
            if success:
                logger.info(f"Refunded {amount} points to user {user_id}: {reason}")
            return success
        except Exception as e:
            logger.error(f"Error refunding balance to user {user_id}: {e}")
            return False