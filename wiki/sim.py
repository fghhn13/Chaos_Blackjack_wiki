"""Facts from the balance simulator (`black-jack-sim`, package `bjsim`).

The simulator is its own repository. We never import it: its CLI is run in a
subprocess from a clean worktree of its `main`, against the wiki's clean
worktree of the game, and its JSON reports are stored without timestamps.
Results are deterministic for a given (game commit, simulator commit), so they
are reused while neither moves.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# (fact key, bjsim arguments). Same seed as the simulator's default.
EXPERIMENTS = {
    "bands": ["check"],
    "edge": ["edge", "--rules", "all"],
    "items": ["items", "--rules", "none"],
}


def static_facts(sim: Path) -> dict[str, Any]:
    """What the simulator offers, read from its sources (no import)."""
    main = (sim / "bjsim/__main__.py").read_text(encoding="utf-8")
    usage = [line.strip() for line in (ast.get_docstring(ast.parse(main)) or "").splitlines()
             if line.strip().startswith("python -m bjsim")]
    commands: dict[str, str] = {}
    for line in usage:
        cmd = line.split()[3]
        commands.setdefault(cmd, re.sub(r"\s{2,}", "  ", line))
    bands = json.loads((sim / "bands.json").read_text(encoding="utf-8"))
    return {
        "commands": commands,
        "bet_policies": _dict_keys(sim / "bjsim/bots.py", "BET_POLICIES"),
        "shop_policies": _dict_keys(sim / "bjsim/bots.py", "SHOP_POLICIES"),
        "rules": _dict_keys(sim / "bjsim/adapter.py", "RULES"),
        "bands_about": bands.get("about", ""),
        "band_defs": bands.get("metrics", []),
    }


def measure(sim: Path, game: Path, jobs: int | None = None) -> dict[str, Any]:
    """Run the experiments; raises RuntimeError with the simulator's stderr on failure."""
    env = {**os.environ, "CHAOS_BLACKJACK_ROOT": str(game), "CHAOS_USE_LLM": "0", "PYTHONUTF8": "1"}
    # The simulator tries an import before consulting CHAOS_BLACKJACK_ROOT.
    # Ensure an installed game or inherited path cannot shadow this checkout.
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (str(game.resolve()), env.get("PYTHONPATH", ""))))
    jobs = jobs or max(1, (os.cpu_count() or 2) - 2)
    out: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="wiki-sim-") as tmp:
        for key, args in EXPERIMENTS.items():
            path = Path(tmp) / f"{key}.json"
            proc = subprocess.run([sys.executable, "-m", "bjsim", *args, "--jobs", str(jobs), "--out", str(path)],
                                  cwd=sim, env=env, capture_output=True, text=True, encoding="utf-8")
            if not path.exists():  # `check` exits 1 on a failed band but still writes its report
                raise RuntimeError(f"bjsim {' '.join(args)} failed:\n" + proc.stderr.strip()[-2000:])
            rep = json.loads(path.read_text(encoding="utf-8"))
            out[key] = {"args": " ".join(args), "seed": rep.get("seed"), "balance": rep.get("balance"),
                        "tables": rep.get("tables", [])}
    return {
        "bands": [dict(zip(("metric", "value", "band", "ok"), r)) for r in _rows(out["bands"])],
        "edge": [dict(zip(("rule", "ev", "se"), r)) for r in _rows(out["edge"])],
        "items": [dict(zip(("item", "ev", "se"), r)) for r in _rows(out["items"])],
        "runs": {k: {"args": v["args"], "seed": v["seed"], "balance": v["balance"],
                     "title": v["tables"][0]["title"] if v["tables"] else ""} for k, v in out.items()},
    }


def collect(sim_repo: Path, sim_wt: Path, game_wt: Path, game_commit: str, old: dict[str, Any] | None,
            run: bool = True) -> tuple[dict[str, Any] | None, tuple[str, str] | None]:
    """(sim facts, drift entry or None). Reuses old measurements while game and simulator commits are unchanged."""
    if not sim_repo.exists():
        return None, None
    sha = _git(sim_repo, "rev-parse", "--verify", "main^{commit}")
    if sim_wt.exists():
        _git(sim_wt, "checkout", "--quiet", "--detach", sha)
    else:
        _git(sim_repo, "worktree", "add", "--quiet", "--detach", str(sim_wt), sha)
    commit, date, subject = (_git(sim_wt, "log", "-1", "--format=%h%x09%cs%x09%s").split("\t") + ["", "", ""])[:3]
    facts: dict[str, Any] = {"source": {"ref": "main", "commit": commit, "date": date, "subject": subject},
                             "game_commit": game_commit, **static_facts(sim_wt)}
    old = old or {}
    same = old.get("measured") and old.get("source", {}).get("commit") == commit \
        and old.get("measured_on") == game_commit
    if same:
        facts["measured"], facts["measured_on"] = old["measured"], old["measured_on"]
        return facts, None
    if not run:
        facts["measured"], facts["measured_on"] = old.get("measured"), old.get("measured_on")
        return facts, ("stale", "simulator results not re-measured (--no-sim); run `python -m wiki sync`")
    print("simulator: measuring (about a minute)...", flush=True)
    try:
        facts["measured"], facts["measured_on"] = measure(sim_wt, game_wt), game_commit
        return facts, None
    except RuntimeError as e:
        facts["measured"], facts["measured_on"] = old.get("measured"), old.get("measured_on")
        return facts, ("breaking", "bjsim failed against game main; the fix belongs in black-jack-sim, "
                                   f"not here; previous results kept. {str(e).splitlines()[-1]}")


def game_rule(sim_rule: str, game_rules: set[str]) -> str | None:
    """`modify_card_value-1` -> `modify_card_value`, `tiebreaker_dealer` -> `tiebreaker_shift`."""
    if sim_rule in game_rules:
        return sim_rule
    stem = re.sub(r"[-+]\d+$", "", sim_rule)
    if stem in game_rules:
        return stem
    prefix = sim_rule.split("_")[0]
    hits = [g for g in game_rules if g.startswith(prefix + "_")]
    return hits[0] if len(hits) == 1 else None


def _rows(report: dict[str, Any]) -> list[list[str]]:
    return report["tables"][0]["rows"] if report["tables"] else []


def _dict_keys(path: Path, name: str) -> list[str]:
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        target = node.target if isinstance(node, ast.AnnAssign) else (
            node.targets[0] if isinstance(node, ast.Assign) else None)
        if isinstance(target, ast.Name) and target.id == name and isinstance(node.value, ast.Dict):
            return [k.value for k in node.value.keys if isinstance(k, ast.Constant)]
    return []


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    return out.stdout.strip() if out.returncode == 0 else ""
