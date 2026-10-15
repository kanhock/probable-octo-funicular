# Разделы 16–20: исключения, файлы, контекстные менеджеры, итераторы и генераторы, декораторы.

SECTIONS = [
{
"title": "Исключения",
"items": ["Exception", "try", "except", "else", "finally", "raise", "custom exceptions"],
"intro": "Ошибки во время работы программы — это тоже объекты. Их можно поймать, обработать и даже создать свои.",
"lessons": [
{
"title": "Что такое исключение",
"covers": ["Exception"],
"text": """Когда Python не может выполнить действие (деление на ноль, нет ключа в словаре, неверный тип), он создаёт **объект-исключение** и «выбрасывает» его. Выполнение текущей функции прерывается, и исключение летит вверх по стеку вызовов, пока его кто-нибудь не поймает. Если не поймал никто — программа падает.

Все обычные исключения наследуют от `Exception`: `ValueError`, `TypeError`, `KeyError`, `IndexError`, `ZeroDivisionError`… Смотри в визуализаторе на шаги с красным «!».""",
"code": """
def divide(a, b):
    return a / b  #! При b = 0 здесь возникнет ZeroDivisionError

def calc():
    return divide(10, 0)  #! Исключение пролетит и через эту функцию

try:
    calc()
except Exception as e:  #! Ловим на самом верху
    print("Поймали:", type(e).__name__, "-", e)
    print(isinstance(e, ZeroDivisionError), isinstance(e, Exception))
""",
"key": ["Исключение — объект, описывающий ошибку.", "Оно поднимается вверх по стеку вызовов.", "Не поймано — программа завершается с ошибкой."],
},
{
"title": "try / except / else / finally",
"covers": ["try", "except", "else", "finally"],
"text": """`try` — «попробуй выполнить». `except Тип` — «если случилась такая ошибка, сделай это». `else` — выполняется, **если ошибки не было**. `finally` — выполняется **всегда**, при ошибке и без — туда кладут уборку: закрыть файл, соединение.

Можно писать несколько `except` для разных ошибок: срабатывает первый подходящий. Пройди по шагам оба запуска: с хорошими данными и с плохими.""",
"code": """
def parse_age(text):
    try:
        age = int(text)  #! Может бросить ValueError
    except ValueError:
        print(f"'{text}' — не число")
        age = None
    else:
        print("Успешно:", age)  #! Только если ошибки не было
    finally:
        print("Проверка завершена")  #! Всегда
    return age

parse_age("25")
parse_age("abc")
""",
"key": ["`try` → `except` при ошибке → `else` без ошибки → `finally` всегда.", "Лови конкретные исключения, а не все подряд.", "`finally` — для освобождения ресурсов."],
"quiz": {"q": "Что выполнится, если в `try` ошибки НЕ было?", "options": ["except и finally", "else и finally", "только finally", "только else"], "answer": 1, "why": "`else` — для случая без ошибки, `finally` — всегда."},
},
{
"title": "raise и свои исключения",
"covers": ["raise", "custom exceptions"],
"text": """`raise` бросает исключение самостоятельно — когда твоя функция обнаружила недопустимую ситуацию. Свои исключения создают, наследуя от `Exception`: так их можно ловить отдельно и добавлять полезные поля.

`raise ... from e` сохраняет исходную причину — удобно, когда одну ошибку превращаешь в другую.""",
"code": """
class NotEnoughMoney(Exception):  #! Своё исключение
    def __init__(self, need, have):
        super().__init__(f"Нужно {need}, есть {have}")
        self.need = need
        self.have = have

def buy(price, wallet):
    if price > wallet:
        raise NotEnoughMoney(price, wallet)  #! Бросаем своё исключение
    return wallet - price

try:
    buy(500, 120)
except NotEnoughMoney as e:
    print("Ошибка:", e)
    print("Не хватает:", e.need - e.have)
""",
"key": ["`raise X(...)` — бросить исключение.", "Свои исключения — `class MyError(Exception)`.", "В них можно хранить дополнительные данные."],
},
],
},
{
"title": "Файлы и I/O",
"items": ["open()", "read()", "write()", "close()", "with", "context manager", "streams"],
"intro": "Ввод-вывод (I/O): как программа читает и пишет данные в файлы и потоки.",
"lessons": [
{
"title": "open, write и close",
"covers": ["open()", "write()", "close()"],
"text": """`open(путь, режим)` открывает файл и возвращает **файловый объект**. Режимы: `"r"` — читать, `"w"` — записать заново (старое содержимое стирается), `"a"` — дописать в конец. Для русских букв указывай `encoding="utf-8"`.

`write(текст)` пишет строку (перевод строки `\\n` нужно добавлять самому). `close()` закрывает файл и сбрасывает данные на диск. Забыть `close()` — частая ошибка, поэтому обычно используют `with` (следующие уроки).""",
"code": """
f = open("notes.txt", "w", encoding="utf-8")  #! Открываем на запись — файл создаётся
f.write("Купить хлеб\\n")  #! write возвращает число записанных символов
f.write("Позвонить маме\\n")
f.close()  #! Закрываем: данные сохранены на диск
print(f.closed)
g = open("notes.txt", "a", encoding="utf-8")  #! Режим a — дописать в конец
g.write("Выучить Python\\n")
g.close()
print(open("notes.txt", encoding="utf-8").read())
""",
"key": ["`open(path, mode, encoding='utf-8')`.", "`w` — перезаписать, `a` — дописать, `r` — читать.", "После работы файл нужно закрыть."],
},
{
"title": "read и потоки",
"covers": ["read()", "streams"],
"text": """`read()` читает весь файл в одну строку, `readline()` — одну строку, а перебор `for line in f` читает **построчно**, не загружая весь файл в память. Это и есть идея **потока** (stream): данные текут порциями, а файл помнит позицию, где остановился.

Потоки бывают не только файлами: `print` пишет в поток `sys.stdout`, а `io.StringIO` — поток в памяти, который ведёт себя как файл.""",
"code": """
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("первая\\nвторая\\nтретья\\n")

f = open("data.txt", encoding="utf-8")
print(repr(f.readline()))  #! Прочитали одну строку — позиция сдвинулась
for line in f:  #! Продолжаем с текущей позиции, по строке за раз
    print("строка:", line.strip())
f.close()

import io
buf = io.StringIO()  #! Поток в памяти
buf.write("hello ")
buf.write("stream")
print(buf.getvalue())
""",
"key": ["`read()` — всё, `readline()` — строка, `for line in f` — построчно.", "Поток помнит позицию чтения.", "`sys.stdout` и `StringIO` — тоже потоки."],
},
{
"title": "with — файлы без забот",
"covers": ["with", "context manager"],
"text": """`with open(...) as f:` открывает файл и **гарантированно закрывает** его в конце блока — даже если внутри произошла ошибка. Файловый объект — это **контекстный менеджер**: объект, который знает, что делать при входе в блок и при выходе.

Это стандартный и правильный способ работы с файлами. Как это устроено внутри — в разделе 18.""",
"code": """
with open("log.txt", "w", encoding="utf-8") as f:  #! Вход: файл открыт
    f.write("старт\\n")
    print("Внутри блока, закрыт?", f.closed)
print("После блока, закрыт?", f.closed)  #! Выход из with закрыл файл сам

try:
    with open("log.txt", encoding="utf-8") as f:
        print(f.read().strip())
        raise RuntimeError("что-то сломалось")  #! Ошибка внутри блока…
except RuntimeError:
    print("Ошибка, но файл всё равно закрыт:", f.closed)  #! …файл всё равно закрыт
""",
"key": ["`with` сам закрывает файл.", "Работает и при ошибках внутри блока.", "Файл — пример контекстного менеджера."],
},
],
},
{
"title": "Контекстные менеджеры",
"items": ["__enter__", "__exit__", "with", "contextlib"],
"intro": "Шаблон «подготовить → поработать → гарантированно убрать за собой».",
"lessons": [
{
"title": "__enter__ и __exit__",
"covers": ["__enter__", "__exit__", "with"],
"text": """`with obj as x:` работает так: 1) вызывается `obj.__enter__()`, его результат попадает в `x`; 2) выполняется блок; 3) вызывается `obj.__exit__(тип_ошибки, ошибка, трассировка)` — **всегда**, даже при исключении.

Если `__exit__` вернёт `True`, исключение считается обработанным и дальше не полетит. Смотри по шагам, как появляются кадры `__enter__` и `__exit__`.""",
"code": """
class Timer:
    def __enter__(self):  #! Вход в блок with
        print("▶ старт")
        self.steps = 0
        return self  #! Это значение попадёт в переменную после as

    def __exit__(self, exc_type, exc, tb):  #! Выход — всегда
        print("■ стоп, шагов:", self.steps, "ошибка:", exc_type.__name__ if exc_type else None)
        return exc_type is ValueError  #! True = «ошибку я обработал»

with Timer() as t:
    t.steps += 1
    t.steps += 1

with Timer() as t:
    t.steps += 1
    raise ValueError("упс")  #! __exit__ получит эту ошибку и подавит её
print("Программа продолжается")
""",
"key": ["`with` → `__enter__` → блок → `__exit__`.", "`__exit__` вызывается всегда.", "Вернёт `True` — исключение подавлено."],
},
{
"title": "contextlib",
"covers": ["contextlib"],
"text": """Модуль `contextlib` упрощает создание менеджеров. Декоратор `@contextmanager` превращает **генератор** в контекстный менеджер: код до `yield` — это `__enter__`, значение `yield` попадает в `as`, код после — `__exit__`. Оберни `yield` в `try/finally`, чтобы уборка шла даже при ошибке.

Ещё полезное: `contextlib.suppress(Ошибка)` — тихо игнорировать конкретную ошибку.""",
"code": """
from contextlib import contextmanager, suppress

@contextmanager
def tag(name):
    print(f"<{name}>")  #! Это как __enter__
    try:
        yield name.upper()  #! Значение уходит в as; генератор ждёт конца блока
    finally:
        print(f"</{name}>")  #! Это как __exit__ — всегда

with tag("div") as t:
    print("  содержимое", t)

with suppress(KeyError):
    {}["нет такого"]  #! Ошибка тихо подавлена
print("дальше")
""",
"key": ["`@contextmanager` + генератор = простой менеджер.", "До `yield` — вход, после — выход.", "`suppress` — игнорировать конкретное исключение."],
},
],
},
{
"title": "Итераторы и генераторы",
"items": ["iterable", "iterator", "iter()", "next()", "yield", "generator", "generator expression"],
"intro": "Как Python перебирает элементы по одному и как создавать данные «лениво» — только когда они нужны.",
"lessons": [
{
"title": "iterable, iterator, iter() и next()",
"covers": ["iterable", "iterator", "iter()", "next()"],
"text": """**Iterable** (итерируемое) — то, что можно перебрать: список, строка, словарь, файл. **Iterator** (итератор) — объект, который выдаёт элементы по одному и **помнит позицию**.

`iter(iterable)` создаёт итератор, `next(iterator)` берёт следующий элемент. Когда элементы закончились — `StopIteration`. Итератор одноразовый: прошёл до конца — нужно создавать новый. А список можно перебирать сколько угодно раз, потому что каждый `for` создаёт новый итератор.""",
"code": """
colors = ["red", "green", "blue"]  #! Iterable
it = iter(colors)  #! Создаём итератор — у него своя позиция
print(next(it))  #! Первый элемент
print(next(it))  #! Второй — итератор помнит, где был
print(list(it))  #! Остаток
print(list(it))  #! Итератор исчерпан — пусто
try:
    next(it)
except StopIteration:
    print("StopIteration: элементов нет")
""",
"key": ["Iterable — можно перебрать; iterator — перебирает и помнит позицию.", "`iter()` создаёт итератор, `next()` берёт элемент.", "Итератор одноразовый."],
},
{
"title": "yield и generator",
"covers": ["yield", "generator"],
"text": """Функция с `yield` — **генератор**. Её вызов возвращает объект-генератор (который является итератором), а тело выполняется по кусочкам: до `yield` → пауза → до следующего `yield` → пауза…

В визуализаторе объект `generator` показывает своё состояние («на паузе», «завершён») и локальные переменные, которые сохраняются между паузами. Генераторы экономят память: элементы создаются по запросу, а не все сразу.""",
"code": """
def fib():
    a, b = 0, 1
    while True:  #! Бесконечный цикл — но генератору это не страшно
        yield a  #! Отдаём a и замираем
        a, b = b, a + b

gen = fib()  #! Тело не начало выполняться
first = [next(gen) for _ in range(6)]  #! Берём только 6 значений
print(first)
print(next(gen))  #! Можно продолжить с того же места
""",
"key": ["`yield` = отдать значение и встать на паузу.", "Локальные переменные сохраняются между вызовами.", "Генератор ленивый: можно описать даже бесконечную последовательность."],
},
{
"title": "Generator expression",
"covers": ["generator expression"],
"text": """`(x * x for x in data)` — как list comprehension, но в **круглых** скобках. Получается не список, а генератор: значения не создаются заранее, а вычисляются по одному при переборе.

Это экономит память на больших данных. Часто пишется прямо в аргументе функции: `sum(x * x for x in data)`.""",
"code": """
nums = [1, 2, 3, 4]
squares_list = [n * n for n in nums]  #! Список: все значения сразу в памяти
squares_gen = (n * n for n in nums)  #! Генератор: пока ничего не посчитано
print(squares_list)
print(next(squares_gen), next(squares_gen))  #! Считаем по требованию
print(sum(squares_gen))  #! Досчитали остаток: 9 + 16
print(max(len(w) for w in ["кот", "собака", "ёж"]))  #! Генератор прямо в аргументе функции
""",
"key": ["`(expr for x in seq)` — генераторное выражение.", "Ленивое: значения считаются по одному.", "Отлично подходит для `sum`, `max`, `any`, `all`."],
},
],
},
{
"title": "Декораторы",
"items": ["функция как объект", "функция высшего порядка", "decorator", "@decorator", "functools"],
"intro": "Как добавить функции новое поведение, не меняя её код.",
"lessons": [
{
"title": "Функция как объект и функции высшего порядка",
"covers": ["функция как объект", "функция высшего порядка"],
"text": """Функция — обычный объект: её можно присвоить другому имени, положить в словарь, передать аргументом и вернуть из другой функции. Обрати внимание: `say` без скобок — это **сама функция**, а `say()` — **вызов**.

**Функция высшего порядка** — функция, которая принимает другую функцию или возвращает её. `map`, `filter`, `sorted(key=...)` — встроенные примеры.""",
"code": """
def say(text):
    return text + "!"

shout = say  #! Новое имя для ТОЙ ЖЕ функции (без скобок!)
print(shout("эй"))

def apply_twice(func, value):  #! Функция высшего порядка: принимает функцию
    return func(func(value))

print(apply_twice(say, "ура"))

ops = {"+": lambda a, b: a + b, "*": lambda a, b: a * b}  #! Функции в словаре
print(ops["*"](3, 4))
""",
"key": ["`f` — функция, `f()` — её вызов.", "Функции можно передавать и возвращать.", "Функция высшего порядка работает с функциями."],
},
{
"title": "decorator и @decorator",
"covers": ["decorator", "@decorator"],
"text": """Декоратор — функция высшего порядка, которая принимает функцию и возвращает **обёртку**. Обёртка делает что-то до и после вызова оригинала.

Синтаксис `@timer` над `def work` — просто сокращение для `work = timer(work)`. После этого имя `work` указывает на обёртку, а оригинал сохранён в замыкании (видно в памяти как «замыкание: func»). Декоратор может принимать параметры — тогда это функция, возвращающая декоратор (три уровня вложенности).""",
"code": """
def log_calls(func):  #! Декоратор получает функцию
    def wrapper(*args):
        print("→ вызов", func.__name__, args)
        result = func(*args)  #! Вызываем оригинал
        print("← результат", result)
        return result
    return wrapper  #! Возвращаем обёртку

@log_calls  #! То же, что add = log_calls(add)
def add(a, b):
    return a + b

def repeat(n):  #! Декоратор с параметром
    def deco(func):
        def wrapper():
            return [func() for _ in range(n)]
        return wrapper
    return deco

@repeat(3)
def hi():
    return "hi"

add(2, 3)
print(hi())
""",
"key": ["`@deco` над `def f` = `f = deco(f)`.", "Обёртка вызывает оригинал из замыкания.", "Декоратор с параметрами — функция, возвращающая декоратор."],
},
{
"title": "functools",
"covers": ["functools"],
"text": """Модуль `functools` — инструменты для работы с функциями:

`@wraps(func)` внутри декоратора копирует имя и документацию оригинала на обёртку (иначе `__name__` будет `wrapper`). `@lru_cache` запоминает результаты вызовов — повторный вызов с теми же аргументами возвращается мгновенно. `partial` создаёт новую функцию с частично заданными аргументами.""",
"code": """
from functools import wraps, lru_cache, partial

def noisy(func):
    @wraps(func)  #! Сохраняем имя оригинала
    def wrapper(*a):
        return func(*a)
    return wrapper

@noisy
def greet(name):
    return "hi " + name

print(greet.__name__)  #! greet, а не wrapper

@lru_cache
def slow_square(n):
    print("  считаю", n)  #! Напечатается только при первом вызове для n
    return n * n

slow_square(4)
slow_square(4)  #! Результат из кэша — «считаю» не печатается
power2 = partial(pow, 2)  #! pow(2, x) с зафиксированным первым аргументом
print(power2(10))
""",
"key": ["`@wraps` — обёртка сохраняет имя оригинала.", "`@lru_cache` — кэширование результатов.", "`partial` — фиксирует часть аргументов."],
},
],
},
]
