"""Payment handlers - creating YooKassa payments and sending confirmation links"""

import asyncio
import logging
from typing import Optional

from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

from ..keyboards import main_menu_keyboard, payment_amount_keyboard, payment_link_keyboard
from ..states import UserState

logger = logging.getLogger(__name__)

router = Router()


async def show_top_up_menu(message: types.Message, state: FSMContext, *, edit: bool = False) -> None:
    await state.set_state(UserState.awaiting_payment)
    await state.update_data(awaiting_custom_amount=False)

    text = (
        "💳 Пополнение баланса\n\n"
        "Выберите сумму (СБП/карта через YooKassa) или введите свою сумму (1-10000 ₽)."
    )

    if edit:
        await message.edit_text(text, reply_markup=payment_amount_keyboard())
    else:
        await message.answer(text, reply_markup=payment_amount_keyboard())


@router.callback_query(F.data == "top_up")
async def callback_top_up(callback: types.CallbackQuery, state: FSMContext):
    try:
        await show_top_up_menu(callback.message, state, edit=True)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in top_up callback: {e}")
        await callback.answer("Произошла ошибка")


async def _create_and_send_payment(
    chat_id: int,
    amount: int,
    message: types.Message,
    state: FSMContext,
    bot: Bot,
    *,
    edit: bool,
) -> None:
    from ..main import api_client

    payment = await api_client.create_payment(chat_id, amount)

    confirmation_url = payment.get("confirmation_url")
    payment_id = payment.get("payment_id")

    if not confirmation_url or not payment_id:
        await message.answer("Не удалось создать платёж. Попробуйте позже.")
        return

    text = f"💳 Оплата {amount} ₽\n\nНажмите кнопку ниже для оплаты через СБП или карту."

    if edit:
        await message.edit_text(text, reply_markup=payment_link_keyboard(confirmation_url))
    else:
        await message.answer(text, reply_markup=payment_link_keyboard(confirmation_url))

    await state.update_data(payment_id=payment_id, amount=amount, awaiting_custom_amount=False)

    asyncio.create_task(check_payment_status(bot, chat_id, payment_id))


@router.callback_query(F.data.startswith("pay_amount_"))
async def callback_pay_amount(callback: types.CallbackQuery, state: FSMContext):
    try:
        suffix = callback.data.replace("pay_amount_", "", 1)

        if suffix == "custom":
            await state.set_state(UserState.awaiting_payment)
            await state.update_data(awaiting_custom_amount=True)
            await callback.message.edit_text(
                "✍️ Введите сумму для пополнения (1-10000 ₽):",
                reply_markup=None,
            )
            await callback.answer()
            return

        amount = int(suffix)
        await _create_and_send_payment(
            callback.from_user.id,
            amount,
            callback.message,
            state,
            callback.bot,
            edit=True,
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in payment amount callback: {e}")
        await callback.answer("Произошла ошибка")


@router.message(UserState.awaiting_payment)
async def message_custom_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("awaiting_custom_amount"):
        return

    try:
        amount = int((message.text or "").strip())
    except Exception:
        await message.answer("Введите число от 1 до 10000.")
        return

    if amount < 1 or amount > 10000:
        await message.answer("Введите сумму от 1 до 10000.")
        return

    try:
        await _create_and_send_payment(message.from_user.id, amount, message, state, message.bot, edit=False)
    except Exception as e:
        logger.error(f"Error creating custom amount payment: {e}")
        await message.answer("Не удалось создать платёж. Попробуйте позже.")


async def check_payment_status(bot: Bot, user_id: int, payment_id: int) -> None:
    from ..main import api_client

    for _ in range(12):
        try:
            payment: Optional[dict] = await api_client.get_payment(payment_id)
            if not payment:
                await asyncio.sleep(5)
                continue

            status = payment.get("status")

            if status == "succeeded":
                await bot.send_message(
                    user_id,
                    "✅ Платёж успешен! Баллы добавлены.",
                    reply_markup=main_menu_keyboard(),
                )
                return
            if status in ("failed", "canceled"):
                await bot.send_message(
                    user_id,
                    "❌ Платёж не прошёл. Попробуйте снова.",
                    reply_markup=main_menu_keyboard(),
                )
                return

        except Exception:
            pass

        await asyncio.sleep(5)
