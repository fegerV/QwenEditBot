"""Main bot application"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .config import settings
from .services import BackendAPIClient
from .handlers import (
    start_router,
    menu_router,
    presets_router,
    custom_prompt_router,
    image_upload_router,
    balance_router,
    help_router,
    payments_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global API client instance
api_client = BackendAPIClient()


async def create_bot():
    """Create and configure bot instance"""
    # Initialize bot
    bot = Bot(token=settings.BOT_TOKEN)
    
    # Initialize dispatcher with memory storage
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(presets_router)
    dp.include_router(custom_prompt_router)
    dp.include_router(image_upload_router)
    dp.include_router(balance_router)
    dp.include_router(help_router)
    dp.include_router(payments_router)
    
    logger.info("Bot initialized successfully")
    
    return bot, dp


async def start_bot():
    """Start the bot"""
    bot, dp = await create_bot()
    
    try:
        # Delete webhook to use polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted, starting polling...")
        
        # Start polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()
