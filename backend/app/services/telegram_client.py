"""Telegram Bot API client for sending notifications"""

import httpx
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)


class TelegramClient:
    """HTTP client for Telegram Bot API"""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.timeout = 10
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        disable_web_page_preview: bool = True
    ) -> dict:
        """
        Send a message to a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Parse mode (HTML or Markdown)
            disable_web_page_preview: Disable link previews
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                if not result.get("ok"):
                    logger.error(f"Telegram API error: {result}")
                    return {"ok": False, "error": result.get("description")}
                
                logger.info(f"Message sent to chat {chat_id}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Telegram message: {e}")
            return {"ok": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return {"ok": False, "error": str(e)}
    
    async def send_photo(
        self,
        chat_id: int,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: str = "HTML"
    ) -> dict:
        """
        Send a photo to a Telegram chat
        
        Args:
            chat_id: Telegram chat ID
            photo_url: URL of the photo
            caption: Photo caption (optional)
            parse_mode: Parse mode for caption (HTML or Markdown)
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.base_url}/sendPhoto"
        
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "parse_mode": parse_mode
        }
        
        if caption:
            payload["caption"] = caption
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                if not result.get("ok"):
                    logger.error(f"Telegram API error: {result}")
                    return {"ok": False, "error": result.get("description")}
                
                logger.info(f"Photo sent to chat {chat_id}")
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Telegram photo: {e}")
            return {"ok": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {e}")
            return {"ok": False, "error": str(e)}
