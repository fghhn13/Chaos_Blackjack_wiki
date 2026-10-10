"""Wiki command line: sync | extract | build | check | all."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from wiki import facts as F

DEFAULT_REF = os.environ.get("WIKI_GAME_REF", "main")
WORKTREE = Path(".agent_runs") / "worktrees" / "wiki-src"
DRIFT = F.ROOT / "DRIFT.md"


def game_repo() -> Path:
    env = os.environ.get("CHAOS_BLACKJACK_REPO")
    return Path(env).resolve() if env else F.ROOT.parent


def cmd_extract(args: argparse.Namespace) -> int:
    from wiki.adapter import extract_facts

    F.save(extract_facts(Path(args.game), args.ref), Path(args.out))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    repo = game_repo()
    wt = repo / WORKTREE
    sha = _run(["git", "-C", str(repo), "rev-parse", "--verify", f"{args.ref}^{{commit}}"]).strip()
    if wt.exists():
        if _run(["git", "-C", str(wt), "status", "--porcelain"]).strip():
            print(f"error: {wt} has local changes; it is the wiki's read-only source checkout", file=sys.stderr)
            return 2
        _run(["git", "-C", str(wt), "checkout", "--quiet", "--detach", sha])
    else:
        _run(["git", "-C", str(repo), "worktree", "add", "--quiet", "--detach", str(wt), sha])
    print(f"source: {args.ref} @ {sha[:7]} in {wt}")

    old = F.load()
    new_path = F.FACTS.with_name("facts.new.json")
    proc = subprocess.run([sys.executable, "-m", "wiki", "extract", "--game", str(wt), "--ref", args.ref,
                           "--out", str(new_path)], cwd=F.ROOT, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        _write_drift(old, None, [("breaking", "wiki/adapter.py", "extract failed: fix the adapter only")],
                     proc.stderr.strip().splitlines()[-15:])
        print(proc.stderr, file=sys.stderr)
        print(f"BREAKING: extract failed, see {DRIFT.name}", file=sys.stderr)
        return 1
    new = F.load(new_path)
    new_path.replace(F.FACTS)
    _copy_images(wt, new)
    entries = F.diff(old, new) + F.missing_prose(new)
    _write_drift(old, new, entries)
    counts = {k: sum(1 for e in entries if e[0] == k) for k in ("new", "removed", "stale", "auto")}
    print(f"facts updated; drift: " + ", ".join(f"{v} {k}" for k, v in counts.items()) + f" -> {DRIFT.name}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    from wiki.build import build

    errors = build()
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    print(f"built {F.ROOT / 'site'}" + (f" with {len(errors)} error(s)" if errors else ""))
    return 1 if errors else 0


def cmd_check(args: argparse.Namespace) -> int:
    from wiki.check import check

    return check(strict=args.strict)


def cmd_all(args: argparse.Namespace) -> int:
    for step in (cmd_sync, cmd_build, cmd_check):
        rc = step(args)
        if rc:
            return rc
    return 0


def _copy_images(game: Path, facts: dict) -> None:
    """Snapshot the art the facts point at into facts/img/<id>.png (so builds don't need the game)."""
    img = F.FACTS.parent / "img"
    img.mkdir(exist_ok=True)
    wanted = {aid: a["file"] for aid, a in facts.get("assets", {}).items() if a.get("file")}
    for coll in ("chaos_rules", "items"):
        wanted.update({i: e["icon"] for i, e in facts.get(coll, {}).items() if e.get("icon")})
    for old in img.glob("*.png"):
        if old.stem not in wanted:
            old.unlink()
    for aid, rel in wanted.items():
        src, dst = game / rel, img / f"{aid}.png"
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)


def _write_drift(old, new, entries, log=None) -> None:
    a = (old.get("source") or {}).get("commit", "(none)") if old else "(none)"
    b = (new.get("source") or {}).get("commit", "?") if new else "?"
    order = {"breaking": 0, "new": 1, "removed": 2, "stale": 3, "auto": 4}
    lines = [f"# Drift: game {a} -> {b}", "",
             "Handle `breaking`, `new`, `removed` and `stale`; `auto` needs no writing.", ""]
    if not entries:
        lines.append("No drift.")
    lines += [f"- **{k}** `{w}` — {d}" for k, w, d in sorted(entries, key=lambda e: (order[e[0]], e[1]))]
    if log:
        lines += ["", "```text", *log, "```"]
    DRIFT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8").stdout


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m wiki", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync", help="check out the game ref, extract facts, write DRIFT.md")
    s.add_argument("--ref", default=DEFAULT_REF)
    e = sub.add_parser("extract", help="(internal) extract facts from a game checkout")
    e.add_argument("--game", required=True)
    e.add_argument("--ref", default=DEFAULT_REF)
    e.add_argument("--out", default=str(F.FACTS))
    sub.add_parser("build", help="render site/ from facts + content")
    c = sub.add_parser("check", help="coverage, placeholders, links, stamp")
    c.add_argument("--strict", action="store_true", help="treat missing prose / translations as errors")
    a = sub.add_parser("all", help="sync, build, check")
    a.add_argument("--ref", default=DEFAULT_REF)
    a.add_argument("--strict", action="store_true")
    args = p.parse_args(argv)
    return {"sync": cmd_sync, "extract": cmd_extract, "build": cmd_build, "check": cmd_check,
            "all": cmd_all}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
