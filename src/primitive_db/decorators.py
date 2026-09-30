#!/usr/bin/env python3

import functools
import time

import prompt


def handle_db_errors(func):
    """Декоратор для централизованной обработки исключений БД."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")  # noqa: E501
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None
    return wrapper

def confirm_action(action_name):
    """Фабрика декораторов для подтверждения опасных операций."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Запрашиваем подтверждение у пользователя
            prompt.PROMPT = f"Вы уверены, что хотите выполнить \"{action_name}\"? [y/n]: "  # noqa: E501
            confirm = prompt.string()
            
            if confirm and confirm.lower().strip() == 'y':
                return func(*args, **kwargs)
            else:
                print(f"Операция \"{action_name}\" отменена.")
                return None
        return wrapper
    return decorator

def log_time(func):
    """Декоратор для замера времени выполнения функций СУБД."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        print(f"Функция <{func.__name__}> выполнилась за {duration:.6f} секунд.")
        return result
    return wrapper

def create_cacher():
    """Замыкание для кэширования результатов выполнения функций."""
    cache = {}
    
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result
        
    return cache_result

