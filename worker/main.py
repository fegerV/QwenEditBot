import asyncio
import logging
from typing import Optional

from worker.queue.job_queue import JobQueue
from worker.gpu.lock import GPULock
from worker.processors.image_editor import ImageEditorProcessor
from worker.processors.result_handler import ResultHandler
from worker.retry.strategy import RetryStrategy
from worker.config import settings
from worker.services.comfyui_client import ComfyUIClient

logger = logging.getLogger(__name__)


class QwenEditWorker:
    def __init__(self):
        self.queue = JobQueue()
        self.gpu_lock = GPULock()
        self.processor = ImageEditorProcessor()
        self.result_handler = ResultHandler()
        self.retry = RetryStrategy()
        self.comfyui_client = ComfyUIClient()

    async def process_jobs(self):
        """Main worker loop"""
        logger.info("Worker started, polling for jobs...")
        
        while True:
            try:
                # 1. Get pending jobs from queue
                jobs = await self.queue.get_pending_jobs(limit=1)

                if not jobs:
                    logger.debug("No jobs in queue, waiting...")
                    await asyncio.sleep(settings.WORKER_POLLING_INTERVAL)
                    continue

                job = jobs[0]
                logger.info(f"Processing job {job.id} from queue")

                # 2. Try to acquire GPU lock
                if not await self.gpu_lock.acquire(timeout=settings.WORKER_GPU_LOCK_TIMEOUT):
                    logger.warning(f"Failed to acquire GPU lock for job {job.id}")
                    await asyncio.sleep(settings.WORKER_POLLING_INTERVAL)
                    continue

                try:
                    # 3. Check ComfyUI health before processing
                    logger.info(f"Checking ComfyUI health before processing job {job.id}")
                    comfyui_healthy = await self.comfyui_client.check_health()
                    
                    if not comfyui_healthy:
                        logger.warning(f"ComfyUI health check failed for job {job.id}, returning to queue")
                        await asyncio.sleep(settings.WORKER_POLLING_INTERVAL)
                        continue
                    
                    # 4. Update job status to processing
                    await self.queue.update_job_status(
                        job.id, 
                        "processing"
                    )

                    # 5. Process the job
                    result_path = await self.processor.process(job)

                    # 5. Update job status to completed
                    await self.queue.update_job_status(
                        job.id, 
                        "completed", 
                        result_path=result_path
                    )

                    # 6. Send result to user
                    await self.result_handler.send_result(job, result_path)

                    logger.info(f"Job {job.id} completed successfully")

                except Exception as e:
                    logger.error(f"Error processing job {job.id}: {str(e)}", exc_info=True)

                    # Retry logic
                    retry_count = job.retry_count if hasattr(job, 'retry_count') else 0
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

                        # Refund balance to user
                        await self.queue.refund_balance(job.user_id, 30, f"Job {job.id} failed")
                        logger.warning(f"Job {job.id} failed and refunded")

                finally:
                    # Release GPU lock
                    await self.gpu_lock.release()
                    logger.debug("GPU lock released")

            except Exception as e:
                logger.error(f"Unexpected error in main loop: {str(e)}", exc_info=True)
                await asyncio.sleep(5)