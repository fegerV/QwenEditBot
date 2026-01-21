"""Promocode handlers for Telegram bot"""

from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from ..keyboards import balance_menu_keyboard, promocode_keyboard
from ..states import UserState
from ..utils import send_error_message, format_balance

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "enter_promocode")
async def callback_enter_promocode(callback: types.CallbackQuery, state: FSMContext):
    """Handle enter promocode callback"""
    try:
        await state.set_state(UserState.awaiting_promocode)
        
        text = (
            "🎁 *Введите промокод*\n\n"
            "Введите код, чтобы получить бонусные баллы."
        )
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=promocode_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in enter_promocode callback: {e}")
        await callback.answer("Произошла ошибка")


@router.message(StateFilter(UserState.awaiting_promocode))
async def handle_promocode_input(message: types.Message, state: FSMContext):
    """Handle promocode input from user"""
    try:
        from ..main import api_client
        
        promocode = message.text.strip()
        
        if not promocode or len(promocode) < 4:
            await message.answer("❌ Неверный формат промокода. Попробуйте снова.", reply_markup=promocode_keyboard())
            return
        
        # Use promocode via backend API
        result = await api_client.use_promocode(message.from_user.id, promocode)
        
        if result.get("success"):
            amount = result.get("amount", 0)
            new_balance = result.get("new_balance", 0)
            
            text = (
                f"✅ {result['message']}\n\n"
                f"💰 Ваш баланс: {format_balance(new_balance)}"
            )
            
            await message.answer(text, parse_mode="Markdown", reply_markup=balance_menu_keyboard())
            await state.clear()
        else:
            await message.answer(
                f"❌ {result['message']}\n\nПопробуйте другой промокод.",
                reply_markup=promocode_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error handling promocode input: {e}")
        await send_error_message(message)
        await state.clear()


@router.callback_query(F.data == "cancel_promocode", StateFilter(UserState.awaiting_promocode))
async def callback_cancel_promocode(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel promocode input"""
    try:
        await state.clear()
        
        from ..main import api_client
        balance = await api_client.get_balance(callback.from_user.id)
        
        text = f"💰 *Ваш баланс: {format_balance(balance)}*\n\nСтоимость редактирования: 30 баллов"
        
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=balance_menu_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error canceling promocode input: {e}")
        await callback.answer("Произошла ошибка")
