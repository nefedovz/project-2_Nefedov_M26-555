import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
    validate_clause,
)
from primitive_db.parser import parse_delete, parse_insert, parse_select, parse_update
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    print_command_error,
    save_metadata,
    save_table_data,
)

META_FILE = "db_meta.json"


def print_help() -> None:
    """Print the list of available commands."""

    print("\n***Операции с данными***\n")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print()
    print("\n***Управление таблицами***\n")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print()
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def table_exists(metadata: dict, table_name: str) -> bool:
    """Check that table exists, print an error if not."""

    if table_name in metadata:
        return True
    print(f'Ошибка: Таблица "{table_name}" не существует.')
    return False


def print_rows(columns: dict, rows: list) -> None:
    """Print records as a PrettyTable."""

    table = PrettyTable()
    table.field_names = list(columns)
    for row in rows:
        table.add_row([row[column] for column in columns])
    print(table)


def handle_insert(metadata: dict, command: str) -> None:
    """Parse and execute an insert command."""

    table_name, values = parse_insert(command)
    table_data = insert(metadata, table_name, values)
    if table_data is not None:
        save_table_data(table_name, table_data)


def handle_select(metadata: dict, command: str) -> None:
    """Parse and execute a select command, print results as a table."""

    table_name, where_clause = parse_select(command)
    if not table_exists(metadata, table_name):
        return
    columns = metadata[table_name]
    if where_clause and not validate_clause(columns, where_clause):
        return

    rows = select(load_table_data(table_name), where_clause)
    if not rows:
        print("Записи не найдены.")
        return
    print_rows(columns, rows)


def handle_update(metadata: dict, command: str) -> None:
    """Parse and execute an update command, print updated record IDs."""

    table_name, set_clause, where_clause = parse_update(command)
    if not table_exists(metadata, table_name):
        return
    columns = metadata[table_name]
    if "ID" in set_clause:
        print("Ошибка: Столбец ID нельзя изменять.")
        return
    if not validate_clause(columns, set_clause):
        return
    if not validate_clause(columns, where_clause):
        return

    table_data = load_table_data(table_name)
    ids = [row["ID"] for row in select(table_data, where_clause)]
    if not ids:
        print("Записи не найдены.")
        return

    save_table_data(table_name, update(table_data, set_clause, where_clause))
    for record_id in ids:
        print(f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.')


def handle_delete(metadata: dict, command: str) -> None:
    """Parse and execute a delete command, print deleted record IDs."""

    table_name, where_clause = parse_delete(command)
    if not table_exists(metadata, table_name):
        return
    if not validate_clause(metadata[table_name], where_clause):
        return

    table_data = load_table_data(table_name)
    ids = [row["ID"] for row in select(table_data, where_clause)]
    if not ids:
        print("Записи не найдены.")
        return

    save_table_data(table_name, delete(table_data, where_clause))
    for record_id in ids:
        print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')


def handle_info(metadata: dict, table_name: str) -> None:
    """Print table name, columns and number of records."""

    if not table_exists(metadata, table_name):
        return
    columns = metadata[table_name]
    columns_str = ", ".join(f"{name}:{col_type}" for name, col_type in columns.items())
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_str}")
    print(f"Количество записей: {len(load_table_data(table_name))}")


def execute(command: str, params: list, user_input: str, metadata: dict) -> None:
    """Dispatch a command. Raise ValueError on invalid input."""

    match command:
        case "create_table":
            if len(params) < 2:
                raise ValueError(user_input)
            save_metadata(META_FILE, create_table(metadata, params[0], params[1:]))
        case "drop_table":
            if len(params) != 1:
                raise ValueError(user_input)
            save_metadata(META_FILE, drop_table(metadata, params[0]))
        case "list_tables":
            list_tables(metadata)
        case "insert":
            handle_insert(metadata, user_input)
        case "select":
            handle_select(metadata, user_input)
        case "update":
            handle_update(metadata, user_input)
        case "delete":
            handle_delete(metadata, user_input)
        case "info":
            if len(params) != 1:
                raise ValueError(user_input)
            handle_info(metadata, params[0])
        case "help":
            print_help()
        case _:
            print(f"Функции {command} нет. Попробуйте снова.")


def run() -> None:
    """Run the main command loop."""

    print("\n***База данных***\n")
    print_help()
    print()

    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ").strip()

        try:
            args = shlex.split(user_input)
        except ValueError:
            print_command_error(user_input)
            print()
            continue
        if not args:
            continue

        command, *params = args
        if command == "exit":
            break

        try:
            execute(command, params, user_input, metadata)
        except ValueError as error:
            print_command_error(str(error))
        print()