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
