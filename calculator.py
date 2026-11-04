"""Консольный калькулятор с историей операций."""

import logging
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path

getcontext().prec = 28

HISTORY_FILE = Path("history.txt")
LOG_FILE = Path("calculator.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)

MENU = """
=== Консольный калькулятор ===
1. Сложение
2. Вычитание
3. Умножение
4. Деление
5. Показать историю
6. Очистить историю
7. Возведение в степень
8. Квадратный корень
0. Выход

Пустая строка или 'stop' завершает ввод чисел.
"""

STOP_WORDS = {"stop", "стоп", "q", "exit", "выход"}
YES_WORDS = {"да", "д", "yes", "y"}

# Название, знак и функция операции
BINARY_OPERATIONS = {
    "1": ("Сложение", "+", lambda a, b: a + b),
    "2": ("Вычитание", "-", lambda a, b: a - b),
    "3": ("Умножение", "*", lambda a, b: a * b),
    "4": ("Деление", "/", lambda a, b: a / b),
}


def out(*args):
    """Выводит текст и сразу сбрасывает буфер."""
    print(*args, flush=True)


def read_number(prompt):
    """Читает конечное число или возвращает None для завершения ввода."""
    while True:
        raw = input(prompt).strip().replace(",", ".")
        if not raw or raw.lower() in STOP_WORDS:
            return None

        try:
            number = Decimal(raw)
            if number.is_finite():
                return number
        except InvalidOperation:
            pass

        out("Ошибка: введите корректное конечное число или 'stop'.")


def format_number(number):
    """Убирает незначащие нули из представления числа."""
    if number == number.to_integral_value():
        return str(number.quantize(Decimal("1")))
    return format(number.normalize(), "f")


def calculate(operation, a, b):
    """Выполняет бинарную операцию с проверкой деления на ноль."""
    if operation == "/":
        if b == 0:
            raise ZeroDivisionError("деление на ноль невозможно")
        return a / b
    if operation == "^":
        return a ** b
    raise ValueError(f"Неизвестная операция: {operation}")


def save_history(expression, result):
    """Сохраняет результат операции в файл."""
    line = (
        f"{datetime.now():%Y-%m-%d %H:%M:%S} | "
        f"{expression} = {format_number(result)}\n"
    )
    try:
        with HISTORY_FILE.open("a", encoding="utf-8") as file:
            file.write(line)
    except OSError:
        out("Не удалось сохранить историю.")
        logging.exception("Ошибка записи истории")


def show_step(expression, result):
    """Показывает, сохраняет и записывает в лог результат."""
    formatted = format_number(result)
    out(f"\n{expression} = {formatted}")
    out(f"Результат: {formatted}")
    save_history(expression, result)
    logging.info("Операция: %s = %s", expression, formatted)


def show_history():
    """Показывает сохранённые операции."""
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        content = ""
    except OSError:
        out("Не удалось прочитать историю.")
        logging.exception("Ошибка чтения истории")
        return

    if not content:
        out("\nИстория пуста.")
        return

    out("\n--- История операций ---")
    out(content)
    out("------------------------")


def clear_history():
    """Очищает историю после подтверждения."""
    if not HISTORY_FILE.exists():
        out("\nИстория уже пуста.")
        return

    if input("Очистить историю? (да/нет): ").strip().lower() not in YES_WORDS:
        out("Очистка отменена.")
        return

    try:
        HISTORY_FILE.unlink()
        out("История очищена.")
        logging.info("История очищена")
    except OSError:
        out("Не удалось очистить историю.")
        logging.exception("Ошибка очистки истории")


def run_binary_operation(name, symbol, function):
    """Выполняет последовательность операций с накоплением результата."""
    out(f"\n{name}")
    current = read_number("Введите первое число (или stop): ")
    if current is None:
        return

    while True:
        next_number = read_number("Введите следующее число (или stop): ")
        if next_number is None:
            break

        try:
            result = function(current, next_number)
        except ArithmeticError as error:
            out(f"Ошибка: {error}.")
            logging.warning("Ошибка операции %s: %s", name, error)
            continue

        expression = (
            f"{format_number(current)} {symbol} "
            f"{format_number(next_number)}"
        )
        show_step(expression, result)
        current = result


def run_power_operation():
    """Вычисляет степени для последовательных пар чисел."""
    out("\nВозведение в степень")
    while True:
        base = read_number("Введите основание (или stop): ")
        if base is None:
            break
        exponent = read_number("Введите показатель степени (или stop): ")
        if exponent is None:
            break

        try:
            result = calculate("^", base, exponent)
        except ArithmeticError as error:
            out(f"Ошибка: {error}.")
            logging.warning("Ошибка возведения в степень: %s", error)
            continue

        expression = f"{format_number(base)} ^ {format_number(exponent)}"
        show_step(expression, result)


def run_sqrt_operation():
    """Вычисляет квадратные корни введённых чисел."""
    out("\nКвадратный корень")
    while True:
        number = read_number("Введите число (или stop): ")
        if number is None:
            break
        if number < 0:
            out("Ошибка: корень из отрицательного числа не существует.")
            logging.warning("Попытка извлечь корень из %s", number)
            continue

        try:
            result = number.sqrt()
        except ArithmeticError as error:
            out(f"Ошибка: {error}.")
            logging.warning("Ошибка извлечения корня: %s", error)
            continue

        show_step(f"sqrt({format_number(number)})", result)


def run_self_test():
    """Проверяет основные вычисления и запись истории."""
    a, b = Decimal("2.5"), Decimal("3")
    tests = [
        ("Сложение", a + b),
        ("Вычитание", a - b),
        ("Умножение", a * b),
        ("Деление", a / b),
        ("Степень", a ** b),
        ("Корень", a.sqrt()),
    ]

    out("=== САМОТЕСТ ===")
    for name, result in tests:
        out(f"{name}: {format_number(result)}")

    try:
        calculate("/", a, Decimal("0"))
    except ZeroDivisionError:
        out("OK: деление на ноль обработано.")

    save_history("самотест 2.5 + 3", a + b)
    out("История после записи:")
    show_history()
    out("=== САМОТЕСТ ЗАВЕРШЁН ===")


def main():
    """Главный цикл программы."""
    if "--test" in sys.argv:
        run_self_test()
        return

    actions = {
        "5": show_history,
        "6": clear_history,
        "7": run_power_operation,
        "8": run_sqrt_operation,
    }

    out("Добро пожаловать в консольный калькулятор!")

    while True:
        out(MENU)
        choice = input("Выберите пункт меню: ").strip()

        if choice == "0":
            out("До свидания!")
            break

        if choice in BINARY_OPERATIONS:
            name, symbol, function = BINARY_OPERATIONS[choice]
            run_binary_operation(name, symbol, function)
        elif choice in actions:
            actions[choice]()
        else:
            out("Ошибка: выберите пункт из меню (0–8).")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        out("\nВыход из программы.")
    except Exception:
        logging.exception("Непредвиденная ошибка")
        out("Произошла непредвиденная ошибка. Подробности в calculator.log.")
        raise
