"""Payment handlers for Telegram bot"""

import asyncio
from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from ..services.api_client import BackendAPIClient
from ..keyboards import main_menu_keyboard
from ..states import UserState

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "top_up")
async def handle_top_up(callback_query: CallbackQuery, state: FSMContext):
    """Show top-up options"""
    text = """💳 Пополнение баланса

Выберите сумму (СБП, Карта):
• 100 ₽
• 250 ₽
• 500 ₽
• 1000 ₽

Или введите свою сумму (1-10000 ₽)"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="100 ₽", callback_data="pay_100"),
            InlineKeyboardButton(text="250 ₽", callback_data="pay_250")
        ],
        [
            InlineKeyboardButton(text="500 ₽", callback_data="pay_500"),
            InlineKeyboardButton(text="1000 ₽", callback_data="pay_1000")
        ],
        [
            InlineKeyboardButton(text="✍️ Свою сумму", callback_data="pay_custom")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
        ]
    ])
    
    try:
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        await state.set_state(UserState.awaiting_payment)
    except Exception as e:
        logger.error(f"Error showing top-up options: {e}")


@router.callback_query(F.data.startswith("pay_"), StateFilter(UserState.awaiting_payment))
async def handle_payment_amount(callback_query: CallbackQuery, state: FSMContext):
    """Handle payment amount selection"""
    data = callback_query.data.split("_")
    
    if data[1] == "custom":
        # Prompt for custom amount
        text = """💰 Введите сумму пополнения

Минимум: 1 ₽
Максимум: 10000 ₽

Отправьте число (например: 500)"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="top_up")]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        # Reuse awaiting_custom_prompt state for custom amount input
        await state.set_state(UserState.awaiting_custom_prompt)
        return
    
    try:
        amount = int(data[1])
        await _create_payment(callback_query, state, amount)
    except ValueError:
        await callback_query.answer("❌ Неверная сумма", show_alert=True)


@router.message(StateFilter(UserState.awaiting_custom_prompt))
async def handle_custom_amount(message: Message, state: FSMContext):
    """Handle custom amount input"""
    try:
        amount = int(message.text)
        
        if amount < 1 or amount > 10000:
            await message.answer(
                "❌ Сумма должна быть от 1 до 10000 рублей. Попробуйте снова."
            )
            return
        
        # Create payment using callback query from state
        await _create_payment_from_message(message, state, amount)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (например: 500)")


async def _create_payment(callback_query: CallbackQuery, state: FSMContext, amount: int):
    """Create payment and show payment link"""
    user_id = callback_query.from_user.id
    
    try:
        # Create payment via backend API
        api_client = BackendAPIClient()
        payment = await api_client.create_payment(user_id, amount)
        
        # Show payment link
        text = f"""💳 Оплата {amount} ₽

Нажмите кнопку ниже для оплаты через СБП или карту

💎 {amount * 100} баллов будет зачислено на ваш баланс"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=payment["confirmation_url"])],
            [
                InlineKeyboardButton(text="🔄 Проверить статус", callback_data=f"check_payment_{payment['payment_id']}"),
                InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_menu")
            ]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
        # Store payment info for status checking
        await state.update_data(
            payment_id=payment["payment_id"],
            amount=amount
        )
        
        # Start checking payment status in background
        asyncio.create_task(
            _check_payment_status(user_id, payment["payment_id"], amount, state)
        )
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        await callback_query.answer("❌ Ошибка создания платежа", show_alert=True)


async def _create_payment_from_message(message: Message, state: FSMContext, amount: int):
    """Create payment from message input"""
    user_id = message.from_user.id
    
    try:
        # Create payment via backend API
        api_client = BackendAPIClient()
        payment = await api_client.create_payment(user_id, amount)
        
        # Show payment link
        text = f"""💳 Оплата {amount} ₽

Нажмите кнопку ниже для оплаты через СБП или карту

💎 {amount * 100} баллов будет зачислено на ваш баланс"""
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить", url=payment["confirmation_url"])],
            [
                InlineKeyboardButton(text="🔄 Проверить статус", callback_data=f"check_payment_{payment['payment_id']}"),
                InlineKeyboardButton(text="🔙 Отмена", callback_data="back_to_menu")
            ]
        ])
        
        await message.answer(text, reply_markup=keyboard)
        
        # Store payment info for status checking
        await state.update_data(
            payment_id=payment["payment_id"],
            amount=amount
        )
        
        # Start checking payment status in background
        asyncio.create_task(
            _check_payment_status(user_id, payment["payment_id"], amount, state)
        )
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        await message.answer("❌ Ошибка создания платежа. Попробуйте позже.")


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
        else:
            await callback_query.answer(f"⏳ Статус: {payment['status']}", show_alert=True)
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        await callback_query.answer("❌ Ошибка проверки статуса", show_alert=True)


async def _check_payment_status(user_id: int, payment_id: int, amount: int, state: FSMContext):
    """Check payment status periodically"""
    from ..main import api_client
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
                        f"✅ Платёж успешен! Баллы добавлены 🎉\n\n💰 Пополнено: {amount * 100} баллов\n💳 Новый баланс: {payment.get('new_balance', 'нажмите /balance')} баллов",
                        reply_markup=main_menu_keyboard()
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
                        reply_markup=main_menu_keyboard()
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
                        reply_markup=main_menu_keyboard()
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
