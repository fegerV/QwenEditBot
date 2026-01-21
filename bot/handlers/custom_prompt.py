"""Custom prompt handlers - user input for custom editing"""

import logging
import tempfile
from pathlib import Path

from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from ..states import UserState
from ..keyboards import cancel_keyboard, main_menu_keyboard, main_menu_inline_keyboard
from ..utils import download_telegram_photo, send_error_message

logger = logging.getLogger(__name__)

router = Router()


async def start_custom_prompt(
    message: types.Message,
    state: FSMContext,
    is_callback: bool = False,
):
    """Start custom prompt flow (photo → confirm → prompt → process)."""
    try:
        await state.clear()
        await state.set_state(UserState.awaiting_image_for_custom)

        text = (
            "✍️ *Свой промпт*\n\n"
            "Сначала загрузите фото, которое нужно обработать.\n"
            "После этого вы подтвердите фото и сможете написать промпт.\n\n"
            "📸 *Загрузите фото для обработки:*"
        )

        await message.answer(text, parse_mode="Markdown", reply_markup=cancel_keyboard())

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
