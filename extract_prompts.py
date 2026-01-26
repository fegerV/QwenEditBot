#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для извлечения всех промптов из кодовой базы
и создания документации
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def extract_presets_from_database() -> List[Dict]:
    """Извлечь промпты из database.py (seed данные)"""
    presets = []
    
    try:
        db_file = Path(__file__).parent / "backend" / "app" / "database.py"
        content = db_file.read_text(encoding='utf-8')
        
        # Найти секцию presets_data
        pattern = r'presets_data = \[(.*?)\]'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            presets_text = match.group(1)
            # Извлечь отдельные пресеты
            preset_pattern = r'\{"category":\s*"([^"]+)",\s*"name":\s*"([^"]+)",\s*"icon":\s*"([^"]+)",\s*"prompt":\s*"([^"]+)",\s*"order_index":\s*(\d+)\}'
            for match in re.finditer(preset_pattern, presets_text):
                presets.append({
                    "category": match.group(1),
                    "name": match.group(2),
                    "icon": match.group(3),
                    "prompt": match.group(4),
                    "order_index": int(match.group(5)),
                    "source": "database.py (seed presets)"
                })
    except Exception as e:
        print(f"Ошибка при извлечении из database.py: {e}", file=sys.stderr)
    
    return presets


def extract_prompts_from_menu() -> List[Dict]:
    """Извлечь все промпты из menu.py"""
    prompts = []
    
    try:
        menu_file = Path(__file__).parent / "bot" / "handlers" / "menu.py"
        content = menu_file.read_text(encoding='utf-8')
        
        # Более простой подход: найти все блоки с "prompt": ( и извлечь контекст
        # Ищем паттерн: "key": { ... "name": "...", ... "icon": "...", ... "prompt": (...)}
        
        # Найти все вхождения "prompt": (
        prompt_positions = []
        for match in re.finditer(r'"prompt":\s*\(', content):
            prompt_positions.append(match.start())
        
        # Для каждого промпта найти начало блока (ключ) и извлечь данные
        for prompt_pos in prompt_positions:
            # Найти начало блока - ищем "key": { перед промптом
            before_prompt = content[:prompt_pos]
            
            # Найти последний "key": { перед промптом
            key_pattern = r'"([^"]+)":\s*\{'
            key_matches = list(re.finditer(key_pattern, before_prompt))
            
            if not key_matches:
                continue
            
            # Берем последний найденный ключ (ближайший к промпту)
            key_match = key_matches[-1]
            key = key_match.group(1)
            block_start = key_match.start()
            
            # Найти конец блока - следующая закрывающая скобка на том же уровне
            block_content = content[block_start:prompt_pos + 10000]  # Достаточно большой кусок
            
            # Извлечь name и icon из блока
            name_match = re.search(r'"name":\s*"([^"]+)"', block_content)
            icon_match = re.search(r'"icon":\s*"([^"]+)"', block_content)
            price_match = re.search(r'"price":\s*(\d+)', block_content)
            
            if not name_match or not icon_match:
                continue
            
            name = name_match.group(1)
            icon = icon_match.group(1)
            price = int(price_match.group(1)) if price_match else 30
            
            # Извлечь сам промпт - найти закрывающую скобку для prompt
            prompt_start = prompt_pos + len('"prompt": (')
            # Найти соответствующую закрывающую скобку
            depth = 1
            prompt_end = prompt_start
            for i, char in enumerate(content[prompt_start:], start=prompt_start):
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                    if depth == 0:
                        prompt_end = i
                        break
            
            prompt_text = content[prompt_start:prompt_end]
            
            # Очистить промпт - убрать кавычки и лишние пробелы, но сохранить структуру
            prompt = re.sub(r'\n\s*"', '\n', prompt_text)  # Заменить перенос строки + кавычку на просто перенос
            prompt = re.sub(r'"\s*\n', '\n', prompt)  # Заменить кавычку + перенос на просто перенос
            prompt = re.sub(r'\n\s+', '\n', prompt)  # Убрать лишние пробелы в начале строк
            prompt = re.sub(r'\n{3,}', '\n\n', prompt)  # Убрать множественные переносы
            prompt = prompt.strip()
            
            # Определить категорию по контексту - найти название словаря
            before_block = content[:block_start]
            category_match = re.search(r'([A-Z_]+_PRESETS):\s*dict', before_block)
            category = category_match.group(1).replace("_PRESETS", "").lower() if category_match else "unknown"
            
            prompts.append({
                "key": key,
                "name": name,
                "icon": icon,
                "price": price,
                "prompt": prompt,
                "category": category,
                "source": "menu.py"
            })
                
    except Exception as e:
        print(f"Ошибка при извлечении из menu.py: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    
    return prompts


def extract_fitting_room_prompt() -> Dict:
    """Извлечь промпт для fitting room"""
    try:
        menu_file = Path(__file__).parent / "bot" / "handlers" / "menu.py"
        content = menu_file.read_text(encoding='utf-8')
        
        # Найти fitting_prompt
        pattern = r'fitting_prompt\s*=\s*\((.*?)\)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            prompt_lines = match.group(1)
            prompt = re.sub(r'\n\s*"', ' ', prompt_lines)
            prompt = re.sub(r'"\s*\n', ' ', prompt)
            prompt = re.sub(r'\s+', ' ', prompt).strip()
            
            return {
                "name": "Fitting Room (Примерочная)",
                "icon": "👔",
                "prompt": prompt,
                "category": "special",
                "source": "menu.py (fitting room)"
            }
    except Exception as e:
        print(f"Ошибка при извлечении fitting room промпта: {e}", file=sys.stderr)
    
    return None


def generate_documentation(presets: List[Dict], menu_prompts: List[Dict], fitting_prompt: Dict = None) -> str:
    """Сгенерировать документацию в формате Markdown"""
    
    doc = []
    doc.append("# Описание всех промптов\n")
    doc.append("Этот документ содержит описание всех промптов, используемых в системе.\n")
    doc.append(f"**Дата создания:** {Path(__file__).stat().st_mtime}\n")
    doc.append(f"**Всего промптов:** {len(presets) + len(menu_prompts) + (1 if fitting_prompt else 0)}\n")
    
    # 1. Промпты из базы данных (seed presets)
    doc.append("\n## 1. Промпты из базы данных (Seed Presets)\n")
    doc.append("Эти промпты загружаются в базу данных при первой инициализации.\n")
    
    # Группировать по категориям
    categories = {}
    for preset in presets:
        cat = preset.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(preset)
    
    for category in sorted(categories.keys()):
        doc.append(f"\n### Категория: {category}\n")
        for preset in sorted(categories[category], key=lambda x: x.get("order_index", 0)):
            doc.append(f"#### {preset.get('icon', '')} {preset.get('name', 'Unknown')}\n")
            doc.append(f"**Промпт:**\n```\n{preset.get('prompt', '')}\n```\n")
            doc.append(f"**Источник:** {preset.get('source', 'unknown')}\n")
            doc.append(f"**Порядок:** {preset.get('order_index', 0)}\n\n")
    
    # 2. Промпты из menu.py
    doc.append("\n## 2. Промпты из menu.py\n")
    doc.append("Эти промпты определены в коде и используются для различных функций бота.\n")
    
    # Группировать по категориям
    menu_categories = {}
    for prompt in menu_prompts:
        cat = prompt.get("category", "other")
        if cat not in menu_categories:
            menu_categories[cat] = []
        menu_categories[cat].append(prompt)
    
    for category in sorted(menu_categories.keys()):
        doc.append(f"\n### Категория: {category}\n")
        for prompt in sorted(menu_categories[category], key=lambda x: x.get("name", "")):
            doc.append(f"#### {prompt.get('icon', '')} {prompt.get('name', 'Unknown')}\n")
            doc.append(f"**Ключ:** `{prompt.get('key', 'unknown')}`\n")
            doc.append(f"**Цена:** {prompt.get('price', 30)} баллов\n")
            doc.append(f"**Промпт:**\n```\n{prompt.get('prompt', '')}\n```\n")
            doc.append(f"**Источник:** {prompt.get('source', 'unknown')}\n\n")
    
    # 3. Специальные промпты
    if fitting_prompt:
        doc.append("\n## 3. Специальные промпты\n")
        doc.append(f"### {fitting_prompt.get('icon', '')} {fitting_prompt.get('name', 'Unknown')}\n")
        doc.append(f"**Промпт:**\n```\n{fitting_prompt.get('prompt', '')}\n```\n")
        doc.append(f"**Источник:** {fitting_prompt.get('source', 'unknown')}\n\n")
    
    # 4. Кастомные промпты
    doc.append("\n## 4. Кастомные промпты пользователей\n")
    doc.append("Пользователи могут создавать свои собственные промпты через функцию \"✍️ Свой промпт\".\n")
    doc.append("Эти промпты хранятся в базе данных в таблице `jobs` и не имеют предопределенных шаблонов.\n")
    doc.append("Для просмотра кастомных промптов используйте скрипт `view_custom_prompts.py`.\n")
    
    # Статистика
    doc.append("\n## Статистика\n")
    doc.append(f"- **Промпты из базы данных (устаревшие):** {len(presets)}\n")
    doc.append(f"- **Промпты из menu.py (основные):** {len(menu_prompts)}\n")
    doc.append(f"- **Специальные промпты:** {1 if fitting_prompt else 0}\n")
    doc.append(f"- **Всего предопределенных промптов:** {len(presets) + len(menu_prompts) + (1 if fitting_prompt else 0)}\n")
    doc.append(f"\n**Примечание:** Основная функциональность использует промпты из `menu.py`. Промпты из базы данных используются только для старой системы пресетов.\n")
    
    return "\n".join(doc)


def main():
    """Главная функция"""
    print("Извлечение промптов из кодовой базы...")
    
    # Извлечь промпты
    presets = extract_presets_from_database()
    print(f"Найдено {len(presets)} промптов в database.py")
    
    menu_prompts = extract_prompts_from_menu()
    print(f"Найдено {len(menu_prompts)} промптов в menu.py")
    
    fitting_prompt = extract_fitting_room_prompt()
    if fitting_prompt:
        print(f"Найден промпт для fitting room")
    
    # Сгенерировать документацию
    doc = generate_documentation(presets, menu_prompts, fitting_prompt)
    
    # Сохранить в файл
    output_file = Path(__file__).parent / "PROMPTS_DOCUMENTATION.md"
    output_file.write_text(doc, encoding='utf-8')
    
    print(f"\nДокументация сохранена в: {output_file}")
    print(f"Всего промптов: {len(presets) + len(menu_prompts) + (1 if fitting_prompt else 0)}")


if __name__ == "__main__":
    main()
