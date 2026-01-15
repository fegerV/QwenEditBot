"""Preset handlers - showing and selecting presets"""

import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from ..states import UserState
from ..keyboards import category_keyboard, presets_keyboard
from ..utils import send_error_message
from ..services import BackendAPIClient

logger = logging.getLogger(__name__)

router = Router()


# Category selection handlers
@router.callback_query(F.data.startswith("category_"))
async def callback_category(callback: types.CallbackQuery, state: FSMContext):
    """Handle category selection callback"""
    try:
        # Import api_client from main module
        from ..main import api_client
        
        category = callback.data.split("_")[1]
        
        # Update state
        await state.set_state(UserState.select_preset)
        await state.update_data(category=category)
        
        # Show presets
        await show_presets_by_category(callback.message, state, category, api_client, is_callback=True)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in category callback: {e}")
        await callback.answer("Произошла ошибка")


async def show_presets_by_category(
    message: types.Message,
    state: FSMContext,
    category: str,
    api_client = None,
    is_callback: bool = False
):
    """Show presets for a specific category"""
    try:
        # Get presets from backend
        if api_client is None:
            from ..main import api_client as global_api_client
            api_client = global_api_client
        
        presets = await api_client.get_presets(category=category)
        
        if not presets:
            text = f"Пресеты в категории {category} не найдены."
        else:
            # Determine category title
            category_titles = {
                "styles": "🎨 Художественные стили",
                "portrait": "🧑 Портреты",
                "product": "📦 Товары",
                "lighting": "💡 Освещение",
                "animation": "🎬 Комиксы и анимация",
                "enhancement": "✨ Улучшение"
            }
            title = category_titles.get(category, f"Категория: {category}")
            
            text = f"{title}\n\nВыберите пресет:"
        
        keyboard = presets_keyboard(presets)
        
        if is_callback:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing presets: {e}")
        if not is_callback:
            await send_error_message(message)


# Preset selection handlers
@router.callback_query(F.data.startswith("preset_"))
async def callback_preset_selected(callback: types.CallbackQuery, state: FSMContext):
    """Handle preset selection callback"""
    try:
        # Import api_client from main module
        from ..main import api_client
        
        preset_id = int(callback.data.split("_")[1])
        
        # Get preset details
        presets = await api_client.get_presets()
        selected_preset = None
        
        for preset in presets:
            if preset.get('id') == preset_id:
                selected_preset = preset
                break
        
        if not selected_preset:
            await callback.answer("Пресет не найден", show_alert=True)
            return
        
        # Save preset data to state
        await state.update_data(
            selected_preset=selected_preset,
            prompt=selected_preset.get("prompt")  # ← АВТОМАТИЧЕСКИ ПОДСТАВЛЯЕТСЯ ПРОМПТ!
        )
        
        # Move to image upload state
        await state.set_state(UserState.awaiting_image_for_preset)
        
        # Ask for image
        icon = selected_preset.get('icon', '📷')
        preset_name = selected_preset.get('name', 'Без названия')
        cost = selected_preset.get('price', 30)
        
        text = (
            f"✅ Выбран пресет: {icon} {preset_name}\n\n"
            f"Стоимость: {cost} баллов\n\n"
            f"📸 Теперь загрузите фото для обработки:"
        )
        
        from ..keyboards import cancel_keyboard
        await callback.message.edit_text(
            text,
            reply_markup=cancel_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in preset callback: {e}")
        await callback.answer("Произошла ошибка при выборе пресета", show_alert=True)


@router.callback_query(F.data == "back_to_edit")
async def callback_back_to_edit(callback: types.CallbackQuery, state: FSMContext):
    """Handle back to edit menu callback"""
    try:
        await state.set_state(UserState.select_preset_category)
        
        from ..keyboards import category_keyboard
        await callback.message.edit_text(
            "Выберите категорию:",
            reply_markup=category_keyboard()
        )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in back_to_edit callback: {e}")
        await callback.answer("Произошла ошибка")


# Cancel handler
@router.callback_query(F.data == "cancel", StateFilter(UserState.awaiting_image_for_preset))
async def callback_cancel_preset(callback: types.CallbackQuery, state: FSMContext):
    """Handle cancel when waiting for image"""
    try:
        await state.clear()
        await state.set_state(UserState.main_menu)
         
        from ..keyboards import main_menu_inline_keyboard
        await callback.message.edit_text(
            "Операция отменена. Вы в главном меню.",
            reply_markup=main_menu_inline_keyboard()
        )
         
        await callback.answer()
         
    except Exception as e:
        logger.error(f"Error in cancel callback: {e}")
        await callback.answer("Произошла ошибка")
