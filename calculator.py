"""Консольный калькулятор с историей операций.
Итоговый проект, Кейс 1.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Optional, Callable

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

В операциях вводите числа по одному.
Пустая строка или 'stop' — завершить операцию.
"""


def out(*args, **kwargs) -> None:
    """print с принудительным сбросом буфера."""
    kwargs.setdefault("flush", True)
    print(*args, **kwargs)


def read_decimal(prompt: str) -> Decimal:
    """Запрашивает число и возвращает Decimal. Без возможности остановки."""
    while True:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        raw = sys.stdin.readline()
        if raw == "":
            raise EOFError("Стандартный ввод закрыт.")
        raw = raw.strip().replace(",", ".")
        if not raw:
            out("Ошибка: пустой ввод. Введите число.")
            continue
        try:
            value = Decimal(raw)
        except (InvalidOperation, ValueError):
            out("Ошибка: введите корректное число, например 10 или 2.5.")
            continue
        if not value.is_finite():
            out("Ошибка: число должно быть конечным.")
            continue
        return value


def read_decimal_or_stop(prompt: str) -> Optional[Decimal]:
    """Запрашивает число или возвращает None, если пользователь хочет остановиться."""
    while True:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        raw = sys.stdin.readline()
        if raw == "":
            return None
        raw = raw.strip()
        if not raw:
            return None
        if raw.lower() in {"stop", "стоп", "q", "exit", "выход"}:
            return None
        raw = raw.replace(",", ".")
        try:
            value = Decimal(raw)
        except (InvalidOperation, ValueError):
            out("Ошибка: введите корректное число или 'stop' для завершения.")
            continue
        if not value.is_finite():
            out("Ошибка: число должно быть конечным.")
            continue
        return value


def format_number(value: Decimal) -> str:
    """Форматирует Decimal без лишних нулей."""
    if value == value.to_integral():
        return str(value.quantize(Decimal("1")))
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def add(a: Decimal, b: Decimal) -> Decimal:
    return a + b


def subtract(a: Decimal, b: Decimal) -> Decimal:
    return a - b


def multiply(a: Decimal, b: Decimal) -> Decimal:
    return a * b


def divide(a: Decimal, b: Decimal) -> Decimal:
    """Делит a на b; выбрасывает ZeroDivisionError при b == 0."""
    if b == 0:
        raise ZeroDivisionError("деление на ноль невозможно")
    return a / b


def power(a: Decimal, b: Decimal) -> Decimal:
    """Возводит a в степень b."""
    try:
        return a ** b
    except ArithmeticError as exc:
        raise ArithmeticError(f"не удалось возвести в степень: {exc}") from exc


def sqrt_decimal(a: Decimal) -> Decimal:
    """Извлекает квадратный корень из a."""
    if a < 0:
        raise ArithmeticError("квадратный корень из отрицательного числа не существует")
    try:
        return a.sqrt()
    except ArithmeticError as exc:
        raise ArithmeticError(f"не удалось извлечь корень: {exc}") from exc


def append_history(expression: str, result: Decimal) -> None:
    """Добавляет запись в history.txt."""
    line = (
        f"{datetime.now():%Y-%m-%d %H:%M:%S} | "
        f"{expression} = {format_number(result)}\n"
    )
    try:
        with HISTORY_FILE.open("a", encoding="utf-8") as file:
            file.write(line)
    except OSError as exc:
        out(f"Не удалось сохранить историю: {exc}")
        logging.exception("Ошибка записи истории")


def show_history() -> None:
    """Выводит историю операций."""
    if not HISTORY_FILE.exists():
        out("\nИстория пуста.")
        return
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8").strip()
    except OSError as exc:
        out(f"Не удалось прочитать историю: {exc}")
        logging.exception("Ошибка чтения истории")
        return
    if not content:
        out("\nИстория пуста.")
        return
    out("\n--- История операций ---")
    out(content)
    out("------------------------")


def clear_history() -> None:
    """Очищает файл истории после подтверждения."""
    if not HISTORY_FILE.exists():
        out("\nИстория уже пуста.")
        return
    sys.stdout.write("Очистить историю? (да/нет): ")
    sys.stdout.flush()
    answer = sys.stdin.readline().strip().lower()
    if answer not in {"да", "д", "yes", "y"}:
        out("Очистка отменена.")
        return
    try:
        HISTORY_FILE.unlink()
        out("История очищена.")
        logging.info("История очищена")
    except OSError as exc:
        out(f"Не удалось очистить историю: {exc}")
        logging.exception("Ошибка очистки истории")


def show_step(expression: str, result: Decimal) -> None:
    """Выводит и сохраняет один шаг вычисления."""
    formatted_result = format_number(result)
    out("")
    out(f"{expression} = {formatted_result}")
    out(f"Результат: {formatted_result}")
    append_history(expression, result)
    logging.info("Операция: %s = %s", expression, formatted_result)


def run_binary_operation(name: str, symbol: str, func: Callable[[Decimal, Decimal], Decimal]) -> None:
    """Непрерывная бинарная операция с накоплением результата."""
    out(f"\n{name}")
    out("Вводите числа по одному. Пустая строка или 'stop' — завершить.")

    current = read_decimal_or_stop("Введите первое число (или stop): ")
    if current is None:
        return

    while True:
        next_val = read_decimal_or_stop("Введите следующее число (или stop): ")
        if next_val is None:
            break
        try:
            result = func(current, next_val)
        except ZeroDivisionError as exc:
            out(f"Ошибка: {exc}.")
            logging.warning("Ошибка в операции %s: %s %s %s", name, current, symbol, next_val)
            continue
        except ArithmeticError as exc:
            out(f"Ошибка: {exc}.")
            logging.warning("Ошибка в операции %s: %s %s %s", name, current, symbol, next_val)
            continue

        expression = f"{format_number(current)} {symbol} {format_number(next_val)}"
        show_step(expression, result)
        current = result


def run_power_operation() -> None:
    """Непрерывное возведение в степень: пары основание — показатель."""
    out("\nВозведение в степень")
    out("Вводите основание и показатель. Пустая строка или 'stop' — завершить.")

    while True:
        base = read_decimal_or_stop("Введите основание (или stop): ")
        if base is None:
            break
        exponent = read_decimal_or_stop("Введите показатель степени (или stop): ")
        if exponent is None:
            break

        try:
            result = power(base, exponent)
        except ArithmeticError as exc:
            out(f"Ошибка: {exc}.")
            logging.warning("Ошибка возведения в степень: %s ^ %s", base, exponent)
            continue

        expression = f"{format_number(base)} ^ {format_number(exponent)}"
        show_step(expression, result)


def run_sqrt_operation() -> None:
    """Непрерывное извлечение квадратного корня."""
    out("\nКвадратный корень")
    out("Вводите числа. Пустая строка или 'stop' — завершить.")

    while True:
        number = read_decimal_or_stop("Введите число (или stop): ")
        if number is None:
            break

        try:
            result = sqrt_decimal(number)
        except ArithmeticError as exc:
            out(f"Ошибка: {exc}.")
            logging.warning("Ошибка извлечения корня: sqrt(%s)", number)
            continue

        expression = f"sqrt({format_number(number)})"
        show_step(expression, result)


def run_self_test() -> None:
    """Проверка работы программы без ввода: вычисления и история."""
    out("=== САМОТЕСТ ===")
    a, b = Decimal("2.5"), Decimal("3")
    out(f"{a} + {b} = {add(a, b)}")
    out(f"{a} - {b} = {subtract(a, b)}")
    out(f"{a} * {b} = {multiply(a, b)}")
    out(f"{a} / {b} = {divide(a, b)}")
    out(f"{a} ^ {b} = {power(a, b)}")
    out(f"sqrt({a}) = {sqrt_decimal(a)}")
    try:
        divide(a, Decimal("0"))
    except ZeroDivisionError as exc:
        out(f"OK: поймано деление на ноль — {exc}")

    append_history("самотест 2.5 + 3", add(a, b))
    out("История после записи:")
    show_history()
    out("=== САМОТЕСТ ЗАВЕРШЁН ===")


def main() -> None:
    if "--test" in sys.argv:
        run_self_test()
        return

    out("Добро пожаловать в консольный калькулятор!")
    while True:
        out(MENU)
        sys.stdout.write("Выберите пункт меню: ")
        sys.stdout.flush()
        choice = sys.stdin.readline()
        if choice == "":
            out("\nВвод закрыт. Выход.")
            break
        choice = choice.strip()

        if choice == "0":
            out("До свидания!")
            break
        if choice == "1":
            run_binary_operation("Сложение", "+", add)
        elif choice == "2":
            run_binary_operation("Вычитание", "-", subtract)
        elif choice == "3":
            run_binary_operation("Умножение", "*", multiply)
        elif choice == "4":
            run_binary_operation("Деление", "/", divide)
        elif choice == "5":
            show_history()
        elif choice == "6":
            clear_history()
        elif choice == "7":
            run_power_operation()
        elif choice == "8":
            run_sqrt_operation()
        else:
            out("Ошибка: выберите пункт из меню (0–8).")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        out("\nВыход из программы.")
    except Exception:
        logging.exception("Непредвиденная ошибка")
        out("Произошла непредвиденная ошибка. Подробности в calculator.log.")
        raise