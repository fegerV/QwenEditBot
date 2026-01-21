"""Keyboard layouts for Telegram bot"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# Main Menu Keyboard (Reply) - Updated structure

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard - 8 main sections"""
    builder = ReplyKeyboardBuilder()
    
    # Row 1: Artistic styles and Image transformation
    builder.row(
        KeyboardButton(text="🎨 Художественные стили"),
        KeyboardButton(text="🧝‍ Изменить образ")
    )
    
    # Row 2: Fitting room (requires 2 photos)
    builder.row(KeyboardButton(text="👕 ПРИМЕРОЧНАЯ"))
    
    # Row 3: Photo editing and Custom prompt
    builder.row(
        KeyboardButton(text="✨ Редактировать фото"),
        KeyboardButton(text="✍️ Свой промпт")
    )
    
    # Row 4: Knowledge base and Profile
    builder.row(
        KeyboardButton(text="📚 База знаний"),
        KeyboardButton(text="👩 Профиль")
    )
    
    # Row 5: Help
    builder.row(KeyboardButton(text="ℹ️ Помощь"))
    
    return builder.as_markup(resize_keyboard=True)


# Main Menu Inline Keyboard (for use in callbacks)
def main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard for inline use"""
    builder = InlineKeyboardBuilder()
    
    # Row 1: Artistic styles and Image transformation
    builder.row(InlineKeyboardButton(text="🎨 Художественные стили", callback_data="category_artistic"))
    builder.add(InlineKeyboardButton(text="🧝‍ Изменить образ", callback_data="change_appearance"))
    
    # Row 2: Fitting room
    builder.row(InlineKeyboardButton(text="👕 ПРИМЕРОЧНАЯ", callback_data="fitting_room"))
    
    # Row 3: Photo editing and Custom prompt
    builder.row(InlineKeyboardButton(text="✨ Редактировать фото", callback_data="edit_photo"))
    builder.add(InlineKeyboardButton(text="✍️ Свой промпт", callback_data="custom_prompt"))
    
    # Row 4: Knowledge base and Profile
    builder.row(InlineKeyboardButton(text="📚 База знаний", callback_data="knowledge_base"))
    builder.add(InlineKeyboardButton(text="👩 Профиль", callback_data="profile"))
    
    # Row 5: Help
    builder.row(InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help"))
    
    return builder.as_markup()


# Edit Photo Submenu Keyboard (Inline) - Updated

def edit_photo_submenu_keyboard() -> InlineKeyboardMarkup:
    """Create edit photo submenu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🧩 Выбрать пресет", callback_data="edit_preset"))
    builder.add(InlineKeyboardButton(text="✍️ Свой промпт", callback_data="edit_custom"))
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


# Back and Main Menu Keyboard (Inline) - Universal

def back_and_main_menu_keyboard(back_callback: str = "back_to_menu") -> InlineKeyboardMarkup:
    """Create keyboard with Back and Main Menu buttons"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


# Fitting Room Instructions Keyboard (Inline)

def fitting_room_instructions_keyboard() -> InlineKeyboardMarkup:
    """Create fitting room instructions and start button"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚀 Начать примерку", callback_data="start_fitting"))
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


# Profile Menu Keyboard (Inline)

def profile_menu_keyboard() -> InlineKeyboardMarkup:
    """Create profile menu keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="top_up"))
    builder.add(InlineKeyboardButton(text="🎁 Промокод", callback_data="enter_promocode"))
    builder.row(InlineKeyboardButton(text="📜 История платежей", callback_data="payment_history"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Knowledge Base Menu Keyboard (Inline)

def knowledge_base_keyboard() -> InlineKeyboardMarkup:
    """Create knowledge base placeholder keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📖 Промпты и стили", callback_data="kb_prompts"))
    builder.add(InlineKeyboardButton(text="👗 Одежда и fashion", callback_data="kb_fashion"))
    builder.row(InlineKeyboardButton(text="🎭 Художественные техники", callback_data="kb_art"))
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


# Category Selection Keyboard (Inline)
def category_keyboard() -> InlineKeyboardMarkup:
    """Create category selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎨 Художественные стили", callback_data="category_styles"))
    builder.row(InlineKeyboardButton(text="🧑 Портреты", callback_data="category_portrait"))
    builder.row(InlineKeyboardButton(text="📦 Товары", callback_data="category_product"))
    builder.row(InlineKeyboardButton(text="💡 Освещение", callback_data="category_lighting"))
    builder.row(InlineKeyboardButton(text="🎬 Комиксы и анимация", callback_data="category_animation"))
    builder.row(InlineKeyboardButton(text="✨ Улучшение", callback_data="category_enhancement"))
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
    builder.row(InlineKeyboardButton(text="💳 Пополнить", callback_data="top_up"))
    builder.add(InlineKeyboardButton(text="🎁 Промокод", callback_data="enter_promocode"))
    builder.row(InlineKeyboardButton(text="📜 История", callback_data="payment_history"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Top Up Keyboard (Inline)
def top_up_keyboard() -> InlineKeyboardMarkup:
    """Create top up keyboard with payment options"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="300 ₽", callback_data="pay_300"))
    builder.row(InlineKeyboardButton(text="500 ₽ (+30 🎁)", callback_data="pay_500_30"))
    builder.row(InlineKeyboardButton(text="1000 ₽ (+60 🎁)", callback_data="pay_1000_60"))
    builder.row(InlineKeyboardButton(text="2000 ₽ (+90 🎁)", callback_data="pay_2000_90"))
    builder.row(InlineKeyboardButton(text="3000 ₽ (+120 🎁)", callback_data="pay_3000_120"))
    builder.row(InlineKeyboardButton(text="5000 ₽ (+150 🎁)", callback_data="pay_5000_150"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="balance"))
    
    return builder.as_markup()


# Top Up Selection Keyboard (Inline)
def top_up_amount_keyboard() -> InlineKeyboardMarkup:
    """Create top up amount selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔒 Пополнение отключено", callback_data="disabled"))
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


# Promocode Keyboard (Inline)
def promocode_keyboard() -> InlineKeyboardMarkup:
    """Create promocode keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="balance"))
    
    return builder.as_markup()
