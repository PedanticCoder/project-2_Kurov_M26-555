#!/usr/bin/env python3

VALID_TYPES = {"int", "str", "bool"}

def create_table(metadata, table_name, columns):
    """Создает таблицу, проверяет типы данных и добавляет столбец ID:int первым."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    parsed_columns = {"ID": "int"}

    for col in columns:
        if ":" not in col:
            print(f"Ошибка: Неверный формат столбца '{col}'. Используйте имя:тип.")
            return None
        
        col_name, col_type = col.split(":", 1)
        if col_type not in VALID_TYPES:
            print(f"Ошибка: Неподдерживаемый тип данных '{col_type}'. Разрешены: int, str, bool.") # noqa: E501
            return None
        
        parsed_columns[col_name] = col_type

    metadata[table_name] = {"columns": parsed_columns, "data": []}

    cols_str = ", ".join([f"{k}:{v}" for k, v in parsed_columns.items()])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata

def drop_table(metadata, table_name):
    """Удаляет информацию о таблице из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

def list_tables(metadata):
    """Выводит список всех существующих таблиц."""
    if not metadata:
        return
    for table_name in metadata.keys():
        print(f"- {table_name}")

