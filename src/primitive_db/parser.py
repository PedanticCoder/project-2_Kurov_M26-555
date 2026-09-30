#!/usr/bin/env python3


def parse_where(args, schema):
    """Ищет блок 'where <столбец> = <значение>' в списке аргументов."""
    if "where" not in args:
        return {}
    
    idx = args.index("where")
    if len(args) < idx + 4 or args[idx + 2] != "=":
        raise ValueError("Неверный синтаксис условия WHERE. Ожидалось: where столбец = значение") # noqa: E501
        
    col_name = args[idx + 1]
    raw_val = args[idx + 3].strip('"\'') # Срезаем кавычки у значения для фильтрации
    
    if col_name not in schema:
        raise KeyError(f"Столбец '{col_name}' не найден в схеме таблицы.")
        
    from .core import cast_value
    casted_val = cast_value(raw_val, schema[col_name])
    return {col_name: casted_val}

def parse_set(args, schema):
    """Разбирает блок 'set <столбец> = <значение>'."""
    if "set" not in args:
        raise ValueError("Отсутствует ключевое слово SET.")
        
    start_idx = args.index("set")
    end_idx = args.index("where") if "where" in args else len(args)
    
    set_args = args[start_idx + 1:end_idx]
    if len(set_args) < 3 or set_args[1] != "=":
        raise ValueError("Неверный синтаксис блока SET. Ожидалось: set столбец = значение") # noqa: E501
        
    col_name = set_args[0]
    raw_val = set_args[2].strip('"\'') # Срезаем кавычки у нового значения
    
    if col_name not in schema:
        raise KeyError(f"Столбец '{col_name}' не найден в схеме таблицы.")
        
    from .core import cast_value
    casted_val = cast_value(raw_val, schema[col_name])
    return {col_name: casted_val}

