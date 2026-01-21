"""Payment handlers for Telegram bot"""

import asyncio
from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from ..services import BackendAPIClient
from ..keyboards import main_menu_keyboard, main_menu_inline_keyboard, top_up_keyboard
from ..states import UserState

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "top_up")
async def handle_top_up(callback_query: CallbackQuery, state: FSMContext):
    """Show top-up options with bonus amounts"""
    try:
        await state.set_state(UserState.awaiting_payment)
        
        text = """💳 *Пополнение баланса*

Выберите сумму пополнения. Чем больше сумма, тем больше бонус 🎁"""

        if callback_query.message:
            await callback_query.message.edit_text(
                text,
                parse_mode="Markdown",
                reply_markup=top_up_keyboard()
            )
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error showing top-up options: {e}")
        await callback_query.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("pay_"), StateFilter(UserState.awaiting_payment))
async def handle_payment_amount(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment amount selection with bonus calculation"""
    try:
        # Parse callback data (e.g., "pay_500_30" -> amount=500, bonus=30)
        parts = callback_query.data.split("_")
        amount = int(parts[1])
        bonus = int(parts[2]) if len(parts) > 2 else 0
        total_points = amount * 100 + bonus  # Base points from amount + bonus
        
        # Show payment confirmation with bonus info
        bonus_text = f"\n🎁 Бонус: +{bonus} баллов" if bonus > 0 else ""
        text = f"""💳 Пополнение на {amount} ₽

💰 Вы получите: {total_points} баллов{bonus_text}

Нажмите кнопку ниже для оплаты через ЮКасса"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", callback_data=f"confirm_pay_{amount}_{bonus}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="top_up")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Error handling payment amount: {e}")
        await callback_query.answer("Произошла ошибка")


@router.message(StateFilter(UserState.awaiting_custom_prompt))
async def handle_custom_amount(message: Message, state: FSMContext):
    """Handle custom amount input"""
    # Payment functionality is disabled
    text = """💳 Пополнение баланса

Функция временно отключена для тестирования."""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard)


async def show_payment_method_selection(message: Message, state: FSMContext):
    """Show payment method selection (Card or SBP)"""
    data = await state.get_data()
    amount = data.get("payment_amount")
    
    text = f"""💳 Выберите способ оплаты для суммы {amount} ₽:"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Карта", callback_data="method_card"),
            InlineKeyboardButton(text="📲 СБП", callback_data="method_sbp")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="top_up")
        ]
    ])
    
    await message.edit_text(text, reply_markup=keyboard)
    await state.set_state(UserState.selecting_payment_method)


async def show_payment_method_selection_message(message: Message, state: FSMContext):
    """Show payment method selection after custom amount message"""
    data = await state.get_data()
    amount = data.get("payment_amount")
    
    text = f"""💳 Выберите способ оплаты для суммы {amount} ₽:"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Карта", callback_data="method_card"),
            InlineKeyboardButton(text="📲 СБП", callback_data="method_sbp")
        ],
        [
            InlineKeyboardButton(text="🔙 Отмена", callback_data="top_up")
        ]
    ])
    
    await message.answer(text, reply_markup=keyboard)
    await state.set_state(UserState.selecting_payment_method)


@router.callback_query(F.data.startswith("method_"), StateFilter(UserState.selecting_payment_method))
async def handle_payment_method(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment method selection"""
    # Payment functionality is disabled
    text = """💳 Пополнение баланса

Функция временно отключена для тестирования."""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
        ]
    ])
    
    await callback_query.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("confirm_pay_"), StateFilter(UserState.awaiting_payment))
async def handle_confirm_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment confirmation and create payment"""
    user_id = callback_query.from_user.id
    
    try:
        # Parse callback data (e.g., "confirm_pay_500_30" -> amount=500, bonus=30)
        parts = callback_query.data.split("_")
        amount = int(parts[2])
        bonus = int(parts[3]) if len(parts) > 3 else 0
        total_points = amount * 100 + bonus
        
        # Create payment via backend API (use card as default method)
        api_client = BackendAPIClient()
        payment = await api_client.create_payment(user_id, amount, "card")
        
        # Show payment link
        bonus_text = f"\n🎁 Бонус: +{bonus} баллов" if bonus > 0 else ""
        text = f"""💳 Оплата {amount} ₽ через карту

💰 Вы получите: {total_points} баллов{bonus_text}

Нажмите кнопку ниже для оплаты через ЮКассу"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=payment["confirmation_url"])],
            [
                InlineKeyboardButton(text="🔄 Проверить статус", callback_data=f"check_payment_{payment['id']}"),
                InlineKeyboardButton(text="🔙 Назад", callback_data="top_up")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
        # Store payment info for status checking
        await state.update_data(
            payment_id=payment["id"],
            amount=amount,
            bonus=bonus
        )
        
        # Start checking payment status in background
        asyncio.create_task(
            _check_payment_status(user_id, payment["id"], total_points, state)
        )
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        await callback_query.answer("❌ Ошибка создания платежа", show_alert=True)


async def _create_payment(callback_query: CallbackQuery, state: FSMContext, amount: int, method: str = "card"):
    """Create payment and show payment link"""
    user_id = callback_query.from_user.id
    
    try:
        # Create payment via backend API
        api_client = BackendAPIClient()
        payment = await api_client.create_payment(user_id, amount, method)
        
        # Show payment link
        method_name = "Карту" if method == "card" else "СБП"
        text = f"""💳 Оплата {amount} ₽ через {method_name}

Нажмите кнопку ниже для оплаты через ЮКасса ({method_name})

💎 {amount * 100} баллов будет зачислено на ваш баланс"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=payment["confirmation_url"])],
            [
                InlineKeyboardButton(text="🔄 Проверить статус", callback_data=f"check_payment_{payment['id']}"),
                InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_menu")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
        # Store payment info for status checking
        await state.update_data(
            payment_id=payment["id"],
            amount=amount
        )
        
        # Start checking payment status in background
        asyncio.create_task(
            _check_payment_status(user_id, payment["id"], amount, state)
        )
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        await callback_query.answer("❌ Ошибка создания платежа", show_alert=True)


@router.callback_query(F.data.startswith("check_payment_"))
async def handle_check_payment(callback_query: CallbackQuery, state: FSMContext):
    """Handle manual payment status check"""
    payment_id = int(callback_query.data.split("_")[2])
    
    try:
        api_client = BackendAPIClient()
        payment = await api_client.get_payment(payment_id)
        
        if payment["status"] == "succeeded":
            await callback_query.answer("✅ Платёж уже успешен!", show_alert=True)
        elif payment["status"] == "failed":
            await callback_query.answer("❌ Платёж отклонён", show_alert=True)
        elif payment["status"] == "cancelled":
            await callback_query.answer("🚫 Платёж отменён", show_alert=True)
        else:
            await callback_query.answer(f"⏳ Статус: {payment['status']}", show_alert=True)
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        await callback_query.answer("❌ Ошибка проверки статуса", show_alert=True)


async def _check_payment_status(user_id: int, payment_id: int, amount: int, state: FSMContext):
    """Check payment status periodically"""
    from main import api_client
    from aiogram import Bot
    from ..config import settings
    
    bot = Bot(token=settings.BOT_TOKEN)
    
    for i in range(12):  # Check for 60 seconds (12 * 5)
        try:
            payment = await api_client.get_payment(payment_id)
            
            if payment["status"] == "succeeded":
                # Send success notification
                try:
                    await bot.send_message(
                        user_id,
                        f"✅ Платёж успешен! Баллы добавлены 🎉\n\n💰 Пополнено: {amount} баллов\n💳 Статус: Успешно",
                        reply_markup=main_menu_inline_keyboard()
                    )
                except Exception as e:
                    logger.error(f"Error sending success notification: {e}")
                
                # Clear state
                await state.clear()
                return
                
            elif payment["status"] == "failed":
                # Send failure notification
                try:
                    await bot.send_message(
                        user_id,
                        "❌ Платёж отклонен. Попробуйте снова.",
                        reply_markup=main_menu_inline_keyboard()
                    )
                except Exception as e:
                    logger.error(f"Error sending failure notification: {e}")
                
                await state.clear()
                return
            
            elif payment["status"] == "cancelled":
                # Payment cancelled
                try:
                    await bot.send_message(
                        user_id,
                        "❌ Платёж отменён.",
                        reply_markup=main_menu_inline_keyboard()
                    )
                except Exception as e:
                    logger.error(f"Error sending cancelled notification: {e}")
                
                await state.clear()
                return
            
            # Wait 5 seconds before next check
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            await asyncio.sleep(5)
    
    # Timeout after 60 seconds
    logger.info(f"Payment status check timeout for payment {payment_id}")
    
    # Close bot session
    try:
        await bot.session.close()
    except:
        pass
