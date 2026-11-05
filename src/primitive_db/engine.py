import prompt

HELP_TEXT = (
    "<command> exit - выйти из программы\n"
    "<command> help - справочная информация"
)


def welcome():
    print("Первая попытка запустить проект!\n")
    print("***")
    print(HELP_TEXT)

    while True:
        command = prompt.string("Введите команду: ").strip()

        if command == "exit":
            break
        elif command == "help":
            print()
            print(HELP_TEXT)
        else:
            print(f"Неизвестная команда: {command}")