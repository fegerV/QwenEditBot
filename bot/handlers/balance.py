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
        
        # Check if user is admin to provide special messaging
        from backend.app.config import settings as backend_settings
        user_is_admin = message.from_user.id in getattr(backend_settings, 'ADMIN_IDS', [])
        
        if balance is not None:
            if user_is_admin:
                text = (
                    f"💰 *Ваш баланс: {format_balance(balance)}*\n\n"
                    f"✅ *Администратор: Неограниченное количество обработок*\n"
                    f"Стоимость редактирования: 30 баллов (для обычных пользователей)"
                )
            else:
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


@router.callback_query(F.data == "payment_history")
async def callback_payment_history(callback: types.CallbackQuery):
    """Handle payment history callback"""
    try:
        from ..main import api_client
        
        result = await api_client.get_user_payments(callback.from_user.id, limit=10)
        
        if result and result.get("payments"):
            payments = result["payments"]
            
            text = "📜 *История платежей*\n\n"
            
            for payment in payments:
                # Convert amount from kopeks to rubles
                amount_rubles = payment["amount"] / 100
                
                # Format status
                status_emoji = {
                    "succeeded": "✅",
                    "pending": "⏳",
                    "failed": "❌",
                    "cancelled": "🚫"
                }.get(payment["status"], "❓")
                
                # Format payment type
                type_label = {
                    "payment": "Пополнение",
                    "weekly_bonus": "Бонус",
                    "refund": "Возврат"
                }.get(payment["payment_type"], "Платёж")
                
                method_label = ""
                if payment.get("payment_method") == "sbp":
                    method_label = " (СБП)"
                elif payment.get("payment_method") == "card":
                    method_label = " (Карта)"
                
                text += (
                    f"{status_emoji} *{type_label}{method_label}*\n"
                    f"💰 {amount_rubles:.0f} ₽\n"
                    f"📅 {payment['created_at'][:10]}\n\n"
                )
            
            text += f"Всего: {result['total']} платежей"
        else:
            text = "📜 *История платежей*\n\nУ вас пока нет платежей."
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="balance")]
        ])
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in payment history callback: {e}")
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
            from keyboards import back_to_menu_keyboard
            await message.answer(text, parse_mode="Markdown", reply_markup=top_up_keyboard())
        
    except Exception as e:
        logger.error(f"Error showing top up menu: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "top_up")
async def callback_top_up(callback: types.CallbackQuery, state: FSMContext):
    """Handle top up callback - redirect to payments handler"""
    try:
        from .payments import handle_top_up
        await handle_top_up(callback, state)
        
    except Exception as e:
        logger.error(f"Error in top_up callback: {e}")
        await callback.answer("Произошла ошибка")
