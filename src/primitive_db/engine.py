#!/usr/bin/env python3
  
import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"

def print_welcome_menu():
    """Выводит короткое меню строго при первом запуске программы."""
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")

def print_help():
    """Выводит полную справочную информацию по процессам работы с таблицами."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу") # noqa: E501
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")

def run():
    """Основная точка входа и цикл работы базы данных."""
    # Выводим короткое меню при старте
    print_welcome_menu()
    
    while True:
        prompt.PROMPT = "\n>>>Введите команду: "
        
        try:
            user_input = prompt.string()
            if not user_input:
                continue

            args = shlex.split(user_input)
            command = args[0]
        except (ValueError, IndexError):
            print("Ошибка: Некорректный ввод.")
            continue

        metadata = load_metadata(DB_FILE)

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
                table_name = args[1]
                columns = args[2:]
                
                new_meta = create_table(metadata, table_name, columns)
                if new_meta is not None:
                    save_metadata(DB_FILE, new_meta)
                    
            case "drop_table":
                if len(args) < 2:
                    print("Ошибка: Укажите имя таблицы.")
                    continue
                table_name = args[1]
                
                new_meta = drop_table(metadata, table_name)
                if new_meta is not None:
                    save_metadata(DB_FILE, new_meta)
                    
            case _:
                print(f"Ошибка: Неизвестная команда '{command}'.")
