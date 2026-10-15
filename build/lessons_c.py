# Разделы 11–15: специальные методы, дескрипторы, property, метаклассы, модули.

SECTIONS = [
{
"title": "Специальные методы",
"items": ["__str__", "__repr__", "__len__", "__getitem__", "__setitem__", "__iter__", "__next__", "__eq__", "__lt__", "__add__", "__call__", "..."],
"intro": "Методы с двойными подчёркиваниями (dunder-методы) — это «крючки», через которые Python подключает твои объекты к встроенному синтаксису: `print`, `len`, `[]`, `for`, `==`, `+`, `()`. Ты их не вызываешь напрямую — их вызывает Python.",
"lessons": [
{
"title": "__str__ и __repr__",
"covers": ["__str__", "__repr__"],
"text": """`__str__` отвечает за **красивый текст для людей** — его использует `print()` и `str()`. `__repr__` — за **точное описание для программиста** — его видно в отладчике, в консоли и когда объект лежит внутри списка.

Хорошее правило: `__repr__` должен выглядеть как код, которым можно создать такой же объект.""",
"code": """
class Money:
    def __init__(self, amount, cur):
        self.amount = amount
        self.cur = cur

    def __str__(self):  #! Для людей
        return f"{self.amount} {self.cur}"

    def __repr__(self):  #! Для программистов
        return f"Money({self.amount!r}, {self.cur!r})"

m = Money(100, "₽")
print(m)  #! print вызывает __str__
print([m])  #! Внутри списка используется __repr__
print(repr(m))
""",
"key": ["`print(obj)` → `__str__`.", "Отладка, консоль, содержимое списков → `__repr__`.", "Если `__str__` нет, Python берёт `__repr__`."],
},
{
"title": "__len__, __getitem__, __setitem__",
"covers": ["__len__", "__getitem__", "__setitem__"],
"text": """Эти методы делают объект похожим на коллекцию. `len(obj)` вызывает `obj.__len__()`, `obj[k]` — `obj.__getitem__(k)`, а `obj[k] = v` — `obj.__setitem__(k, v)`.

Смотри: в визуализаторе каждый `[]` превращается в вызов метода — появляется кадр `__getitem__()` или `__setitem__()`.""",
"code": """
class Playlist:
    def __init__(self, *songs):
        self.songs = list(songs)

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, i):  #! Срабатывает на p[i]
        return self.songs[i]

    def __setitem__(self, i, value):  #! Срабатывает на p[i] = value
        self.songs[i] = value.upper()

p = Playlist("intro", "song", "outro")
print(len(p))  #! → p.__len__()
print(p[1])  #! → p.__getitem__(1)
p[0] = "opening"  #! → p.__setitem__(0, "opening")
print(p.songs)
""",
"key": ["`len()` → `__len__`.", "`obj[k]` → `__getitem__`, `obj[k] = v` → `__setitem__`.", "Так строятся собственные коллекции."],
},
{
"title": "__iter__ и __next__",
"covers": ["__iter__", "__next__"],
"text": """Цикл `for` работает через два метода. Сначала `iter(obj)` вызывает `obj.__iter__()` и получает **итератор**. Потом цикл раз за разом вызывает `__next__()` у итератора, пока тот не бросит `StopIteration` — сигнал «элементы кончились».

Ниже класс сам себе итератор: `__iter__` возвращает `self`.""",
"code": """
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):  #! for сначала вызывает этот метод
        return self

    def __next__(self):  #! …а потом этот — на каждом круге
        if self.current <= 0:
            raise StopIteration  #! Сигнал циклу: стоп
        self.current -= 1
        return self.current + 1

for n in Countdown(3):
    print(n)
""",
"key": ["`for` = `iter()` + много `next()` + перехват `StopIteration`.", "`__iter__` возвращает итератор.", "`__next__` отдаёт следующий элемент или бросает `StopIteration`."],
},
{
"title": "__eq__ и __lt__",
"covers": ["__eq__", "__lt__"],
"text": """`a == b` вызывает `a.__eq__(b)`. Без него объекты равны, только если это один и тот же объект. `a < b` вызывает `a.__lt__(b)` — и этого достаточно, чтобы `sorted()` и `min()` научились сортировать твои объекты.

Модуль `functools.total_ordering` по `__eq__` и `__lt__` достроит `<=`, `>`, `>=`.""",
"code": """
class Version:
    def __init__(self, major, minor):
        self.major, self.minor = major, minor

    def __eq__(self, other):  #! Правило равенства
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other):  #! Правило «меньше» — этого хватит sorted()
        return (self.major, self.minor) < (other.major, other.minor)

    def __repr__(self):
        return f"v{self.major}.{self.minor}"

print(Version(1, 2) == Version(1, 2))  #! Разные объекты, но равны по правилу
vs = [Version(2, 0), Version(1, 5), Version(1, 10)]
print(sorted(vs))  #! sorted использует __lt__
""",
"key": ["`==` → `__eq__`, `<` → `__lt__`.", "`__lt__` достаточно для `sorted`, `min`, `max`.", "Без `__eq__` сравнивается identity."],
},
{
"title": "__add__ и __call__",
"covers": ["__add__", "__call__"],
"text": """`a + b` вызывает `a.__add__(b)` — так можно научить свои объекты складываться (векторы, деньги, матрицы). Есть и другие: `__sub__`, `__mul__`, `__truediv__`.

`__call__` превращает объект в «функцию»: `obj(x)` вызывает `obj.__call__(x)`. Такой объект может хранить состояние между вызовами.""",
"code": """
class Vec:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, other):  #! v1 + v2
        return Vec(self.x + other.x, self.y + other.y)
    def __repr__(self):
        return f"Vec({self.x}, {self.y})"

class Multiplier:
    def __init__(self, k):
        self.k = k
    def __call__(self, x):  #! Объект можно вызывать как функцию
        return x * self.k

print(Vec(1, 2) + Vec(3, 4))
triple = Multiplier(3)
print(triple(5), callable(triple))
""",
"key": ["`+` → `__add__` (и `-` → `__sub__`, `*` → `__mul__`…).", "`obj()` → `__call__`.", "Операторы в Python — это вызовы методов."],
},
{
"title": "И другие: __contains__, __bool__, __hash__ …",
"covers": ["..."],
"text": """Dunder-методов десятки. Самые полезные из остальных: `__contains__` (оператор `in`), `__bool__` (истинность в `if`), `__hash__` (можно ли класть в `set` и делать ключом `dict`), `__enter__/__exit__` (`with`, раздел 18), `__get__/__set__` (дескрипторы, раздел 12), `__init_subclass__` (раздел 14).

Принцип всегда один: синтаксис Python → вызов соответствующего dunder-метода.""",
"code": """
class Team:
    def __init__(self, *names):
        self.names = set(names)
    def __contains__(self, name):  #! Оператор in
        return name in self.names
    def __bool__(self):  #! Истинность в if
        return len(self.names) > 0
    def __hash__(self):  #! Позволяет класть объект в set
        return hash(frozenset(self.names))
    def __eq__(self, other):
        return self.names == other.names

t = Team("Аня", "Боря")
print("Аня" in t, "Гоша" in t)
if not Team():
    print("Пустая команда — ложь")
print(len({t, Team("Боря", "Аня")}))  #! Равные команды с одним хешем — в set один элемент
""",
"key": ["`in` → `__contains__`, `if obj` → `__bool__`.", "`__hash__` нужен для set и ключей dict.", "Синтаксис → dunder-метод: это общее правило."],
},
],
},
{
"title": "Дескрипторы",
"items": ["__get__", "__set__", "__delete__", "property", "descriptor protocol"],
"intro": "Механизм, который стоит за `property`, методами, `classmethod` и `staticmethod`. Дескриптор — объект в классе, который перехватывает чтение, запись и удаление атрибута.",
"lessons": [
{
"title": "Протокол дескрипторов",
"covers": ["descriptor protocol", "__get__", "__set__", "__delete__"],
"text": """Если в **классе** лежит объект с методами `__get__`, `__set__` или `__delete__`, он становится **дескриптором**. Теперь обращение `obj.attr` не просто читает значение, а вызывает `Descriptor.__get__(obj, type)`; присваивание `obj.attr = v` — `__set__(obj, v)`; `del obj.attr` — `__delete__(obj)`.

Это и есть **descriptor protocol**. Ниже дескриптор `Positive` проверяет, что значение положительное, и его можно переиспользовать для разных полей.""",
"code": """
class Positive:
    def __set_name__(self, owner, name):
        self.name = "_" + name  #! Запоминаем, где хранить значение

    def __get__(self, obj, objtype=None):  #! Чтение obj.price
        return getattr(obj, self.name, 0)

    def __set__(self, obj, value):  #! Запись obj.price = …
        if value <= 0:
            raise ValueError(f"{self.name[1:]} должно быть > 0")
        setattr(obj, self.name, value)

    def __delete__(self, obj):  #! del obj.price
        print("Удаляем", self.name)
        delattr(obj, self.name)

class Product:
    price = Positive()  #! Дескриптор живёт в КЛАССЕ
    weight = Positive()

p = Product()
p.price = 250  #! → Positive.__set__(p, 250)
print(p.price)  #! → Positive.__get__(p, Product)
try:
    p.weight = -1
except ValueError as e:
    print(e)
del p.price  #! → Positive.__delete__(p)
""",
"key": ["Дескриптор — объект в классе с `__get__`/`__set__`/`__delete__`.", "Он перехватывает доступ к атрибуту у экземпляров.", "Один дескриптор можно использовать для многих полей."],
},
{
"title": "property — готовый дескриптор",
"covers": ["property"],
"text": """`property` — встроенный дескриптор, который вызывает твои функции при чтении и записи атрибута. Поэтому `obj.area` выглядит как поле, а на деле вызывает метод.

Даже обычные методы работают через дескрипторы: функция в классе имеет `__get__`, который и превращает её в «привязанный метод» с `self`. Проверим это в коде.""",
"code": """
class Rect:
    def __init__(self, w, h):
        self.w, self.h = w, h

    @property
    def area(self):  #! Вычисляется при каждом чтении
        return self.w * self.h

    def describe(self):
        return f"{self.w}×{self.h}"

r = Rect(3, 4)
print(r.area)  #! Без скобок — но вызывается функция
r.w = 10
print(r.area)  #! Пересчиталось автоматически
print(type(Rect.__dict__["area"]).__name__)  #! В классе лежит объект property
print(hasattr(Rect.__dict__["describe"], "__get__"))  #! У функции тоже есть __get__!
""",
"key": ["`property` — это дескриптор.", "Методы — тоже дескрипторы (функции имеют `__get__`).", "Подробнее про property — в разделе 13."],
},
],
},
{
"title": "Property",
"items": ["getter", "setter", "deleter", "управление доступом к атрибутам"],
"intro": "Как сделать атрибут, который выглядит как обычное поле, но под капотом проверяет, вычисляет или защищает данные.",
"lessons": [
{
"title": "getter и setter",
"covers": ["getter", "setter"],
"text": """`@property` над методом делает его **getter**-ом: `obj.celsius` вызывает метод без скобок. `@celsius.setter` задаёт **setter**: `obj.celsius = 30` вызывает его с новым значением.

Снаружи — обычное поле. Внутри — проверки и логика. Данные хранятся в «скрытом» атрибуте `_celsius`.""",
"code": """
class Thermometer:
    def __init__(self, c):
        self.celsius = c  #! Даже здесь срабатывает setter

    @property
    def celsius(self):  #! getter
        return self._celsius

    @celsius.setter
    def celsius(self, value):  #! setter — с проверкой
        if value < -273.15:
            raise ValueError("Ниже абсолютного нуля!")
        self._celsius = value

    @property
    def fahrenheit(self):  #! Вычисляемое свойство без setter
        return self._celsius * 9 / 5 + 32

t = Thermometer(25)
t.celsius = 30  #! Выглядит как присваивание — на деле вызов setter
print(t.celsius, t.fahrenheit)
try:
    t.celsius = -300
except ValueError as e:
    print(e)
""",
"key": ["`@property` → getter, `@имя.setter` → setter.", "Значение хранят в `_имя`.", "Можно добавить проверку, не меняя код, который использует класс."],
},
{
"title": "deleter и управление доступом",
"covers": ["deleter", "управление доступом к атрибутам"],
"text": """`@имя.deleter` срабатывает на `del obj.имя`. А если setter **не объявить**, атрибут станет **только для чтения** — попытка записи даст `AttributeError`.

Так property управляет доступом: что можно читать, что писать, что удалять, и что при этом проверять или логировать.""",
"code": """
class User:
    def __init__(self, login):
        self._login = login
        self._token = "abc123"

    @property
    def login(self):  #! Только getter — значит только чтение
        return self._login

    @property
    def token(self):
        return self._token[:2] + "***"  #! Показываем частично

    @token.deleter
    def token(self):  #! Выход из системы
        print("Токен удалён")
        self._token = ""

u = User("anna")
print(u.login, u.token)
try:
    u.login = "hacker"
except AttributeError as e:
    print("Запрещено:", e)
del u.token
""",
"key": ["`@имя.deleter` → `del obj.имя`.", "Нет setter — атрибут только для чтения.", "property позволяет контролировать чтение, запись и удаление."],
},
],
},
{
"title": "Метаклассы",
"items": ["type", "class creation", "metaclass", "__new__", "__init_subclass__"],
"intro": "Классы — тоже объекты, а значит, их кто-то создаёт. Этот «кто-то» — метакласс. По умолчанию это `type`.",
"lessons": [
{
"title": "type и создание класса",
"covers": ["type", "class creation"],
"text": """`type` — не только функция «узнать тип». Это **класс всех классов**: `type(Dog)` — это `type`. И им можно создать класс вручную: `type("Dog", (Base,), {"sound": "Гав"})` — имя, родители, словарь атрибутов.

Инструкция `class` делает то же самое: выполняет тело, собирает словарь атрибутов и вызывает `type(имя, родители, словарь)`.""",
"code": """
class Cat:  #! Обычный способ
    sound = "Мяу"

def bark(self):
    return "Гав"

Dog = type("Dog", (), {"sound": "Гав", "speak": bark})  #! Класс без слова class!
print(Dog().speak(), Dog.sound)
print(type(Cat), type(Dog))  #! Оба класса созданы type
print(type(type))  #! type — сам себе тип
""",
"key": ["`type(name, bases, dict)` создаёт класс.", "`class` — удобная запись для того же.", "Тип любого класса по умолчанию — `type`."],
},
{
"title": "metaclass и __new__",
"covers": ["metaclass", "__new__"],
"text": """**Метакласс** — класс, экземпляры которого — классы. Наследуешь от `type`, переопределяешь `__new__` (создание класса) — и можешь вмешаться в момент, когда пишется `class ...:`. Например, автоматически регистрировать классы или проверять, что у них есть нужные методы.

`__new__` у метакласса получает: сам метакласс, имя будущего класса, родителей и словарь атрибутов.""",
"code": """
registry = {}

class PluginMeta(type):
    def __new__(mcls, name, bases, attrs):  #! Вызывается при создании КЛАССА
        cls = super().__new__(mcls, name, bases, attrs)
        if bases:  #! Базовый класс не регистрируем
            registry[name.lower()] = cls
        return cls

class Plugin(metaclass=PluginMeta):
    pass

class Csv(Plugin):  #! В этот момент сработает PluginMeta.__new__
    pass

class Json(Plugin):
    pass

print(registry)
print(type(Csv).__name__)
""",
"key": ["Метакласс создаёт классы, как класс создаёт объекты.", "`__new__` метакласса срабатывает при выполнении `class ...:`.", "Нужен редко: чаще хватает декоратора класса или `__init_subclass__`."],
},
{
"title": "__init_subclass__",
"covers": ["__init_subclass__"],
"text": """`__init_subclass__` — простая альтернатива метаклассам. Этот метод родителя вызывается **автоматически при создании каждого потомка**. Можно зарегистрировать потомка или проверить, что он объявил обязательные атрибуты.""",
"code": """
class Command:
    commands = {}

    def __init_subclass__(cls, name, **kw):  #! Вызывается при создании потомка
        super().__init_subclass__(**kw)
        Command.commands[name] = cls

class Hello(Command, name="hello"):  #! Параметр name уходит в __init_subclass__
    def run(self):
        return "Привет!"

class Bye(Command, name="bye"):
    def run(self):
        return "Пока!"

print(list(Command.commands))
print(Command.commands["bye"]().run())
""",
"key": ["`__init_subclass__` вызывается при создании подкласса.", "Принимает параметры из строки `class X(Base, param=...)`.", "Проще метакласса для регистрации и проверок."],
},
],
},
{
"title": "Модули и пакеты",
"items": ["module", "package", "import", "from ... import", "__name__", "__main__", "__init__.py", "namespace"],
"intro": "Как разложить код по файлам и папкам и собрать его вместе.",
"lessons": [
{
"title": "Модуль и import",
"covers": ["module", "import", "from ... import", "namespace"],
"opts": {"show_modules": True},
"files": {"geometry.py": "PI = 3.14159\n\ndef circle_area(r):\n    return PI * r * r\n\nprint('geometry загружен')\n"},
"text": """**Модуль** — это просто файл `.py`. `import geometry` выполняет этот файл **один раз** и создаёт объект-модуль; его содержимое доступно через точку: `geometry.PI`. У каждого модуля своё **пространство имён** (namespace) — поэтому имена из разных файлов не конфликтуют.

`from geometry import circle_area` берёт из модуля конкретное имя и кладёт его в **твоё** пространство имён. Повторный `import` не выполняет файл заново — модуль берётся из кэша `sys.modules`.""",
"code": """
import geometry  #! Выполняется geometry.py, создаётся объект-модуль
print(geometry.PI)  #! Доступ через имя модуля
from geometry import circle_area  #! Копируем одно имя в наше пространство имён
print(circle_area(2))
import geometry  #! Повторный импорт — файл НЕ выполняется второй раз
import math as m  #! Псевдоним
print(m.sqrt(16))
""",
"key": ["Модуль = файл .py, выполняется при первом импорте.", "`import m` → `m.имя`; `from m import имя` → просто `имя`.", "У каждого модуля своё пространство имён."],
},
{
"title": "Пакет и __init__.py",
"covers": ["package", "__init__.py"],
"opts": {"show_modules": True},
"files": {
"shop/__init__.py": "print('пакет shop инициализирован')\nfrom .cart import Cart\n",
"shop/cart.py": "class Cart:\n    def __init__(self):\n        self.items = []\n    def add(self, item):\n        self.items.append(item)\n        return self\n",
},
"text": """**Пакет** — папка с модулями. Файл `__init__.py` внутри папки выполняется при импорте пакета: в нём часто «поднимают» важные имена наверх, чтобы писать `from shop import Cart` вместо `from shop.cart import Cart`.

Импорт внутри пакета пишут с точкой: `from .cart import Cart` — «из соседнего модуля».""",
"code": """
import shop  #! Выполняется shop/__init__.py
from shop.cart import Cart  #! Полный путь: пакет.модуль
from shop import Cart as C2  #! Короткий путь — благодаря __init__.py
print(Cart is C2)  #! Это один и тот же класс
c = Cart().add("хлеб").add("сыр")
print(c.items)
""",
"key": ["Пакет = папка с модулями.", "`__init__.py` выполняется при импорте пакета.", "`from .модуль import X` — импорт внутри пакета."],
},
{
"title": "__name__ и __main__",
"covers": ["__name__", "__main__"],
"opts": {"show_name": True},
"files": {"tools.py": "def shout(s):\n    return s.upper() + '!'\n\nprint('tools: __name__ =', __name__)\n\nif __name__ == '__main__':\n    print('Запущен как программа — тесты')\n"},
"text": """У каждого модуля есть переменная `__name__`. Если файл **запущен напрямую** (`python tools.py`), в ней лежит строка `"__main__"`. Если файл **импортирован**, там его имя — `"tools"`.

Поэтому блок `if __name__ == "__main__":` выполняется только при прямом запуске. Туда кладут демонстрацию или тесты, которые не должны срабатывать при импорте.""",
"code": """
print("Этот файл:", __name__)  #! Мы запущены напрямую → "__main__"
import tools  #! В tools.py __name__ будет "tools", поэтому блок if там не сработает
print(tools.shout("привет"))
if __name__ == "__main__":
    print("Главная программа стартует")  #! Сработает: мы — главный модуль
""",
"key": ["Запущен напрямую → `__name__ == '__main__'`.", "Импортирован → `__name__` = имя модуля.", "`if __name__ == '__main__':` — точка входа программы."],
},
],
},
]
