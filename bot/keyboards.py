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


# Artistic Styles Section Keyboards (Inline)

def artistic_styles_root_keyboard() -> InlineKeyboardMarkup:
    """Create artistic styles section keyboard with subsections"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="🎨 Художники", callback_data="as_artists"))
    builder.row(InlineKeyboardButton(text="✏️ Техника", callback_data="as_technique"))
    builder.row(InlineKeyboardButton(text="⚡ Комиксы", callback_data="as_comics"))
    builder.row(InlineKeyboardButton(text="🐰 Мультфильмы", callback_data="as_cartoons"))
    builder.row(InlineKeyboardButton(text="🌸 Аниме", callback_data="as_anime"))
    builder.row(InlineKeyboardButton(text="🧙 Фэнтези", callback_data="as_fantasy"))
    builder.row(InlineKeyboardButton(text="📸 Фотографы", callback_data="as_photographers"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_artists_keyboard() -> InlineKeyboardMarkup:
    """Create artists submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Vincent van Gogh", callback_data="as_style_van_gogh"))
    builder.row(InlineKeyboardButton(text="Claude Monet", callback_data="as_style_monet"))
    builder.row(InlineKeyboardButton(text="Pablo Picasso", callback_data="as_style_picasso"))
    builder.row(InlineKeyboardButton(text="Salvador Dalí", callback_data="as_style_dali"))

    builder.row(InlineKeyboardButton(text="💻 Цифровые художники", callback_data="as_artists_digital"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_digital_artists_keyboard() -> InlineKeyboardMarkup:
    """Create digital artists submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="Beeple (Mike Winkelmann)", callback_data="as_style_beeple"))
    builder.row(InlineKeyboardButton(text="Artgerm (Stanley Lau)", callback_data="as_style_artgerm"))
    builder.row(InlineKeyboardButton(text="Loish", callback_data="as_style_loish"))
    builder.row(InlineKeyboardButton(text="Ross Tran (RossDraws)", callback_data="as_style_ross_tran"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_artists"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_techniques_keyboard() -> InlineKeyboardMarkup:
    """Create techniques submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="🎨 Масляная живопись", callback_data="as_style_tech_oil"))
    builder.row(InlineKeyboardButton(text="💧 Акварель", callback_data="as_style_tech_watercolor"))
    builder.row(InlineKeyboardButton(text="🖌 Пастель", callback_data="as_style_tech_pastel"))
    builder.row(InlineKeyboardButton(text="✏️ Карандаш", callback_data="as_style_tech_pencil"))
    builder.row(InlineKeyboardButton(text="🖋 Чернила / тушь", callback_data="as_style_tech_ink"))
    builder.row(InlineKeyboardButton(text="💻 Цифровая живопись", callback_data="as_style_tech_digital_painting"))
    builder.row(InlineKeyboardButton(text="🧠 Концепт-арт", callback_data="as_style_tech_concept_art"))
    builder.row(InlineKeyboardButton(text="🎮 3D-рендер", callback_data="as_style_tech_3d_render"))
    builder.row(InlineKeyboardButton(text="📰 Гравюра / офорт", callback_data="as_style_tech_engraving"))
    builder.row(InlineKeyboardButton(text="🪵 Уголь", callback_data="as_style_tech_charcoal"))
    builder.row(InlineKeyboardButton(text="🖍 Маркеры", callback_data="as_style_tech_markers"))
    builder.row(InlineKeyboardButton(text="📐 Линейный арт", callback_data="as_style_tech_line_art"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_comics_keyboard() -> InlineKeyboardMarkup:
    """Create comics submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="💥 Jack Kirby (Classic Marvel)", callback_data="as_style_jack_kirby"))
    builder.row(InlineKeyboardButton(text="🌑 Frank Miller (Noir / Sin City)", callback_data="as_style_frank_miller"))
    builder.row(InlineKeyboardButton(text="🌌 Moebius (Jean Giraud)", callback_data="as_style_moebius"))
    builder.row(InlineKeyboardButton(text="⚡ Jim Lee (Modern DC / Marvel)", callback_data="as_style_jim_lee"))
    builder.row(InlineKeyboardButton(text="🎨 Alex Ross (Painterly Realism)", callback_data="as_style_alex_ross"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_cartoons_keyboard() -> InlineKeyboardMarkup:
    """Create cartoons submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="🏰 Disney Renaissance Style", callback_data="as_style_disney_renaissance"))
    builder.row(InlineKeyboardButton(text="🤖 Pixar Style", callback_data="as_style_pixar"))
    builder.row(InlineKeyboardButton(text="🐲 DreamWorks Style", callback_data="as_style_dreamworks"))
    builder.row(InlineKeyboardButton(text="⚔️ Genndy Tartakovsky", callback_data="as_style_genndy_tartakovsky"))
    builder.row(InlineKeyboardButton(text="🐰 Looney Tunes / Chuck Jones", callback_data="as_style_looney_tunes"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_anime_keyboard() -> InlineKeyboardMarkup:
    """Create anime submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="🌸 Makoto Shinkai Style", callback_data="as_style_makoto_shinkai"))
    builder.row(InlineKeyboardButton(text="🪽 Yoshitaka Amano Style", callback_data="as_style_yoshitaka_amano"))
    builder.row(InlineKeyboardButton(text="⚔️ Akihiko Yoshida Style", callback_data="as_style_akihiko_yoshida"))
    builder.row(InlineKeyboardButton(text="🌙 CLAMP Style", callback_data="as_style_clamp"))
    builder.row(InlineKeyboardButton(text="🍃 Studio Ghibli Style (Hayao Miyazaki)", callback_data="as_style_studio_ghibli"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_fantasy_keyboard() -> InlineKeyboardMarkup:
    """Create fantasy submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="⚔️ Frank Frazetta", callback_data="as_style_frank_frazetta"))
    builder.row(InlineKeyboardButton(text="🚀 Ralph McQuarrie", callback_data="as_style_ralph_mcquarrie"))
    builder.row(InlineKeyboardButton(text="🧙 Greg Rutkowski", callback_data="as_style_greg_rutkowski"))
    builder.row(InlineKeyboardButton(text="🪄 Magali Villeneuve", callback_data="as_style_magali_villeneuve"))
    builder.row(InlineKeyboardButton(text="🐉 Brom", callback_data="as_style_brom"))
    builder.row(InlineKeyboardButton(text="🔥 Wayne Barlowe", callback_data="as_style_wayne_barlowe"))
    builder.row(InlineKeyboardButton(text="🏰 John Blanche", callback_data="as_style_john_blanche"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")
    )

    return builder.as_markup()


def artistic_styles_photographers_keyboard() -> InlineKeyboardMarkup:
    """Create photographers submenu keyboard"""
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text="📸 Annie Leibovitz", callback_data="as_style_annie_leibovitz"))
    builder.row(InlineKeyboardButton(text="🌍 Steve McCurry", callback_data="as_style_steve_mccurry"))
    builder.row(InlineKeyboardButton(text="🖤 Peter Lindbergh", callback_data="as_style_peter_lindbergh"))
    builder.row(InlineKeyboardButton(text="⚡ Helmut Newton", callback_data="as_style_helmut_newton"))
    builder.row(InlineKeyboardButton(text="✨ Richard Avedon", callback_data="as_style_richard_avedon"))
    builder.row(InlineKeyboardButton(text="📸 Mario Testino", callback_data="as_style_mario_testino"))
    builder.row(InlineKeyboardButton(text="🌍 Sebastião Salgado", callback_data="as_style_sebastiao_salgado"))
    builder.row(InlineKeyboardButton(text="🕊 Dorothea Lange", callback_data="as_style_dorothea_lange"))
    builder.row(InlineKeyboardButton(text="🎭 Tim Walker", callback_data="as_style_tim_walker"))
    builder.row(InlineKeyboardButton(text="🏔 Ansel Adams", callback_data="as_style_ansel_adams"))

    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="as_root"),
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


# Change Appearance (Образ) Root Menu - Gender Selection
def appearance_short_hairstyles_keyboard() -> InlineKeyboardMarkup:
    """Create short hairstyles presets keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add hairstyle presets (2 per row)
    hairstyles = [
        ("h_short_pixie", "Пикси"),
        ("h_short_pixie_volume", "Пикси с объёмом"),
        ("h_short_bob", "Короткий боб"),
        ("h_short_french_bob", "Французский боб"),
        ("h_short_garcon", "Гарсон"),
        ("h_short_asymmetric", "Асимметричная"),
        ("h_short_textured", "Текстурная"),
        ("h_short_elongated", "Удлинённые пряди"),
        ("h_short_crown_volume", "Объём на макушке"),
    ]
    
    for i, (key, name) in enumerate(hairstyles):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_medium_hairstyles_keyboard() -> InlineKeyboardMarkup:
    """Create medium length hairstyles presets keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add hairstyle presets (2 per row)
    hairstyles = [
        ("h_medium_classic_bob", "Классический боб"),
        ("h_medium_lob", "Удлинённый боб (LOB)"),
        ("h_medium_carre", "Каре"),
        ("h_medium_carre_long", "Каре с удлинением"),
        ("h_medium_layered", "С слоями"),
        ("h_medium_shoulder", "До плеч"),
        ("h_medium_textured", "Текстурная"),
        ("h_medium_volume", "С объёмом"),
        ("h_medium_waves", "С волнами"),
    ]
    
    for i, (key, name) in enumerate(hairstyles):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_long_hairstyles_keyboard() -> InlineKeyboardMarkup:
    """Create long hairstyles presets keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add hairstyle presets (2 per row)
    hairstyles = [
        ("h_long_straight", "Прямые"),
        ("h_long_wavy", "Волнистые"),
        ("h_long_curly", "Кудрявые"),
        ("h_long_layered", "С слоями"),
        ("h_long_volume", "С объёмом"),
        ("h_long_sleek", "Гладкие"),
        ("h_long_natural", "Натуральная текстура"),
        ("h_long_soft_curls", "С локонами"),
    ]
    
    for i, (key, name) in enumerate(hairstyles):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_bangs_keyboard() -> InlineKeyboardMarkup:
    """Create bangs presets keyboard (can be added to any hairstyle)"""
    builder = InlineKeyboardBuilder()
    
    # Add bangs presets (2 per row)
    bangs = [
        ("h_bangs_straight", "Прямая"),
        ("h_bangs_side_swept", "Косая"),
        ("h_bangs_curtain", "Шторка"),
        ("h_bangs_choppy", "Рваная"),
        ("h_bangs_long", "Удлинённая"),
        ("h_bangs_airy", "Воздушная"),
    ]
    
    for i, (key, name) in enumerate(bangs):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_updo_keyboard() -> InlineKeyboardMarkup:
    """Create updo hairstyles presets keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add updo presets (2 per row)
    updos = [
        ("h_updo_low_bun", "Низкий пучок"),
        ("h_updo_high_bun", "Высокий пучок"),
        ("h_updo_low_ponytail", "Низкий хвост"),
        ("h_updo_high_ponytail", "Высокий хвост"),
        ("h_updo_slicked_back", "Гладкие"),
        ("h_updo_half_up", "Полусобранные"),
        ("h_updo_bun_with_framing", "Пучок с прядями"),
    ]
    
    for i, (key, name) in enumerate(updos):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_braids_keyboard() -> InlineKeyboardMarkup:
    """Create braids presets keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add braids presets (2 per row)
    braids = [
        ("h_braids_classic", "Классическая"),
        ("h_braids_french", "Французская"),
        ("h_braids_dutch", "Голландская"),
        ("h_braids_fishtail", "Рыбий хвост"),
        ("h_braids_crown", "Вокруг головы"),
        ("h_braids_two", "Две косы"),
        ("h_braids_loose_messy", "Небрежная"),
    ]
    
    for i, (key, name) in enumerate(braids):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_stylistic_keyboard() -> InlineKeyboardMarkup:
    """Create stylistic directions presets keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add stylistic presets (2 per row)
    stylistics = [
        ("h_style_natural", "Натуральный"),
        ("h_style_minimalism", "Минимализм"),
        ("h_style_romantic", "Романтический"),
        ("h_style_elegant", "Элегантный"),
        ("h_style_boho", "Бохо"),
        ("h_style_glamour", "Гламур"),
        ("h_style_retro", "Ретро"),
        ("h_style_modern", "Современный"),
        ("h_style_editorial", "Editorial"),
    ]
    
    for i, (key, name) in enumerate(stylistics):
        button = InlineKeyboardButton(text=name, callback_data=f"hairstyle_{key}")
        if i % 2 == 0:
            builder.row(button)
        else:
            builder.add(button)
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female_hair"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


def appearance_gender_keyboard() -> InlineKeyboardMarkup:
    """Create gender selection keyboard for appearance customization"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👨 Мужской", callback_data="appearance_male"))
    builder.row(InlineKeyboardButton(text="👩 Женский", callback_data="appearance_female"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Male Appearance Menu
def appearance_male_keyboard() -> InlineKeyboardMarkup:
    """Create male appearance menu"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💇 Прическа", callback_data="appearance_male_hair"))
    builder.row(InlineKeyboardButton(text="🧔 Борода, Усы", callback_data="appearance_male_beard"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_gender"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Female Appearance Menu
def appearance_female_keyboard() -> InlineKeyboardMarkup:
    """Create female appearance menu"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💇 Прически", callback_data="appearance_female_hair"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_gender"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()


# Female Hairstyles Categories Menu
def appearance_female_hairstyle_categories_keyboard() -> InlineKeyboardMarkup:
    """Create female hairstyle categories menu"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✂️ Короткие причёски", callback_data="appearance_female_hair_short"))
    builder.row(InlineKeyboardButton(text="🌊 Средняя длина волос", callback_data="appearance_female_hair_medium"))
    builder.row(InlineKeyboardButton(text="💁 Длинные волосы", callback_data="appearance_female_hair_long"))
    builder.row(InlineKeyboardButton(text="🪮 Чёлки", callback_data="appearance_female_hair_bangs"))
    builder.row(InlineKeyboardButton(text="🎀 Убранные волосы", callback_data="appearance_female_hair_updo"))
    builder.row(InlineKeyboardButton(text="🧵 Косы", callback_data="appearance_female_hair_braids"))
    builder.row(InlineKeyboardButton(text="✨ Стилистические направления", callback_data="appearance_female_hair_styles"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="appearance_female"))
    builder.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    
    return builder.as_markup()
