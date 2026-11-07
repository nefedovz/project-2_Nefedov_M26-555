import os

from primitive_db.utils import load_table_data, print_command_error, get_table_data_path

VALID_TYPES = {"int": int, "str": str, "bool": bool}


def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Create a table with an auto-added ID column and return updated metadata."""

    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    table_columns = {}
    if "ID:int" not in columns:
        table_columns["ID"] = "int"
    for column in columns:
        name, sep, col_type = column.partition(":")
        if not sep or not name or col_type not in VALID_TYPES:
            print_command_error(column)
            return metadata
        if name == "ID" and col_type != "int":
            print("Ошибка: Столбец ID должен иметь тип int.")
            return metadata
        if name in table_columns:
            print(f'Ошибка: Столбец "{name}" повторяется.')
            return metadata
        table_columns[name] = col_type
        if len(table_columns) == 1:
            print("Ошибка: Таблица должна содержать хотя бы один столбец кроме ID.")
            return metadata

    metadata[table_name] = table_columns
    columns_str = ", ".join(f"{n}:{t}" for n, t in table_columns.items())
    print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_str}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Delete a table from metadata and return updated metadata."""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    if os.path.exists(get_table_data_path(table_name)):
        os.remove(get_table_data_path(table_name))
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> None:
    """Print names of all tables."""

    if not metadata:
        print("Таблиц пока нет.")
        return
    for table_name in metadata:
        print(f"— {table_name}")


def insert(metadata: dict, table_name: str, values: list) -> list | None:
    """Add a record with auto-generated ID."""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name]
    data_columns = [name for name in columns if name != "ID"]

    if len(values) != len(data_columns):
        print(
            f"Ошибка: Ожидается значений: {len(data_columns)}, "
            f"получено: {len(values)}."
        )
        return None

    record = {}
    for name, value in zip(data_columns, values):
        if type(value) is not VALID_TYPES[columns[name]]:
            print_command_error(str(value))
            return None
        record[name] = value

    table_data = load_table_data(table_name)
    new_id = max((row["ID"] for row in table_data), default=0) + 1
    table_data.append({"ID": new_id, **record})

    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def matches(row: dict, where_clause: dict) -> bool:
    """Check if a record satisfies all conditions."""

    return all(row.get(column) == value for column, value in where_clause.items())


def validate_clause(columns: dict, clause: dict) -> bool:
    """Check that clause columns exist and values match column types."""

    for column, value in clause.items():
        if column not in columns:
            print(f'Ошибка: Столбец "{column}" не существует.')
            return False
        if type(value) is not VALID_TYPES[columns[column]]:
            print_command_error(str(value))
            return False
    return True


def select(table_data: list, where_clause: dict | None = None) -> list:
    """Return all records or matching where_clause."""

    if not where_clause:
        return table_data
    return [row for row in table_data if matches(row, where_clause)]


def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Update fields of matching records."""

    for row in table_data:
        if matches(row, where_clause):
            row.update(set_clause)
    return table_data


def delete(table_data: list, where_clause: dict) -> list:
    """Remove matching records."""

    return [row for row in table_data if not matches(row, where_clause)]