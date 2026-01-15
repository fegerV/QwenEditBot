# 🚀 YuKassa Quick Start Guide - Production Ready

## 📌 Цель
Привести YuKassa интеграцию в **production-ready** состояние с полной документацией для быстрого старта.

---

## 📋 Checklist для быстрого старта

### **Шаг 1: Получить ключи YuKassa** (5 минут)

1. Зарегистрируйтесь на https://yookassa.ru
2. Создайте ТЕСТОВЫЙ магазин (для разработки)
3. В личном кабинете найдите:
   - **Идентификатор магазина** (Shop ID) → `YUKASSA_SHOP_ID`
   - **Секретный ключ** (API ключ) → `YUKASSA_API_KEY`
   - **Вебхук секрет** → `YUKASSA_WEBHOOK_SECRET`
4. Скопируйте в `.env` файл

### **Шаг 2: Конфигурировать backend** (2 минуты)

```bash
cd backend
cp .env.example .env
```

**Заполнить в .env**:
```env
# YuKassa Configuration
YUKASSA_SHOP_ID="your_shop_id_from_dashboard"
YUKASSA_API_KEY="live_your_api_key_from_dashboard"  
YUKASSA_WEBHOOK_SECRET="your_webhook_secret"

# Payment Settings
PAYMENT_MIN_AMOUNT=1           # Минимум 1 рубль
PAYMENT_MAX_AMOUNT=10000       # Максимум 10000 рублей
PAYMENT_RETURN_URL="https://t.me/YourBotUsername"
POINTS_PER_RUBLE=100           # 1 рубль = 100 поинтов

# Weekly Bonus
WEEKLY_BONUS_ENABLED=true
WEEKLY_BONUS_AMOUNT=10
WEEKLY_BONUS_DAY=4              # 0=Пн, 4=Пт
WEEKLY_BONUS_TIME="20:00"       # UTC
```

### **Шаг 3: Запустить backend** (1 минута)

```bash
cd backend
pip install -r requirements.txt
python run.py
# Backend доступен на http://localhost:8000
# Swagger UI на http://localhost:8000/docs
```

### **Шаг 4: Запустить Bot** (1 минута)

```bash
cd bot
cp .env.example .env
# Заполнить BOT_TOKEN в bot/.env
pip install -r requirements.txt
python run.py
```

### **Шаг 5: Тестировать платеж** (2 минуты)

1. Откройте Telegram и напишите боту `/start`
2. Нажмите "➕ Пополнить"
3. Выберите сумму (например, 100₽)
4. Откроется ссылка на YuKassa

**ТЕСТОВАЯ карта для оплаты**:
```
Номер карты: 5555555555554444
Месяц/Год: любой из будущего (например, 12/25)
CVC: любое 3-значное число
Статус: Успешный платеж
```

5. После оплаты вернетесь в бота
6. Проверьте баланс: должно быть +10000 поинтов (100₽ × 100)

---

## ✅ Проверка текущей реализации

### **Файлы, которые должны быть**:

```
✅ backend/app/services/yukassa.py
   - class YuKassaClient
   - create_payment() → POST /v3/payments
   - get_payment() → GET /v3/payments/{id}
   - verify_signature() → HMAC-SHA256 проверка

✅ backend/app/services/payment_service.py
   - class PaymentService
   - create_payment() → создание платежа через YuKassa
   - handle_webhook() → обработка вебхука
   - refund_payment() → возврат денег

✅ backend/app/api/payments.py
   - POST /api/payments/create → создать платеж
   - GET /api/payments/{id} → статус платежа
   - GET /api/payments/user/{id} → история платежей
   - POST /api/webhooks/yukassa → webhook от YuKassa

✅ backend/app/services/scheduler.py
   - class WeeklyBonusScheduler
   - Еженедельный бонус (пятница 20:00 UTC)

✅ backend/app/models.py
   - class Payment
   - class PaymentStatus (pending/succeeded/failed/cancelled)
   - class PaymentType (payment/weekly_bonus/refund)

✅ bot/handlers/payments.py
   - Выбор суммы пополнения
   - Создание платежа через API
   - Проверка статуса платежа каждые 5 сек
   - Уведомления об успехе/ошибке

✅ bot/keyboards.py
   - "➕ Пополнить" кнопка в главном меню
   - "📜 История" кнопка в балансе

✅ bot/services/api_client.py
   - create_payment()
   - get_payment()
   - get_user_payments()
```

---

## 🔧 Если что-то не работает

### **Ошибка 1: "YuKassa integration not configured"**
```python
# Проблема: YUKASSA_SHOP_ID или YUKASSA_API_KEY не установлены
# Решение:
cd backend
cat .env  # Проверить что переменные есть
# Или перезагрузить backend
python run.py
```

### **Ошибка 2: "Invalid signature" при webhook**
```python
# Проблема: YUKASSA_WEBHOOK_SECRET не совпадает
# Решение:
# 1. В YuKassa личном кабинете перейти в Webhook настройки
# 2. Скопировать SECRET точно из панели
# 3. Вставить в .env
# 4. Перезагрузить backend
```

### **Ошибка 3: "CORS error" при запросе из бота**
```python
# Проблема: Backend не разрешает запросы с бота
# Решение: CORS уже настроен в main.py
# allow_origins=["*"]  # Разрешены все источники
# Если все равно ошибка, проверить BACKEND_URL в bot/.env
```

### **Ошибка 4: Платеж создался, но вебхук не пришел**
```python
# Проблема: YuKassa не может отправить вебхук на localhost
# Решение: Для production используйте реальный URL
# Для development используйте локальное тестирование или ngrok

# Локальное тестирование:
python test_api.py  # Тест платежа без webhook
```

---

## 📚 API Endpoints

### **Создать платеж**
```bash
curl -X POST http://localhost:8000/api/payments/create \
  -d "user_id=1&amount=100"

# Response:
{
  "payment_id": 1,
  "yukassa_payment_id": "23d93cac-000f-5000-...",
  "status": "pending",
  "confirmation_url": "https://yoomoney.ru/api-pages/v2/...",
  "amount": 100.00,
  "created_at": "2024-01-13T..."
}
```

### **Проверить статус**
```bash
curl http://localhost:8000/api/payments/1

# Response:
{
  "payment_id": 1,
  "status": "succeeded",
  "amount": 100.00,
  "paid_at": "2024-01-13T..."
}
```

### **История платежей**
```bash
curl http://localhost:8000/api/payments/user/1

# Response:
{
  "payments": [
    {"id": 1, "amount": 100, "status": "succeeded", "type": "payment"},
    {"id": 2, "amount": 10, "status": "succeeded", "type": "weekly_bonus"},
    ...
  ],
  "total": 2
}
```

---

## 🧪 Тестирование платежей

### **Unit тесты**
```bash
cd backend
pytest tests/test_payments.py -v
```

### **Integration тесты**
```bash
python test_api.py        # Тест всех endpoints
python test_phase4_complete.py  # Проверка Phase 4
```

### **Manual тесты**
1. Откройте http://localhost:8000/docs (Swagger UI)
2. Тестируйте endpoints прямо в браузере
3. Или используйте Postman/curl

---

## 📊 Поток платежа (диаграмма)

```
┌─────────────────────────────────────────────────────┐
│  User в Telegram: "➕ Пополнить"                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Bot: "Выберите сумму"                              │
│  [100₽] [250₽] [500₽] [1000₽]                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼ User: "250₽"
┌─────────────────────────────────────────────────────┐
│  Bot отправляет Backend:                            │
│  POST /api/payments/create?user_id=123&amount=250   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Backend создает платеж в YuKassa:                  │
│  POST https://api.yookassa.ru/v3/payments           │
│  {                                                   │
│    "amount": {"value": "250.00", "currency": "RUB"}│
│    "capture": true,                                 │
│    "confirmation": {"type": "redirect"}             │
│  }                                                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼ YuKassa returns confirmation_url
┌─────────────────────────────────────────────────────┐
│  Bot отправляет User:                               │
│  "Нажмите сюда для оплаты: [ссылка]"                │
│  https://yoomoney.ru/api-pages/v2/...               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼ User переходит по ссылке
┌─────────────────────────────────────────────────────┐
│  YuKassa Checkout (выбор способа оплаты):           │
│  • Карта Visa/Mastercard                            │
│  • СБП (быстро)                                     │
│  • Яндекс.Касса                                     │
│  • Другие способы                                   │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼ User платит
┌─────────────────────────────────────────────────────┐
│  YuKassa: Платеж успешен!                           │
│  status: "succeeded"                                │
│  ✅ Деньги на счете                                 │
└────────────────┬────────────────────────────────────┘
                 │
                 ├─→ Вебхук → Backend
                 │   POST /api/webhooks/yukassa
                 │   {"type": "payment.succeeded", ...}
                 │
                 └─→ User вернулся в бота
                     (нажал "Вернуться в бот")
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Backend обработал платеж:                          │
│  ✅ Payment.status = "succeeded"                    │
│  ✅ User.balance += 25000 поинтов (250₽ × 100)     │
│  ✅ Создана запись в БД                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Bot получает уведомление:                          │
│  "✅ Платеж принят! +25000 поинтов"                │
│  Показывает новый баланс                            │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Что делать дальше

### **Для development**:
1. ✅ Зарегистрируйте ТЕСТОВЫЙ магазин на YuKassa
2. ✅ Получите Shop ID и API ключ
3. ✅ Запустите backend + bot
4. ✅ Протестируйте с тестовой картой 5555555555554444
5. ✅ Проверьте что баланс зачисляется

### **Для production**:
1. Создайте настоящий магазин на YuKassa
2. Получите production Shop ID и API ключ
3. Обновите .env файл
4. Разверните на сервер с реальным URL
5. Настройте webhook в личном кабинете YuKassa
6. Протестируйте реальный платеж на небольшую сумму

### **Опциональные улучшения**:
1. Добавить email уведомления при платежах
2. Добавить панель администратора для просмотра платежей
3. Интегрировать с аналитикой (сколько заработано, etc)

---

## 📞 Поддержка YuKassa

Если что-то не работает:
- 📖 Документация: https://yookassa.ru/developers
- 💬 Форум: https://yookassa.ru/support
- 📧 Email: support@yookassa.ru
- 🔍 API тестер: https://yookassa.ru/api-playground

---

## ✨ Итого

**QwenEditBot с YuKassa это**:
- ✅ Надежная система платежей
- ✅ Полная автоматизация (вебхуки, webhook)
- ✅ Еженедельные бонусы для пользователей
- ✅ История всех платежей
- ✅ Поддержка множества способов оплаты
- ✅ Безопасная обработка платежей

**ETA до первого платежа**: ~10 минут! 🚀
