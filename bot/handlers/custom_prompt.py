"""Custom prompt handlers - user input for custom editing"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from states import UserState
from keyboards import cancel_keyboard, main_menu_keyboard
from utils import send_error_message

logger = logging.getLogger(__name__)

router = Router()


async def start_custom_prompt(
    message: types.Message,
    state: FSMContext,
    is_callback: bool = False
):
    """Start custom prompt input flow"""
    try:
        await state.set_state(UserState.awaiting_custom_prompt)
        
        text = (
            "✍️ *Свой промпт*\n\n"
            "Опишите что нужно сделать с фото:\n"
            "Например: \"Сделать фото чёрно-белым и добавить виньетку\""
        )
        
        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=cancel_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error starting custom prompt: {e}")
        if not is_callback:
            await send_error_message(message)


@router.message(StateFilter(UserState.awaiting_custom_prompt))
async def handle_custom_prompt(message: types.Message, state: FSMContext):
    """Handle custom prompt text input"""
    try:
        prompt_text = message.text.strip()
        
        # Validate prompt
        if not prompt_text:
            await message.answer(
                "Пожалуйста, введите описание того, что нужно сделать с фото."
            )
            return
        
        if len(prompt_text) < 5:
            await message.answer(
                "Слишком короткое описание. Пожалуйста, напишите подробнее (минимум 5 символов)."
            )
            return
        
        if len(prompt_text) > 500:
            await message.answer(
                "Слишком длинное описание. Пожалуйста, сократите его (максимум 500 символов)."
            )
            return
        
        # Save prompt to state
        await state.update_data(custom_prompt=prompt_text)
        
        # Move to image upload state
        await state.set_state(UserState.awaiting_image_for_custom)
        
        await message.answer(
            "Отлично! Теперь загрузите фото для обработки:",
            reply_markup=cancel_keyboard()
        )
        
        logger.info(f"User {message.from_user.id} entered custom prompt")
        
    except Exception as e:
        logger.error(f"Error handling custom prompt: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "cancel", StateFilter(UserState.awaiting_custom_prompt))
async def callback_cancel_custom_prompt(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for custom prompt"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.delete()
        
        await callback.message.answer(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "cancel", StateFilter(UserState.awaiting_image_for_custom))
async def callback_cancel_custom_image(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for image (custom prompt)"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.delete()
        
        await callback.message.answer(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка")
