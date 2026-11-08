import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath: str) -> dict:
    """Load table metadata from a JSON file. Return {} if the file is missing."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Save table metadata to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_data_path(table_name: str) -> str:
    """Return path to the JSON file with table data."""

    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name: str) -> list:
    """Load table data. Return [] if missing."""

    try:
        with open(get_table_data_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Save table data."""

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_table_data_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_version(table_name: str) -> int:
    """Return data file modification time, or 0 if the file does not exist."""
    path = get_table_data_path(table_name)
    return os.stat(path).st_mtime_ns if os.path.exists(path) else 0
