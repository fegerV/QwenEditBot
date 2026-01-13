"""Utility functions for bot"""

import logging
from typing import Optional
from aiogram import Bot
from aiogram.types import Message, User
from services import BackendAPIClient

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
    """Download photo from Telegram and return as bytes"""
    try:
        file = await bot.get_file(file_id)
        downloaded = await bot.download_file(file.file_path)
        
        # Protect against different return types (bytes or stream)
        if isinstance(downloaded, (bytes, bytearray)):
            return bytes(downloaded)
        
        # If it's a stream (BytesIO or similar)
        if hasattr(downloaded, 'read'):
            return downloaded.read()
        
        # Fallback: try to convert to bytes
        return bytes(downloaded)
        
    except Exception as e:
        logger.error(f"Failed to download photo {file_id}: {e}")
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
