# primitive_db

Простая консольная база данных на Python.

## Требования

- Python 3.12+
- uv

Установка uv (macOS / Linux):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Установка

Устанавливает глобальную команду `database`:

```bash
uv tool install git+https://github.com/nefedovz/project-2_Nefedov_M26-555
```


## Запуск

После установки:

```bash
database
```

Из папки проекта:

```bash
make run
make project
```

## Удаление

```bash
uv tool uninstall project-2-nefedov-m26-555
```

## Управление таблицами

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец:тип> ...` | создать таблицу |
| `list_tables` | показать список всех таблиц |
| `drop_table <имя>` | удалить таблицу |
| `help` | справочная информация |
| `exit` | выход из программы |

Поддерживаемые типы данных: `int`, `str`, `bool`.
Столбец `ID:int` добавляется автоматически, если не указан пользователем.

### Пример

```
>>>Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```

### Демонстрация

[![asciicast](https://asciinema.org/a/MjY1vSHYT7ATf6TM.svg)](https://asciinema.org/a/MjY1vSHYT7ATf6TM)

## CRUD-операции

| Команда | Описание |
|---|---|
| `insert into <таблица> values (<знач1>, <знач2>, ...)` | создать запись |
| `select from <таблица>` | прочитать все записи |
| `select from <таблица> where <столбец> = <значение>` | прочитать записи по условию |
| `update <таблица> set <столбец> = <значение> where <столбец> = <значение>` | обновить записи |
| `delete from <таблица> where <столбец> = <значение>` | удалить записи |
| `info <таблица>` | информация о таблице |

Строковые значения указываются в кавычках, логические — `true`/`false`.
`ID` генерируется автоматически и не передаётся в `insert`.
Данные каждой таблицы хранятся в `data/<имя_таблицы>.json`.

### Демонстрация CRUD

[![asciicast](https://asciinema.org/a/MUuhrZKg0FtojJ80.svg)](https://asciinema.org/a/MUuhrZKg0FtojJ80)

## Декораторы и замыкания

### Обработка ошибок

Все операции с базой обёрнуты декоратором `handle_db_errors`. Он перехватывает
`ValueError`, `KeyError` и `FileNotFoundError` и выводит сообщение вместо
 завершения программы.

### Подтверждение опасных операций

`drop_table` и `delete` запрашивают подтверждение (декоратор `confirm_action`).
Любой ответ, кроме `y`, отменяет операцию.

### Замер времени выполнения

Декоратор `log_time` выводит время выполнения `insert` и `select`.

### Кэширование запросов

Результаты `select` кэшируются с помощью замыкания (`create_cacher`). Повторный
одинаковый запрос возвращается из кэша без чтения файла. Кэш автоматически
сбрасывается при изменении данных таблицы.

### Демонстрация

[![asciicast](https://asciinema.org/a/0tnIYFDqy0B0lOH1.svg)](https://asciinema.org/a/0tnIYFDqy0B0lOH1)