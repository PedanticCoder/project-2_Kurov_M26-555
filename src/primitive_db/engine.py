#!/usr/bin/env python3

import shlex

import prompt
from prettytable import PrettyTable

from .core import create_table, delete, drop_table, insert, list_tables, select, update
from .decorators import create_cacher
from .parser import parse_set, parse_where
from .utils import load_metadata, load_table_data, save_metadata, save_table_data

DB_FILE = "db_meta.json"

# Создаем замыкание для кэширования запросов SELECT
query_cache = create_cacher()

def print_welcome_menu():
    print("<command> exit - выход из программы")
    print("<command> help- справочная информация")

def print_help():
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись.")  # noqa: E501
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию.")  # noqa: E501
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись.")  # noqa: E501
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись.")  # noqa: E501
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help- справочная информация")

def render_table(schema, data):
    if not data:
        return
    x = PrettyTable()
    x.field_names = list(schema.keys())
    for row in data:
        x.add_row([row.get(col) for col in x.field_names])
    print(x)

def run():
    print_welcome_menu()
    
    while True:
        prompt.PROMPT = "\n>>> Введите команду: "
        
        try:
            user_input = prompt.string()
            if not user_input:
                continue
            args = shlex.split(user_input.strip())
            if not args:
                continue
        except (ValueError, IndexError):
            print("Ошибка: Некорректный ввод.")
            continue

        metadata = load_metadata(DB_FILE)
        
        if len(args) > 1 and args[0] == "insert" and args[1] == "into":
            command = "insert into"
        elif len(args) > 1 and args[0] == "select" and args[1] == "from":
            command = "select from"
        elif len(args) > 1 and args[0] == "delete" and args[1] == "from":
            command = "delete from"
        else:
            command = args[0]

        match command:
            case "exit":
                break
                
            case "help":
                print_help()
                
            case "list_tables":
                list_tables(metadata)
                
            case "create_table":
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                new_meta = create_table(metadata, args[1], args[2:])
                if new_meta is not None:
                    save_metadata(DB_FILE, new_meta)
                
            case "drop_table":
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                new_meta = drop_table(metadata, args[1])
                if new_meta is not None:
                    save_metadata(DB_FILE, new_meta)

            case "info":
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                t_name = args[1]
                if t_name not in metadata:
                    print(f"Ошибка: Таблица '{t_name}' не существует.")
                    continue
                schema = metadata[t_name]["columns"]
                cols_str = ", ".join([f"{k}:{v}" for k, v in schema.items()])
                t_data = load_table_data(t_name)
                print(f"Таблица: {t_name}")
                print(f"Столбцы: {cols_str}")
                print(f"Количество записей: {len(t_data)}")

            case "insert into":
                if len(args) < 4 or args[3] != "values":
                    print("Ошибка: Неверный синтаксис.")
                    continue
                t_name = args[2]
                raw_values = args[4:]
                
                t_data = load_table_data(t_name)
                new_t_data = insert(metadata, t_name, t_data, raw_values)
                if new_t_data is not None:
                    save_table_data(t_name, new_t_data)

            case "select from":
                if len(args) < 3:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                t_name = args[2]
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue
                    
                schema = metadata[t_name]["columns"]
                t_data = load_table_data(t_name)
                
                try:
                    where_clause = parse_where(args, schema)
                except (ValueError, KeyError) as e:
                    print(f"Ошибка: {e}")
                    continue
                
                # Формируем уникальный ключ для кэша на основе запроса
                cache_key = f"{t_name}_{str(where_clause)}"
                
                # Интегрируем замыкание для получения кэшированного или нового результата  # noqa: E501
                res = query_cache(cache_key, lambda: select(t_data, where_clause))
                render_table(schema, res)

            case "update":
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                t_name = args[1]
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue
                    
                schema = metadata[t_name]["columns"]
                t_data = load_table_data(t_name)
                
                try:
                    where_clause = parse_where(args, schema)
                    set_clause = parse_set(args, schema)
                except (ValueError, KeyError) as e:
                    print(f"Ошибка: {e}")
                    continue
                
                res_update = update(t_data, set_clause, where_clause)
                if res_update is not None:
                    new_t_data, updated_ids = res_update
                    save_table_data(t_name, new_t_data)
                    target_id = updated_ids[0] if updated_ids else 1
                    print(f'Запись с ID={target_id} в таблице "{t_name}" успешно обновлена.')  # noqa: E501

            case "delete from":
                if len(args) < 3:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                t_name = args[2]
                if t_name not in metadata:
                    print(f'Ошибка: Таблица "{t_name}" не существует.')
                    continue
                    
                schema = metadata[t_name]["columns"]
                t_data = load_table_data(t_name)
                
                try:
                    where_clause = parse_where(args, schema)
                except (ValueError, KeyError) as e:
                    print(f"Ошибка: {e}")
                    continue
                    
                res_delete = delete(t_data, where_clause)
                if res_delete is not None:
                    new_t_data, deleted_ids = res_delete
                    if not deleted_ids:
                        print('Ошибка: Запись не найдена.')
                        continue
                    save_table_data(t_name, new_t_data)
                    target_id = deleted_ids[0]
                    print(f'Запись с ID={target_id} успешно удалена из таблицы "{t_name}".')  # noqa: E501

            case _:
                print(f"Ошибка: Неизвестная команда '{command}'.")
