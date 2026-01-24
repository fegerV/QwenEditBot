"""Main bot application"""

import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.services import BackendAPIClient
from bot.handlers import (
    start_router,
    menu_router,
    presets_router,
    custom_prompt_router,
    image_upload_router,
    balance_router,
    help_router,
    payments_router,
    promocodes_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global API client instance
api_client = BackendAPIClient()


# Make sure all handlers modules are imported properly
def import_handlers():
    """Ensure all handler modules are imported to register routes"""
    from bot.handlers import start, menu, presets, custom_prompt, image_upload, balance, help, payments, promocodes
    return [start, menu, presets, custom_prompt, image_upload, balance, help, payments, promocodes]


async def create_bot():
    """Create and configure bot instance"""
    # Initialize bot
    bot = Bot(token=settings.BOT_TOKEN)
    
    # Use Redis storage instead of MemoryStorage to avoid memory leaks
    # For now keep MemoryStorage but with cleanup strategy
    from aiogram.fsm.storage.memory import MemoryStorage
    storage = MemoryStorage()
    
    # Initialize dispatcher with memory storage
    dp = Dispatcher(storage=storage)
    
    # Register handlers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(presets_router)
    dp.include_router(custom_prompt_router)
    dp.include_router(image_upload_router)
    dp.include_router(balance_router)
    dp.include_router(help_router)
    dp.include_router(payments_router)
    dp.include_router(promocodes_router)
    
    logger.info("Bot initialized successfully")
    
    return bot, dp


async def start_bot():
    """Start the bot with graceful error handling"""
    bot, dp = await create_bot()
    
    try:
        # Delete webhook to use polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted, starting polling...")
        
        # Configure session with connection pooling
        session = bot.session
        if session:
            # Reuse session for better performance
            logger.info("Using bot session with connection pooling")
        
        # Start polling with error recovery
        try:
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                skip_updates=False
            )
        except Exception as polling_error:
            logger.error(f"Polling error: {polling_error}", exc_info=True)
            # Wait a bit before potentially restarting
            import asyncio
            await asyncio.sleep(5)
            raise
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise
    finally:
        logger.info("Closing bot session...")
        if bot.session:
            await bot.session.close()
        logger.info("Bot stopped")
