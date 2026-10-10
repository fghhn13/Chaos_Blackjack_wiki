"""Loading, saving and diffing `facts/facts.json`."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "facts" / "facts.json"
CONTENT = ROOT / "content"
LANGS = ("en", "zh")

# Collections whose keys are game ids: an added key needs a wiki card, a removed one orphans prose.
ID_COLLECTIONS = ("settings", "chaos_rules", "items", "assets", "permissions")
# Collections with a prose page per id (content/<lang>/<folder>/<id>.md).
PROSE_FOLDERS = {"chaos_rules": "chaos", "items": "items"}
# Changes here are expected on every new commit and are not worth listing one by one.
NOISY = ("source", "changelog", "transcript")


def load(path: Path = FACTS) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def dumps(facts: dict[str, Any]) -> str:
    return json.dumps(facts, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def save(facts: dict[str, Any], path: Path = FACTS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(facts), encoding="utf-8", newline="\n")


def fingerprint(path: Path = FACTS) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else ""


def lookup(facts: dict[str, Any], dotted: str) -> Any:
    """`items.peek.price` -> value. Raises KeyError for an unknown path."""
    node: Any = facts
    parts = dotted.split(".")
    while parts:
        if isinstance(node, dict):
            # Keys may contain dots (`settings.run.start_money`): take the longest match.
            for n in range(len(parts), 0, -1):
                key = ".".join(parts[:n])
                if key in node:
                    node, parts = node[key], parts[n:]
                    break
            else:
                raise KeyError(dotted)
        elif isinstance(node, list) and parts[0].isdigit() and int(parts[0]) < len(node):
            node, parts = node[int(parts[0])], parts[1:]
        else:
            raise KeyError(dotted)
    return node


def flatten(node: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(node, dict) and node:
        out: dict[str, Any] = {}
        for k, v in node.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    return {prefix: node}


def ids(facts: dict[str, Any]) -> set[str]:
    return {i for c in ID_COLLECTIONS for i in facts.get(c, {})}


def prose_path(lang: str, collection: str, item_id: str) -> Path:
    return CONTENT / lang / PROSE_FOLDERS[collection] / f"{item_id}.md"


def diff(old: dict[str, Any], new: dict[str, Any]) -> list[tuple[str, str, str]]:
    """(kind, where, detail) entries: auto | new | removed | stale. `breaking` is added by the caller."""
    out: list[tuple[str, str, str]] = []
    for coll in ID_COLLECTIONS:
        a, b = old.get(coll, {}), new.get(coll, {})
        for i in sorted(b.keys() - a.keys()):
            out.append(("new", f"{coll}.{i}", _new_detail(coll, i)))
        for i in sorted(a.keys() - b.keys()):
            out.append(("removed", f"{coll}.{i}", _removed_detail(coll, i)))
    fa, fb = flatten({k: v for k, v in old.items() if k not in NOISY}), flatten(
        {k: v for k, v in new.items() if k not in NOISY})
    touched = {w for _, w, _ in out}
    for path in sorted(fa.keys() | fb.keys()):
        if any(path == t or path.startswith(t + ".") for t in touched):
            continue
        a, b = fa.get(path, "<absent>"), fb.get(path, "<absent>")
        if {_fmt(a), _fmt(b)} <= {"{}", "[]", "<absent>"}:
            continue  # an empty container gained or lost children; the children are listed
        if a != b:
            out.append(("auto", path, f"{_fmt(fa.get(path, '<absent>'))} -> {_fmt(fb.get(path, '<absent>'))}"))
    if old.get("transcript") != new.get("transcript") and old:
        out.append(("auto", "transcript", "agent transcript changed (re-read the agents page)"))
    gone = ids(old) - ids(new)
    for f, line_no, token in _backticked_ids():
        if token in gone:
            out.append(("stale", f"{f.relative_to(ROOT).as_posix()}:{line_no}", f"mentions removed id `{token}`"))
    return out


def missing_prose(facts: dict[str, Any]) -> list[tuple[str, str, str]]:
    out = []
    for coll in PROSE_FOLDERS:
        for i in facts.get(coll, {}):
            langs = [lang for lang in LANGS if not prose_path(lang, coll, i).exists()]
            if langs:
                out.append(("new", f"{coll}.{i}", f"no prose in {', '.join(langs)}"))
    return out


def _new_detail(coll: str, i: str) -> str:
    if coll in PROSE_FOLDERS:
        return f"write content/{{en,zh}}/{PROSE_FOLDERS[coll]}/{i}.md"
    return "card is generated; mention it in prose if players need to know"


def _removed_detail(coll: str, i: str) -> str:
    if coll in PROSE_FOLDERS:
        return f"delete content/{{en,zh}}/{PROSE_FOLDERS[coll]}/{i}.md"
    return "gone from the game"


def _backticked_ids():
    for f in sorted(CONTENT.rglob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for token in re.findall(r"`([a-z][a-z0-9_.]*)`", line):
                yield f, n, token


def _fmt(v: Any) -> str:
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    return s if len(s) <= 60 else s[:57] + "..."
