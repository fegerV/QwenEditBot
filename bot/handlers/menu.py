"""Menu handlers - main menu and navigation with 8 main sections"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from ..states import UserState
from ..keyboards import (
    edit_photo_submenu_keyboard,
    category_keyboard,
    main_menu_keyboard,
    main_menu_inline_keyboard,
    back_and_main_menu_keyboard,
    fitting_room_instructions_keyboard,
    profile_menu_keyboard,
    knowledge_base_keyboard,
    artistic_styles_root_keyboard,
    artistic_styles_artists_keyboard,
    artistic_styles_digital_artists_keyboard,
    artistic_styles_techniques_keyboard,
)
from ..utils import send_error_message

logger = logging.getLogger(__name__)

router = Router()


ARTISTIC_STYLE_PRESETS: dict[str, dict[str, str]] = {
    # Classic artists
    "as_style_van_gogh": {
        "name": "Vincent van Gogh",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply the artistic style of Vincent van Gogh,\n"
            "oil painting, expressive swirling brushstrokes,\n"
            "vibrant saturated colors,\n"
            "visible canvas texture.\n"
            "High quality, painterly result."
        ),
    },
    "as_style_monet": {
        "name": "Claude Monet",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply the artistic style of Claude Monet,\n"
            "impressionist painting,\n"
            "soft diffused light,\n"
            "pastel color palette,\n"
            "gentle brushstrokes.\n"
            "High quality, atmospheric result."
        ),
    },
    "as_style_picasso": {
        "name": "Pablo Picasso",
        "icon": "🎨",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "For portraits, loosely preserve facial features.\n"
            "Apply a cubist style inspired by Pablo Picasso,\n"
            "abstract geometric shapes,\n"
            "bold color blocks,\n"
            "fragmented forms.\n"
            "Artistic interpretation, coherent structure."
        ),
    },
    "as_style_dali": {
        "name": "Salvador Dalí",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply the surrealist style inspired by Salvador Dalí,\n"
            "dreamlike atmosphere,\n"
            "distorted reality elements,\n"
            "smooth painterly technique.\n"
            "High quality, surreal but coherent result."
        ),
    },

    # Digital artists
    "as_style_beeple": {
        "name": "Beeple (Mike Winkelmann)",
        "icon": "💻",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply a digital art style inspired by Beeple,\n"
            "futuristic and surreal elements,\n"
            "high-contrast lighting,\n"
            "detailed textures,\n"
            "modern digital aesthetic.\n"
            "High quality digital artwork"
        ),
    },
    "as_style_artgerm": {
        "name": "Artgerm (Stanley Lau)",
        "icon": "💻",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions exactly.\n"
            "Apply the semi-realistic digital art style of Artgerm,\n"
            "smooth painterly shading,\n"
            "clean detailed features,\n"
            "professional illustration quality.\n"
            "High quality, polished result."
        ),
    },
    "as_style_loish": {
        "name": "Loish",
        "icon": "💻",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply a soft colorful illustration style inspired by Loish,\n"
            "smooth gradients,\n"
            "gentle lighting,\n"
            "expressive but simplified forms.\n"
            "High quality illustration."
        ),
    },
    "as_style_ross_tran": {
        "name": "Ross Tran (RossDraws)",
        "icon": "💻",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply a vibrant stylized digital painting style inspired by Ross Tran (RossDraws),\n"
            "dynamic lighting,\n"
            "bold colors,\n"
            "energetic brushwork.\n"
            "High quality digital illustration."
        ),
    },

    # Techniques
    "as_style_tech_oil": {
        "name": "Масляная живопись",
        "icon": "🎨",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply oil painting technique,\n"
            "rich thick brushstrokes,\n"
            "deep saturated colors,\n"
            "visible canvas texture.\n"
            "High quality painterly result."
        ),
    },
    "as_style_tech_watercolor": {
        "name": "Акварель",
        "icon": "💧",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply watercolor painting technique,\n"
            "soft translucent washes,\n"
            "gentle color bleeding,\n"
            "visible paper texture.\n"
            "Light, atmospheric result."
        ),
    },
    "as_style_tech_pastel": {
        "name": "Пастель",
        "icon": "🖌",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply pastel drawing technique,\n"
            "soft chalk textures,\n"
            "smooth color transitions,\n"
            "matte finish.\n"
            "High quality illustration."
        ),
    },
    "as_style_tech_pencil": {
        "name": "Карандаш",
        "icon": "✏️",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply pencil drawing technique,\n"
            "graphite linework,\n"
            "hand-drawn shading,\n"
            "white paper background.\n"
            "Clean sketch style."
        ),
    },
    "as_style_tech_ink": {
        "name": "Чернила / тушь",
        "icon": "🖋",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply ink drawing technique,\n"
            "bold black lines,\n"
            "high contrast,\n"
            "hand-inked illustration style.\n"
            "Crisp, graphic result."
        ),
    },
    "as_style_tech_digital_painting": {
        "name": "Цифровая живопись",
        "icon": "💻",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity and proportions.\n"
            "Apply digital painting technique,\n"
            "smooth brushwork,\n"
            "detailed lighting,\n"
            "high-resolution textures.\n"
            "Professional digital artwork."
        ),
    },
    "as_style_tech_concept_art": {
        "name": "Концепт-арт",
        "icon": "🧠",
        "prompt": (
            "Preserve the original composition of the image.\n"
            "Apply concept art technique,\n"
            "cinematic lighting,\n"
            "dramatic atmosphere,\n"
            "detailed forms and environments.\n"
            "Professional illustration quality."
        ),
    },
    "as_style_tech_3d_render": {
        "name": "3D-рендер",
        "icon": "🎮",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply 3D render technique,\n"
            "realistic materials,\n"
            "studio lighting,\n"
            "high detail,\n"
            "photorealistic rendering.\n"
            "Clean, modern 3D result."
        ),
    },
    "as_style_tech_engraving": {
        "name": "Гравюра / офорт",
        "icon": "📰",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply engraving technique,\n"
            "fine linework,\n"
            "cross-hatching,\n"
            "vintage illustration style.\n"
            "High detail monochrome result."
        ),
    },
    "as_style_tech_charcoal": {
        "name": "Уголь",
        "icon": "🪵",
        "prompt": (
            "Preserve the original content and structure of the image.\n"
            "For portraits, preserve facial identity.\n"
            "Apply charcoal drawing technique,\n"
            "rough expressive strokes,\n"
            "deep shadows,\n"
            "textured paper.\n"
            "Dramatic monochrome result."
        ),
    },
    "as_style_tech_markers": {
        "name": "Маркеры",
        "icon": "🖍",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply marker illustration technique,\n"
            "bold saturated colors,\n"
            "visible strokes,\n"
            "graphic illustration style.\n"
            "Clean and vibrant result."
        ),
    },
    "as_style_tech_line_art": {
        "name": "Линейный арт",
        "icon": "📐",
        "prompt": (
            "Preserve the original structure of the image.\n"
            "Apply clean line art technique,\n"
            "precise outlines,\n"
            "minimal shading,\n"
            "illustration style.\n"
            "Sharp and minimal result."
        ),
    },
}


async def _start_art_style_flow(
    callback: types.CallbackQuery,
    state: FSMContext,
    style_key: str,
):
    style = ARTISTIC_STYLE_PRESETS.get(style_key)
    if not style:
        await callback.answer("Стиль не найден", show_alert=True)
        return

    await state.update_data(
        selected_preset={
            "name": style["name"],
            "icon": style.get("icon", "🎨"),
            "price": 30,
        },
        prompt=style["prompt"],
    )
    await state.set_state(UserState.awaiting_image_for_preset)

    from ..keyboards import cancel_keyboard

    icon = style.get("icon", "")
    name = style.get("name", "")
    display_name = f"{icon} {name}".strip()

    await callback.message.edit_text(
        f"✅ Выбран стиль: {display_name}\n\n"
        f"Стоимость: 30 баллов\n\n"
        "📸 Теперь загрузите фото для обработки:",
        reply_markup=cancel_keyboard(),
    )

    await callback.answer()


# ===== NEW MENU STRUCTURE - 8 MAIN SECTIONS =====

# 1. 🎨 Художественные стили
@router.message(UserState.main_menu, F.text == "🎨 Художественные стили")
async def btn_artistic_styles(message: types.Message, state: FSMContext):
    """Handle 'Художественные стили' button"""
    try:
        await message.answer(
            "🎨 Художественные стили\n\n"
            "Выберите подраздел:\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=artistic_styles_root_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in artistic_styles button: {e}")
        await send_error_message(message)


# 2. 🧝‍ Изменить образ
@router.message(UserState.main_menu, F.text == "🧝‍ Изменить образ")
async def btn_change_appearance(message: types.Message, state: FSMContext):
    """Handle 'Изменить образ' button - disabled for testing"""
    try:
        await message.answer(
            "🧝‍ Изменить образ\n\n"
            "Кнопка временно не активна. Подразделы находятся в разработке.\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=back_and_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in change_appearance button: {e}")
        await send_error_message(message)


# 3. 👕 ПРИМЕРОЧНАЯ (Fitting room with 2 photos)
@router.message(UserState.main_menu, F.text == "👕 ПРИМЕРОЧНАЯ")
async def btn_fitting_room(message: types.Message, state: FSMContext):
    """Handle 'ПРИМЕРОЧНАЯ' button - 2 photo workflow"""
    try:
        instructions = (
            "👕 ПРИМЕРОЧНАЯ\n\n"
            "Здесь вы можете примерить любую одежду на свое фото!\n\n"
            "📸 Вам понадобится 2 фото:\n\n"
            "1️⃣ Фото с ВАМИ\n"
            "Подойдет:\n"
            "• фото по пояс или во весь рост\n"
            "• обычное фото с телефона\n"
            "• можно в зеркале, дома, на улице\n"
            "❗ Главное — чтобы было хорошо видно тело.\n\n"
            "2️⃣ Фото ОДЕЖДЫ\n"
            "Просто:\n"
            "• откройте любой маркетплейс (Ozon, Wildberries, Lamoda и т.д.)\n"
            "• скачайте фото понравившейся одежды\n"
            "• платье, костюм, куртка, рубашка — что угодно\n\n"
            "💡 После загрузки 2 фото, нейросеть создаст реалистичное фото в новой одежде!\n\n"
            "Стоимость: 30 баллов"
        )
        
        await message.answer(
            instructions,
            reply_markup=fitting_room_instructions_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in fitting_room button: {e}")
        await send_error_message(message)


@router.callback_query(F.data == "start_fitting")
async def callback_start_fitting(callback: types.CallbackQuery, state: FSMContext):
    """Start fitting room workflow - ask for first photo"""
    try:
        await state.set_state(UserState.awaiting_first_fitting_photo)
        
        await callback.message.edit_text(
            "📸 Загрузите ПЕРВОЕ фото — фото с ВАМИ (по пояс или во весь рост)\n\n"
            "Убедитесь, что хорошо видно тело.",
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in start_fitting callback: {e}")
        await callback.answer("Произошла ошибка")


@router.message(UserState.awaiting_first_fitting_photo, F.photo)
async def handle_first_fitting_photo(message: types.Message, state: FSMContext):
    """Handle first photo in fitting room workflow"""
    try:
        # Store first photo
        photo_id = message.photo[-1].file_id
        await state.update_data(first_photo_id=photo_id)
        
        # Move to second photo state
        await state.set_state(UserState.awaiting_second_fitting_photo)
        
        await message.answer(
            "✅ Первое фото получено!\n\n"
            "📸 Теперь загрузите ВТОРОЕ фото — фото ОДЕЖДЫ\n\n"
            "Это может быть скриншот с маркетплейса или фото одежды.",
            reply_markup=back_and_main_menu_keyboard("back_to_menu")
        )
    except Exception as e:
        logger.error(f"Error handling first fitting photo: {e}")
        await send_error_message(message)


@router.message(UserState.awaiting_second_fitting_photo, F.photo)
async def handle_second_fitting_photo(message: types.Message, state: FSMContext):
    """Handle second photo and create job with special prompt"""
    try:
        from ..main import api_client
        
        # Store second photo
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        first_photo_id = data.get('first_photo_id')
        
        if not first_photo_id:
            await message.answer("❌ Ошибка: не найдено первое фото. Начните сначала.")
            await state.clear()
            await state.set_state(UserState.main_menu)
            return
        
        # Special prompt for fitting room
        fitting_prompt = (
            "Use photo 1 as the primary subject reference. "
            "Preserve the face, facial features, skin texture, head shape and overall identity from photo 1 exactly. "
            "Use photo 2 as clothing reference only. "
            "Take only the clothing item from photo 2. "
            "Do not transfer the person, face, body shape, pose, hair or background from photo 2. "
            "Dress the person from photo 1 in the clothing from photo 2. "
            "Ensure the clothing fits naturally to the body proportions of the person from photo 1. "
            "Maintain realistic fabric folds, texture, proportions and lighting. "
            "Do not change the hairstyle, face, facial expression or body shape from photo 1. "
            "Photorealistic result, high realism, natural lighting."
        )
        
        # Create job with both photos
        # Note: This requires backend support for multiple photos
        # For now, we'll use the first photo as main and include clothing photo ID
        job_data = await api_client.create_job(
            user_id=message.from_user.id,
            image_id=first_photo_id,
            prompt=fitting_prompt,
            metadata={"second_photo_id": photo_id, "workflow_type": "fitting_room"}
        )
        
        if job_data:
            await message.answer(
                "✅ Фото принято! Начинаем примерку...\n\n"
                "Результат будет готов в течение нескольких минут.\n\n"
                "С вашего баланса списано 30 баллов.",
                reply_markup=main_menu_keyboard()
            )
            await state.clear()
            await state.set_state(UserState.main_menu)
        else:
            await message.answer("❌ Ошибка создания задания. Попробуйте позже.", reply_markup=main_menu_keyboard())
            await state.clear()
            await state.set_state(UserState.main_menu)
            
    except Exception as e:
        logger.error(f"Error handling second fitting photo: {e}")
        await send_error_message(message)
        await state.clear()
        await state.set_state(UserState.main_menu)


# 4. ✨ Редактировать фото (existing functionality)
@router.message(UserState.main_menu, F.text == "✨ Редактировать фото")
async def btn_edit_photo(message: types.Message, state: FSMContext):
    """Handle 'Редактировать фото' button"""
    try:
        await state.set_state(UserState.select_preset_category)
        
        await message.answer(
            "Как вы хотите редактировать фото?",
            reply_markup=edit_photo_submenu_keyboard()  # Already has Back and Main Menu buttons
        )
        
    except Exception as e:
        logger.error(f"Error in edit_photo button: {e}")
        await send_error_message(message)


# 5. ✍️ Свой промпт (existing functionality)
@router.message(UserState.main_menu, F.text == "✍️ Свой промпт")
async def btn_custom_prompt(message: types.Message, state: FSMContext):
    """Handle 'Свой промпт' button"""
    try:
        from .custom_prompt import start_custom_prompt
        await start_custom_prompt(message, state)
        
    except Exception as e:
        logger.error(f"Error in custom_prompt button: {e}")
        await send_error_message(message)


# 6. 📚 База знаний
@router.message(UserState.main_menu, F.text == "📚 База знаний")
async def btn_knowledge_base(message: types.Message, state: FSMContext):
    """Handle 'База знаний' button"""
    try:
        welcome_text = (
            "📚 База знаний\n\n"
            "Здесь будут полезные статьи и гайды по:\n"
            "• Промптам и стилям редактирования\n"
            "• Подбору одежды и fashion\n"
            "• Художественным техникам\n"
            "• Фотосъемке для нейросетей\n\n"
            "Скоро добавим первые материалы!"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=knowledge_base_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in knowledge_base button: {e}")
        await send_error_message(message)


# 7. 👩 Профиль (enhanced balance functionality)
@router.message(UserState.main_menu, F.text == "👩 Профиль")
async def btn_profile(message: types.Message, state: FSMContext):
    """Handle 'Профиль' button - show balance, payment history, promo codes"""
    try:
        from ..main import api_client
        
        # Get user balance from backend
        balance = await api_client.get_balance(message.from_user.id)
        
        if balance is None:
            balance = 0
        
        profile_text = (
            f"👩 Ваш Профиль\n\n"
            f"💰 Баланс: {balance} баллов\n\n"
            f"Стоимость генерации 1 фото: 30 баллов\n"
            f"Курс: 1 балл = 1 рубль\n\n"
            f"📊 Статистика:\n"
            f"• Приветственный бонус: 100 баллов\n"
            f"• Еженедельный бонус: 10 баллов (каждую пятницу)\n"
        )
        
        await message.answer(
            profile_text,
            reply_markup=profile_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error in profile button: {e}")
        await send_error_message(message)


# 8. ℹ️ Помощь (existing functionality)
@router.message(UserState.main_menu, F.text == "ℹ️ Помощь")
async def btn_help(message: types.Message):
    """Handle 'Помощь' button"""
    try:
        from .help import show_help
        await show_help(message)
        
    except Exception as e:
        logger.error(f"Error in help button: {e}")
        await send_error_message(message)


# ===== CALLBACK HANDLERS FOR NAVIGATION =====


# Inline keyboard callbacks
@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'back to menu' callback"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
        
        await callback.message.edit_text(
            "Главное меню:",
            reply_markup=main_menu_inline_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back_to_menu callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "back_to_balance")
async def callback_back_to_balance(callback: types.CallbackQuery):
    """Handle 'back to balance' callback"""
    try:
        from .balance import callback_balance
        await callback_balance(callback)
        
    except Exception as e:
        logger.error(f"Error in back_to_balance callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_preset")
async def callback_edit_preset(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit with preset' callback"""
    try:
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=category_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in edit_preset callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "edit_custom")
async def callback_edit_custom(callback: types.CallbackQuery, state: FSMContext):
    """Handle 'edit with custom prompt' callback"""
    try:
        from .custom_prompt import start_custom_prompt
        await start_custom_prompt(callback.message, state, is_callback=True)
        
        await callback.message.delete()
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in edit_custom callback: {e}")
        await callback.answer("Произошла ошибка")


# ===== NEW CALLBACK HANDLERS FOR DISABLED FEATURES =====

@router.callback_query(F.data == "category_artistic")
async def callback_artistic_styles(callback: types.CallbackQuery, state: FSMContext):
    """Handle artistic styles callback"""
    try:
        await callback.message.edit_text(
            "🎨 Художественные стили\n\n"
            "Выберите подраздел:\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=artistic_styles_root_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles callback: {e}")
        await callback.answer("Произошла ошибка")


# Artistic styles section navigation

@router.callback_query(F.data == "as_root")
async def callback_artistic_styles_root(callback: types.CallbackQuery, state: FSMContext):
    """Show artistic styles root menu"""
    try:
        await callback.message.edit_text(
            "🎨 Художественные стили\n\n"
            "Выберите подраздел:\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=artistic_styles_root_keyboard(),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles_root callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "as_artists")
async def callback_artistic_styles_artists(callback: types.CallbackQuery, state: FSMContext):
    """Show artists submenu"""
    try:
        await callback.message.edit_text(
            "🎨 Художники\n\nВыберите художника:",
            reply_markup=artistic_styles_artists_keyboard(),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles_artists callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "as_artists_digital")
async def callback_artistic_styles_digital_artists(callback: types.CallbackQuery, state: FSMContext):
    """Show digital artists submenu"""
    try:
        await callback.message.edit_text(
            "💻 Цифровые художники\n\nВыберите художника:",
            reply_markup=artistic_styles_digital_artists_keyboard(),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles_digital_artists callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "as_technique")
async def callback_artistic_styles_technique(callback: types.CallbackQuery, state: FSMContext):
    """Show techniques submenu"""
    try:
        await callback.message.edit_text(
            "✏️ Техника\n\nВыберите технику:",
            reply_markup=artistic_styles_techniques_keyboard(),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles_technique callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.in_({"as_comics", "as_cartoons", "as_anime", "as_fantasy", "as_photographers"}))
async def callback_artistic_styles_placeholder(callback: types.CallbackQuery, state: FSMContext):
    """Show placeholder message for not-yet-implemented subsections"""
    try:
        titles = {
            "as_comics": "⚡ Комиксы",
            "as_cartoons": "🐰 Мультфильмы",
            "as_anime": "🌸 Аниме",
            "as_fantasy": "🧙 Фэнтези",
            "as_photographers": "📸 Фотографы",
        }
        title = titles.get(callback.data, "Раздел")

        await callback.message.edit_text(
            f"{title}\n\n"
            "Раздел в разработке. Подразделы будут добавлены позже.",
            reply_markup=back_and_main_menu_keyboard("as_root"),
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles_placeholder callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data.startswith("as_style_"))
async def callback_artistic_style_selected(callback: types.CallbackQuery, state: FSMContext):
    """Select artistic style (artist/technique) and switch to photo upload"""
    try:
        await _start_art_style_flow(callback, state, callback.data)
    except Exception as e:
        logger.error(f"Error in artistic style selection: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "change_appearance")
async def callback_change_appearance(callback: types.CallbackQuery, state: FSMContext):
    """Handle change appearance callback"""
    try:
        await callback.message.edit_text(
            "🧝‍ Изменить образ\n\n"
            "Кнопка временно не активна. Подразделы находятся в разработке.\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=main_menu_inline_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in change_appearance callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "knowledge_base")
async def callback_knowledge_base(callback: types.CallbackQuery, state: FSMContext):
    """Handle knowledge base callback"""
    try:
        welcome_text = (
            "📚 База знаний\n\n"
            "Здесь будут полезные статьи и гайды по:\n"
            "• Промптам и стилям редактирования\n"
            "• Подбору одежды и fashion\n"
            "• Художественным техникам\n"
            "• Фотосъемке для нейросетей\n\n"
            "Скоро добавим первые материалы!"
        )
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=knowledge_base_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in knowledge_base callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "profile")
async def callback_profile(callback: types.CallbackQuery, state: FSMContext):
    """Handle profile callback"""
    try:
        from ..main import api_client
        
        # Get user balance from backend
        balance = await api_client.get_balance(callback.from_user.id)
        
        if balance is None:
            balance = 0
        
        profile_text = (
            f"👩 Ваш Профиль\n\n"
            f"💰 Баланс: {balance} баллов\n\n"
            f"Стоимость генерации 1 фото: 30 баллов\n"
            f"Курс: 1 балл = 1 рубль\n\n"
            f"📊 Статистика:\n"
            f"• Приветственный бонус: 100 баллов\n"
            f"• Еженедельный бонус: 10 баллов (каждую пятницу)\n"
        )
        
        await callback.message.edit_text(
            profile_text,
            reply_markup=profile_menu_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in profile callback: {e}")
        await callback.answer("Произошла ошибка")


# Knowledge base subcategories (placeholders)
@router.callback_query(F.data == "kb_prompts")
async def callback_kb_prompts(callback: types.CallbackQuery):
    """Handle knowledge base - prompts section"""
    try:
        await callback.answer("📖 Раздел 'Промпты и стили' в разработке", show_alert=True)
    except Exception as e:
        logger.error(f"Error in kb_prompts callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "kb_fashion")
async def callback_kb_fashion(callback: types.CallbackQuery):
    """Handle knowledge base - fashion section"""
    try:
        await callback.answer("👗 Раздел 'Одежда и fashion' в разработке", show_alert=True)
    except Exception as e:
        logger.error(f"Error in kb_fashion callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "kb_art")
async def callback_kb_art(callback: types.CallbackQuery):
    """Handle knowledge base - art techniques section"""
    try:
        await callback.answer("🎭 Раздел 'Художественные техники' в разработке", show_alert=True)
    except Exception as e:
        logger.error(f"Error in kb_art callback: {e}")
        await callback.answer("Произошла ошибка")


@router.callback_query(F.data == "disabled")
async def callback_disabled_feature(callback: types.CallbackQuery):
    """Handle disabled feature callback"""
    try:
        await callback.answer("🔒 Эта функция временно отключена для тестирования", show_alert=True)
    except Exception as e:
        logger.error(f"Error handling disabled feature: {e}")
        await callback.answer("Произошла ошибка")
