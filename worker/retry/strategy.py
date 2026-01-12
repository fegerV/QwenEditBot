import logging
from typing import List
from worker.config import settings

logger = logging.getLogger(__name__)


class RetryStrategy:
    """Exponential backoff retry logic"""

    def __init__(self):
        self.max_retries = settings.MAX_RETRIES
        self.retry_delays = [int(delay) for delay in settings.RETRY_DELAYS.split(",")]

    async def should_retry(self, job_id: int, error: str, retry_count: int) -> bool:
        """
        Check if job should be retried.
        If retry_count < MAX_RETRIES -> True
        If retry_count >= MAX_RETRIES -> False
        """
        if retry_count < self.max_retries:
            logger.info(f"Job {job_id} will be retried (attempt {retry_count + 1}/{self.max_retries})")
            return True
        else:
            logger.warning(f"Job {job_id} max retries reached ({self.max_retries})")
            return False

    async def get_next_delay(self, retry_count: int) -> int:
        """
        Get delay before next retry attempt.
        retry_count=0 -> delay=5 sec
        retry_count=1 -> delay=10 sec
        retry_count=2 -> delay=20 sec
        """
        if retry_count < len(self.retry_delays):
            return self.retry_delays[retry_count]
        return self.retry_delays[-1]  # Return last delay if retry_count exceeds delays list

    async def handle_error(self, job_id: int, error: str, retry_count: int) -> int:
        """
        Handle job error.
        Increase retry_count.
        If should_retry -> return new retry_count.
        If not -> return -1 to indicate final failure.
        """
        new_retry_count = retry_count + 1
        
        if await self.should_retry(job_id, error, retry_count):
            delay = await self.get_next_delay(retry_count)
            logger.info(f"Job {job_id} retry scheduled in {delay} seconds")
            return new_retry_count
        else:
            return -1