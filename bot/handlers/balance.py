"""Balance handlers - showing balance and payment options"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from ..states import UserState
from ..keyboards import balance_menu_keyboard, top_up_keyboard, main_menu_keyboard
from ..utils import send_error_message, format_balance

logger = logging.getLogger(__name__)

router = Router()


async def show_balance(message: types.Message):
    """Show user balance"""
    try:
        # Import api_client from main module
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
        # Import api_client from main module
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
                reply_markup=balance_menu_keyboard()
            )
        else:
            await callback.answer("Не удалось получить баланс.")
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in balance callback: {e}")
        await callback.answer("Произошла ошибка")


async def show_top_up_menu(message: types.Message, state: FSMContext):
    """Show top up menu"""
    try:
        await state.set_state(UserState.awaiting_payment)
        
        text = (
            "➕ *Пополнение баланса*\n\n"
            "Выберите способ пополнения:"
        )
        
        if message.text:
            await message.answer(text, parse_mode="Markdown", reply_markup=top_up_keyboard())
        else:
            # For callback (from balance menu)
            from ..keyboards import back_to_menu_keyboard
            await message.answer(text, parse_mode="Markdown", reply_markup=top_up_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing top up menu: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "top_up")
async def callback_top_up(callback: types.CallbackQuery, state: FSMContext):
    """Handle top up callback"""
    try:
        await state.set_state(UserState.awaiting_payment)
        
        text = (
            "➕ *Пополнение баланса*\n\n"
            "Выберите способ пополнения:"
        )
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=top_up_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in top_up callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("pay_"))
async def callback_payment(callback: types.CallbackQuery):
    """Handle payment method selection"""
    try:
        payment_method = callback.data.split("_")[1]
        
        if payment_method == "sbp":
            text = (
                "💳 *Пополнение через СБП*\n\n"
                "Функция пополнения будет доступна в Фазе 4.\n\n"
                "Следите за обновлениями! 🚀"
            )
        elif payment_method == "card":
            text = (
                "💳 *Пополнение картой*\n\n"
                "Функция пополнения будет доступна в Фазе 4.\n\n"
                "Следите за обновлениями! 🚀"
            )
        else:
            text = "Неизвестный способ оплаты."
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown"
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in payment callback: {e}")
        await callback.answer("Произошла ошибка")
