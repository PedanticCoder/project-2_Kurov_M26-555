#!/usr/bin/env python3

import json


def load_metadata(filepath):
    """Загружает данные из JSON-файла. Возвращает {} если файл не найден."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(filepath, data):
    """Сохраняет переданные данные в JSON-файл."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

