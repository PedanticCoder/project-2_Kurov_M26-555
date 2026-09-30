#!/usr/bin/env python3

from .decorators import confirm_action, handle_db_errors, log_time

VALID_TYPES = {"int", "str", "bool"}

def cast_value(val_str, target_type):
    if target_type == "int":
        return int(val_str)
    elif target_type == "bool":
        if val_str.lower() == "true":
            return True
        if val_str.lower() == "false":
            return False
        raise ValueError("Неверное булево значение")
    elif target_type == "str":
        if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):  # noqa: E501
            return val_str[1:-1]
        return val_str
    return val_str

@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return None

    parsed_columns = {"ID": "int"}

    for col in columns:
        if ":" not in col:
            raise ValueError(f"Неверный формат столбца '{col}'. Используйте имя:тип.")
        
        col_name, col_type = col.split(":", 1)
        if col_type not in VALID_TYPES:
            raise KeyError(col_type)
        
        parsed_columns[col_name] = col_type

    metadata[table_name] = {"columns": parsed_columns}
    cols_str = ", ".join([f"{k}:{v}" for k, v in parsed_columns.items()])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(table_name)
        
    del metadata[table_name]
    
    import os
    data_file = os.path.join("data", f"{table_name}.json")
    if os.path.exists(data_file):
        os.remove(data_file)
        
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

@handle_db_errors
def list_tables(metadata):
    if not metadata:
        return
    for table_name in metadata.keys():
        print(f"- {table_name}")

@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    if table_name not in metadata:
        raise KeyError(table_name)

    schema = metadata[table_name]["columns"]
    expected_cols = [k for k in schema.keys() if k != "ID"]

    if len(values) != len(expected_cols):
        raise ValueError(f"Неверное количество значений. Ожидалось {len(expected_cols)}.")  # noqa: E501

    new_row = {}
    if table_data:
        new_id = max(row["ID"] for row in table_data) + 1
    else:
        new_id = 1
    new_row["ID"] = new_id

    for idx, col_name in enumerate(expected_cols):
        target_type = schema[col_name]
        raw_val = values[idx].strip("(), ")
        new_row[col_name] = cast_value(raw_val, target_type)

    table_data.append(new_row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
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
            filtered_data.append(row)
    return filtered_data

@handle_db_errors
def update(table_data, set_clause, where_clause):
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

@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    deleted_ids = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if col not in row or row[col] != val:
                match = False
                break
        if match:
            deleted_ids.append(row["ID"])
            
    new_table_data = [row for row in table_data if row["ID"] not in deleted_ids]
    return new_table_data, deleted_ids


