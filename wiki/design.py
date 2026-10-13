"""Design documents (`docs/design/*.md`) from every local branch of the game repo.

Facts describe `main`; design docs describe plans, so they are tracked wherever
they live. When a doc is on several branches, the newest version wins (and
`main` wins ties). Read-only `git` plumbing; nothing is checked out.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

FOLDER = "docs/design"


def slug(path: str) -> str:
    return Path(path).stem.lower().replace("_", "-")


def scan(repo: Path, main_ref: str = "main") -> dict[str, Any]:
    best: dict[str, dict[str, Any]] = {}
    branches = _git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads").split()
    for ref in sorted(branches, key=lambda b: (b != main_ref, b)):
        for path in _git(repo, "ls-tree", "-r", "--name-only", ref, "--", FOLDER).splitlines():
            if not path.endswith(".md"):
                continue
            ts, commit, date = _git(repo, "log", "-1", "--format=%ct%x09%h%x09%cs", ref, "--", path).split("\t")
            cur = best.get(path)
            if cur is None or int(ts) > cur["_ts"]:
                text = _git(repo, "show", f"{ref}:{path}")
                best[path] = {
                    "_ts": int(ts), "path": path, "ref": ref, "commit": commit, "date": date,
                    "blob": _git(repo, "rev-parse", f"{ref}:{path}")[:12],
                    "title": _title(text, path), "status": _status(text),
                }
    main_blobs = {}
    for line in _git(repo, "ls-tree", "-r", main_ref, "--", FOLDER).splitlines():
        entry, path = line.split("\t", 1)
        main_blobs[path] = entry.split()[2][:12]
    out = {}
    for path, d in sorted(best.items()):
        d.pop("_ts")
        # An older document at the same path does not make this version shipped.
        d["on_main"] = main_blobs.get(path) == d["blob"]
        out[slug(path)] = d
    return out


def _title(text: str, path: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else Path(path).stem.replace("_", " ").title()


def _status(text: str) -> str | None:
    """`Status: **agreed plan**, ...` -> "agreed plan" (the bold part, else the first sentence)."""
    m = re.search(r"^Status:\s*(.+)$", text, re.M)
    if not m:
        return None
    bold = re.match(r"\*\*(.+?)\*\*", m.group(1))
    return bold.group(1).strip() if bold else re.split(r"[.,]", m.group(1))[0].strip()


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    return out.stdout.strip() if out.returncode == 0 else ""
