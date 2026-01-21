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
    knowledge_base_keyboard
)
from ..utils import send_error_message

logger = logging.getLogger(__name__)

router = Router()


# ===== NEW MENU STRUCTURE - 8 MAIN SECTIONS =====

# 1. 🎨 Художественные стили
@router.message(UserState.main_menu, F.text == "🎨 Художественные стили")
async def btn_artistic_styles(message: types.Message, state: FSMContext):
    """Handle 'Художественные стили' button - currently disabled"""
    try:
        await message.answer(
            "🎨 Художественные стили\n\n"
            "Данный раздел находится в разработке. Подразделы будут добавлены позже.\n\n"
            "Стоимость генерации 1 фото: 30 баллов\n"
            "Ваш баланс можно проверить в разделе 👩 Профиль",
            reply_markup=back_and_main_menu_keyboard()
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
            "Данный раздел находится в разработке. Подразделы будут добавлены позже.\n\n"
            "Стоимость генерации 1 фото: 30 баллов",
            reply_markup=main_menu_inline_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in artistic_styles callback: {e}")
        await callback.answer("Произошла ошибка")


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
