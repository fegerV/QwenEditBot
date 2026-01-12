import logging
from typing import Optional

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or settings.BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: int, text: str) -> bool:
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return bool(data.get("ok"))
        except Exception as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            return False
