"""Image upload handlers - receiving photos and creating jobs"""

import logging
import tempfile
from pathlib import Path
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from ..states import UserState
from ..keyboards import main_menu_keyboard
from ..services import BackendAPIClient
from ..utils import download_telegram_photo, send_error_message, format_balance
from ..config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.message(UserState.awaiting_image_for_preset, F.photo)
async def handle_preset_image(message: types.Message, state: FSMContext):
    """Handle image upload for preset editing"""
    try:
        # Import api_client from main module
        from ..main import api_client
        
        # Get state data
        state_data = await state.get_data()
        preset_id = state_data.get('preset_id')
        
        if not preset_id:
            await message.answer("Ошибка: не выбран пресет. Попробуйте заново.")
            await state.clear()
            await message.answer("Главное меню:", reply_markup=main_menu_keyboard())
            return
        
        # Check balance
        has_balance = await api_client.check_balance(message.from_user.id, settings.EDIT_COST)
        
        if not has_balance:
            balance = await api_client.get_balance(message.from_user.id)
            text = (
                f"❌ Недостаточно баллов!\n\n"
                f"Стоимость: {settings.EDIT_COST} баллов\n"
                f"Ваш баланс: {format_balance(balance)}\n\n"
                f"Пополните баланс и попробуйте снова."
            )
            await message.answer(text, reply_markup=main_menu_keyboard())
            await state.clear()
            return
        
        # Download photo from Telegram
        await message.answer("📥 Получаю фото...")
        
        photo = message.photo[-1]  # Get highest resolution photo
        photo_data = await download_telegram_photo(message.bot, photo.file_id)
        
        if not photo_data:
            await message.answer("Ошибка при загрузке фото. Попробуйте другое фото.")
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
            
            await message.answer("📤 Отправляю фото на обработку...")
            
            # Create job via API
            job_data = await api_client.create_job(
                user_id=message.from_user.id,
                image_file=file_tuple,
                preset_id=preset_id
            )
            
            job_id = job_data.get('id')
            
            # Update state
            await state.set_state(UserState.processing_job)
            await state.update_data(job_id=job_id)
            
            await message.answer(
                f"✅ Фото отправлено на обработку!\n\n"
                f"ID задачи: {job_id}\n"
                f"Статус: ⏳ В очереди\n\n"
                f"Когда результат будет готов, вы получите уведомление.",
                reply_markup=main_menu_keyboard()
            )
            
            logger.info(f"Job {job_id} created for user {message.from_user.id} with preset {preset_id}")
            
        finally:
            # Clean up temporary file
            Path(temp_file_path).unlink(missing_ok=True)
        
    except Exception as e:
        logger.error(f"Error handling preset image: {e}")
        await message.answer(
            "Произошла ошибка при обработке фото. Попробуйте позже.",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()


@router.message(UserState.awaiting_image_for_custom, F.photo)
async def handle_custom_image(message: types.Message, state: FSMContext):
    """Handle image upload for custom prompt editing"""
    try:
        # Import api_client from main module
        from ..main import api_client
        
        # Get state data
        state_data = await state.get_data()
        custom_prompt = state_data.get('custom_prompt')
        
        if not custom_prompt:
            await message.answer("Ошибка: не указан промпт. Попробуйте заново.")
            await state.clear()
            await message.answer("Главное меню:", reply_markup=main_menu_keyboard())
            return
        
        # Check balance
        has_balance = await api_client.check_balance(message.from_user.id, settings.EDIT_COST)
        
        if not has_balance:
            balance = await api_client.get_balance(message.from_user.id)
            text = (
                f"❌ Недостаточно баллов!\n\n"
                f"Стоимость: {settings.EDIT_COST} баллов\n"
                f"Ваш баланс: {format_balance(balance)}\n\n"
                f"Пополните баланс и попробуйте снова."
            )
            await message.answer(text, reply_markup=main_menu_keyboard())
            await state.clear()
            return
        
        # Download photo from Telegram
        await message.answer("📥 Получаю фото...")
        
        photo = message.photo[-1]  # Get highest resolution photo
        photo_data = await download_telegram_photo(message.bot, photo.file_id)
        
        if not photo_data:
            await message.answer("Ошибка при загрузке фото. Попробуйте другое фото.")
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
            
            await message.answer("📤 Отправляю фото на обработку...")
            
            # Create job via API
            job_data = await api_client.create_job(
                user_id=message.from_user.id,
                image_file=file_tuple,
                prompt=custom_prompt
            )
            
            job_id = job_data.get('id')
            
            # Update state
            await state.set_state(UserState.processing_job)
            await state.update_data(job_id=job_id)
            
            await message.answer(
                f"✅ Фото отправлено на обработку!\n\n"
                f"Ваш промпт: {custom_prompt}\n\n"
                f"ID задачи: {job_id}\n"
                f"Статус: ⏳ В очереди\n\n"
                f"Когда результат будет готов, вы получите уведомление.",
                reply_markup=main_menu_keyboard()
            )
            
            logger.info(f"Job {job_id} created for user {message.from_user.id} with custom prompt")
            
        finally:
            # Clean up temporary file
            Path(temp_file_path).unlink(missing_ok=True)
        
    except Exception as e:
        logger.error(f"Error handling custom image: {e}")
        await message.answer(
            "Произошла ошибка при обработке фото. Попробуйте позже.",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()


# Handle text messages when expecting photo
@router.message(UserState.awaiting_image_for_preset)
async def handle_preset_wrong_input(message: types.Message):
    """Handle wrong input when expecting photo for preset"""
    await message.answer(
        "Пожалуйста, отправьте фото (не документ)."
    )


@router.message(UserState.awaiting_image_for_custom)
async def handle_custom_wrong_input(message: types.Message):
    """Handle wrong input when expecting photo for custom prompt"""
    await message.answer(
        "Пожалуйста, отправьте фото (не документ)."
    )
