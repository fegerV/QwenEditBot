import logging
import aiohttp
from typing import Optional, Dict, Any
from worker.config import settings
import ssl

logger = logging.getLogger(__name__)


class TelegramClient:
    """HTTP client for Telegram Bot API"""

    def __init__(self):
        self.base_url = f"{settings.TELEGRAM_API_URL}/bot{settings.BOT_TOKEN}"
        self.timeout = aiohttp.ClientTimeout(total=60)  # Increased timeout to 60 seconds

    async def send_photo(self, chat_id: int, photo: bytes, caption: str) -> bool:
        """Send photo to user"""
        url = f"{self.base_url}/sendPhoto"
        
        try:
            # Create SSL context that skips certificate verification
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(timeout=self.timeout, connector=connector) as session:
                form_data = aiohttp.FormData()
                form_data.add_field('chat_id', str(chat_id))
                form_data.add_field('photo', photo, filename='result.png', content_type='image/png')
                form_data.add_field('caption', caption)
                
                logger.debug(f"Sending photo to chat_id {chat_id}, size: {len(photo)} bytes")
                async with session.post(url, data=form_data) as response:
                    response_text = await response.text()
                    logger.debug(f"Telegram API response status: {response.status}")
                    logger.debug(f"Telegram API response: {response_text}")
                    
                    if response.status == 200:
                        data = await response.json()
                        success = data.get('ok', False)
                        logger.debug(f"Photo sent successfully: {success}")
                        return success
                    else:
                        logger.error(f"Failed to send photo: {response.status} - {response_text}")
                        return False
        except Exception as e:
            logger.error(f"Error sending photo to Telegram: {str(e)}")
            return False

    async def send_message(self, chat_id: int, message: str) -> bool:
        """Send text message"""
        url = f"{self.base_url}/sendMessage"
        
        try:
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            logger.debug(f"Sending message to chat_id {chat_id}")
            # Create SSL context that skips certificate verification
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(timeout=self.timeout, connector=connector) as session:
                async with session.post(url, json=payload) as response:
                    response_text = await response.text()
                    logger.debug(f"Telegram API response status: {response.status}")
                    logger.debug(f"Telegram API response: {response_text}")
                    
                    if response.status == 200:
                        data = await response.json()
                        success = data.get('ok', False)
                        logger.debug(f"Message sent successfully: {success}")
                        return success
                    else:
                        logger.error(f"Failed to send message: {response.status} - {response_text}")
                        return False
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {str(e)}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user info (we need to implement this in backend)"""
        # For now, we'll use a simple approach - get user from backend
        # In a real implementation, we might cache this or use a different approach
        from worker.services.backend_client import BackendAPIClient
        backend_client = BackendAPIClient()
        return await backend_client.get_user(user_id)