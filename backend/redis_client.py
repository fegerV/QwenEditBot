import logging
from typing import Optional, List, Dict, Any
import json
import asyncio
from redis.asyncio import Redis
from app.config import settings

logger = logging.getLogger(__name__)


class RedisQueueClient:
    """Redis client for job queue management"""
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        
    async def connect(self):
        """Connect to Redis server"""
        try:
            self.redis = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            await self.redis.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            
    async def enqueue_job(self, job_data: Dict[str, Any]) -> str:
        """Add job to queue"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        job_id = job_data.get('id')
        if not job_id:
            raise ValueError("Job must have an id field")
        
        # Add job to queue
        queue_item = {
            'id': job_id,
            'user_id': job_data['user_id'],
            'image_path': job_data['image_path'],
            'prompt': job_data['prompt'],
            'status': 'queued',
            'created_at': job_data.get('created_at'),
            'updated_at': job_data.get('updated_at')
        }
        
        await self.redis.lpush(settings.REDIS_JOB_QUEUE_KEY, json.dumps(queue_item))
        logger.info(f"Job {job_id} added to Redis queue")
        
        return str(job_id)
    
    async def dequeue_job(self) -> Optional[Dict[str, Any]]:
        """Get next job from queue (blocking pop)"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        # Blocking pop from queue
        result = await self.redis.brpop(settings.REDIS_JOB_QUEUE_KEY, timeout=1)
        if result:
            _, job_json = result
            job_data = json.loads(job_json)
            logger.info(f"Job {job_data['id']} dequeued from Redis")
            return job_data
        
        return None
    
    async def get_pending_jobs(self, limit: int = 1) -> List[Dict[str, Any]]:
        """Get pending jobs without removing from queue"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        # Get jobs from queue without removing them
        job_jsons = await self.redis.lrange(settings.REDIS_JOB_QUEUE_KEY, 0, limit - 1)
        jobs = []
        
        for job_json in job_jsons:
            job_data = json.loads(job_json)
            jobs.append(job_data)
        
        return jobs
    
    async def update_job_status(self, job_id: int, status: str, **kwargs) -> bool:
        """Update job status in Redis"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        # Update job status - for now just log that this would happen
        logger.info(f"Job {job_id} status would be updated to {status} in Redis with data: {kwargs}")
        return True
    
    async def set_job_result(self, job_id: int, result_path: str) -> bool:
        """Store job result in Redis"""
        if not self.redis:
            raise RuntimeError("Redis client not connected")
        
        result_data = {
            'job_id': job_id,
            'result_path': result_path,
            'completed_at': asyncio.get_event_loop().time()
        }
        
        await self.redis.setex(
            f"job_result:{job_id}",
            settings.REDIS_RESULT_TTL,
            json.dumps(result_data)
        )
        
        logger.info(f"Job {job_id} result stored in Redis")
        return True


# Global Redis client instance
redis_client = RedisQueueClient()