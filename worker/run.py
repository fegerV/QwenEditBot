import asyncio
import logging
from worker.main import QwenEditWorker
from worker.config import settings
from worker.utils.logger import setup_logger
from worker.redis_client import redis_client

# Setup logging
setup_logger(settings.WORKER_LOG_LEVEL)
logger = logging.getLogger(__name__)

async def cleanup():
    """Cleanup function to close Redis connection"""
    await redis_client.close()
    logger.info("Redis connection closed")

def main():
    logger.info("Starting QwenEditBot Worker...")
    worker = QwenEditWorker()
    
    try:
        asyncio.run(worker.process_jobs())
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully...")
    except Exception as e:
        logger.error(f"Worker crashed: {str(e)}", exc_info=True)
        raise
    finally:
        # Close Redis connection on exit
        try:
            loop = asyncio.get_running_loop()
            # If there's already a running loop, create a task to clean up
            loop.create_task(cleanup())
        except RuntimeError:
            # If there's no running loop, run cleanup directly
            asyncio.run(cleanup())

if __name__ == "__main__":
    main()