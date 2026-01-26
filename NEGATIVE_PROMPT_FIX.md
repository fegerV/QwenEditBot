# Исправление проблемы с Negative Prompt

## Проблема

Один и тот же промпт работает по-разному в боте и в ComfyUI в браузере:
- **В боте:** приходят фото с одетыми лифчиками и трусиками
- **В браузере ComfyUI:** тот же промпт генерирует без одежды

## Причина

В файле `worker/workflows/qwen_edit_2511.py` на строке 108 negative prompt был пустым:

```python
"69": {
    "inputs": {
        "prompt": "",  # ← ПРОБЛЕМА: пустой negative prompt
        ...
    },
    ...
}
```

В браузере ComfyUI, вероятно, используется какой-то negative prompt, который предотвращает появление одежды. Без negative prompt модель может добавлять нежелательные элементы (одежду) в изображение.

## Решение

Добавлена настройка `QWEN_EDIT_NEGATIVE_PROMPT` в конфигурацию worker'а, которая позволяет задать negative prompt через переменную окружения.

### Изменения в коде:

1. **`worker/config.py`** - добавлена настройка:
```python
QWEN_EDIT_NEGATIVE_PROMPT: str = Field("", env="QWEN_EDIT_NEGATIVE_PROMPT")
```

2. **`worker/workflows/qwen_edit_2511.py`** - обновлен workflow:
```python
"69": {
    "inputs": {
        "prompt": settings.QWEN_EDIT_NEGATIVE_PROMPT,  # ← Теперь использует настройку
        ...
    },
    ...
}
```

### Настройка через .env файл

Добавьте в файл `worker/.env` (или `.env` в корне проекта, если используется общий файл):

```env
QWEN_EDIT_NEGATIVE_PROMPT=clothing, underwear, bra, panties, lingerie, swimsuit, bikini, nsfw
```

Или более мягкий вариант:

```env
QWEN_EDIT_NEGATIVE_PROMPT=underwear, bra, panties
```

### Рекомендуемые значения

Для предотвращения появления одежды можно использовать:

**Строгий вариант:**
```
clothing, underwear, bra, panties, lingerie, swimsuit, bikini, nsfw, nude, naked
```

**Мягкий вариант (только нижнее белье):**
```
underwear, bra, panties, lingerie
```

**Минимальный вариант:**
```
underwear
```

## Как проверить

1. Добавьте `QWEN_EDIT_NEGATIVE_PROMPT` в `.env` файл worker'а
2. Перезапустите worker
3. Отправьте тот же промпт через бота
4. Проверьте, что результат соответствует ожиданиям (без одежды)

## Примечание

Если в браузере ComfyUI используется другой negative prompt, скопируйте его значение в настройку `QWEN_EDIT_NEGATIVE_PROMPT` для обеспечения одинакового поведения.

## Связанные файлы

- `worker/config.py` - конфигурация worker'а
- `worker/workflows/qwen_edit_2511.py` - построение workflow для ComfyUI
- `worker/.env` - файл с переменными окружения (создайте, если его нет)
