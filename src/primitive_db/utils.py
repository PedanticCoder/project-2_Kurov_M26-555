#!/usr/bin/env python3

import json
import os


def load_metadata(filepath):
    """Загружает данные из JSON-файла. Возвращает {} если файл не найден."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_table_data(table_name):
    """Загружает строки таблицы из папки data/. Если файла нет, возвращает []."""
    filepath = os.path.join("data", f"{table_name}.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_table_data(table_name, data):
    """Сохраняет строки таблицы в папку data/."""
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

