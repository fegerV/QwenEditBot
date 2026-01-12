import asyncio
import logging
from worker.main import QwenEditWorker
from worker.config import settings
from worker.utils.logger import setup_logger

# Setup logging
setup_logger(settings.WORKER_LOG_LEVEL)
logger = logging.getLogger(__name__)

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

if __name__ == "__main__":
    main()