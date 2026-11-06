import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, print_command_error, save_metadata

META_FILE = "db_meta.json"


def print_help() -> None:
    """Print the help message."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    """Run the main command loop."""

    print("\n***База данных***\n")
    print_help()
    print()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print_command_error(user_input)
            print()
            continue

        if not args:
            continue

        command, *params = args

        match command:
            case "create_table":
                if len(params) < 2:
                    print_command_error(user_input)
                else:
                    metadata = create_table(metadata, params[0], params[1:])
                    save_metadata(META_FILE, metadata)
            case "drop_table":
                if len(params) != 1:
                    print_command_error(user_input)
                else:
                    metadata = drop_table(metadata, params[0])
                    save_metadata(META_FILE, metadata)
            case "list_tables":
                list_tables(metadata)
            case "help":
                print_help()
            case "exit":
                break
            case _:
                print(f"Функции {command} нет. Попробуйте снова.")

        print()
