import logging
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import time

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
                try:
                    # Check if all required fields are present
                    required_fields = ['id', 'user_id', 'image_path', 'prompt', 'status']
                    missing_fields = [field for field in required_fields if field not in job_data or job_data[field] is None]
                    
                    if missing_fields:
                        logger.error(f"Missing required fields in job data: {missing_fields}")
                        logger.error(f"Job data: {job_data}")
                        continue  # Skip this job
                    
                    # Handle date conversion with error checking
                    created_at_val = job_data.get('created_at')
                    updated_at_val = job_data.get('updated_at')
                    
                    # Parse dates - handle different possible formats
                    if created_at_val:
                        if isinstance(created_at_val, str):
                            # If it's already a string, try to parse as ISO format
                            try:
                                parsed_created_at = datetime.fromisoformat(created_at_val.replace('Z', '+00:00'))
                            except ValueError:
                                logger.warning(f"Invalid date format for created_at: {created_at_val}, using current time")
                                parsed_created_at = datetime.utcnow()
                        elif hasattr(created_at_val, 'isoformat'):  # If it's a datetime object
                            parsed_created_at = created_at_val
                        else:
                            # Fallback to current time
                            parsed_created_at = datetime.utcnow()
                    else:
                        parsed_created_at = datetime.utcnow()
                    
                    if updated_at_val:
                        if isinstance(updated_at_val, str):
                            # If it's already a string, try to parse as ISO format
                            try:
                                parsed_updated_at = datetime.fromisoformat(updated_at_val.replace('Z', '+00:00'))
                            except ValueError:
                                logger.warning(f"Invalid date format for updated_at: {updated_at_val}, using current time")
                                parsed_updated_at = datetime.utcnow()
                        elif hasattr(updated_at_val, 'isoformat'):  # If it's a datetime object
                            parsed_updated_at = updated_at_val
                        else:
                            # Fallback to current time
                            parsed_updated_at = datetime.utcnow()
                    else:
                        parsed_updated_at = datetime.utcnow()
                    
                    job = Job(
                        id=job_data['id'],
                        user_id=job_data['user_id'],
                        image_path=job_data['image_path'],
                        prompt=job_data['prompt'],
                        status=job_data['status'],
                        created_at=parsed_created_at,
                        updated_at=parsed_updated_at
                    )
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error creating Job object from Redis data: {e}")
                    logger.error(f"Job data: {job_data}")
                    # Continue processing other jobs
                    continue
                
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
            if job:
                logger.debug(f"Job {job_id} status updated to {status} via API")
            else:
                logger.warning(f"Job {job_id} status update failed via API, but updated in Redis")
            
            return True
        except Exception as e:
            logger.error(f"Error updating job {job_id} status: {e}")
            # Still return True if Redis update was successful, since that's our primary storage
            return success  # Return the Redis update success status

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

    async def add_job(self, job: Job) -> bool:
        """
        Add job to queue
        """
        try:
            # Add to Redis queue
            job_data = job.dict()
            job_id = await redis_client.enqueue_job(job_data)
            
            logger.info(f"Job {job.id} added to queue")
            return True
        except Exception as e:
            logger.error(f"Error adding job {job.id} to queue: {e}")
            return False

    async def create_job(self, user_id: int, image_path: str, prompt: str) -> Job:
        """
        Create a new job instance
        """
        import time
        timestamp = datetime.utcnow()
        job_id = int(time.time() * 1000000)  # microseconds timestamp as ID
        
        job = Job(
            id=job_id,
            user_id=user_id,
            image_path=image_path,
            prompt=prompt,
            status="queued",
            created_at=timestamp,
            updated_at=timestamp
        )
        
        return job

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