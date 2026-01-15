"""Utility functions for bot"""

import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import Message, User
from .services import BackendAPIClient

logger = logging.getLogger(__name__)


async def register_or_get_user(
    telegram_user: User,
    api_client: BackendAPIClient
) -> dict:
    """Register user if not exists, otherwise get user info"""
    try:
        # Try to get user first
        user_data = await api_client.get_user(telegram_user.id)
        
        if user_data:
            logger.info(f"Existing user found: {telegram_user.id}")
            return user_data
        else:
            # Register new user
            logger.info(f"Registering new user: {telegram_user.id}")
            user_data = await api_client.register_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username or telegram_user.first_name
            )
            return user_data
            
    except Exception as e:
        logger.error(f"Error in register_or_get_user: {e}")
        raise


async def download_telegram_photo(
    bot: Bot,
    file_id: str
) -> Optional[bytes]:
    """Download photo from Telegram servers"""
    try:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        
        # Download file
        downloaded_file = await bot.download_file(file_path)
        
        # bot.download_file may return bytes or a file-like object
        if downloaded_file is None:
            return None
        if isinstance(downloaded_file, (bytes, bytearray)):
            return bytes(downloaded_file)
        # file-like
        try:
            return downloaded_file.read()
        except Exception:
            return None
        
    except Exception as e:
        logger.error(f"Error downloading photo: {e}")
        return None


async def send_error_message(
    message: Message,
    text: str = "Произошла ошибка. Попробуйте позже."
) -> None:
    """Send error message to user"""
    try:
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error sending error message: {e}")


def format_balance(balance: int) -> str:
    """Format balance for display"""
    return f"{balance} баллов"


def format_job_status(status: str) -> str:
    """Format job status for display"""
    status_map = {
        "queued": "⏳ В очереди",
        "processing": "🔄 Обрабатывается",
        "completed": "✅ Готово",
        "failed": "❌ Ошибка"
    }
    return status_map.get(status, status)
