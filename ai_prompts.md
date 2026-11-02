# ИИ оптимизация

## Запрос 1: 
*Добавь функции:*
- *для возведения в любую степень*
- *для извлечения квадратного корня*

**Ответ:**
> Добавил в калькулятор:

- возведение в любую степень (пункт меню 7);

```python
def power(a: Decimal, b: Decimal) -> Decimal:
    """Возводит a в степень b."""
    try:
        return a ** b
    except ArithmeticError as exc:
        raise ArithmeticError(f"не удалось возвести в степень: {exc}") from exc
```

- извлечение квадратного корня (пункт меню 8);
```python
def sqrt_decimal(a: Decimal) -> Decimal:
    """Извлекает квадратный корень из a."""
    if a < 0:
        raise ArithmeticError("квадратный корень из отрицательного числа не существует")
    try:
        return a.sqrt()
    except ArithmeticError as exc:
        raise ArithmeticError(f"не удалось извлечь корень: {exc}") from exc
```

- запись этих операций в историю;

- **обработку ошибок:** отрицательное основание при дробной степени, корень из отрицательного числа, переполнение и т.п.



## Запрос 2: 
*Обеспечь возможность неограниченного ввода чисел до момента его прекращения пользователем.*

> Функция **read_decimal_or_stop()** — именно она позволяет вводить число до бесконечности и возвращает None, когда пользователь хочет остановиться. Остановка срабатывает на:

- пустую строку;

- stop, стоп, q, exit, выход;

- закрытие стандартного ввода (EOF).

```python
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
```

> Циклы while True в операциях — они повторяют запрос числа, пока read_decimal_or_stop() не вернёт None. 

> Для бинарных операций это **run_binary_operation()**:
```python
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
```

> Аналогично — в **run_power_operation()** и **run_sqrt_operation()**:
```python
# run_power_operation()
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

# run_sqrt_operation()

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
```
> Общий цикл меню в main() — тоже while True, поэтому после завершения одной операции можно снова выбирать пункты меню и запускать новые операции без перезапуска программы:
```python
while True:
    out(MENU)
    ...
    choice = sys.stdin.readline()
    if choice == "":
        break
    ...
```