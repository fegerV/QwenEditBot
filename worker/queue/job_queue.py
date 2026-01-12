import logging
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from worker.services.backend_client import BackendAPIClient
from worker.config import settings

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
    """Job queue (works with backend API)"""

    def __init__(self):
        self.backend_client = BackendAPIClient()

    async def get_pending_jobs(self, limit: int = 1) -> List[Job]:
        """
        Get jobs with status='queued'
        """
        try:
            jobs_data = await self.backend_client.get_pending_jobs(limit=limit)
            jobs = [Job(**job_data) for job_data in jobs_data]
            logger.debug(f"Found {len(jobs)} pending jobs")
            return jobs
        except Exception as e:
            logger.error(f"Error getting pending jobs: {e}")
            return []

    async def update_job_status(self, job_id: int, status: str, **kwargs) -> bool:
        """
        Update job status
        kwargs: result_path, error, retry_count
        """
        try:
            update_data = {"status": status}
            update_data.update(kwargs)
            
            job = await self.backend_client.update_job(job_id, update_data)
            logger.debug(f"Job {job_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id} status: {e}")
            return False

    async def get_job(self, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        try:
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