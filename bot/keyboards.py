"""Keyboard layouts for Telegram bot"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# Main Menu Keyboard (Reply)
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🎨 Редактировать фото"))
    builder.row(KeyboardButton(text="🧩 Стили"), KeyboardButton(text="💡 Освещение"), KeyboardButton(text="🖼 Оформление"))
    builder.add(KeyboardButton(text="✍️ Свой промпт"))
    builder.row(KeyboardButton(text="💰 Баланс"), KeyboardButton(text="➕ Пополнить"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    
    return builder.as_markup(resize_keyboard=True)


# Edit Photo Submenu Keyboard (Inline)
def edit_photo_submenu_keyboard() -> InlineKeyboardMarkup:
    """Create edit photo submenu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🧩 Выбрать пресет", callback_data="edit_preset"))
    builder.add(InlineKeyboardButton(text="✍️ Собственный промпт", callback_data="edit_custom"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Category Selection Keyboard (Inline)
def category_keyboard() -> InlineKeyboardMarkup:
    """Create category selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🧩 Стили", callback_data="category_styles"))
    builder.add(InlineKeyboardButton(text="💡 Освещение", callback_data="category_lighting"))
    builder.add(InlineKeyboardButton(text="🖼 Оформление", callback_data="category_design"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Presets Keyboard (Inline) - dynamic based on available presets
def presets_keyboard(presets: list) -> InlineKeyboardMarkup:
    """Create presets keyboard from list of presets"""
    builder = InlineKeyboardBuilder()
    
    # Add preset buttons (2 per row)
    for i, preset in enumerate(presets):
        preset_id = preset.get('id')
        name = preset.get('name', 'Без названия')
        icon = preset.get('icon', '📷')
        
        button = InlineKeyboardButton(text=f"{icon} {name}", callback_data=f"preset_{preset_id}")
        
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    # Add back button
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_edit"))
    
    return builder.as_markup()


# Balance Menu Keyboard (Inline)
def balance_menu_keyboard() -> InlineKeyboardMarkup:
    """Create balance menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Пополнить", callback_data="top_up"))
    builder.add(InlineKeyboardButton(text="📜 История", callback_data="payment_history"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Top Up Keyboard (Inline) - kept for backward compatibility
def top_up_keyboard() -> InlineKeyboardMarkup:
    """Create top up keyboard (deprecated - use payments handler)"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 СБП", callback_data="top_up"))
    builder.add(InlineKeyboardButton(text="💳 Карта", callback_data="top_up"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Top Up Selection Keyboard (Inline)
def top_up_amount_keyboard() -> InlineKeyboardMarkup:
    """Create top up amount selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="100 ₽", callback_data="top_up_100"))
    builder.add(InlineKeyboardButton(text="250 ₽", callback_data="top_up_250"))
    builder.row(InlineKeyboardButton(text="500 ₽", callback_data="top_up_500"))
    builder.add(InlineKeyboardButton(text="1000 ₽", callback_data="top_up_1000"))
    builder.row(InlineKeyboardButton(text="💳 Своя сумма", callback_data="top_up_custom"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_balance"))
    
    return builder.as_markup()


# Custom Amount Input Keyboard (Inline)
def custom_amount_keyboard() -> InlineKeyboardMarkup:
    """Create custom amount input keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_custom_amount"))
    
    return builder.as_markup()


# Payment Confirmation Keyboard (Inline)
def payment_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Create payment confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_payment"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_payment"))
    
    return builder.as_markup()


# Cancel Keyboard (Inline)
def cancel_keyboard() -> InlineKeyboardMarkup:
    """Create cancel keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel"))
    
    return builder.as_markup()
