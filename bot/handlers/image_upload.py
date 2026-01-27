"""Image upload handlers - receiving photos and creating jobs"""

import logging
import tempfile
from pathlib import Path
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from ..states import UserState
from ..keyboards import main_menu_keyboard, main_menu_inline_keyboard, cancel_keyboard, back_and_main_menu_keyboard
from ..utils import download_telegram_photo, send_error_message

logger = logging.getLogger(__name__)

router = Router()


@router.message(StateFilter(UserState.awaiting_image_for_preset), F.photo)
async def handle_image_upload(message: types.Message, state: FSMContext):
    """Handle image upload for preset processing"""
    try:
        # Import api_client from main module
        from ..main import api_client
        
        # Get data from state
        data = await state.get_data()
        selected_preset = data.get("selected_preset")
        prompt = data.get("prompt")
        
        if not prompt:
            await message.answer("❌ Промпт не найден. Попробуйте снова.")
            return
        
        # Get balance and check if admin
        # For testing purposes, disable balance check completely
        from backend.app.config import settings as backend_settings
        user_is_admin = message.from_user.id in getattr(backend_settings, 'ADMIN_IDS', [])
        
        # Set fixed values for testing
        balance = 99999  # High balance for display
        cost = 0  # No cost for testing
        
        # Skip balance checks completely during testing
        
        # Show confirmation
        preset_name = selected_preset.get("name", "Обработка")
        await message.answer(
            f"✅ Фото загружено!\n\n"
            f"Обработка: {preset_name}\n"
            f"Подтверждаете обработку?",
            reply_markup=confirmation_keyboard()
        )
        
        # Save photo in state for confirmation
        await state.update_data(photo_id=message.photo[-1].file_id)
        
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        await send_error_message(message)


@router.message(StateFilter(UserState.awaiting_image_for_custom), F.photo)
async def handle_image_upload_for_custom(message: types.Message, state: FSMContext):
    """Handle image upload for custom prompt flow (photo first)."""
    try:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)

        await state.set_state(UserState.awaiting_custom_photo_confirmation)

        await message.answer(
            "✅ Фото загружено!\n\nПодтверждаете это фото?",
            reply_markup=custom_photo_confirmation_keyboard(),
        )

    except Exception as e:
        logger.error(f"Error uploading image for custom prompt: {e}")
        await send_error_message(message)


@router.message(StateFilter(UserState.awaiting_custom_photo_confirmation), F.photo)
async def handle_custom_photo_reupload(message: types.Message, state: FSMContext):
    """Allow user to replace the uploaded photo while on confirmation step."""
    try:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)

        await message.answer(
            "✅ Фото обновлено!\n\nПодтверждаете это фото?",
            reply_markup=custom_photo_confirmation_keyboard(),
        )

    except Exception as e:
        logger.error(f"Error re-uploading custom photo: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "confirm_processing")
async def confirm_processing(callback: types.CallbackQuery, state: FSMContext):
    """Confirm image processing"""
    try:
        # Import api_client from main module
        from ..main import api_client
        
        # Get data from state
        data = await state.get_data()
        selected_preset = data.get("selected_preset")
        custom_prompt = data.get("custom_prompt")  # For custom prompts
        prompt = data.get("prompt") or custom_prompt  # Use custom prompt if preset prompt not available
        photo_id = data.get("photo_id")
        
        if not photo_id or not prompt:
            await callback.answer("Ошибка данных. Попробуйте заново.", show_alert=True)
            return
        
        # Check balance again and verify admin status
        # For testing purposes, disable balance check completely
        from backend.app.config import settings as backend_settings
        user_is_admin = callback.from_user.id in getattr(backend_settings, 'ADMIN_IDS', [])
        
        # Set fixed values for testing
        balance = 99999  # High balance for display
        cost = 0  # No cost for testing
        
        # Skip balance checks completely during testing
        
        # Download photo from Telegram
        await callback.message.edit_text("📥 Загружаю фото...")
        
        photo_data = await download_telegram_photo(callback.bot, photo_id)
        
        if not photo_data:
            await callback.message.answer("Ошибка при загрузке фото. Попробуйте другое фото.")
            return
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(photo_data)
            temp_file_path = temp_file.name
        
        try:
            # Prepare file for upload
            filename = Path(temp_file_path).name
            with open(temp_file_path, 'rb') as f:
                file_content = f.read()
            
            file_tuple = (filename, file_content, 'image/jpeg')
            
            await callback.message.edit_text("📤 Отправляю фото на обработку...")
            
            # Create job via API with appropriate prompt
            job_data = await api_client.create_job(
                telegram_id=callback.from_user.id,
                image_file=file_tuple,
                prompt=prompt
            )
            
            job_id = job_data.get('id')
            
            # Update state
            await state.set_state(UserState.processing_job)
            await state.update_data(job_id=job_id)
            
            # Determine the name for display
            if custom_prompt:
                operation_name = "Свой промпт"
            else:
                operation_name = selected_preset.get("name", "Обработка") if selected_preset else "Обработка"
            
            await callback.message.edit_text(
                f"✅ Фото отправлено на обработку!\n\n"
                f"Обработка: {operation_name}\n"
                f"ID задачи: {job_id}\n"
                f"Статус: ⏳ В очереди\n\n"
                f"Как результат будет готов, вы получите уведомление.",
                reply_markup=main_menu_inline_keyboard()
            )
            
            logger.info(f"Job {job_id} created for user {callback.from_user.id} with prompt: {prompt[:50]}...")
            
        finally:
            # Clean up temporary file
            Path(temp_file_path).unlink(missing_ok=True)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error confirming processing: {e}")
        await callback.message.edit_text(f"❌ Ошибка при обработке запроса: {str(e)}")
        await callback.answer("Ошибка при подтверждении обработки", show_alert=True)


@router.callback_query(F.data == "cancel_processing")
async def cancel_processing(callback: types.CallbackQuery, state: FSMContext):
    """Cancel image processing"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error canceling processing: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.message(StateFilter(UserState.awaiting_image_for_preset), ~F.photo)
async def handle_wrong_input(message: types.Message, state: FSMContext):
    """Handle wrong input when expecting photo for preset"""
    from ..keyboards import balance_menu_keyboard
    await message.answer(
        "Пожалуйста, отправьте фото.\n\nЕсли вы хотите вернуться к меню баланса, нажмите на кнопку ниже.",
        reply_markup=balance_menu_keyboard()
    )


@router.message(
    StateFilter(UserState.awaiting_first_custom_photo_2, UserState.awaiting_second_custom_photo_2),
    ~F.photo
)
async def handle_wrong_input_custom_2_photos(message: types.Message, state: FSMContext):
    """Handle wrong input when expecting photo for 2 photos custom prompt"""
    try:
        current_state = await state.get_state()
        if current_state == UserState.awaiting_first_custom_photo_2:
            await message.answer(
                "📸 Пожалуйста, загрузите ПЕРВОЕ фото (файл изображения).",
                reply_markup=back_and_main_menu_keyboard("back_to_menu")
            )
        elif current_state == UserState.awaiting_second_custom_photo_2:
            await message.answer(
                "📸 Пожалуйста, загрузите ВТОРОЕ фото (файл изображения).",
                reply_markup=back_and_main_menu_keyboard("back_to_menu")
            )
    except Exception as e:
        logger.error(f"Error handling wrong input for 2 photos custom: {e}")
        await send_error_message(message)


@router.message(StateFilter(UserState.awaiting_image_for_custom), ~F.photo)
async def handle_wrong_input_for_custom(message: types.Message, state: FSMContext):
    """Handle wrong input when expecting photo for custom prompt (photo-first flow)."""
    await message.answer(
        "Пожалуйста, отправьте фото для обработки.",
        reply_markup=cancel_keyboard(),
    )


@router.message(StateFilter(UserState.awaiting_custom_photo_confirmation), ~F.photo)
async def handle_wrong_input_for_custom_confirmation(message: types.Message, state: FSMContext):
    """Handle wrong input when expecting photo on custom confirmation step."""
    await message.answer(
        "Пожалуйста, отправьте фото (или подтвердите уже загруженное).",
        reply_markup=cancel_keyboard(),
    )


# Confirmation keyboard
def confirmation_keyboard():
    """Create confirmation keyboard"""
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_processing"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_processing"))

    return builder.as_markup()


def custom_photo_confirmation_keyboard():
    """Confirmation keyboard for custom prompt photo step."""
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить фото", callback_data="confirm_custom_photo"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel"))

    return builder.as_markup()
