import json


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


def print_command_error(value: str) -> None:
    """Print an invalid value error."""

    print(f"Некорректное значение: {value}. Попробуйте снова.")
