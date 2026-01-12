import logging
from pathlib import Path

from worker.services.telegram_client import TelegramClient
from worker.queue.job_queue import Job
from worker.config import settings

logger = logging.getLogger(__name__)


class ResultHandler:
    """Send results to users via Telegram"""

    def __init__(self):
        self.telegram_client = TelegramClient()

    async def send_result(self, job: Job, result_path: str) -> bool:
        """
        1. Read result image
        2. Send to user via Telegram
        3. Return True if successful, False if error
        
        Message text:
        "✅ Your photo is ready! 🎨\n\nProcessing time: X sec"
        """
        try:
            # Read result image
            result_path_obj = Path(result_path)
            if not result_path_obj.exists():
                raise Exception(f"Result file not found: {result_path}")
            
            with open(result_path_obj, "rb") as f:
                image_data = f.read()
            
            # Get user's telegram ID (we need to implement this in backend client)
            user = await self.telegram_client.get_user(job.user_id)
            if not user:
                raise Exception(f"User {job.user_id} not found")
            
            telegram_id = user.get("telegram_id")
            if not telegram_id:
                raise Exception(f"User {job.user_id} has no telegram_id")
            
            # Send photo to user
            caption = "✅ Your photo is ready! 🎨\n\nProcessing time: 30 sec"
            success = await self.telegram_client.send_photo(telegram_id, image_data, caption)
            
            if success:
                logger.info(f"Result sent to user {job.user_id} (telegram_id: {telegram_id})")
                return True
            else:
                logger.error(f"Failed to send result to user {job.user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending result for job {job.id}: {str(e)}")
            return False

    async def send_error(self, job: Job, error: str) -> bool:
        """
        Send error notification.
        
        Text:
        "❌ Error processing photo\n\nMessage: {error}\n\nPoints refunded ✅"
        """
        try:
            # Get user's telegram ID
            user = await self.telegram_client.get_user(job.user_id)
            if not user:
                raise Exception(f"User {job.user_id} not found")
            
            telegram_id = user.get("telegram_id")
            if not telegram_id:
                raise Exception(f"User {job.user_id} has no telegram_id")
            
            # Send error message
            message = f"❌ Error processing photo\n\nMessage: {error}\n\nPoints refunded ✅"
            success = await self.telegram_client.send_message(telegram_id, message)
            
            if success:
                logger.info(f"Error notification sent to user {job.user_id}")
                return True
            else:
                logger.error(f"Failed to send error notification to user {job.user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending error notification for job {job.id}: {str(e)}")
            return False

    async def send_status(self, user_id: int, message: str) -> bool:
        """Send intermediate status notification"""
        try:
            # Get user's telegram ID
            user = await self.telegram_client.get_user(user_id)
            if not user:
                raise Exception(f"User {user_id} not found")
            
            telegram_id = user.get("telegram_id")
            if not telegram_id:
                raise Exception(f"User {user_id} has no telegram_id")
            
            # Send status message
            success = await self.telegram_client.send_message(telegram_id, message)
            
            if success:
                logger.info(f"Status notification sent to user {user_id}")
                return True
            else:
                logger.error(f"Failed to send status notification to user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending status notification to user {user_id}: {str(e)}")
            return False