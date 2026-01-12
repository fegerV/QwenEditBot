import asyncio
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GPULock:
    """File-based GPU lock mechanism (prevents concurrent processing)"""

    def __init__(self, lock_file: str = ".gpu_lock"):
        self.lock_file = Path(lock_file)

    async def acquire(self, timeout: int = 30) -> bool:
        """
        Acquire GPU lock.
        Create file: .gpu_lock
        If file exists -> wait (with timeout)
        Return True if successful, False if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if lock file exists
            if not self.lock_file.exists():
                try:
                    # Try to create the lock file
                    self.lock_file.touch()
                    logger.debug("GPU lock acquired")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to create GPU lock file: {e}")
                    await asyncio.sleep(0.1)
            else:
                # Lock file exists, check if we've timed out
                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - start_time
                
                if elapsed >= timeout:
                    logger.warning(f"GPU lock timeout after {timeout} seconds")
                    return False
                
                # Wait a bit before checking again
                await asyncio.sleep(0.1)

    async def release(self):
        """Release lock (delete file)"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.debug("GPU lock released")
        except Exception as e:
            logger.error(f"Failed to release GPU lock: {e}")

    async def is_locked(self) -> bool:
        """Check if GPU is locked"""
        return self.lock_file.exists()