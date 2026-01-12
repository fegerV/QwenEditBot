"""Handlers for Telegram bot"""

from .start import router as start_router
from .menu import router as menu_router
from .presets import router as presets_router
from .custom_prompt import router as custom_prompt_router
from .image_upload import router as image_upload_router
from .balance import router as balance_router
from .help import router as help_router
from .payments import router as payments_router

__all__ = [
    "start_router",
    "menu_router",
    "presets_router",
    "custom_prompt_router",
    "image_upload_router",
    "balance_router",
    "help_router",
    "payments_router"
]
