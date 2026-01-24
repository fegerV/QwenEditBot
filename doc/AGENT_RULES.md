# Правила для агента QwenEditBot

Этот документ описывает набор правил и стандартов разработки, которых должен придерживаться агент при работе над проектом QwenEditBot.

## 1. SOLID и архитектура

### 1.1 Разделение ответственности (Single Responsibility Principle)

Проект разделён на три независимых сервиса:

- **Backend** (FastAPI)
  - Ответственность: бизнес-логика (баланс, платежи, управление пресетами, job-ы)
  - Интеграция: SQLite (SQLAlchemy), Redis, YooKassa, ComfyUI, Telegram-уведомления
  - Эндпоинты: `/api/users/`, `/api/jobs/`, `/api/payments/`, `/api/balance/`, `/api/presets/`, `/webhooks/`

- **Bot** (aiogram 3.x)
  - Ответственность: UI/UX, управление состояниями пользователя (FSM)
  - Не содержит бизнес-логику; все операции делегирует Backend через `BackendAPIClient`
  - Обработчики: `handlers/*` организованы по функциональности (menu, presets, payments, balance, и т.д.)

- **Worker** (asyncio)
  - Ответственность: асинхронная обработка заданий (jobs) из Redis-очереди
  - Управление ресурсами: GPU-lock (файловая блокировка), мониторинг ComfyUI
  - Жизненный цикл: прочитать job → взять GPU-lock → выполнить workflow → отправить результат в Telegram

### 1.2 Зависимости и направление потока

```
Bot ──HTTP─→ Backend ←──webhook─── YooKassa
              ↑         ↓
           Redis     SQLite
              ↑
          Worker ──HTTP→ ComfyUI
              ↓
         Telegram API
```

**Правила:**
- Backend не зависит от Bot; Bot инициирует.
- Worker читает из Redis (Backend туда пишет); не общается с Bot напрямую.
- Webhook YooKassa идёт в Backend (NOT Bot), Backend обновляет баланс.

### 1.3 Расширяемость

При добавлении новых функций:
- **Новый способ оплаты** (например, СБП): добавить логику в `backend/app/services/payment_service.py` (или отдельный сервис), не трогать основные эндпоинты.
- **Новый пресет/workflow**: добавить в конфиг или БД, используя существующий механизм `presets.py`.
- **Новый workflow (ComfyUI)**: добавить JSON в `worker/workflows/`, обновить `workflows/*.py` (builder).
- **Новый обработчик в боте**: создать отдельный handler в `bot/handlers/`, зарегистрировать в роутере.

## 2. Стиль кода и наименование

### 2.1 Язык и синтаксис

- **Язык**: английский для всего кода (переменные, функции, классы, комментарии).
- **Классы**: `CamelCase` (например, `BalanceService`, `BackendAPIClient`).
- **Функции, переменные**: `snake_case` (например, `fetch_user()`, `user_balance`).
- **Константы**: `UPPER_SNAKE_CASE` (например, `ADMIN_IDS`, `MAX_RETRIES`).

### 2.2 Type hints и аннотации

**Требуется везде** (Python 3.9+):

```python
# Функции
async def fetch_user(user_id: int) -> User | None:
    """Fetch user from database by ID."""
    pass

# Переменные в функциях (если неочевидно)
users: list[User] = []
balance: float = 0.0

# Аргументы с типом
def calculate_bonus(amount_rubles: int, bonus_percent: int = 10) -> int:
    return (amount_rubles * bonus_percent) // 100
```

### 2.3 Функции и методы

- **Длина**: максимум 20–30 строк, идеально 10–15.
- **Ответственность**: одна функция = одна задача.
- **Примеры плохого**:
  ```python
  async def process_everything(user_id):
      # Это делает 5 вещей: проверку, расчёт, сохранение, уведомление, логирование
      pass
  ```
- **Пример хорошего**:
  ```python
  async def deduct_balance(user_id: int, amount: int) -> bool:
      """Deduct amount from user balance. Returns True if successful."""
      user = await get_user(user_id)
      if user.balance < amount:
          return False
      user.balance -= amount
      await user.save()
      return True
  ```

### 2.4 Docstrings (Google-стиль)

**Для публичных функций и классов**:

```python
def calculate_job_cost(preset_id: str, region: str) -> int:
    """Calculate cost of image processing job based on preset.
    
    Args:
        preset_id: Unique preset identifier.
        region: Geographic region for pricing adjustments.
    
    Returns:
        Cost in rubles.
    
    Raises:
        PresetNotFoundError: If preset doesn't exist.
    """
    pass

class BalanceService:
    """Service for managing user balance and transactions.
    
    Handles balance deductions, replenishments, and historical tracking.
    Ensures all operations go through single source of truth.
    """
    pass
```

## 3. Конфигурация и окружение

### 3.1 Принцип 12 Factor App

Все параметры окружения читаются через файл `.env`:
- Backend: [`backend/.env`](../backend/.env) → [`backend/app/config.py`](../backend/app/config.py)
- Bot: [`bot/.env`](../bot/.env) → [`bot/config.py`](../bot/config.py)
- Worker: [`worker/.env`](../worker/.env) → [`worker/config.py`](../worker/config.py)

**Примеры параметров:**
```env
# Backend
DATABASE_URL=sqlite:///./test.db
REDIS_URL=redis://localhost:6379
ADMIN_IDS=12345,67890
UNLIMITED_PROCESSING=False
COMFYUI_URL=http://localhost:8188
YUKASSA_SHOP_ID=123456
YUKASSA_API_KEY=test_abc123

# Bot
BOT_TOKEN=123456:ABC-xyz
BACKEND_URL=http://localhost:8000
INITIAL_BALANCE=100

# Worker
COMFYUI_HEALTH_CHECK_URL=http://localhost:8188/system_stats
GPU_LOCK_PATH=/tmp/gpu.lock
```

### 3.2 Чувствительные данные

**Никогда**:
- ❌ Коммитить `.env` файлы
- ❌ Хардкодить токены, ключи, пароли в коде
- ❌ Логировать полные credentials

**Всегда**:
- ✅ Хранить credentials в `.env` или переменных окружения
- ✅ Использовать `settings` объект для доступа к конфигам
- ✅ При необходимости логировать только неполные версии (например, первые 4 символа токена)

## 4. Ошибки и логирование

### 4.1 Логирование везде

```python
import logging

logger = logging.getLogger(__name__)

async def process_job(job_id: str):
    try:
        logger.info(f"Processing job {job_id}")
        # ... логика ...
        logger.debug(f"Job {job_id} processed successfully")
    except ComfyUIError as e:
        logger.error(f"ComfyUI error for job {job_id}: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing job {job_id}")
        raise
```

### 4.2 Обработка исключений

- **Backend**: вернуть HTTP error (400, 404, 500) с понятным сообщением.
- **Bot**: отправить юзеру сообщение об ошибке, логировать в бэкэнде.
- **Worker**: залогировать, пометить job как failed, отправить уведомление юзеру.

**Пример в Bot:**
```python
try:
    # ... операция ...
except Exception as e:
    logger.error(f"Error: {e}")
    await message.answer(
        "Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
    )
```

### 4.3 Контекст в логах

Всегда логируй **контекст**:
- `user_id` или `user_name` (для операций с пользователем)
- `job_id` (для работы с job-ами)
- `preset_id` (для пресетов)
- `payment_id` (для платежей)

```python
logger.info(f"User {user_id} created job {job_id} with preset {preset_id}")
logger.warning(f"Job {job_id} failed after {retry_count} retries")
```

## 5. Тестирование

### 5.1 Unit-тесты

Создавать для:
- `backend/app/services/` (balance, payment, comfyui_client)
- `backend/app/schemas.py` (валидация)
- `worker/services/` (retry strategy, gpu lock)

```python
# tests/backend/test_balance_service.py
import pytest
from backend.app.services.balance import BalanceService

@pytest.mark.asyncio
async def test_deduct_balance_success():
    service = BalanceService()
    result = await service.deduct_balance(user_id=1, amount=10)
    assert result is True

@pytest.mark.asyncio
async def test_deduct_balance_insufficient():
    service = BalanceService()
    result = await service.deduct_balance(user_id=1, amount=999999)
    assert result is False
```

### 5.2 Integration-тесты

Для API эндпоинтов:
```python
# tests/backend/test_api.py
@pytest.mark.asyncio
async def test_create_job_endpoint(client):
    response = await client.post(
        "/api/jobs/",
        json={"user_id": 1, "preset_id": "test", "image_url": "..."}
    )
    assert response.status_code == 201
    assert "job_id" in response.json()
```

### 5.3 Мокирование

Mock Redis, ComfyUI и внешние API в тестах:
```python
@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def mock_comfyui_client(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr("worker.services.comfyui_client.ComfyUIClient", mock)
    return mock
```

## 6. Баланс и платежи

### 6.1 Балансовые операции

**Правило**: все операции **только через `BalanceService`**, никогда напрямую в БД.

```python
# ✅ Правильно
balance_service = BalanceService()
await balance_service.deduct_balance(user_id, amount)

# ❌ Неправильно
user.balance -= amount
await user.save()
```

Это обеспечивает:
- Консистентность логики (проверки, ограничения)
- Возможность логирования
- Возможность добавления side effects (уведомления, аналитика)

### 6.2 YooKassa webhook обработка

В `backend/app/api/webhooks.py`:

```python
@router.post("/yukassa/notification")
async def yukassa_notification(request: Request, payment_service: PaymentService):
    """Handle YooKassa payment notification."""
    # 1. Получить тело запроса
    body = await request.body()
    
    # 2. Проверить HMAC подпись
    if not payment_service.verify_hmac(body, request.headers.get("...signature...")):
        logger.warning("Invalid YooKassa HMAC signature")
        return {"status": "error"}
    
    # 3. Обработать платёж (идемпотентно)
    event = await request.json()
    payment_id = event["object"]["id"]
    
    # Используй idempotency_key или уникальное поле для идемпотентности
    result = await payment_service.process_payment(payment_id, event)
    
    return {"status": "success"}
```

### 6.3 Идемпотентность

Webhook может быть отправлен несколько раз → не дублировать операции:

```python
async def process_payment(payment_id: str, event: dict) -> bool:
    # Проверить, уже ли обработан этот платёж
    existing = await db.get_payment_by_id(payment_id)
    if existing and existing.status == "confirmed":
        logger.info(f"Payment {payment_id} already processed, skipping")
        return True
    
    # Обработать...
    return True
```

## 7. FSM и Bot handlers

### 7.1 Иерархия состояний

Состояния определены в [`bot/states.py`](../bot/states.py):

```python
class UserState(StatesGroup):
    main_menu = State()  # Главное меню
    select_preset_category = State()  # Выбор категории пресета
    awaiting_image_for_preset = State()  # Загрузка фото для пресета
    awaiting_custom_prompt = State()  # Ввод кастомного промпта
    viewing_profile = State()  # Просмотр профиля
    # ... и т.д.
```

### 7.2 Правила для обработчиков

**Одна функция = один переход или одно состояние:**

```python
# ✅ Правильно: обработчик для одного кнопки/коллбэка
@router.callback_query(F.data == "top_up")
async def handle_top_up(callback: CallbackQuery, state: FSMContext):
    """Show top-up options."""
    await state.set_state(UserState.awaiting_payment)
    # ... отправить клавиатуру ...

# ❌ Неправильно: обработчик для всех платежей и профиля
@router.callback_query(F.data.startswith("pay_") | F.data == "profile")
async def handle_everything(callback: CallbackQuery):
    pass  # Слишком много логики
```

### 7.3 Callback answer()

Всегда отвечай на `callback_query`:

```python
@router.callback_query(F.data == "my_action")
async def handle_action(callback: CallbackQuery, state: FSMContext):
    try:
        # ... логика ...
        await callback.answer()  # Просто закрыть spinning indicator
        
        # Или с сообщением
        await callback.answer("✅ Выполнено!", show_alert=False)
        
        # Или с модальным окном
        await callback.answer("❌ Ошибка!", show_alert=True)
    except Exception as e:
        logger.error(f"Error: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
```

### 7.4 Навигация ("Назад" / "Главное меню")

Всегда предусмотреть возврат:

```python
# В клавиатуре
def my_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu"))
    return builder.as_markup()

# В обработчике
@router.callback_query(F.data == "back_to_menu")
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(UserState.main_menu)
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu_inline_keyboard()
    )
    await callback.answer()
```

### 7.5 Обработка текстовых сообщений в состояниях

```python
@router.message(StateFilter(UserState.awaiting_custom_prompt))
async def handle_custom_prompt_input(message: Message, state: FSMContext):
    """User entered custom prompt."""
    prompt = message.text
    
    # Валидация
    if not prompt or len(prompt) > 500:
        await message.answer("Промпт должен быть от 1 до 500 символов")
        return
    
    # Логика
    state_data = await state.get_data()
    image_path = state_data["image_path"]
    
    # Создать job
    await create_job_with_custom_prompt(...)
    
    # Вернуться в меню
    await state.clear()
    await state.set_state(UserState.main_menu)
    await message.answer("✅ Задание создано!", reply_markup=main_menu_keyboard())
```

## 8. ComfyUI и Worker

### 8.1 Workflow и JSON

ComfyUI workflow хранится в `worker/workflows/qwen_edit_2511.json`:

```json
{
  "1": {"class_type": "LoadImage", "inputs": {"image": "..."}},
  "2": {"class_type": "QwenEditModel", "inputs": {"image": [1, 0], "prompt": "..."}},
  "3": {"class_type": "SaveImage", "inputs": {"images": [2, 0]}}
}
```

**Правило**: никогда не редактировать JSON вручную для каждого job. Использовать builder:

```python
# worker/workflows/qwen_edit_2511.py
class QwenEditWorkflowBuilder:
    def build(self, image_path: str, prompt: str) -> dict:
        """Build ComfyUI workflow JSON."""
        workflow = load_template("qwen_edit_2511.json")
        # ... модифицировать workflow ...
        return workflow
```

### 8.2 GPU Lock

Файловая блокировка перед запуском job:

```python
from worker.gpu.lock import GPULock

async def process_job(job_id: str):
    lock = GPULock(lock_path="/tmp/gpu.lock")
    
    try:
        # Ждём, пока освободится GPU
        async with lock.acquire():
            logger.info(f"GPU lock acquired for job {job_id}")
            # Запустить ComfyUI workflow...
    except TimeoutError:
        logger.error(f"Could not acquire GPU lock for job {job_id}")
        # Retry или пометить как failed
```

### 8.3 Retry Strategy

Экспоненциальная задержка при ошибках:

```python
# worker/retry/strategy.py
class RetryStrategy:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute(self, func, *args, **kwargs):
        """Execute function with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt+1} failed, retrying in {delay}s")
                await asyncio.sleep(delay)
```

### 8.4 ComfyUI Health Check

Перед запуском job проверить, живой ли ComfyUI:

```python
async def is_comfyui_ready(self) -> bool:
    """Check if ComfyUI is running and ready."""
    try:
        response = await self.client.get(
            f"{self.base_url}/system_stats",
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"ComfyUI health check failed: {e}")
        return False

async def process_job_with_health_check(job_id: str):
    if not await self.is_comfyui_ready():
        logger.error(f"ComfyUI not ready for job {job_id}")
        # Retry позже
        return False
    
    # Запустить job...
```

## 9. Примеры: добавление новой функции

### Пример 1: Добавить новый пресет

1. **Backend**: добавить пресет в БД или конфиг:
   ```python
   # backend/app/models.py
   presets = [
       {"id": "new_style", "name": "New Style", "prompt": "..."},
   ]
   ```

2. **Bot**: использовать существующий механизм выбора пресета.

3. **Worker**: если новый workflow, добавить JSON в `worker/workflows/`.

### Пример 2: Добавить новый способ оплаты

1. **Backend**: создать новый payment provider:
   ```python
   # backend/app/services/payment_providers.py
   class SBPPaymentProvider:
       async def create_payment(self, amount: int) -> dict:
           """Create SBP payment."""
           pass
   ```

2. **Backend**: обновить `PaymentService`:
   ```python
   async def create_payment(self, payment_method: str, amount: int) -> dict:
       if payment_method == "sbp":
           return await self.sbp_provider.create_payment(amount)
       # ... другие методы
   ```

3. **Bot**: добавить кнопку выбора способа оплаты:
   ```python
   # bot/keyboards.py
   def payment_method_keyboard() -> InlineKeyboardMarkup:
       builder = InlineKeyboardBuilder()
       builder.row(InlineKeyboardButton(text="💳 Карта", callback_data="pay_card"))
       builder.add(InlineKeyboardButton(text="🏦 СБП", callback_data="pay_sbp"))
       return builder.as_markup()
   ```

---

## Резюме

Следуя этим правилам, код останется:
- **Читаемым**: понятная структура, хорошие имена, тайп-хинты.
- **Поддерживаемым**: разделение ответственности, тесты, логирование.
- **Расширяемым**: легко добавлять новые функции без рефакторинга основного кода.
- **Безопасным**: обработка ошибок, валидация, конфиденциальность данных.
