"""Balance handlers - showing user balance"""

import logging

from aiogram import F, Router, types

from ..keyboards import balance_menu_keyboard
from ..utils import format_balance, send_error_message

logger = logging.getLogger(__name__)

router = Router()


async def show_balance(message: types.Message):
    """Show user balance"""
    try:
        from ..main import api_client

        balance = await api_client.get_balance(message.from_user.id)

        if balance is not None:
            text = (
                f"💰 *Ваш баланс: {format_balance(balance)}*\n\n"
                f"Стоимость редактирования: 30 баллов"
            )

            await message.answer(text, parse_mode="Markdown", reply_markup=balance_menu_keyboard())
        else:
            await message.answer("Не удалось получить баланс. Попробуйте позже.")

    except Exception as e:
        logger.error(f"Error showing balance: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "balance")
async def callback_balance(callback: types.CallbackQuery):
    """Handle balance callback"""
    try:
        from ..main import api_client

        balance = await api_client.get_balance(callback.from_user.id)

        if balance is not None:
            text = (
                f"💰 *Ваш баланс: {format_balance(balance)}*\n\n"
                f"Стоимость редактирования: 30 баллов"
            )

            await callback.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=balance_menu_keyboard(),
            )
        else:
            await callback.answer("Не удалось получить баланс.")

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in balance callback: {e}")
        await callback.answer("Произошла ошибка")
