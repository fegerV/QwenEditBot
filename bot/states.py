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
    
    # Fitting room states (2 photo workflow)
    awaiting_first_fitting_photo = State()  # First photo (user with visible body)
    awaiting_second_fitting_photo = State()  # Second photo (clothing item)
    
    # Custom prompt states
    awaiting_custom_prompt = State()    # Ввод ручного промпта
    
    # Balance states
    checking_balance = State()
    awaiting_payment = State()
    selecting_payment_method = State()
    awaiting_promocode = State()
    
    # Profile states
    viewing_profile = State()
    viewing_payment_history = State()
    
    # Knowledge base states
    viewing_knowledge_base = State()
    
    # Job processing state
    processing_job = State()
