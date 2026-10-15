"""Run a lesson snippet under sys.settrace and record every step.

Each step captures: the line about to run, the call stack with local names,
every object reachable from those names (the "heap") and the printed output.
Snapshots are interned per lesson so repeated states cost almost nothing.
"""
import builtins
import inspect
import io
import json
import os
import re
import sys
import tempfile
import types

FILENAME = "<lesson>"
MAX_STEPS = 600
MAX_ITEMS = 12
MAX_STR = 60
MAX_HEAP = 60

PRIMS = (int, float, bool, str, type(None), complex)
HIDDEN_GLOBALS = {"__builtins__", "__name__", "__doc__", "__package__", "__loader__",
                  "__spec__", "__file__", "__cached__", "__annotations__"}


def short(s, n=MAX_STR):
    return s if len(s) <= n else s[: n - 1] + "…"


def prim_repr(v):
    if isinstance(v, str):
        return short(repr(v))
    if isinstance(v, float):
        return repr(round(v, 6))
    return repr(v)


def is_lesson_func(f):
    return isinstance(f, types.FunctionType) and f.__code__.co_filename == FILENAME


def is_lesson_class(c):
    return isinstance(c, type) and getattr(c, "__module__", None) == "__main__"


def hidden_global(name, v, opts):
    if name in HIDDEN_GLOBALS and not (name == "__name__" and opts.get("show_name")):
        return True
    if isinstance(v, types.ModuleType):
        return not opts.get("show_modules")
    if isinstance(v, type) and not is_lesson_class(v):
        return True
    if callable(v) and not isinstance(v, type) and not is_lesson_func(v) \
            and not isinstance(v, (types.MethodType, types.GeneratorType)) \
            and getattr(v, "__module__", "__main__") not in ("__main__", None) \
            and not hasattr(v, "__wrapped__"):
        return True
    if getattr(v, "__module__", None) in ("typing", "typing_extensions") and not opts.get("show_typing"):
        # TypeVar, Union[...] etc. defined via typing are still interesting if user-made
        return not isinstance(v, (typing_TypeVar(),))
    return False


def typing_TypeVar():
    import typing
    return typing.TypeVar


class Snapshotter:
    def __init__(self, opts):
        self.opts = opts
        self.idmap = {}      # id(obj) -> (num, typename)
        self.next_num = 1

    def num_for(self, obj):
        key = id(obj)
        tname = type(obj).__name__
        if key in self.idmap and self.idmap[key][1] == tname:
            return self.idmap[key][0]
        n = self.next_num
        self.next_num += 1
        self.idmap[key] = (n, tname)
        return n

    def encode(self, v, heap, depth=0):
        """Return a value cell: ["p", text] inline or ["r", num] reference."""
        if isinstance(v, PRIMS) and not self.opts.get("heap_all"):
            return ["p", prim_repr(v)]
        if isinstance(v, bool) or v is None:
            # True/False/None stay inline even in heap_all mode: they are singletons
            if not self.opts.get("heap_all") or v is None or isinstance(v, bool):
                return ["p", prim_repr(v)]
        if isinstance(v, (types.BuiltinFunctionType,)):
            return ["p", f"<встроенная {v.__name__}>"]
        if isinstance(v, type) and not is_lesson_class(v):
            return ["p", f"<класс {v.__name__}>"]
        if isinstance(v, types.ModuleType) and not self.opts.get("show_modules"):
            return ["p", f"<модуль {v.__name__}>"]
        n = self.num_for(v)
        if n not in heap:
            if len(heap) >= MAX_HEAP or depth > 6:
                return ["p", short(type(v).__name__ + "…")]
            heap[n] = None  # reserve to stop cycles
            heap[n] = self.describe(v, heap, depth + 1)
        return ["r", n]

    def describe(self, v, heap, depth):
        enc = lambda x: self.encode(x, heap, depth)
        t = type(v).__name__
        if isinstance(v, PRIMS):
            return {"k": "prim", "t": t, "v": prim_repr(v)}
        if isinstance(v, (list, tuple)) and type(v) in (list, tuple):
            items = [enc(x) for x in v[:MAX_ITEMS]]
            return {"k": t, "t": t, "items": items, "more": max(0, len(v) - MAX_ITEMS)}
        if type(v) in (set, frozenset):
            try:
                seq = sorted(v, key=repr)
            except Exception:
                seq = list(v)
            return {"k": "set", "t": t, "items": [enc(x) for x in seq[:MAX_ITEMS]],
                    "more": max(0, len(v) - MAX_ITEMS)}
        if type(v) is dict or (isinstance(v, dict) and not is_lesson_class(type(v))):
            pairs = [[enc(k), enc(x)] for k, x in list(v.items())[:MAX_ITEMS]]
            return {"k": "dict", "t": t, "pairs": pairs, "more": max(0, len(v) - MAX_ITEMS)}
        if isinstance(v, types.FunctionType):
            try:
                sig = str(inspect.signature(v))
            except Exception:
                sig = "(…)"
            d = {"k": "func", "t": "function", "name": v.__qualname__ if v.__name__ != "<lambda>" else "lambda",
                 "sig": short(sig, 50)}
            if v.__closure__:
                cells = {}
                for name, c in zip(v.__code__.co_freevars, v.__closure__):
                    try:
                        cells[name] = enc(c.cell_contents)
                    except ValueError:
                        cells[name] = ["p", "<пусто>"]
                d["cells"] = cells
            if hasattr(v, "__wrapped__"):
                d["wraps"] = enc(v.__wrapped__)
            return d
        if isinstance(v, types.MethodType):
            return {"k": "other", "t": "bound method",
                    "r": f"{v.__func__.__qualname__} привязан к", "attrs": {"__self__": enc(v.__self__)}}
        if isinstance(v, types.GeneratorType):
            fr = v.gi_frame
            state = inspect.getgeneratorstate(v)
            st = {"GEN_CREATED": "создан, ещё не запускался", "GEN_RUNNING": "работает",
                  "GEN_SUSPENDED": "на паузе (yield)", "GEN_CLOSED": "завершён"}[state]
            d = {"k": "gen", "t": "generator", "name": v.__name__, "state": st}
            if fr is not None and state != "GEN_RUNNING":
                d["locals"] = {k: enc(x) for k, x in fr.f_locals.items() if not k.startswith(".")}
                if state == "GEN_SUSPENDED":
                    d["line"] = fr.f_lineno
            return d
        if isinstance(v, type):
            attrs = {}
            for k, x in v.__dict__.items():
                if k.startswith("__") and k not in self.opts.get("show_dunders", ()) and k != "__init__":
                    continue
                if k in ("_abc_impl", "__dataclass_params__", "__dataclass_fields__", "__match_args__"):
                    continue
                if isinstance(x, types.FunctionType):
                    attrs[k] = ["p", "метод" + (" ⚠abstract" if getattr(x, "__isabstractmethod__", False) else "")]
                elif isinstance(x, classmethod):
                    attrs[k] = ["p", "@classmethod"]
                elif isinstance(x, staticmethod):
                    attrs[k] = ["p", "@staticmethod"]
                elif isinstance(x, property):
                    attrs[k] = ["p", "@property"]
                elif hasattr(type(x), "__get__") and not isinstance(x, PRIMS) and not callable(x):
                    attrs[k] = ["p", f"дескриптор {type(x).__name__}"]
                else:
                    attrs[k] = enc(x)
            d = {"k": "class", "t": "class", "name": v.__name__,
                 "bases": [b.__name__ for b in v.__bases__ if b is not object], "attrs": attrs}
            mt = type(v)
            if mt is not type and mt.__name__ != "ABCMeta":
                d["meta"] = mt.__name__
            elif mt.__name__ == "ABCMeta":
                d["meta"] = "ABCMeta"
            return d
        if isinstance(v, types.ModuleType):
            names = [k for k in vars(v) if not k.startswith("_")][:8]
            return {"k": "other", "t": "module", "r": f"модуль {v.__name__}: " + ", ".join(names)}
        if isinstance(v, BaseException):
            attrs = {"args": enc(v.args)}
            for k, x in getattr(v, "__dict__", {}).items():
                attrs[k] = enc(x)
            return {"k": "obj", "t": t, "attrs": attrs, "exc": True}
        if is_lesson_class(type(v)) or hasattr(v, "__dict__") and type(v).__module__ == "__main__":
            attrs = {}
            src = {}
            if hasattr(v, "__dict__"):
                src = dict(vars(v))
            for slot in getattr(type(v), "__slots__", ()):
                if hasattr(v, slot):
                    src[slot] = getattr(v, slot)
            for k, x in list(src.items())[:MAX_ITEMS + 4]:
                attrs[k] = enc(x)
            d = {"k": "obj", "t": t, "attrs": attrs}
            # containers made from lesson classes (e.g. class Stack(list))
            if isinstance(v, list):
                d["items"] = [enc(x) for x in v[:MAX_ITEMS]]
            if isinstance(v, dict):
                d["pairs"] = [[enc(k), enc(x)] for k, x in list(v.items())[:MAX_ITEMS]]
            return d
        try:
            r = repr(v)
        except Exception:
            r = f"<{t}>"
        r = re.sub(r" at 0x[0-9a-f]+", "", r)
        return {"k": "other", "t": t, "r": short(r, 70)}


def run_lesson(code, opts=None, files=None):
    """Execute code, return dict with the trace."""
    opts = opts or {}
    lines = code.split("\n")
    snap = Snapshotter(opts)
    steps = []
    obj_table, obj_index = [], {}
    frame_table, frame_index = [], {}
    out = io.StringIO()
    state = {"stopped": False, "depth0": None}

    def intern(table, index, item):
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in index:
            index[key] = len(table)
            table.append(item)
        return index[key]

    def lesson_frames(frame):
        fs = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == FILENAME:
                fs.append(f)
            f = f.f_back
        return list(reversed(fs))

    def capture(frame, event, arg):
        heap = {}
        frames = []
        for f in lesson_frames(frame):
            code_name = f.f_code.co_name
            is_module = code_name == "<module>"
            if is_module:
                items = [(k, v) for k, v in f.f_globals.items() if not hidden_global(k, v, opts)]
                name = "глобальная область"
            else:
                items = [(k, v) for k, v in f.f_locals.items()
                         if not k.startswith(".") and not (k == "__class__")
                         and k not in ("__module__", "__qualname__", "__firstlineno__", "__static_attributes__", "__classdictcell__")]
                if f.f_code.co_flags & inspect.CO_GENERATOR:
                    name = f"{code_name}() ⟳генератор"
                elif "__module__" in f.f_locals and "__qualname__" in f.f_locals:
                    name = f"тело класса {code_name}"
                else:
                    name = f"{code_name}()"
            vars_ = []
            for k, v in items:
                try:
                    vars_.append([k, snap.encode(v, heap)])
                except Exception as e:  # pragma: no cover - defensive
                    vars_.append([k, ["p", f"<{type(v).__name__}>"]])
            frames.append(intern(frame_table, frame_index, {"name": name, "vars": vars_}))
        step = {
            "l": frame.f_lineno,
            "e": event[0],  # l=line r=return x=exception
            "f": frames,
            "h": [intern(obj_table, obj_index, {"n": n, **(d or {"k": "other", "t": "?", "r": "…"})})
                  for n, d in sorted(heap.items())],
            "o": len(out.getvalue()),
        }
        if event == "return":
            step["rv"] = snap.encode(arg, heap) if arg is not None or True else None
            # re-intern heap since return value may add objects
            step["h"] = [intern(obj_table, obj_index, {"n": n, **(d or {"k": "other", "t": "?", "r": "…"})})
                         for n, d in sorted(heap.items())]
            step["fn"] = frame.f_code.co_name
        if event == "exception":
            exc_type, exc, _ = arg
            step["ex"] = f"{exc_type.__name__}: {exc}"
        steps.append(step)

    def tracer(frame, event, arg):
        if state["stopped"]:
            return None
        if frame.f_code.co_filename != FILENAME:
            return None
        if event in ("line", "return", "exception"):
            if len(steps) >= MAX_STEPS:
                state["stopped"] = True
                sys.settrace(None)
                return None
            capture(frame, event, arg)
        return tracer

    tmp = tempfile.mkdtemp(prefix="lesson_")
    old_cwd = os.getcwd()
    old_stdout = sys.stdout
    old_path = list(sys.path)
    for fname, content in (files or {}).items():
        p = os.path.join(tmp, fname)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as fh:
            fh.write(content)
    error = None
    g = {"__name__": "__main__", "__builtins__": builtins}
    try:
        os.chdir(tmp)
        sys.path.insert(0, tmp)
        compiled = compile(code, FILENAME, "exec")
        sys.stdout = out
        sys.settrace(tracer)
        try:
            exec(compiled, g)
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    finally:
        sys.stdout = old_stdout
        os.chdir(old_cwd)
        sys.path[:] = old_path
        for m in list(sys.modules):
            mod = sys.modules[m]
            if getattr(mod, "__file__", None) and str(mod.__file__).startswith(tmp):
                del sys.modules[m]

    # final "done" step showing end state
    if steps:
        last = dict(steps[-1])
        last["e"] = "d"
        last.pop("rv", None)
        last.pop("ex", None)
        last.pop("fn", None)
        last["o"] = len(out.getvalue())
        last["l"] = 0
        # keep only module frame at the end
        last["f"] = last["f"][:1]
        steps.append(last)

    return {
        "steps": steps,
        "objs": obj_table,
        "frames": frame_table,
        "out": out.getvalue(),
        "error": error,
        "truncated": state["stopped"],
    }


if __name__ == "__main__":
    demo = "a = [1, 2]\nb = a\nb.append(3)\nprint(a)\n"
    print(json.dumps(run_lesson(demo), ensure_ascii=False, indent=1)[:2000])
