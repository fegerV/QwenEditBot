"""Custom prompt handlers - user input for custom editing"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from ..states import UserState
from ..keyboards import cancel_keyboard, main_menu_keyboard, main_menu_inline_keyboard
from ..utils import send_error_message

logger = logging.getLogger(__name__)

router = Router()


async def start_custom_prompt(
    message: types.Message,
    state: FSMContext,
    is_callback: bool = False
):
    """Start custom prompt flow: ask for photo first, then prompt."""
    try:
        await state.set_state(UserState.awaiting_image_for_custom)

        text = (
            "✍️ *Свой промпт*\n\n"
            "Сначала загрузите фото, которое нужно обработать.\n"
            "После подтверждения фото я попрошу вас написать промпт."
        )

        await message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )

    except Exception as e:
        logger.error(f"Error starting custom prompt: {e}")
        if not is_callback:
            await send_error_message(message)


@router.message(StateFilter(UserState.awaiting_custom_prompt))
async def handle_custom_prompt(message: types.Message, state: FSMContext):
    """Handle custom prompt text input (after photo is confirmed)."""
    try:
        prompt_text = (message.text or "").strip()

        data = await state.get_data()
        photo_id = data.get("photo_id")

        if not photo_id:
            await message.answer(
                "❌ Фото не найдено. Пожалуйста, начните заново и сначала загрузите фото.",
                reply_markup=main_menu_keyboard(),
            )
            await state.clear()
            await state.set_state(UserState.main_menu)
            return

        # Validate prompt
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

        await state.update_data(custom_prompt=prompt_text)

        await message.answer("📥 Загружаю фото...")

        from ..main import api_client
        from ..utils import download_telegram_photo
        import tempfile
        from pathlib import Path

        photo_data = await download_telegram_photo(message.bot, photo_id)
        if not photo_data:
            await message.answer("Ошибка при загрузке фото. Попробуйте другое фото.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(photo_data)
            temp_file_path = temp_file.name

        try:
            filename = Path(temp_file_path).name
            with open(temp_file_path, "rb") as f:
                file_content = f.read()

            file_tuple = (filename, file_content, "image/jpeg")

            await message.answer("📤 Отправляю фото на обработку...")

            job_data = await api_client.create_job(
                telegram_id=message.from_user.id,
                image_file=file_tuple,
                prompt=prompt_text,
            )

            job_id = job_data.get("id")

            await state.set_state(UserState.processing_job)
            await state.update_data(job_id=job_id)

            await message.answer(
                f"✅ Фото отправлено на обработку!\n\n"
                f"Обработка: Свой промпт\n"
                f"ID задачи: {job_id}\n"
                f"Статус: ⏳ В очереди\n\n"
                f"Как результат будет готов, вы получите уведомление.",
                reply_markup=main_menu_inline_keyboard(),
            )

            logger.info(f"Custom prompt job {job_id} created for user {message.from_user.id}")

        finally:
            Path(temp_file_path).unlink(missing_ok=True)

    except Exception as e:
        logger.error(f"Error handling custom prompt: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "cancel", StateFilter(UserState.awaiting_custom_prompt))
async def callback_cancel_custom_prompt(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for custom prompt"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
         
        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard()
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
         
        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard()
        )
         
        await callback.answer()
         
    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка")
