from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """FSM states for user interaction flow"""
    
    # Main menu state
    main_menu = State()
    
    # Preset selection states
    select_preset_category = State()  # Выбор: Стили/Освещение/Оформление
    select_preset = State()            # Выбор конкретного пресета
    
    # Image upload states
    awaiting_image_for_preset = State()  # После выбора пресета - загрузка фото
    awaiting_image_for_custom = State()  # После ручного промпта - загрузка фото
    
    # Custom prompt states
    awaiting_custom_prompt = State()    # Ввод ручного промпта
    
    # Balance states
    checking_balance = State()
    awaiting_payment = State()
    
    # Job processing state
    processing_job = State()
