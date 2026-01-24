# Руководство по файлам базы данных

## Обзор

В проекте QwenEditBot существуют два файла базы данных SQLite:
- `C:/QwenEditBot/backend/qwen.db`

## Какой файл использовать

**Основной файл базы данных**: `C:/QwenEditBot/backend/qwen.db`

Этот файл используется текущей версией приложения, как указано в:
- `backend/app/config.py`
- `backend/alembic.ini`
- `backend/.env`
- Документации

**Устаревший файл**: `qwen.db` (в корне проекта) - удален

Этот файл является устаревшим и не используется текущей версией приложения.

## Рекомендации

1. Используйте `C:/QwenEditBot/backend/qwen.db` для работы с текущим приложением
2. Файл `qwen.db` из корня проекта был удален, чтобы избежать путаницы
3. При миграции данных убедитесь, что вы работаете с правильным файлом базы данных

## Проверка содержимого базы данных

Для проверки содержимого основной базы данных используйте:

```bash
# Проверить структуру и данные
sqlite3 C:/QwenEditBot/backend/qwen.db ".tables"
sqlite3 C:/QwenEditBot/backend/qwen.db "SELECT COUNT(*) FROM users;"
sqlite3 C:/QwenEditBot/backend/qwen.db "SELECT COUNT(*) FROM jobs;"
sqlite3 C:/QwenEditBot/backend/qwen.db "SELECT COUNT(*) FROM payments;"
```

## Миграции

При выполнении миграций система будет использовать файл `C:/QwenEditBot/backend/qwen.db` как указано в конфигурации Alembic.