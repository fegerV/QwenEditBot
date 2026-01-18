# Подробное описание передачи задания с workflow в ComfyUI

## Общая информация

ComfyUI - это визуальный интерфейс для генерации изображений с помощью диффузионных моделей. Он работает на основе узлов (nodes), которые соединяются между собой для создания сложных рабочих процессов (workflows).

## Формат передачи workflow в ComfyUI

### Структура JSON-файла

Workflow в ComfyUI представляет собой JSON-объект, где ключами являются ID узлов (в виде строк), а значениями - объекты, описывающие каждый узел.

```json
{
  "ID_узла": {
    "inputs": {
      // входные параметры узла
    },
    "class_type": "Тип_узла",
    "_meta": {
      "title": "Название_узла"
    }
  }
}
```

### Пример структуры узла

```json
"41": {
  "inputs": {
    "image": "input_test.jpg"
  },
  "class_type": "LoadImage",
  "_meta": {
    "title": "Load Image"
  }
}
```

Где:
- `"41"` - ID узла (строка)
- `"inputs"` - объект с параметрами узла
- `"image"` - конкретный параметр узла (в данном случае - имя загружаемого файла)
- `"class_type"` - тип узла (LoadImage, KSampler, VAEDecode и т.д.)
- `"_meta"` - метаданные (опционально)

## Синтаксис и связи между узлами

### Связи между узлами

Связи между узлами создаются через массивы в полях inputs:

```json
"65": {
  "inputs": {
    "model": [
      "64",
      0
    ],
    "positive": [
      "70",
      0
    ],
    "negative": [
      "71",
      0
    ],
    "latent_image": [
      "75",
      0
    ]
  },
  "class_type": "KSampler",
  "_meta": {
    "title": "KSampler"
  }
}
```

Формат связи: `[ID_источника, индекс_выхода]`
- `"64"` - ID узла-источника
- `0` - индекс выхода (если узел имеет несколько выходов)

### Типичные параметры узлов

#### LoadImage
```json
"41": {
  "inputs": {
    "image": "имя_файла.jpg"
  },
  "class_type": "LoadImage",
  "_meta": {
    "title": "Load Image"
  }
}
```

#### KSampler
```json
"65": {
  "inputs": {
    "seed": 298021837955899,
    "steps": 4,
    "cfg": 1,
    "sampler_name": "euler",
    "scheduler": "simple",
    "denoise": 1,
    "model": ["64", 0],
    "positive": ["70", 0],
    "negative": ["71", 0],
    "latent_image": ["75", 0]
  },
  "class_type": "KSampler",
  "_meta": {
    "title": "KSampler"
  }
}
```

#### TextEncodeQwenImageEditPlus
```json
"68": {
  "inputs": {
    "prompt": "Convert to in the comic style, while preserving composition and character identity. remove the progress bar and watermarks",
    "clip": ["61", 0],
    "vae": ["10", 0],
    "image1": ["79", 0]
  },
  "class_type": "TextEncodeQwenImageEditPlus",
  "_meta": {
    "title": "TextEncodeQwenImageEditPlus (Positive)"
  }
}
```

## Отправка workflow в ComfyUI API

### Формат запроса

Для отправки workflow в ComfyUI используется HTTP POST-запрос к `/prompt` эндпоинту.

```json
{
  "prompt": {
    // здесь находится сам workflow JSON
  }
}
```

### Пример отправки через curl

```bash
curl -X POST http://127.0.0.1:8188/prompt \
  -H "Content-Type: application/json" \
  -d @path/to/wrapped_workflow.json
```

Где `wrapped_workflow.json` содержит:

```json
{
  "prompt": {
    // сам workflow
  }
}
```

### Реализация в коде (Python)

В проекте QwenEditBot используется следующий подход:

```python
async def send_workflow(self, workflow: Dict) -> str:
    """Send workflow to ComfyUI, return prompt_id"""
    url = f"{self.base_url}/prompt"
    
    try:
        # The workflow needs to be sent as the 'prompt' key in the JSON payload
        payload = {"prompt": workflow}
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.post(url, json=payload) as response:
                # обработка ответа
```

## Пример полного workflow

Вот фрагмент реального workflow из проекта:

```json
{
  "8": {
    "inputs": {
      "samples": [
        "65",
        0
      ],
      "vae": [
        "10",
        0
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "9": {
    "inputs": {
      "filename_prefix": "2511/test",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "10": {
    "inputs": {
      "vae_name": "qwen_image_vae.safetensors"
    },
    "class_type": "VAELoader",
    "_meta": {
      "title": "Load VAE"
    }
  }
}
```


### Ключевые особенности:

1. **Загрузка изображения**: Узел `LoadImage` (ID 41) указывает на конкретное имя файла
2. **Обработка изображения**: Используется специальная модель QwenImageEdit
3. **Масштабирование**: Узел `ImageScaleToTotalPixels` масштабирует изображение до заданного количества мегапикселей
4. **Текстовое описание**: Узлы `TextEncodeQwenImageEditPlus` принимают текстовый промпт для определения стиля обработки

## Процесс обработки задания

1. Изображение копируется в папку ввода ComfyUI
2. Создается workflow JSON с правильными именами файлов
3. Workflow оборачивается в {"prompt": ...} и отправляется на `/prompt`
4. Получаем prompt_id для отслеживания статуса
5. Ожидаем завершения задания, проверяя историю по `/history/{prompt_id}`
6. Загружаем результат по информации из истории
7. Сохраняем результат в выходную директорию

## Ошибки и их обработка

- `"No prompt provided"`: JSON не был обернут в `{"prompt": ...}` объект
- `"Invalid image file"`: Указанный файл изображения не существует в папке ввода ComfyUI
- `"Prompt outputs failed validation"`: Проблема с одним или несколькими узлами в workflow

## Заключение

ComfyUI использует графовую структуру для определения workflow, где каждый узел представляет собой операцию обработки изображения. Workflow передается в виде JSON-объекта, где связи между узлами определяются через массивы в полях inputs. Для вызова API workflow оборачивается в {"prompt": ...} и отправляется на соответствующий эндпоинт.