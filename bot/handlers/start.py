"""Start command handler"""

import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import UserState
from keyboards import main_menu_keyboard
from utils import register_or_get_user
from config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command"""
    try:
        # Import api_client from main module
        from main import api_client
        
        # Register or get user
        user_data = await register_or_get_user(message.from_user, api_client)
        
        # Clear any existing state
        await state.clear()
        
        # Set state to main menu
        await state.set_state(UserState.main_menu)
        
        # Send welcome message
        welcome_text = (
            f"Добро пожаловать в QwenEditBot 🎨\n\n"
            f"Вам начислено {settings.INITIAL_BALANCE} баллов!\n\n"
            f"Выберите действие в меню ниже:"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard()
        )
        
        logger.info(f"User {message.from_user.id} started the bot")
        
    except Exception as e:
        logger.error(f"Error in /start command: {e}")
        await message.answer(
            "Произошла ошибка при запуске бота. Пожалуйста, попробуйте позже."
        )


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command"""
    help_text = (
        "🤖 *QwenEditBot - AI редактор фото*\n\n"
        "*Как использовать:*\n"
        "1. Выберите стиль/освещение/оформление ИЛИ напишите свой промпт\n"
        "2. Загрузите фото\n"
        "3. Фото отправится на обработку\n"
        "4. Когда будет готово, получите результат\n\n"
        "*Стоимость:* 30 баллов за одно редактирование\n"
        "*Приветственный бонус:* 60 баллов\n\n"
        "*Команды:*\n"
        "/start - Запустить бота\n"
        "/menu - Главное меню\n"
        "/help - Справка\n"
        "/balance - Показать баланс\n"
        "/cancel - Отменить действие\n\n"
        "*Вопросы?* Обратитесь в поддержку"
    )
    
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("menu"))
async def cmd_menu(message: types.Message, state: FSMContext):
    """Handle /menu command - return to main menu"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await message.answer(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )
        
        logger.info(f"User {message.from_user.id} returned to main menu")
        
    except Exception as e:
        logger.error(f"Error in /menu command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@router.message(Command("balance"))
async def cmd_balance(message: types.Message):
    """Handle /balance command"""
    try:
        # Import api_client from main module
        from main import api_client
        
        balance = await api_client.get_balance(message.from_user.id)
        
        if balance is not None:
            await message.answer(f"💰 Ваш баланс: {balance} баллов")
        else:
            await message.answer("Не удалось получить баланс. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Error in /balance command: {e}")
        await message.answer("Произошла ошибка при получении баланса.")


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    """Handle /cancel command - clear state and return to menu"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await message.answer(
            "Действие отменено. Вернулись в главное меню:",
            reply_markup=main_menu_keyboard()
        )
        
        logger.info(f"User {message.from_user.id} cancelled action")
        
    except Exception as e:
        logger.error(f"Error in /cancel command: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
