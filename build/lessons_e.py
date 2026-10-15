# Разделы 21–25: типизация, dataclass, память, архитектура, паттерны проектирования.

SECTIONS = [
{
"title": "Типизация",
"items": ["type hints", "TypeVar", "Generic", "Union", "Optional", "Literal", "Protocol", "TypedDict", "dataclass"],
"intro": "Подсказки типов не меняют выполнение программы, но помогают редактору и инструментам (mypy, pyright) находить ошибки ещё до запуска.",
"lessons": [
{
"title": "Type hints",
"covers": ["type hints"],
"text": """Аннотации `name: str`, `-> int` — это **подсказки**, а не проверки. Python их сохраняет (в `__annotations__`), но при выполнении не проверяет: передашь число вместо строки — Python не остановит. Ловят такие ошибки редактор и проверяльщики типов.

Зачем тогда? Код становится самодокументируемым, а автодополнение — умным.""",
"code": """
def greet(name: str, times: int = 1) -> str:  #! Подсказки: ожидается str и int, вернётся str
    return ", ".join([f"Привет, {name}"] * times)

scores: list[int] = [5, 4, 5]  #! Аннотация переменной
print(greet("Аня", 2))
print(greet.__annotations__)  #! Подсказки хранятся, но не проверяются
print(greet(42))  #! Python не мешает — ошибку найдёт только mypy/редактор
""",
"key": ["Аннотации не проверяются при выполнении.", "`x: int`, `def f(a: str) -> bool`.", "Проверяют их mypy, pyright и редактор."],
},
{
"title": "Union, Optional, Literal",
"covers": ["Union", "Optional", "Literal"],
"text": """`Union[int, str]` или `int | str` — «одно из». `Optional[str]` = `str | None` — «строка или ничего». `Literal["r", "w"]` — «только одно из этих конкретных значений».

Такие подсказки заставляют помнить о краевых случаях: если функция возвращает `Optional`, проверяльщик напомнит проверить на `None`.""",
"code": """
from typing import Optional, Literal

def find_user(uid: int) -> Optional[str]:  #! Может вернуть None
    users = {1: "Аня", 2: "Боря"}
    return users.get(uid)

def to_text(value: int | str) -> str:  #! Union: int или str
    return value if isinstance(value, str) else str(value)

Mode = Literal["light", "dark"]

def set_theme(mode: Mode) -> str:  #! Только "light" или "dark"
    return "тема: " + mode

name = find_user(3)
if name is None:  #! Optional напоминает про эту проверку
    print("не найден")
print(to_text(5), to_text("пять"), set_theme("dark"))
""",
"key": ["`A | B` = `Union[A, B]`.", "`Optional[X]` = `X | None`.", "`Literal[...]` — фиксированный набор значений."],
},
{
"title": "TypeVar и Generic",
"covers": ["TypeVar", "Generic"],
"text": """`TypeVar` — «переменная для типа». `def first(items: list[T]) -> T` говорит: «какого типа элементы — того типа и результат». Передал `list[int]` — получишь `int`.

`Generic[T]` позволяет сделать **обобщённый класс**: `Box[int]`, `Box[str]` — одна реализация, разные типы содержимого. В Python 3.12+ можно писать короче: `class Box[T]:`.""",
"code": """
from typing import TypeVar, Generic

T = TypeVar("T")  #! Переменная типа

def first(items: list[T]) -> T:  #! Тип результата = тип элементов
    return items[0]

class Box(Generic[T]):  #! Обобщённый класс
    def __init__(self, item: T):
        self.item = item
    def get(self) -> T:
        return self.item

print(first([3, 1, 2]), first(["a", "b"]))
int_box: Box[int] = Box(42)
str_box: Box[str] = Box("текст")
print(int_box.get(), str_box.get())
""",
"key": ["`TypeVar` связывает типы входа и выхода.", "`Generic[T]` — обобщённый класс.", "Это всё подсказки — на выполнение не влияют."],
},
{
"title": "TypedDict, Protocol и dataclass в типизации",
"covers": ["TypedDict", "Protocol", "dataclass"],
"text": """`TypedDict` описывает **форму словаря**: какие ключи и какого типа значения. Во время выполнения это обычный `dict`. `Protocol` — описание интерфейса по структуре (подробно в разделах 9–10). `@dataclass` — класс с типизированными полями, для которого Python генерирует методы (подробно в разделе 22).

Вместе они дают три способа описать «данные определённой формы».""",
"code": """
from typing import TypedDict, Protocol
from dataclasses import dataclass

class MovieDict(TypedDict):  #! Форма словаря
    title: str
    year: int

class HasTitle(Protocol):  #! Интерфейс: «есть title»
    title: str

@dataclass
class Movie:  #! Класс-данные
    title: str
    year: int

m1: MovieDict = {"title": "Матрица", "year": 1999}
m2 = Movie("Интерстеллар", 2014)
print(type(m1).__name__, m1["title"])  #! TypedDict — это просто dict
print(m2)

def show(x: HasTitle) -> str:
    return x.title

print(show(m2))
""",
"key": ["TypedDict — типизированная форма словаря.", "Protocol — интерфейс по структуре.", "dataclass — класс для данных с типами полей."],
},
],
},
{
"title": "Dataclass",
"items": ["@dataclass", "fields", "default", "frozen", "автоматическая генерация методов"],
"intro": "Как описать класс для данных в пять строк вместо двадцати.",
"lessons": [
{
"title": "@dataclass и автогенерация методов",
"covers": ["@dataclass", "fields", "автоматическая генерация методов"],
"text": """Декоратор `@dataclass` читает **поля** (fields) — аннотированные атрибуты класса — и **автоматически генерирует** `__init__`, `__repr__` и `__eq__`. Тебе не нужно писать `self.x = x` для каждого поля.

`dataclasses.fields(obj)` возвращает описание полей, `asdict(obj)` превращает объект в словарь.""",
"code": """
from dataclasses import dataclass, fields, asdict

@dataclass
class Book:  #! Поля описываются аннотациями
    title: str
    author: str
    pages: int

b = Book("Мастер и Маргарита", "Булгаков", 480)  #! __init__ сгенерирован
print(b)  #! __repr__ сгенерирован
print(b == Book("Мастер и Маргарита", "Булгаков", 480))  #! __eq__ сгенерирован
print([f.name for f in fields(b)])
print(asdict(b))
""",
"key": ["`@dataclass` генерирует `__init__`, `__repr__`, `__eq__`.", "Поля = аннотированные атрибуты класса.", "`fields()`, `asdict()` — полезные помощники."],
},
{
"title": "default и frozen",
"covers": ["default", "frozen"],
"text": """У поля можно задать **значение по умолчанию**: `qty: int = 1`. Для изменяемых значений (списков, словарей) нужно `field(default_factory=list)` — иначе все объекты делили бы один список.

`@dataclass(frozen=True)` делает объект **неизменяемым**: попытка поменять поле вызовет ошибку. Такие объекты можно класть в `set` и делать ключами словаря.""",
"code": """
from dataclasses import dataclass, field, FrozenInstanceError

@dataclass
class Order:
    item: str
    qty: int = 1  #! Значение по умолчанию
    tags: list = field(default_factory=list)  #! Для каждого заказа — свой новый список

@dataclass(frozen=True)
class Point:
    x: int
    y: int

a = Order("чай")
b = Order("кофе", 2)
a.tags.append("срочно")  #! Меняется только список заказа a
print(a, b)
p = Point(1, 2)
try:
    p.x = 10
except FrozenInstanceError:
    print("Point заморожен!")
print({p, Point(1, 2)})  #! Равные замороженные точки — один элемент множества
""",
"key": ["`поле: тип = значение` — значение по умолчанию.", "Для списков — `field(default_factory=list)`.", "`frozen=True` — неизменяемый и хешируемый объект."],
},
],
},
{
"title": "Память и выполнение",
"items": ["stack", "heap", "reference", "garbage collector", "reference counting", "mutability", "object lifecycle"],
"intro": "Что происходит «под капотом»: где живут переменные и объекты, как Python решает, что объект больше не нужен. Визуализатор в каждом уроке и есть модель памяти: слева стек, справа куча.",
"lessons": [
{
"title": "Stack и heap",
"covers": ["stack", "heap"],
"text": """**Стек вызовов** (stack) — стопка кадров: каждый вызов функции кладёт кадр со своими локальными именами, `return` снимает его. В визуализаторе это левая колонка «Имена».

**Куча** (heap) — область, где живут сами объекты: списки, словари, экземпляры, функции. Кадры хранят только **ссылки** на объекты в куче. Поэтому объект может пережить функцию, которая его создала, — если ссылку на него вернули.""",
"code": """
def make_list(n):
    data = list(range(n))  #! Список создаётся в куче, data — ссылка в кадре
    return data  #! Кадр исчезнет, а список останется: на него будет ссылка снаружи

def outer():
    inner_result = make_list(3)  #! Стек: глобальная → outer → make_list
    return len(inner_result)

result = outer()
saved = make_list(2)
print(result, saved)
""",
"key": ["Стек — кадры вызовов с именами.", "Куча — сами объекты.", "Объект живёт, пока на него есть ссылки, а не пока жив кадр."],
},
{
"title": "Reference и reference counting",
"covers": ["reference", "reference counting"],
"text": """Каждая **ссылка** на объект — имя, элемент списка, атрибут — увеличивает его **счётчик ссылок**. Удалил имя (`del`) или перепривязал его — счётчик уменьшился. Когда счётчик падает до нуля, CPython **сразу** освобождает объект.

`sys.getrefcount(obj)` показывает счётчик (он всегда на 1 больше, ведь сам аргумент функции — тоже ссылка). Следи, как объект исчезает из «кучи» в визуализаторе, когда на него не остаётся ссылок.""",
"code": """
import sys

data = [1, 2, 3]  #! Одна ссылка: имя data
print(sys.getrefcount(data) - 1)
alias = data  #! Ещё одна ссылка
box = {"x": data}  #! И ещё одна — из словаря
print(sys.getrefcount(data) - 1)
del alias  #! Ссылок стало меньше
box.clear()
print(sys.getrefcount(data) - 1)
data = None  #! Последняя ссылка исчезла — список освобождён
print("список удалён из памяти")
""",
"key": ["Ссылки: имена, элементы коллекций, атрибуты.", "Счётчик = 0 → объект освобождается сразу.", "`del x` удаляет имя, а не объект."],
},
{
"title": "Garbage collector и жизненный цикл объекта",
"covers": ["garbage collector", "object lifecycle"],
"text": """**Жизненный цикл объекта**: создание (`__new__`) → инициализация (`__init__`) → использование → последняя ссылка исчезла → финализация (`__del__`) → освобождение памяти.

Счётчик ссылок не справляется с **циклами**: если A ссылается на B, а B на A, их счётчики никогда не станут нулём. Для этого есть **сборщик мусора** (garbage collector, модуль `gc`): он периодически ищет группы объектов, недоступные из программы, и удаляет их.""",
"code": """
import gc

class Node:
    def __init__(self, name):
        self.name = name
        print("создан", name)
    def __del__(self):  #! Финализатор — вызывается перед уничтожением
        print("удалён", self.name)

a = Node("A")
a = None  #! Ссылок нет → удаляется сразу (reference counting)
b = Node("B")
c = Node("C")
b.friend = c  #! Цикл: B → C → B
c.friend = b
b = c = None  #! Имён нет, но объекты ссылаются друг на друга
print("цикл ещё в памяти…")
gc.collect()  #! Сборщик мусора находит и удаляет цикл
print("готово")
""",
"key": ["Создание → использование → нет ссылок → удаление.", "Reference counting удаляет сразу, но не видит циклы.", "`gc` находит и удаляет недоступные циклы."],
},
{
"title": "Mutability — изменяемость",
"covers": ["mutability"],
"opts": {"heap_all": True},
"text": """**Изменяемые** объекты (list, dict, set, большинство своих классов) можно менять на месте — identity сохраняется. **Неизменяемые** (int, float, str, tuple, frozenset) изменить нельзя: любая «модификация» создаёт **новый объект**.

Смотри на метки: после `nums += [4]` метка списка та же, а после `n += 1` и `s += "!"` имена указывают на новые объекты. Отсюда классическая ловушка: изменяемый объект, к которому ведут несколько ссылок.""",
"code": """
nums = [1, 2, 3]
other = nums
nums += [4]  #! Список изменён НА МЕСТЕ — метка та же, other видит изменение
n = 10
m = n
n += 1  #! int неизменяем: n теперь указывает на НОВЫЙ объект 11, m — на старый 10
s = "hi"
s += "!"  #! Строка тоже неизменяема — новый объект
print(other, m, n, s)
""",
"key": ["Изменяемые меняются на месте, identity не меняется.", "Неизменяемые при «изменении» заменяются новым объектом.", "Будь осторожен с общими ссылками на изменяемые объекты."],
},
],
},
{
"title": "Архитектура кода",
"items": ["separation of concerns", "cohesion", "coupling", "dependency", "dependency injection", "interface", "abstraction layer", "modularity"],
"intro": "Принципы, которые делают большую программу понятной и легко изменяемой. Код здесь — маленькие модели больших идей.",
"lessons": [
{
"title": "Separation of concerns и модульность",
"covers": ["separation of concerns", "modularity"],
"text": """**Разделение ответственности** (separation of concerns): каждая часть программы занимается **одним делом** — одна читает данные, другая считает, третья показывает результат. Тогда изменение формата вывода не заденет расчёты.

**Модульность** — программа собрана из независимых частей (функций, классов, модулей) с понятными границами. Части можно тестировать и заменять по отдельности.""",
"code": """
def load_scores():  #! Ответственность 1: получить данные
    return {"Аня": [5, 4, 5], "Боря": [3, 4, 4]}

def average(values):  #! Ответственность 2: посчитать
    return round(sum(values) / len(values), 2)

def render(name, avg):  #! Ответственность 3: показать
    return f"{name:<5} {avg}"

for name, marks in load_scores().items():  #! Главный код только соединяет части
    print(render(name, average(marks)))
""",
"key": ["Одна часть — одно дело.", "Модули с чёткими границами легко менять и тестировать.", "Главный код — «клей», соединяющий части."],
},
{
"title": "Cohesion и coupling",
"covers": ["cohesion", "coupling"],
"text": """**Связность** (cohesion) — насколько элементы **внутри** модуля относятся к одной задаче. Высокая связность — хорошо: класс `Cart` занимается только корзиной.

**Сцепление** (coupling) — насколько модули **зависят друг от друга**. Низкое сцепление — хорошо: модули общаются через простой интерфейс и не лезут во внутренности друг друга. Цель: **высокая связность, низкое сцепление**.""",
"code": """
class Cart:  #! Высокая связность: всё про корзину
    def __init__(self):
        self.items = []
    def add(self, name, price):
        self.items.append((name, price))
    def total(self):
        return sum(p for _, p in self.items)

class Receipt:  #! Низкое сцепление: знает только метод total()
    def print_for(self, cart):
        return f"К оплате: {cart.total()} ₽"

cart = Cart()
cart.add("книга", 500)
cart.add("ручка", 50)
print(Receipt().print_for(cart))
""",
"key": ["Cohesion — единство задачи внутри модуля (чем выше, тем лучше).", "Coupling — зависимость между модулями (чем ниже, тем лучше).", "Общайтесь через интерфейсы, а не через внутренности."],
},
{
"title": "Dependency и dependency injection",
"covers": ["dependency", "dependency injection"],
"text": """**Зависимость** (dependency) — объект, без которого другой не может работать: сервису уведомлений нужен способ отправки. Если сервис **сам** создаёт `EmailSender()` внутри, он намертво привязан к почте.

**Внедрение зависимостей** (dependency injection) — зависимость передаётся **снаружи**, например через `__init__`. Тогда можно подставить SMS, Telegram или фейковый отправитель для тестов, не меняя код сервиса.""",
"code": """
class EmailSender:
    def send(self, to, text):
        return f"email → {to}: {text}"

class FakeSender:  #! Подделка для тестов
    def __init__(self):
        self.sent = []
    def send(self, to, text):
        self.sent.append(to)
        return "fake"

class Notifier:
    def __init__(self, sender):  #! Зависимость приходит СНАРУЖИ
        self.sender = sender
    def welcome(self, user):
        return self.sender.send(user, "Добро пожаловать!")

print(Notifier(EmailSender()).welcome("anna@mail.ru"))
fake = FakeSender()
Notifier(fake).welcome("test")  #! Тот же Notifier, другая зависимость
print(fake.sent)
""",
"key": ["Зависимость — то, что нужно объекту для работы.", "DI: передавай зависимости снаружи, а не создавай внутри.", "Так код легко тестировать и менять."],
},
{
"title": "Interface и abstraction layer",
"covers": ["interface", "abstraction layer"],
"text": """**Интерфейс** — договор о том, какие методы есть у объекта. **Слой абстракции** (abstraction layer) — прослойка, которая прячет детали нижнего уровня за простым интерфейсом. Верхний код знает только про `storage.save()` и не знает, файл это, база данных или облако.

Хорошие слои позволяют заменить целый нижний уровень, не трогая верхний.""",
"code": """
from abc import ABC, abstractmethod

class Storage(ABC):  #! Интерфейс слоя хранения
    @abstractmethod
    def save(self, key, value): ...

class DictStorage(Storage):  #! Одна реализация
    def __init__(self):
        self.data = {}
    def save(self, key, value):
        self.data[key] = value

class PrintStorage(Storage):  #! Другая реализация
    def save(self, key, value):
        print(f"[лог] {key} = {value}")

def register(user, storage: Storage):  #! Бизнес-логика знает только интерфейс
    storage.save(user, "активен")

for s in (DictStorage(), PrintStorage()):
    register("anna", s)
""",
"key": ["Интерфейс — договор о методах.", "Слой абстракции прячет детали реализации.", "Верхние слои зависят от интерфейсов, а не от деталей."],
},
],
},
{
"title": "Design patterns",
"items": ["Factory", "Abstract Factory", "Singleton", "Builder", "Adapter", "Facade", "Proxy", "Strategy", "Observer", "Command", "State", "Repository"],
"intro": "Паттерны — проверенные решения типичных задач проектирования. Каждый урок — минимальная работающая модель паттерна.",
"lessons": [
{
"title": "Factory и Abstract Factory",
"covers": ["Factory", "Abstract Factory"],
"text": """**Factory** (фабрика) — функция или метод, который **решает, какой объект создать**, по параметру. Клиент говорит «дай транспорт для `road`» и не знает про класс `Truck`.

**Abstract Factory** — фабрика **семейства** связанных объектов. Например, тема интерфейса: светлая фабрика создаёт светлую кнопку и светлое окно, тёмная — тёмные. Объекты из одной фабрики гарантированно сочетаются.""",
"code": """
class Truck:
    def deliver(self): return "по дороге"
class Ship:
    def deliver(self): return "по морю"

def transport_factory(kind):  #! Factory: выбирает класс по параметру
    return {"road": Truck, "sea": Ship}[kind]()

print(transport_factory("sea").deliver())

class DarkFactory:  #! Abstract Factory: семейство согласованных объектов
    def button(self): return "[тёмная кнопка]"
    def window(self): return "[тёмное окно]"
class LightFactory:
    def button(self): return "[светлая кнопка]"
    def window(self): return "[светлое окно]"

def build_ui(factory):
    return factory.window() + " " + factory.button()

print(build_ui(DarkFactory()))
""",
"key": ["Factory — скрывает, какой класс создаётся.", "Abstract Factory — создаёт согласованное семейство объектов."],
},
{
"title": "Singleton",
"covers": ["Singleton"],
"text": """**Singleton** — у класса может быть **только один экземпляр**, и все получают его. Например, настройки приложения. Реализация через `__new__`: если объект уже создан — вернуть его.

В Python модуль сам по себе — естественный синглтон (импортируется один раз), поэтому паттерн нужен редко.""",
"code": """
class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:  #! Создаём только в первый раз
            cls._instance = super().__new__(cls)
            cls._instance.theme = "light"
        return cls._instance  #! Дальше всегда возвращаем тот же объект

a = Settings()
b = Settings()  #! Новый объект НЕ создаётся
b.theme = "dark"
print(a is b, a.theme)
""",
"key": ["Один экземпляр на всю программу.", "Реализуется через `__new__` или просто модуль."],
},
{
"title": "Builder",
"covers": ["Builder"],
"text": """**Builder** (строитель) собирает сложный объект **по шагам**. Каждый метод добавляет одну деталь и возвращает `self`, поэтому вызовы можно писать цепочкой. В конце `build()` отдаёт готовый результат.

Удобно, когда у объекта много необязательных частей.""",
"code": """
class PizzaBuilder:
    def __init__(self):
        self.parts = ["тесто"]
    def sauce(self, s):
        self.parts.append(s)
        return self  #! Возвращаем себя — для цепочки
    def topping(self, t):
        self.parts.append(t)
        return self
    def build(self):
        return "Пицца: " + ", ".join(self.parts)

pizza = PizzaBuilder().sauce("томатный").topping("сыр").topping("грибы").build()
print(pizza)
""",
"key": ["Собирает объект по шагам.", "Методы возвращают `self` → цепочки вызовов."],
},
{
"title": "Adapter",
"covers": ["Adapter"],
"text": """**Adapter** (адаптер) — обёртка, которая делает **неподходящий интерфейс подходящим**. Твой код ждёт метод `pay(rub)`, а сторонняя библиотека умеет только `make_payment(cents, currency)`. Адаптер переводит один вызов в другой.""",
"analogy": "Переходник для розетки: вилка та же, розетка другая — переходник их соединяет.",
"code": """
class ForeignGateway:  #! Чужой код, менять нельзя
    def make_payment(self, cents, currency):
        return f"оплачено {cents} {currency}-центов"

class GatewayAdapter:  #! Наш интерфейс поверх чужого
    def __init__(self, gateway):
        self.gateway = gateway
    def pay(self, rub):
        return self.gateway.make_payment(rub * 100, "RUB")  #! Перевод вызова

def checkout(payer):
    return payer.pay(250)  #! Код магазина знает только pay()

print(checkout(GatewayAdapter(ForeignGateway())))
""",
"key": ["Adapter переводит один интерфейс в другой.", "Позволяет подключить чужой код без его изменения."],
},
{
"title": "Facade",
"covers": ["Facade"],
"text": """**Facade** (фасад) — один простой вход в сложную подсистему из многих частей. Вместо того чтобы самому включать проектор, звук и свет, вызываешь `home.movie_mode()`.""",
"code": """
class Projector:
    def on(self): return "проектор вкл"
class Sound:
    def on(self, vol): return f"звук {vol}"
class Lights:
    def dim(self): return "свет приглушён"

class HomeTheater:  #! Фасад
    def __init__(self):
        self.p, self.s, self.l = Projector(), Sound(), Lights()
    def movie_mode(self):  #! Одна команда вместо трёх
        return [self.l.dim(), self.p.on(), self.s.on(7)]

print(HomeTheater().movie_mode())
""",
"key": ["Facade — простой интерфейс к сложной системе.", "Клиент не знает о внутренних частях."],
},
{
"title": "Proxy",
"covers": ["Proxy"],
"text": """**Proxy** (заместитель) — объект с **тем же интерфейсом**, что и настоящий, который стоит перед ним и контролирует доступ: кэширует, проверяет права, откладывает дорогое создание, логирует.""",
"code": """
class Database:
    def query(self, q):
        print("  (медленный запрос к БД)")
        return f"результат «{q}»"

class CachingProxy:  #! Тот же метод query, но с кэшем
    def __init__(self, real):
        self.real = real
        self.cache = {}
    def query(self, q):
        if q not in self.cache:  #! Идём в настоящую БД только при промахе
            self.cache[q] = self.real.query(q)
        return self.cache[q]

db = CachingProxy(Database())
print(db.query("users"))
print(db.query("users"))  #! Второй раз — из кэша
""",
"key": ["Proxy имеет тот же интерфейс, что и оригинал.", "Добавляет контроль: кэш, права, ленивость, логи."],
},
{
"title": "Strategy",
"covers": ["Strategy"],
"text": """**Strategy** (стратегия) — семейство взаимозаменяемых алгоритмов. Объект получает стратегию и использует её, не зная деталей. Сменил стратегию — сменилось поведение.

В Python стратегией часто бывает просто функция.""",
"code": """
def no_discount(price):
    return price
def student(price):
    return price * 0.8
def black_friday(price):
    return price * 0.5

class Checkout:
    def __init__(self, strategy):
        self.strategy = strategy  #! Стратегия передаётся снаружи
    def total(self, price):
        return self.strategy(price)

for s in (no_discount, student, black_friday):
    print(s.__name__, Checkout(s).total(1000))
""",
"key": ["Strategy — заменяемый алгоритм.", "В Python стратегией может быть просто функция."],
},
{
"title": "Observer",
"covers": ["Observer"],
"text": """**Observer** (наблюдатель) — объект-издатель хранит список подписчиков и **оповещает всех**, когда что-то происходит. Подписчики не опрашивают издателя постоянно — им сообщают сами.

Так работают события в интерфейсах, уведомления, чаты.""",
"code": """
class Channel:
    def __init__(self):
        self.subscribers = []  #! Список наблюдателей
    def subscribe(self, fn):
        self.subscribers.append(fn)
    def publish(self, video):
        for notify in self.subscribers:  #! Оповещаем каждого
            notify(video)

log = []
ch = Channel()
ch.subscribe(lambda v: log.append("Аня смотрит " + v))
ch.subscribe(lambda v: log.append("Боря смотрит " + v))
ch.publish("Python за 5 минут")
print(log)
""",
"key": ["Издатель хранит подписчиков и оповещает их.", "Подписчики слабо связаны с издателем."],
},
{
"title": "Command",
"covers": ["Command"],
"text": """**Command** (команда) — действие, упакованное в **объект**. Такой объект можно сохранить в очередь, выполнить позже, записать в историю и **отменить** (`undo`).

Так устроены «Отменить/Повторить» в редакторах.""",
"code": """
class AddText:
    def __init__(self, doc, text):
        self.doc, self.text = doc, text
    def do(self):
        self.doc.append(self.text)
    def undo(self):
        self.doc.pop()

doc = []
history = []
for word in ["Привет", "мир", "!!!"]:
    cmd = AddText(doc, word)  #! Действие — объект
    cmd.do()
    history.append(cmd)  #! Сохраняем для отмены
print(doc)
history.pop().undo()  #! Ctrl+Z
print(doc)
""",
"key": ["Команда = действие в виде объекта.", "Можно хранить, откладывать и отменять."],
},
{
"title": "State",
"covers": ["State"],
"text": """**State** (состояние) — поведение объекта зависит от его текущего состояния, а каждое состояние — **отдельный класс**. Вместо длинной цепочки `if state == ...` объект делегирует работу своему текущему состоянию, а состояния сами переключают друг друга.""",
"code": """
class Off:
    def press(self, lamp):
        lamp.state = On()  #! Состояние само решает, куда перейти
        return "включаю"

class On:
    def press(self, lamp):
        lamp.state = Off()
        return "выключаю"

class Lamp:
    def __init__(self):
        self.state = Off()
    def press(self):
        return self.state.press(self)  #! Делегируем текущему состоянию

lamp = Lamp()
for _ in range(3):
    print(lamp.press(), "→", type(lamp.state).__name__)
""",
"key": ["Каждое состояние — отдельный класс.", "Объект делегирует действия текущему состоянию.", "Нет громоздких if/elif по состояниям."],
},
{
"title": "Repository",
"covers": ["Repository"],
"text": """**Repository** (репозиторий) — объект, который выглядит как **коллекция** доменных объектов (`add`, `get`, `find`), а внутри прячет, где и как они хранятся: в памяти, в файле, в базе данных.

Бизнес-логика работает с репозиторием и ничего не знает про SQL. Для тестов подставляют репозиторий в памяти.""",
"code": """
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str

class InMemoryUserRepo:  #! Хранилище спрятано за простыми методами
    def __init__(self):
        self._rows = {}
    def add(self, user):
        self._rows[user.id] = user
    def get(self, uid):
        return self._rows.get(uid)
    def find_by_name(self, prefix):
        return [u for u in self._rows.values() if u.name.startswith(prefix)]

repo = InMemoryUserRepo()
repo.add(User(1, "Анна"))
repo.add(User(2, "Антон"))
repo.add(User(3, "Борис"))
print(repo.get(3))
print(repo.find_by_name("Ан"))
""",
"key": ["Repository — коллекция доменных объектов.", "Прячет детали хранения.", "Легко заменить хранилище для тестов."],
},
],
},
]
