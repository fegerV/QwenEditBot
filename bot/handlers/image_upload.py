"""Image upload handlers - receiving photos and creating jobs"""

import logging
import tempfile
import os
from pathlib import Path
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from states import UserState
from keyboards import main_menu_keyboard, cancel_keyboard
from services import BackendAPIClient
from utils import download_telegram_photo, send_error_message, format_balance
from config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.message(StateFilter(UserState.awaiting_image_for_preset), F.photo)
async def handle_image_upload(message: types.Message, state: FSMContext):
    """Handle image upload for preset processing"""
    try:
        # Import api_client from main module
        from main import api_client
        
        # Get data from state
        data = await state.get_data()
        selected_preset = data.get("selected_preset")
        prompt = data.get("prompt")
        
        if not prompt:
            await message.answer("❌ Промпт не найден. Попробуйте снова.")
            return
        
        # Get balance
        balance = await api_client.get_balance(message.from_user.id)
        cost = 30  # settings.EDIT_COST
        
        if balance < cost:
            await message.answer(
                f"❌ Недостаточно баллов!\n"
                f"Баланс: {balance} баллов\n"
                f"Требуется: {cost} баллов\n\n"
                f"➕ Пополнить баланс?",
                reply_markup=main_menu_keyboard()
            )
            return
        
        # Show confirmation
        preset_name = selected_preset.get("name", "Обработка")
        await message.answer(
            f"✅ Фото загружено!\n\n"
            f"Обработка: {preset_name}\n"
            f"Баланс: {balance} баллов\n"
            f"Стоимость: {cost} баллов\n\n"
            f"Подтверждаете обработку?",
            reply_markup=confirmation_keyboard()
        )
        
        # Save photo in state for confirmation
        await state.update_data(photo_id=message.photo[-1].file_id)
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "confirm_processing")
async def confirm_processing(callback: types.CallbackQuery, state: FSMContext):
    """Confirm image processing"""
    try:
        # Import api_client from main module
        from main import api_client
        
        # Get data from state
        data = await state.get_data()
        selected_preset = data.get("selected_preset")
        prompt = data.get("prompt")
        photo_id = data.get("photo_id")
        
        if not photo_id or not prompt:
            await callback.answer("Ошибка данных. Попробуйте заново.", show_alert=True)
            return
        
        # Check balance again
        balance = await api_client.get_balance(callback.from_user.id)
        cost = 30
        
        if balance < cost:
            await callback.message.edit_text(
                f"❌ Недостаточно баллов!\n"
                f"Баланс: {balance} баллов\n"
                f"Требуется: {cost} баллов\n\n"
                f"➕ Пополнить баланс?",
                reply_markup=main_menu_keyboard()
            )
            return
        
        # Download photo from Telegram
        await callback.message.edit_text("📥 Получаю фото...")
        
        try:
            photo_data = await download_telegram_photo(callback.bot, photo_id)
        except Exception as e:
            logger.error(f"Failed to download photo {photo_id}: {e}")
            await callback.message.answer("Ошибка при загрузке фото. Попробуйте еще раз.")
            return
        
        if not photo_data:
            await callback.message.answer("Ошибка при загрузке фото. Попробуйте другое фото.")
            return
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file_path = temp_file.name
        
        try:
            temp_file.write(photo_data)
            temp_file.close()
            
            # Prepare file for upload
            filename = Path(temp_file_path).name
            with open(temp_file_path, 'rb') as f:
                file_content = f.read()
            
            file_tuple = (filename, file_content, 'image/jpeg')
            
            await callback.message.edit_text("📤 Отправляю фото на обработку...")
            
            # Create job via API with prompt from preset
            job_data = await api_client.create_job(
                telegram_id=callback.from_user.id,
                image_file=file_tuple,
                prompt=prompt  # ← ПРОМПТ ИЗ ПРЕСЕТА!
            )
            
            job_id = job_data.get('id')
            
            # Update state
            await state.set_state(UserState.processing_job)
            await state.update_data(job_id=job_id)
            
            preset_name = selected_preset.get("name", "Обработка")
            
            await callback.message.edit_text(
                f"✅ Фото отправлено на обработку!\n\n"
                f"Пресет: {preset_name}\n"
                f"ID задачи: {job_id}\n"
                f"Статус: ⏳ В очереди\n\n"
                f"Когда результат будет готов, вы получите уведомление.",
                reply_markup=main_menu_keyboard()
            )
            
            logger.info(f"Job {job_id} created for user {callback.from_user.id} with preset {preset_name}")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error confirming processing: {e}")
        await callback.answer("Ошибка при подтверждении обработки", show_alert=True)


@router.callback_query(F.data == "cancel_processing")
async def cancel_processing(callback: types.CallbackQuery, state: FSMContext):
    """Cancel image processing"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error canceling processing: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.message(StateFilter(UserState.awaiting_image_for_preset))
async def handle_wrong_input(message: types.Message):
    """Handle wrong input when expecting photo"""
    await message.answer(
        "Пожалуйста, отправьте фото (не документ).",
        reply_markup=cancel_keyboard()
    )


# Confirmation keyboard
def confirmation_keyboard():
    """Create confirmation keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_processing"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_processing"))
    
    return builder.as_markup()
