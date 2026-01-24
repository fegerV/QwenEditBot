import asyncio
import logging
from typing import Optional
import uuid
from pathlib import Path

from worker.job_queue.job_queue import JobQueue
from worker.gpu.lock import GPULock
from worker.processors.image_editor import ImageEditorProcessor
from worker.processors.result_handler import ResultHandler
from worker.retry.strategy import RetryStrategy
from worker.config import settings
from worker.services.comfyui_client import ComfyUIClient
from worker.redis_client import redis_client
from worker.services.file_monitor import FileMonitor
from worker.job_queue.job_queue import Job

logger = logging.getLogger(__name__)


class QwenEditWorker:
    def __init__(self):
        self.queue = JobQueue()
        self.gpu_lock = GPULock()
        self.processor = ImageEditorProcessor()
        self.result_handler = ResultHandler()
        self.retry = RetryStrategy()
        self.comfyui_client = ComfyUIClient()
        self.file_monitor = None

    async def initialize(self):
        """Initialize worker components"""
        # Connect to Redis
        await redis_client.connect()
        logger.info("Worker initialized successfully")
        
        # Initialize file monitor if enabled
        if settings.MONITOR_INPUT_DIR:
            self.file_monitor = FileMonitor(settings.COMFYUI_INPUT_DIR, self.handle_new_file)
            logger.info("File monitor initialized")

    async def handle_new_file(self, filepath: str):
        """Handle new file detection in input directory"""
        logger.info(f"Handling new file: {filepath}")
        
        try:
            # Create a job for the new file
            # Since we don't have the user context, we'll use a placeholder user_id
            # In a real scenario, you might want to implement a different mechanism
            # to track and associate files with users
            
            # For now, we'll create a basic job with default parameters
            # We'll use a default prompt since we don't have user input
            default_prompt = "Convert to in the comic style, while preserving composition and character identity. remove the progress bar and watermarks"
            
            # Create job object using the factory method from JobQueue
            job = await self.queue.create_job(
                user_id=0,  # Placeholder user_id
                image_path=filepath,
                prompt=default_prompt
            )
            
            # Add job to queue
            success = await self.queue.add_job(job)
            
            if success:
                logger.info(f"Created job {job.id} for new file: {filepath}")
            else:
                logger.error(f"Failed to add job for file: {filepath}")
                
        except Exception as e:
            logger.error(f"Error handling new file {filepath}: {str(e)}")

    async def process_jobs(self):
        """Main worker loop with exponential backoff"""
        logger.info("Worker started, polling for jobs...")
        
        # Initialize components
        await self.initialize()
        
        # Start file monitor in background if enabled
        if self.file_monitor:
            asyncio.create_task(self.file_monitor.run())
            logger.info("File monitor started in background")
        
        # Define local variables to avoid UnboundLocalError
        polling_interval = settings.WORKER_POLLING_INTERVAL
        gpu_lock_timeout = settings.WORKER_GPU_LOCK_TIMEOUT
        max_backoff = 10  # Maximum wait time between job checks
        current_backoff = 0  # Current backoff time
        
        while True:
            try:
                # 1. Get next job from queue (non-blocking)
                logger.debug("Checking queue for next job...")
                job_data = await redis_client.dequeue_job()

                if not job_data:
                    # No job received - use exponential backoff
                    current_backoff = min(current_backoff + polling_interval, max_backoff)
                    logger.debug(f"No job in queue, waiting {current_backoff}s before next check...")
                    await asyncio.sleep(current_backoff)
                    continue
                
                # Reset backoff when job found
                current_backoff = 0

                # Convert job_data to Job object
                from datetime import datetime
                
                # Check if all required fields are present in job_data
                required_fields = ['id', 'user_id', 'image_path', 'prompt', 'status']
                missing_fields = [field for field in required_fields if field not in job_data or job_data[field] is None]
                
                if missing_fields:
                    logger.error(f"Missing required fields in job data: {missing_fields}")
                    logger.error(f"Job data: {job_data}")
                    continue  # Skip this job and continue with the next iteration
                
                # Handle date conversion with error checking
                created_at_val = job_data.get('created_at')
                updated_at_val = job_data.get('updated_at')
                
                # Parse dates - handle different possible formats
                if created_at_val:
                    if isinstance(created_at_val, str):
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
                    second_image_path=job_data.get('second_image_path'),
                    prompt=job_data['prompt'],
                    status=job_data['status'],
                    retry_count=job_data.get('retry_count', 0),
                    created_at=parsed_created_at,
                    updated_at=parsed_updated_at,
                )
                
                logger.info(f"Processing job {job.id} from queue (user: {job.user_id})")

                # 2. Try to acquire GPU lock
                if not await self.gpu_lock.acquire(timeout=gpu_lock_timeout):
                    logger.warning(f"Failed to acquire GPU lock for job {job.id}, returning to queue")
                    # Re-queue the job if GPU is busy
                    await redis_client.enqueue_job(job_data)
                    await asyncio.sleep(polling_interval)
                    continue

                try:
                    # 3. Check ComfyUI health before processing
                    logger.info(f"Checking ComfyUI health before processing job {job.id}")
                    try:
                        comfyui_healthy = await self.comfyui_client.check_health()
                        
                        if not comfyui_healthy:
                            logger.warning(f"ComfyUI health check failed for job {job.id}, returning to queue")
                            await redis_client.enqueue_job(job_data)
                            await asyncio.sleep(polling_interval)
                            continue
                    except Exception as health_error:
                        logger.error(f"Error during ComfyUI health check for job {job.id}: {health_error}")
                        await redis_client.enqueue_job(job_data)
                        await asyncio.sleep(polling_interval)
                        continue
                    
                    # 4. Update job status to processing
                    await self.queue.update_job_status(
                        job.id,
                        "processing"
                    )

                    # 5. Process the job with timeout protection
                    try:
                        result_path = await asyncio.wait_for(
                            self.processor.process(job),
                            timeout=settings.COMFYUI_TIMEOUT + 30  # Add buffer for safety
                        )
                    except asyncio.TimeoutError:
                        logger.error(f"Job {job.id} processing timeout exceeded")
                        raise Exception(f"Processing timeout exceeded ({settings.COMFYUI_TIMEOUT}s)")

                    # 6. Update job status to completed
                    if not Path(result_path).exists():
                        logger.error(f"Result file not found after processing for job {job.id}: {result_path}")
                        raise Exception(f"Result file not found: {result_path}")
                    
                    logger.info(f"Result file verified for job {job.id}: {result_path}")
                    
                    await self.queue.update_job_status(
                        job.id,
                        "completed",
                        result_path=result_path
                    )

                    # Store result in Redis
                    await redis_client.set_job_result(job.id, result_path)

                    # 7. Send result to user
                    logger.info(f"Sending result to user for job {job.id}")
                    try:
                        await self.result_handler.send_result(job, result_path)
                        logger.info(f"Result successfully sent to user for job {job.id}")
                    except Exception as result_error:
                        logger.error(f"Failed to send result to user for job {job.id}: {result_error}", exc_info=True)

                    logger.info(f"Job {job.id} completed successfully")

                except Exception as e:
                    logger.error(f"Error processing job {job.id}: {str(e)}", exc_info=True)

                    # Retry logic
                    retry_count = getattr(job, 'retry_count', 0)
                    should_retry = await self.retry.should_retry(job.id, str(e), retry_count)

                    if should_retry:
                        new_retry_count = retry_count + 1
                        await self.queue.update_job_status(
                            job.id,
                            "queued",
                            retry_count=new_retry_count
                        )
                        logger.info(f"Job {job.id} will be retried (attempt {new_retry_count})")
                    else:
                        # Final error
                        await self.queue.update_job_status(
                            job.id,
                            "failed",
                            error=str(e)
                        )
                        await self.result_handler.send_error(job, str(e))

                finally:
                    # Release GPU lock
                    await self.gpu_lock.release()
                    logger.debug("GPU lock released")

            except Exception as e:
                logger.error(f"Unexpected error in main loop: {str(e)}", exc_info=True)
                # Don't sleep too long on unexpected errors
                await asyncio.sleep(polling_interval)