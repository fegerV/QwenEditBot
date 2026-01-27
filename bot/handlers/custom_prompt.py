"""Custom prompt handlers - user input for custom editing"""

import logging
import tempfile
from pathlib import Path

from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from ..states import UserState
from ..keyboards import cancel_keyboard, main_menu_keyboard, main_menu_inline_keyboard, custom_prompt_type_keyboard, back_and_main_menu_keyboard
from ..utils import download_telegram_photo, send_error_message

logger = logging.getLogger(__name__)

router = Router()


async def start_custom_prompt(
    message: types.Message,
    state: FSMContext,
    is_callback: bool = False,
):
    """Start custom prompt flow - show selection between 1 photo and 2 photos."""
    try:
        await state.clear()
        await state.set_state(UserState.selecting_custom_prompt_type)

        text = (
            "✍️ *Свой промпт*\n\n"
            "Выберите тип промпта:\n\n"
            "1️⃣ *Промпт для 1 фото*\n"
            "Загрузите одно фото и опишите, что нужно с ним сделать.\n\n"
            "2️⃣ *Промпт для 2 фото*\n"
            "Загрузите два фото и опишите, что нужно сделать с ними.\n"
            "Первое фото — основное, второе — дополнительное (как в примерочной)."
        )

        if is_callback:
            await message.edit_text(text, parse_mode="Markdown", reply_markup=custom_prompt_type_keyboard())
        else:
            await message.answer(text, parse_mode="Markdown", reply_markup=custom_prompt_type_keyboard())

    except Exception as e:
        logger.error(f"Error starting custom prompt: {e}")
        if not is_callback:
            await send_error_message(message)


@router.callback_query(
    F.data == "confirm_custom_photo",
    StateFilter(UserState.awaiting_custom_photo_confirmation),
)
async def callback_confirm_custom_photo(callback: types.CallbackQuery, state: FSMContext):
    """After photo confirmation ask user to enter the prompt."""
    try:
        data = await state.get_data()
        if not data.get("photo_id"):
            await callback.answer("Фото не найдено. Загрузите его ещё раз.", show_alert=True)
            await state.set_state(UserState.awaiting_image_for_custom)
            await callback.message.edit_text(
                "📸 Загрузите фото для обработки:", reply_markup=cancel_keyboard()
            )
            return

        await state.set_state(UserState.awaiting_custom_prompt)

        await callback.message.edit_text(
            "✅ Фото подтверждено!\n\n"
            "✍️ Теперь напишите промпт — что нужно сделать с фото?\n"
            "Например: *\"Сделать фото чёрно-белым, добавить виньетку\"*",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error confirming custom photo: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.message(StateFilter(UserState.awaiting_custom_prompt))
async def handle_custom_prompt(message: types.Message, state: FSMContext):
    """Handle custom prompt text input (after photo confirmation)."""
    try:
        prompt_text = (message.text or "").strip()

        if not prompt_text:
            await message.answer("Пожалуйста, введите описание того, что нужно сделать с фото.")
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

        data = await state.get_data()
        photo_id = data.get("photo_id")

        if not photo_id:
            await state.set_state(UserState.awaiting_image_for_custom)
            await message.answer(
                "❌ Не удалось найти загруженное фото. Пожалуйста, отправьте фото ещё раз.",
                reply_markup=cancel_keyboard(),
            )
            return

        # Import api_client from main module
        from ..main import api_client

        progress = await message.answer("📥 Загружаю фото...")
        photo_data = await download_telegram_photo(message.bot, photo_id)

        if not photo_data:
            await progress.edit_text("❌ Ошибка при загрузке фото. Попробуйте другое фото.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(photo_data)
            temp_file_path = temp_file.name

        try:
            filename = Path(temp_file_path).name
            with open(temp_file_path, "rb") as f:
                file_content = f.read()

            file_tuple = (filename, file_content, "image/jpeg")

            await progress.edit_text("📤 Отправляю фото на обработку...")

            job_data = await api_client.create_job(
                telegram_id=message.from_user.id,
                image_file=file_tuple,
                prompt=prompt_text,
            )

            job_id = job_data.get("id")

            await message.answer(
                "✅ Фото отправлено на обработку!\n\n"
                f"ID задачи: {job_id}\n"
                "Результат будет готов в течение нескольких минут.",
                reply_markup=main_menu_keyboard(),
            )

            await state.clear()
            await state.set_state(UserState.main_menu)

            logger.info(f"Custom prompt job {job_id} created for user {message.from_user.id}")

        finally:
            Path(temp_file_path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Error handling custom prompt: {e}")
        await send_error_message(message)


@router.callback_query(
    F.data == "cancel",
    StateFilter(UserState.awaiting_custom_prompt),
)
async def callback_cancel_custom_prompt(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for custom prompt."""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)

        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "custom_prompt")
async def callback_custom_prompt(callback: types.CallbackQuery, state: FSMContext):
    """Handle custom prompt callback from inline menu"""
    try:
        await start_custom_prompt(callback.message, state, is_callback=True)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in custom_prompt callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "custom_prompt_1_photo")
async def callback_custom_prompt_1_photo(callback: types.CallbackQuery, state: FSMContext):
    """Handle selection of 1 photo custom prompt"""
    try:
        await state.set_state(UserState.awaiting_image_for_custom)
        
        text = (
            "✍️ *Промпт для 1 фото*\n\n"
            "Сначала загрузите фото, которое нужно обработать.\n"
            "После этого вы подтвердите фото и сможете написать промпт.\n\n"
            "📸 *Загрузите фото для обработки:*"
        )
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=cancel_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in custom_prompt_1_photo callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "custom_prompt_2_photos")
async def callback_custom_prompt_2_photos(callback: types.CallbackQuery, state: FSMContext):
    """Handle selection of 2 photos custom prompt"""
    try:
        await state.set_state(UserState.awaiting_first_custom_photo_2)
        
        text = (
            "✍️ *Промпт для 2 фото*\n\n"
            "Вам нужно загрузить 2 фото:\n\n"
            "📸 *Загрузите ПЕРВОЕ фото* — основное фото (по пояс или во весь рост)\n\n"
            "После загрузки первого фото вы загрузите второе, а затем напишете промпт."
        )
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in custom_prompt_2_photos callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(
    F.data == "cancel",
    StateFilter(UserState.awaiting_image_for_custom),
)
async def callback_cancel_custom_image(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for image (custom prompt)."""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)

        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(
    F.data == "cancel",
    StateFilter(UserState.awaiting_custom_photo_confirmation),
)
async def callback_cancel_custom_photo_confirmation(
    callback: types.CallbackQuery, state: FSMContext
):
    """Handle cancel when waiting for custom photo confirmation."""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)

        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


# Handlers for 2 photos custom prompt flow
@router.message(UserState.awaiting_first_custom_photo_2, F.photo)
async def handle_first_custom_photo_2(message: types.Message, state: FSMContext):
    """Handle first photo for 2 photos custom prompt"""
    try:
        # Store first photo
        photo_id = message.photo[-1].file_id
        await state.update_data(first_photo_id=photo_id)
        
        # Move to second photo state
        await state.set_state(UserState.awaiting_second_custom_photo_2)
        
        await message.answer(
            "✅ Первое фото получено!\n\n"
            "📸 Теперь загрузите ВТОРОЕ фото\n\n"
            "Это дополнительное фото, которое будет использовано вместе с первым.",
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
    except Exception as e:
        logger.error(f"Error handling first custom photo 2: {e}")
        await send_error_message(message)


@router.message(UserState.awaiting_second_custom_photo_2, F.photo)
async def handle_second_custom_photo_2(message: types.Message, state: FSMContext):
    """Handle second photo and ask for prompt"""
    try:
        # Store second photo ID
        second_photo_id = message.photo[-1].file_id
        data = await state.get_data()
        first_photo_id = data.get('first_photo_id')
        
        if not first_photo_id:
            await message.answer("❌ Ошибка: не найдено первое фото. Начните сначала.")
            await state.clear()
            await state.set_state(UserState.main_menu)
            return
        
        # Store both photo IDs
        await state.update_data(second_photo_id=second_photo_id)
        await state.set_state(UserState.awaiting_custom_prompt_2_photos)
        
        await message.answer(
            "✅ Оба фото получены!\n\n"
            "✍️ Теперь напишите промпт — что нужно сделать с этими двумя фото?\n\n"
            "Например: *\"Применить стиль из второго фото к первому\"* или *\"Объединить элементы из обоих фото\"*\n\n"
            "Первое фото будет основным, второе — дополнительным.",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard()
        )
    except Exception as e:
        logger.error(f"Error handling second custom photo 2: {e}")
        await send_error_message(message)


@router.message(StateFilter(UserState.awaiting_custom_prompt_2_photos))
async def handle_custom_prompt_2_photos(message: types.Message, state: FSMContext):
    """Handle custom prompt text input for 2 photos workflow"""
    try:
        prompt_text = (message.text or "").strip()

        if not prompt_text:
            await message.answer("Пожалуйста, введите описание того, что нужно сделать с фото.")
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

        data = await state.get_data()
        first_photo_id = data.get('first_photo_id')
        second_photo_id = data.get('second_photo_id')

        if not first_photo_id or not second_photo_id:
            await state.set_state(UserState.awaiting_first_custom_photo_2)
            await message.answer(
                "❌ Не удалось найти загруженные фото. Пожалуйста, начните сначала.",
                reply_markup=back_and_main_menu_keyboard("back_to_menu"),
            )
            return

        # Import api_client from main module
        from ..main import api_client

        progress = await message.answer("📥 Загружаю фото...")
        
        # Download both photos
        first_photo_data = await download_telegram_photo(message.bot, first_photo_id)
        second_photo_data = await download_telegram_photo(message.bot, second_photo_id)

        if not first_photo_data or not second_photo_data:
            await progress.edit_text("❌ Ошибка при загрузке фото. Попробуйте другое фото.")
            return

        # Create temporary files for both images
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f1, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f2:
            f1.write(first_photo_data)
            f2.write(second_photo_data)
            f1_path = Path(f1.name)
            f2_path = Path(f2.name)

        try:
            # Prepare files for upload
            with open(f1_path, 'rb') as f1_file, open(f2_path, 'rb') as f2_file:
                f1_content = f1_file.read()
                f2_content = f2_file.read()
            
            f1_tuple = (f1_path.name, f1_content, 'image/jpeg')
            f2_tuple = (f2_path.name, f2_content, 'image/jpeg')
            
            await progress.edit_text("📤 Отправляю фото на обработку...")
            
            # Create job via API with both photos and custom prompt
            job_data = await api_client.create_job(
                telegram_id=message.from_user.id,
                image_file=f1_tuple,
                prompt=prompt_text,
                second_image_file=f2_tuple
            )
            
            job_id = job_data.get('id')
            
            await message.answer(
                f"✅ Фото отправлены на обработку!\n\n"
                f"ID задачи: {job_id}\n"
                f"Результат будет готов в течение нескольких минут.",
                reply_markup=main_menu_keyboard(),
            )
            
            await state.clear()
            await state.set_state(UserState.main_menu)
            
            logger.info(f"Custom prompt 2 photos job {job_id} created for user {message.from_user.id}")
            
        finally:
            # Clean up temporary files
            f1_path.unlink(missing_ok=True)
            f2_path.unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Error handling custom prompt 2 photos: {e}")
        await send_error_message(message)


@router.callback_query(
    F.data == "cancel",
    StateFilter(UserState.awaiting_custom_prompt_2_photos),
)
async def callback_cancel_custom_prompt_2_photos(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for custom prompt (2 photos)."""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)

        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(
    F.data == "cancel",
    StateFilter(UserState.selecting_custom_prompt_type),
)
async def callback_cancel_custom_prompt_type(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when selecting custom prompt type."""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)

        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(
    F.data == "cancel",
    StateFilter(UserState.awaiting_first_custom_photo_2, UserState.awaiting_second_custom_photo_2),
)
async def callback_cancel_custom_photos_2(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for photos (2 photos custom prompt)."""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)

        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard(),
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
