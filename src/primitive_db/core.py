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
        
def cast_value(val_str, target_type):
    """Приводит строковое значение к целевому типу метаданных."""
    if target_type == "int":
        return int(val_str)
    elif target_type == "bool":
        if val_str.lower() == "true":
            return True
        if val_str.lower() == "false":
            return False
        raise ValueError
    elif target_type == "str":
        # Убираем кавычки, если они есть
        if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")): # noqa: E501
            return val_str[1:-1]
        return val_str
    return val_str

def insert(metadata, table_name, table_data, values):
    """Создает запись, валидирует типы данных и автоинкрементирует ID."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    schema = metadata[table_name]["columns"]
    # Список столбцов без ID
    expected_cols = [k for k in schema.keys() if k != "ID"]

    if len(values) != len(expected_cols):
        print(f"Ошибка: Неверное количество значений. Ожидалось {len(expected_cols)}, получено {len(values)}.") # noqa: E501
        return None

    new_row = {}
    
    # Генерация автоинкремента ID
    if table_data:
        new_id = max(row["ID"] for row in table_data) + 1
    else:
        new_id = 1
    new_row["ID"] = new_id

    # Заполнение остальных полей с проверкой типов
    for idx, col_name in enumerate(expected_cols):
        target_type = schema[col_name]
        raw_val = values[idx].strip("(), ")
        try:
            new_row[col_name] = cast_value(raw_val, target_type)
        except ValueError:
            print(f"Ошибка: Значение '{raw_val}' не соответствует типу '{target_type}' для столбца '{col_name}'.") # noqa: E501
            return None

    table_data.append(new_row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data

def select(table_data, where_clause=None):
    """Выбирает записи, опционально фильтруя по словарю where_clause."""
    if not where_clause:
        return table_data

    filtered_data = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if col not in row or row[col] != val:
                match = False
                break
        if match:
            filtered_data = row
    return filtered_data

def update(table_data, set_clause, where_clause):
    """Обновляет значения полей согласно set_clause для записей, подходящих под where_clause.""" # noqa: E501
    updated_ids = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if col not in row or row[col] != val:
                match = False
                break
        if match:
            for s_col, s_val in set_clause.items():
                row[s_col] = s_val
            if row["ID"] not in updated_ids:
                updated_ids.append(row["ID"])

    return table_data, updated_ids

def delete(table_data, where_clause):
    """Удаляет записи, подходящие под условия where_clause."""
    deleted_ids = []
    
    # Вычисляем ID удаляемых строк
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if col not in row or row[col] != val:
                match = False
                break
        if match:
            deleted_ids.append(row["ID"])
            
    # Оставляем только те, что не подошли под фильтр
    new_table_data = [row for row in table_data if row["ID"] not in deleted_ids]
    return new_table_data, deleted_ids


