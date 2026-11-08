import shlex


def parse_value(token: str) -> str | int | bool:
    """Convert a token to str, int or bool. Strings must be quoted."""

    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    if token.lower() == "true":
        return True
    if token.lower() == "false":
        return False
    try:
        return int(token)
    except ValueError:
        raise ValueError(token) from None


def parse_condition(text: str) -> dict:
    """Parse 'column = value' into {column: value}."""

    column, sep, value = text.partition("=")
    column = column.strip()
    if not sep or not column or not value.strip():
        raise ValueError(text.strip())
    return {column: parse_value(value)}


def parse_values(text: str) -> list:
    """Parse '(v1, v2, ...)' into a list of values."""

    text = text.strip()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError(text)
    lexer = shlex.shlex(text[1:-1], posix=False)
    lexer.whitespace = ","
    lexer.whitespace_split = True
    return [parse_value(token) for token in lexer]


def find_keyword(text: str, keyword: str) -> int:
    """Return index of ' keyword ' outside quotes, -1 if not found."""

    target = f" {keyword} "
    quote = None
    for i, char in enumerate(text):
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif text.startswith(target, i):
            return i
    return -1


def split_keyword(
    text: str, keyword: str, required: bool = True
) -> tuple[str, str | None]:
    """Split text by ' keyword ' outside quotes.

    If keyword is missing: raise ValueError when required, else return (text, None).
    """
    index = find_keyword(text, keyword)
    if index == -1:
        if required:
            raise ValueError(text.strip())
        return text.strip(), None
    return text[:index].strip(), text[index + len(keyword) + 2 :].strip()


def parse_table_name(head: str, expected: list[str]) -> str:
    """Check command words and return table name."""

    words = head.split()
    if words[:-1] != expected or len(words) != len(expected) + 1:
        raise ValueError(head)
    return words[-1]


def parse_insert(command: str) -> tuple[str, list]:
    """insert into <table> values (...) -> (table, values)."""

    head, values_part = split_keyword(command, "values")
    return parse_table_name(head, ["insert", "into"]), parse_values(values_part)


def parse_select(command: str) -> tuple[str, dict | None]:
    """select from <table> [where <cond>] -> (table, where or None)."""

    head, condition = split_keyword(command, "where", required=False)
    table_name = parse_table_name(head, ["select", "from"])
    where_clause = parse_condition(condition) if condition is not None else None
    return table_name, where_clause


def parse_update(command: str) -> tuple[str, dict, dict]:
    """update <table> set <col = val> where <cond> -> (table, set, where)."""

    head, rest = split_keyword(command, "set")
    set_part, where_part = split_keyword(f" {rest}", "where")
    table_name = parse_table_name(head, ["update"])
    return table_name, parse_condition(set_part), parse_condition(where_part)


def parse_delete(command: str) -> tuple[str, dict]:
    """delete from <table> where <cond> -> (table, where)."""

    head, condition = split_keyword(command, "where")
    return parse_table_name(head, ["delete", "from"]), parse_condition(condition)
