"""Menu handlers - main menu and navigation"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states import UserState
from keyboards import edit_photo_submenu_keyboard, category_keyboard, main_menu_keyboard
from utils import send_error_message

logger = logging.getLogger(__name__)

router = Router()


# Main menu buttons
@router.message(UserState.main_menu, F.text == "🎨 Редактировать фото")
async def btn_edit_photo(message: types.Message, state: FSMContext):
    """Handle 'Редактировать фото' button"""
    try:
        await state.set_state(UserState.select_preset_category)
        
        await message.answer(
            "Как вы хотите редактировать фото?",
            reply_markup=edit_photo_submenu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in edit_photo button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "🧩 Стили")
async def btn_styles(message: types.Message, state: FSMContext):
    """Handle 'Стили' button"""
    try:
        await state.set_state(UserState.select_preset_category)
        await state.update_data(category="styles")
        
        # Trigger the category callback handler
        from .presets import show_presets_by_category
        await show_presets_by_category(message, state, "styles")
        
    except Exception as e:
        logger.error(f"Error in styles button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "💡 Освещение")
async def btn_lighting(message: types.Message, state: FSMContext):
    """Handle 'Освещение' button"""
    try:
        await state.set_state(UserState.select_preset_category)
        await state.update_data(category="lighting")
        
        # Trigger the category callback handler
        from .presets import show_presets_by_category
        await show_presets_by_category(message, state, "lighting")
        
    except Exception as e:
        logger.error(f"Error in lighting button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "🖼 Оформление")
async def btn_design(message: types.Message, state: FSMContext):
    """Handle 'Оформление' button"""
    try:
        await state.set_state(UserState.select_preset_category)
        await state.update_data(category="design")
        
        # Trigger the category callback handler
        from .presets import show_presets_by_category
        await show_presets_by_category(message, state, "design")
        
    except Exception as e:
        logger.error(f"Error in design button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "✍️ Свой промпт")
async def btn_custom_prompt(message: types.Message, state: FSMContext):
    """Handle 'Свой промпт' button"""
    try:
        from .custom_prompt import start_custom_prompt
        await start_custom_prompt(message, state)
        
    except Exception as e:
        logger.error(f"Error in custom_prompt button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "💰 Баланс")
async def btn_balance(message: types.Message):
    """Handle 'Баланс' button"""
    try:
        from .balance import show_balance
        await show_balance(message)
        
    except Exception as e:
        logger.error(f"Error in balance button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "➕ Пополнить")
async def btn_top_up(message: types.Message, state: FSMContext):
    """Handle 'Пополнить' button"""
    try:
        from .balance import show_top_up_menu
        await show_top_up_menu(message, state)
        
    except Exception as e:
        logger.error(f"Error in top_up button: {e}")
        await send_error_message(message)


@router.message(UserState.main_menu, F.text == "ℹ️ Помощь")
async def btn_help(message: types.Message):
    """Handle 'Помощь' button"""
    try:
        from .help import show_help
        await show_help(message)
        
    except Exception as e:
        logger.error(f"Error in help button: {e}")
        await send_error_message(message)


# Inline keyboard callbacks
@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'back to menu' callback"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=None
        )
        
        await callback.message.answer(
            "Главное меню:",
            reply_markup=main_menu_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back_to_menu callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "back_to_balance")
async def callback_back_to_balance(callback: types.CallbackQuery):
    """Handle 'back to balance' callback"""
    try:
        from .balance import callback_balance
        await callback_balance(callback)
        
    except Exception as e:
        logger.error(f"Error in back_to_balance callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_preset")
async def callback_edit_preset(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit with preset' callback"""
    try:
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=category_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in edit_preset callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_custom")
async def callback_edit_custom(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit with custom prompt' callback"""
    try:
        from .custom_prompt import start_custom_prompt
        await start_custom_prompt(callback.message, state, is_callback=True)
        
        await callback.message.delete()
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in edit_custom callback: {e}")
        await callback.answer("Произошла ошибка")
