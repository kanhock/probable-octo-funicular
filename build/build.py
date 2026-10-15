"""Build the app: trace every lesson and inject the data into app.html.

Usage:  python3 build/build.py
Writes: index.html (standalone page for iPhone / GitHub Pages)
        build/artifact.html (same page without the document skeleton)
"""
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from tracer import run_lesson  # noqa: E402

MODULES = ["lessons_a", "lessons_b", "lessons_c", "lessons_d", "lessons_e"]
NARR = re.compile(r"\s*#!\s?(.*)$")


def prep_code(src):
    src = src.strip("\n")
    lines, narr = [], {}
    for i, line in enumerate(src.split("\n"), 1):
        m = NARR.search(line)
        if m:
            narr[i] = m.group(1).strip()
            line = line[: m.start()].rstrip()
        lines.append(line)
    return "\n".join(lines) + "\n", narr


def run_snippet(code):
    """Run a check's code and return its output on one line ("a | b")."""
    import contextlib
    import io
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<check>", "exec"), {"__name__": "__main__"})
    except Exception as e:  # pragma: no cover - surfaced as a problem
        return f"!{type(e).__name__}: {e}"
    return " | ".join(line.rstrip() for line in buf.getvalue().strip().split("\n"))


def build():
    sections = []
    problems = []
    for modname in MODULES:
        try:
            mod = importlib.import_module(modname)
        except ModuleNotFoundError:
            continue
        sections.extend(mod.SECTIONS)
    for si, sec in enumerate(sections, 1):
        for li, les in enumerate(sec["lessons"], 1):
            les["id"] = f"{si}-{li}"
            for c in les["covers"]:
                if c not in sec["items"]:
                    problems.append(f"{les['id']}: covers '{c}' not in items of section {si}")
            if les.get("code"):
                code, narr = prep_code(les["code"])
                les["code"] = code.rstrip("\n")
                les["narr"] = narr
                tr = run_lesson(code, les.get("opts"), les.get("files"))
                # drop the module-level "return None" step: the final "done" step covers it
                tr["steps"] = [s for s in tr["steps"] if not (s["e"] == "r" and s.get("fn") == "<module>")]
                les["trace"] = tr
                if tr["error"] and not les.get("expect_error"):
                    problems.append(f"{les['id']} {les['title']}: {tr['error']}")
                if tr["truncated"]:
                    problems.append(f"{les['id']} {les['title']}: trace truncated")
                for k, s in narr.items():
                    if not any(st["l"] == k for st in tr["steps"]):
                        problems.append(f"{les['id']}: narration on line {k} never executes")
            if les.get("files"):
                les["files_show"] = les.pop("files")
        covered = {c for les in sec["lessons"] for c in les["covers"]}
        for it in sec["items"]:
            if it not in covered:
                problems.append(f"section {si}: item '{it}' has no lesson")
    from scenes import WORLDS
    deep = {}
    for modname in ("deep_a", "deep_b", "deep_c", "deep_d", "deep_e"):
        try:
            deep.update(importlib.import_module(modname).DEEP)
        except ModuleNotFoundError:
            pass
    for si, sec in enumerate(sections):
        w = WORLDS[si + 1]
        sec["zone"] = si
        sec["world"] = {"name": w["world"], "hue": w["hue"], "kind": w["kind"], "intro": w["intro"], "why": w["why"],
                        "spots": {k: [v[0], v[1]] for k, v in w["spots"].items()}}
        for it in sec["items"]:
            if it not in w["spots"]:
                problems.append(f"world {si + 1}: item '{it}' has no object in the scene")
        for les in sec["lessons"]:
            extra = deep.get(les["id"])
            if not extra:
                problems.append(f"{les['id']}: no deep content")
                continue
            les.update(extra)
            for q in les.get("checks", []):
                if q.pop("run", False):
                    got = run_snippet(q["code"])
                    want = q["options"][q["answer"]]
                    if got != want:
                        problems.append(f"{les['id']}: check output mismatch: want {want!r}, got {got!r}")
                if not (0 <= q["answer"] < len(q["options"])):
                    problems.append(f"{les['id']}: bad answer index in check")
            for lid in les.get("links", []):
                if lid not in {l["id"] for s2 in sections for l in s2["lessons"]}:
                    problems.append(f"{les['id']}: unknown link {lid}")
    zones = [{"name": WORLDS[i + 1]["world"], "kind": WORLDS[i + 1]["kind"], "hue": WORLDS[i + 1]["hue"],
              "intro": WORLDS[i + 1]["intro"], "why": WORLDS[i + 1]["why"]} for i in range(len(sections))]
    data = {"sections": sections, "zones": zones}
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(os.path.join(HERE, "app.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    page = tpl.replace("__DATA__", blob)
    with open(os.path.join(HERE, "artifact.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
    head_extra = (
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="apple-mobile-web-app-capable" content="yes">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
        '<meta name="apple-mobile-web-app-title" content="Python схема">\n'
        '<meta name="theme-color" content="#2B66CF">\n'
        '<link rel="manifest" href="manifest.webmanifest">\n'
        '<link rel="apple-touch-icon" href="icons/icon-180.png">\n'
        '<link rel="icon" type="image/png" href="icons/icon-192.png">\n'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0}[hidden]{display:none!important}</style>\n'
    )
    title_end = page.index("</title>") + len("</title>")
    head_part = page[:title_end]
    rest = page[title_end:]
    style_end = rest.index("</style>") + len("</style>")
    full = ("<!doctype html>\n<html lang=\"ru\">\n<head>\n" + head_extra + head_part + rest[:style_end]
            + "\n</head>\n<body>\n" + rest[style_end:] + "\n</body>\n</html>\n")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(full)
    import hashlib
    ver = hashlib.sha1(full.encode()).hexdigest()[:10]
    with open(os.path.join(HERE, "sw.template.js"), encoding="utf-8") as fh:
        sw = fh.read().replace("__VERSION__", ver)
    with open(os.path.join(ROOT, "sw.js"), "w", encoding="utf-8") as fh:
        fh.write(sw)
    n = sum(len(s["lessons"]) for s in sections)
    print(f"sections={len(sections)} lessons={n} size={len(full) / 1024:.0f} KB")
    for p in problems:
        print("PROBLEM:", p)
    return problems


if __name__ == "__main__":
    sys.exit(1 if build() else 0)
