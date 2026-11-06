from primitive_db.utils import print_command_error

VALID_TYPES = {"int", "str", "bool"}


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
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> None:
    """Print names of all tables."""

    if not metadata:
        print("Таблиц пока нет.")
        return
    for table_name in metadata:
        print(f"— {table_name}")
