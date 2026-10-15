# Углублённое содержание уроков разделов 16–20.
from deep_a import Q

DEEP = {
# ---------------- 16. Исключения ----------------
"16-1": dict(
deep="""Исключения образуют **иерархию классов**. Корень — `BaseException`; от него идут `Exception` (обычные ошибки), а также `KeyboardInterrupt` и `SystemExit`, которые не стоит ловить случайно. Поэтому `except Exception:` безопаснее голого `except:`.

```
BaseException
 ├── KeyboardInterrupt, SystemExit
 └── Exception
      ├── ArithmeticError → ZeroDivisionError
      ├── LookupError → KeyError, IndexError
      ├── ValueError, TypeError, AttributeError …
```

Когда исключение не поймано, Python печатает **traceback** — стек кадров от места вызова до места ошибки. Читать его нужно **снизу вверх**: последняя строка — тип и сообщение, над ней — строка, где всё сломалось.""",
pitfalls=[
"Голый `except:` ловит даже Ctrl+C и `sys.exit()`.",
"Читать traceback сверху и искать ошибку не там.",
],
links=["16-2", "16-3", "23-1"],
checks=[
Q("Что напечатает код?", ["True True", "True False", "False True", "False False"], 0,
  "`KeyError` — подкласс `LookupError`, а тот — подкласс `Exception`.",
  code="print(issubclass(KeyError, LookupError), issubclass(KeyError, Exception))", run=True),
Q("Почему не стоит писать голый `except:`?", ["Он медленный", "Он ловит и KeyboardInterrupt/SystemExit, мешая остановить программу", "Он не ловит ошибки", "Так нельзя по синтаксису"], 1,
  "Голый except перехватывает все BaseException, включая сигналы остановки."),
]),
"16-2": dict(
deep="""Python проверяет `except`-ветки **сверху вниз** и выбирает первую подходящую по `isinstance`. Поэтому узкие исключения ставят выше широких. Можно ловить несколько типов кортежем: `except (KeyError, IndexError):`.

`finally` выполняется **всегда**: и при `return` внутри `try`, и при исключении. Если `finally` сам делает `return`, он перекрывает и возвращаемое значение, и исключение — так писать не стоит.

```
def f():
    try:
        return "try"
    finally:
        print("finally сработал")
print(f())
```

В `try` держи как можно меньше кода — только то, что действительно может бросить ожидаемое исключение.""",
pitfalls=[
"Ставить `except Exception` выше `except ValueError` — узкая ветка никогда не сработает.",
"`return` в `finally` — проглатывает исключения.",
"Огромный блок `try` — непонятно, какая строка бросила ошибку.",
],
links=["16-1", "18-1", "17-3"],
checks=[
Q("Что напечатает код?", ["try", "finally | try", "try | finally", "finally"], 1,
  "`finally` выполняется перед тем, как функция фактически вернёт значение, поэтому сначала печатается 'finally'.",
  code="def f():\n    try:\n        return 'try'\n    finally:\n        print('finally')\nprint(f())", run=True),
Q("Что напечатает код?", ["общая", "значение", "ничего", "Ошибка"], 0,
  "Ветки проверяются по порядку: `Exception` подходит для `ValueError` и стоит первой.",
  code="try:\n    int('x')\nexcept Exception:\n    print('общая')\nexcept ValueError:\n    print('значение')", run=True),
]),
"16-3": dict(
deep="""`raise X from e` сохраняет исходное исключение в `__cause__` — в traceback видно «The above exception was the direct cause…». Если поднять новое исключение внутри `except` без `from`, Python всё равно сохранит контекст в `__context__`. `raise` без аргументов внутри `except` перебрасывает текущее исключение дальше.

Свою иерархию исключений делают так: один базовый класс для библиотеки (`class ShopError(Exception)`) и конкретные потомки. Тогда пользователь может ловить всё сразу или точечно.

Python 3.11 добавил `ExceptionGroup` и `except*` для нескольких одновременных ошибок (например, из параллельных задач) и `e.add_note(...)` для добавления пояснений.""",
pitfalls=[
"Бросать голый `Exception(\"...\")` — его невозможно поймать точечно.",
"Глушить исключение в `except` и бросать новое без `from` — теряется понятная причина.",
],
links=["16-1", "16-2"],
checks=[
Q("Что напечатает код?", ["KeyError", "ValueError", "None", "Ошибка"], 0,
  "`raise ... from e` сохраняет исходное исключение в атрибуте `__cause__`.",
  code="try:\n    try:\n        {}['x']\n    except KeyError as e:\n        raise ValueError('нет настройки') from e\nexcept ValueError as v:\n    print(type(v.__cause__).__name__)", run=True),
Q("Зачем делать свой базовый класс исключений для библиотеки?", ["Так требует Python", "Чтобы можно было поймать все ошибки библиотеки одним except", "Чтобы исключения были быстрее", "Чтобы не писать сообщения"], 1,
  "Общий предок позволяет ловить всю группу ошибок сразу."),
]),

# ---------------- 17. Файлы и I/O ----------------
"17-1": dict(
deep="""`open()` возвращает объект из модуля `io`, собранный слоями:
- `FileIO` — сырые байты от операционной системы (файловый дескриптор);
- `BufferedWriter`/`BufferedReader` — буфер, чтобы не дёргать диск на каждый байт;
- `TextIOWrapper` — превращает байты в строки по кодировке и обрабатывает переводы строк.

Из-за буфера данные попадают на диск не сразу, а при `flush()` или `close()`. Если программа упадёт до закрытия, последние записи могут потеряться — ещё одна причина использовать `with`.

Режим `"b"` (`"rb"`, `"wb"`) работает с байтами без кодировки — для картинок и бинарных файлов.""",
pitfalls=[
"Открыть без `encoding=\"utf-8\"` — на некоторых системах кириллица превратится в «кракозябры».",
"Режим `\"w\"` стирает существующий файл — для дописывания нужен `\"a\"`.",
"Забыть `\\n` в `write()` — всё окажется в одной строке.",
],
links=["17-3", "17-2"],
checks=[
Q("Что напечатает код?", ["5", "None", "hello", "True"], 0,
  "`write` возвращает количество записанных символов.",
  code="import io\nf = io.StringIO()\nprint(f.write('hello'))", run=True),
Q("Что произойдёт при `open('data.txt', 'w')`, если файл уже существует?", ["Новые данные допишутся в конец", "Файл будет очищен и записан заново", "Ошибка FileExistsError", "Ничего"], 1,
  "Режим 'w' обрезает файл до нуля. Для дописывания используется 'a', для ошибки при существовании — 'x'."),
]),
"17-2": dict(
deep="""Файл — **поток** с текущей позицией. `read()` читает от позиции до конца, `seek(0)` возвращает позицию в начало, `tell()` показывает её. Перебор `for line in f` читает буферизованно, по строке — так можно обработать файл размером с гигабайты.

Строки из файла содержат символ `\\n` в конце — его убирают `line.rstrip("\\n")` или `strip()`.

Для путей удобен `pathlib`:
```
from pathlib import Path
p = Path("notes.txt")
p.write_text("a\\nb\\n", encoding="utf-8")
print(p.read_text(encoding="utf-8").splitlines())   # ['a', 'b']
```""",
pitfalls=[
"Вызывать `read()` второй раз и получать пустую строку — позиция уже в конце.",
"`f.read()` для огромного файла — загрузит всё в память.",
],
links=["17-1", "19-1"],
checks=[
Q("Что напечатает код?", ["'abc' 'abc'", "'abc' ''", "'' ''", "Ошибка"], 1,
  "После первого `read()` позиция в конце, второй `read()` возвращает пустую строку.",
  code="import io\nf = io.StringIO('abc')\nprint(repr(f.read()), repr(f.read()))", run=True),
Q("Как прочитать огромный файл, не загружая его целиком в память?", ["f.read()", "f.readlines()", "for line in f", "list(f)"], 2,
  "Перебор файла читает его по строкам через буфер."),
]),
"17-3": dict(
deep="""`with open(...) as f:` превращается в:
```
f = open(...)
f.__enter__()
try:
    ...тело...
finally:
    f.__exit__(...)   # закрывает файл
```
Так ресурс освобождается при любом выходе из блока: обычном, через `return`, `break` или исключение.

В одном `with` можно открыть несколько ресурсов: `with open(a) as src, open(b, "w") as dst:`. Тот же приём работает для блокировок (`threading.Lock`), соединений с базой, временных папок и т. д.""",
pitfalls=[
"Использовать `f` после выхода из `with` — файл уже закрыт (`ValueError: I/O operation on closed file`).",
"Открывать файлы без `with` и забывать `close()` — утечка дескрипторов.",
],
links=["18-1", "16-2"],
checks=[
Q("Что напечатает код?", ["закрыт", "открыт", "Ошибка", "None"], 0,
  "Даже при выходе через исключение `with` закрывает файл.",
  code="import io\ntry:\n    with io.StringIO('x') as f:\n        raise RuntimeError\nexcept RuntimeError:\n    pass\nprint('закрыт' if f.closed else 'открыт')", run=True),
Q("Во что по сути разворачивается `with`?", ["В цикл while", "В __enter__, затем try/finally с __exit__", "В if/else", "В import"], 1,
  "`with` — это гарантированный вызов `__exit__` через try/finally."),
]),

# ---------------- 18. Контекстные менеджеры ----------------
"18-1": dict(
deep="""`__exit__(exc_type, exc, tb)` получает информацию об исключении (или три `None`, если всё прошло хорошо). Вернул **истину** — исключение подавлено; вернул `None`/`False` — исключение летит дальше. Большинство менеджеров возвращают `None`: они только убирают за собой.

Значение после `as` — это то, что вернул `__enter__`, а не сам объект в `with`. У файлов `__enter__` возвращает `self`, поэтому разницы не видно, но у других менеджеров (например, у блокировок) она есть.

Есть и асинхронная версия — `async with` с `__aenter__`/`__aexit__`.""",
pitfalls=[
"Случайно вернуть `True` из `__exit__` — все ошибки в блоке будут молча проглочены.",
"Путать объект в `with` и значение после `as`.",
],
links=["18-2", "17-3", "16-2"],
checks=[
Q("Что напечатает код?", ["enter | body | exit", "body | enter | exit", "enter | exit | body", "enter | body"], 0,
  "Сначала `__enter__`, затем тело, затем `__exit__`.",
  code="class M:\n    def __enter__(self):\n        print('enter')\n    def __exit__(self, *a):\n        print('exit')\nwith M():\n    print('body')", run=True),
Q("Что напечатает код?", ["X", "<M object>", "None", "Ошибка"], 0,
  "После `as` оказывается то, что вернул `__enter__`.",
  code="class M:\n    def __enter__(self):\n        return 'X'\n    def __exit__(self, *a):\n        pass\nwith M() as v:\n    print(v)", run=True),
]),
"18-2": dict(
deep="""`@contextmanager` оборачивает генератор: `__enter__` запускает его до `yield`, а `__exit__` продолжает после. Если в блоке `with` возникло исключение, оно **бросается внутрь генератора** в точке `yield` — поэтому `try/finally` вокруг `yield` обязателен для уборки.

Другие полезные инструменты `contextlib`:
- `suppress(*исключения)` — проглотить конкретные ошибки;
- `redirect_stdout(buf)` — перенаправить `print`;
- `ExitStack` — открыть заранее неизвестное число ресурсов и закрыть их все;
- `nullcontext()` — пустой менеджер, когда менеджер нужен лишь иногда.""",
pitfalls=[
"Не обернуть `yield` в `try/finally` — при ошибке уборка не выполнится.",
"Сделать в генераторе два `yield` — `RuntimeError: generator didn't stop`.",
],
links=["18-1", "19-2"],
checks=[
Q("Что напечатает код?", ["start | end", "start", "start | body | end", "end"], 0,
  "Блок `with` бросил ошибку, она пришла в генератор, `finally` всё равно выполнился, а `suppress` проглотил ошибку снаружи.",
  code="from contextlib import contextmanager, suppress\n@contextmanager\ndef cm():\n    print('start')\n    try:\n        yield\n    finally:\n        print('end')\nwith suppress(ValueError):\n    with cm():\n        raise ValueError", run=True),
Q("Что напечатает код?", ["hi", "''", "None", "Ошибка"], 0,
  "`redirect_stdout` перенаправил print в буфер, затем мы печатаем содержимое буфера.",
  code="import io\nfrom contextlib import redirect_stdout\nbuf = io.StringIO()\nwith redirect_stdout(buf):\n    print('hi')\nprint(buf.getvalue().strip())", run=True),
]),

# ---------------- 19. Итераторы и генераторы ----------------
"19-1": dict(
deep="""Протокол итерации:
- **iterable**: `iter(x)` возвращает итератор (метод `__iter__`);
- **iterator**: `next(it)` возвращает следующий элемент или бросает `StopIteration`; сам итератор тоже iterable (`__iter__` возвращает self).

Функции `map`, `filter`, `zip`, `enumerate`, `reversed` возвращают **ленивые итераторы**: элементы вычисляются по требованию и только один раз. Модуль `itertools` — набор строительных блоков для потоков данных: `islice`, `chain`, `count`, `groupby`, `product`.

```
from itertools import islice, count
print(list(islice(count(10), 3)))   # [10, 11, 12]
```""",
pitfalls=[
"Перебирать результат `map`/`zip` второй раз — он уже исчерпан.",
"Вызывать `len()` у итератора — `TypeError`.",
],
links=["19-2", "11-3", "3-3"],
checks=[
Q("Что напечатает код?", ["[2, 4] [2, 4]", "[2, 4] []", "[] []", "Ошибка"], 1,
  "`map` возвращает одноразовый итератор.",
  code="m = map(lambda x: x * 2, [1, 2])\nprint(list(m), list(m))", run=True),
Q("Что напечатает код?", ["[(1, 'a'), (2, 'b')]", "[(1, 'a'), (2, 'b'), (3, None)]", "Ошибка", "[1, 2, 'a', 'b']"], 0,
  "`zip` останавливается на самой короткой последовательности.",
  code="print(list(zip([1, 2, 3], 'ab')))", run=True),
]),
"19-2": dict(
deep="""Генератор — это функция с «замороженным» кадром. Кроме `next()`, у него есть:
- `send(value)` — продолжить и передать значение: оно станет результатом выражения `yield` внутри;
- `throw(exc)` — бросить исключение в точку `yield`;
- `close()` — завершить генератор (внутри возникнет `GeneratorExit`).

`yield from другой_итерируемый` делегирует выдачу значений вложенному генератору — удобно для рекурсивных структур:
```
def flat(items):
    for x in items:
        if isinstance(x, list): yield from flat(x)
        else: yield x
print(list(flat([1, [2, [3]], 4])))   # [1, 2, 3, 4]
```""",
pitfalls=[
"Ждать, что `return value` в генераторе вернёт значение в `for` — оно попадает в `StopIteration.value`.",
"Хранить генератор и забыть, что его нельзя «перемотать» назад.",
],
links=["19-1", "19-3", "4-8"],
checks=[
Q("Что напечатает код?", ["[1, 2, 3, 4]", "[1, [2, [3]], 4]", "[1, 4]", "Ошибка"], 0,
  "`yield from` рекурсивно разворачивает вложенные списки.",
  code="def flat(items):\n    for x in items:\n        if isinstance(x, list):\n            yield from flat(x)\n        else:\n            yield x\nprint(list(flat([1, [2, [3]], 4])))", run=True),
Q("Что напечатает код?", ["A 1", "A B", "1 2", "A"], 1,
  "Первый `next` выполняет тело до первого yield ('A'), второй — до второго ('B').",
  code="def g():\n    yield 'A'\n    yield 'B'\nit = g()\nprint(next(it), next(it))", run=True),
]),
"19-3": dict(
deep="""Генераторное выражение `(expr for x in it)` создаёт объект-генератор, почти не занимая памяти, сколько бы элементов ни было. Список `[expr for x in it]` хранит все результаты сразу.

```
import sys
print(sys.getsizeof([x for x in range(10**6)]) > 1_000_000)  # True
print(sys.getsizeof(x for x in range(10**6)) < 1000)          # True
```

Первая (самая левая) последовательность вычисляется **сразу**, при создании выражения; остальное — лениво. Если генераторное выражение — единственный аргумент функции, скобки можно не дублировать: `sum(x * x for x in data)`.""",
pitfalls=[
"Использовать генераторное выражение там, где результат нужен несколько раз (он одноразовый).",
"Ждать от `(x for x in data)` кортеж — это генератор; кортеж — `tuple(...)`.",
],
links=["3-7", "19-2"],
checks=[
Q("Что напечатает код?", ["generator", "tuple", "list", "Ошибка"], 0,
  "Круглые скобки вокруг comprehension дают генератор, а не кортеж.",
  code="print(type(x for x in 'ab').__name__)", run=True),
Q("Что напечатает код?", ["True", "False", "[True, False]", "Ошибка"], 0,
  "`any` останавливается на первом истинном значении генератора.",
  code="print(any(n > 2 for n in [1, 5, 0]))", run=True),
]),

# ---------------- 20. Декораторы ----------------
"20-1": dict(
deep="""Функция высшего порядка — функция, которая работает с функциями: принимает их или возвращает. Это основа функционального стиля: `map`, `filter`, `sorted(key=...)`, `functools.reduce`.

```
from functools import reduce
print(reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))   # 24
```

У объекта-функции много полезных атрибутов: `__name__`, `__doc__`, `__defaults__`, `__code__`, `__closure__`, `__annotations__`. Можно даже добавлять свои атрибуты: `f.calls = 0`.""",
pitfalls=[
"Передать результат вызова вместо функции: `map(str.upper(), ...)`.",
"Писать `reduce` там, где читаемее `sum`, `max` или цикл.",
],
links=["5-1", "20-2", "4-5"],
checks=[
Q("Что напечатает код?", ["24", "10", "4", "Ошибка"], 0,
  "reduce последовательно умножает: 1·1·2·3·4 = 24.",
  code="from functools import reduce\nprint(reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))", run=True),
Q("Что напечатает код?", ["['A', 'B']", "['a', 'b']", "Ошибка", "AB"], 0,
  "`map` принимает саму функцию `str.upper` и применяет её к каждому элементу.",
  code="print(list(map(str.upper, ['a', 'b'])))", run=True),
]),
"20-2": dict(
deep="""Декоратор работает в два момента:
1. **время определения**: `@deco` над `def f` выполняет `f = deco(f)` один раз;
2. **время вызова**: при каждом `f(...)` выполняется обёртка.

Шаблон декоратора:
```
import functools
def deco(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # до
        result = func(*args, **kwargs)
        # после
        return result
    return wrapper
```

Декоратор с параметрами — функция, которая **возвращает декоратор** (три уровня). Декорировать можно и классы: `@dataclass` — пример декоратора класса.""",
pitfalls=[
"Забыть `return result` в обёртке — функция начнёт возвращать `None`.",
"Не использовать `*args, **kwargs` — обёртка сломается на функциях с другой сигнатурой.",
"Забыть `@wraps` — пропадут имя и документация функции.",
],
links=["20-3", "4-6", "4-4"],
checks=[
Q("Что напечатает код?", ["5", "None", "10", "Ошибка"], 1,
  "Обёртка вызывает функцию, но не возвращает её результат, поэтому получаем None.",
  code="def deco(func):\n    def wrapper(*a):\n        func(*a)\n    return wrapper\n@deco\ndef add(a, b):\n    return a + b\nprint(add(2, 3))", run=True),
Q("Что напечатает код?", ["def | call", "call | def", "call", "def"], 0,
  "Декоратор применяется при определении функции ('def'), обёртка срабатывает при вызове ('call').",
  code="def deco(func):\n    print('def')\n    def wrapper():\n        print('call')\n    return wrapper\n@deco\ndef f():\n    pass\nf()", run=True),
]),
"20-3": dict(
deep="""`functools.wraps(func)` копирует в обёртку `__name__`, `__doc__`, `__module__`, `__qualname__` и ставит `__wrapped__` — ссылку на оригинал (её используют `inspect` и отладчики).

`lru_cache(maxsize=128)` хранит словарь «аргументы → результат» и вытесняет давно не использованные записи. Аргументы должны быть хешируемыми. `cache` (3.9+) — без ограничения размера. Статистику показывает `f.cache_info()`.

Ещё полезное: `partial` (зафиксировать аргументы), `singledispatch` (разные реализации функции по типу первого аргумента), `cached_property`, `total_ordering`.""",
pitfalls=[
"Кэшировать функцию с изменяемыми аргументами (списками) — `TypeError: unhashable type`.",
"Кэшировать функции с побочными эффектами или зависящие от времени.",
],
links=["20-2", "4-7", "11-4"],
checks=[
Q("Что напечатает код?", ["CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)", "CacheInfo(hits=0, misses=2, maxsize=128, currsize=2)", "2", "Ошибка"], 0,
  "Первый вызов — промах (вычисление), второй с тем же аргументом — попадание в кэш.",
  code="from functools import lru_cache\n@lru_cache(maxsize=128)\ndef sq(n):\n    return n * n\nsq(3); sq(3)\nprint(sq.cache_info())", run=True),
Q("Что напечатает код?", ["8", "6", "9", "Ошибка"], 0,
  "`partial(pow, 2)` фиксирует первый аргумент: pow(2, 3) = 8.",
  code="from functools import partial\nprint(partial(pow, 2)(3))", run=True),
]),
}
