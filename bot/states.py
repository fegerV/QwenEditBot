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
    awaiting_image_for_custom = State()  # После выбора «Свой промпт» - загрузка фото
    awaiting_custom_photo_confirmation = State()  # Подтверждение загруженного фото перед вводом промпта

    # Fitting room states (2 photo workflow)
    awaiting_first_fitting_photo = State()  # First photo (user with visible body)
    awaiting_second_fitting_photo = State()  # Second photo (clothing item)

    # Custom prompt states
    selecting_custom_prompt_type = State()  # Выбор типа: 1 фото или 2 фото
    awaiting_custom_prompt = State()    # Ввод ручного промпта (после подтверждения фото для 1 фото)
    awaiting_first_custom_photo_2 = State()  # Первое фото для промпта с 2 фото
    awaiting_second_custom_photo_2 = State()  # Второе фото для промпта с 2 фото
    awaiting_custom_prompt_2_photos = State()  # Ввод промпта после загрузки 2 фото

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
