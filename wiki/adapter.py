"""The only module that imports `chaos_blackjack`.

Everything the wiki knows about the game passes through `extract_facts()`,
which returns plain JSON-safe data. When the game's API changes, fix this file
and nothing else.

Documented exceptions to "public API only":
- the registry has no listing method, so rule and item ids are read from
  `Registry._chaos_rules` / `Registry._items`;
- agent CLI commands and error codes are scraped from the agent sources.
"""

from __future__ import annotations

import dataclasses
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Transcript of a short scripted run, replayed on every extract.
TRANSCRIPT_SEED = 7
TRANSCRIPT_ROUNDS = 3
TRANSCRIPT_BET = 10

_BRIEF_KEYS = ("phase", "summary", "hint", "legal_actions", "bankroll", "bet_range", "last_round", "run_end")


def load_game(root: Path) -> Any:
    """Import `chaos_blackjack` from `root` (a clean checkout), offline and headless."""
    root = root.resolve()
    os.environ["CHAOS_USE_LLM"] = "0"
    os.environ["CHAOS_DB"] = ":memory:"
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    sys.path.insert(0, str(root))
    pkg = importlib.import_module("chaos_blackjack")
    loaded = Path(pkg.__file__).resolve()
    if root not in loaded.parents:
        raise RuntimeError(f"chaos_blackjack imported from {loaded}, expected inside {root}")
    from chaos_blackjack.registry.loader import auto_load_plugins

    auto_load_plugins()
    return pkg


def extract_facts(root: Path, ref: str) -> dict[str, Any]:
    pkg = load_game(root)
    balance = _balance()
    return {
        "schema": 1,
        "source": _source(root, ref, getattr(pkg, "__version__", None)),
        "settings": balance["settings"],
        "chaos_rules": _chaos_rules(root, balance),
        "items": _items(root, balance),
        "permissions": _permissions(root),
        "prompts": sorted(p.stem for p in (root / "chaos_blackjack/ai/prompts").glob("*.txt")),
        "assets": _assets(root),
        "agent": _agent(root),
        "transcript": _transcript(),
        "changelog": _changelog(root),
    }


# --- source ----------------------------------------------------------------

def _git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8")
    return out.stdout.strip() if out.returncode == 0 else ""


def _source(root: Path, ref: str, version: str | None) -> dict[str, Any]:
    sha, date, subject = (_git(root, "log", "-1", "--format=%h%x09%cs%x09%s").split("\t") + ["", "", ""])[:3]
    return {"ref": ref, "commit": sha, "date": date, "subject": subject, "version": version}


def _changelog(root: Path, limit: int = 40) -> list[dict[str, str]]:
    out = []
    for line in _git(root, "log", "--first-parent", f"-n{limit}", "--format=%h%x09%cs%x09%s").splitlines():
        sha, date, subject = line.split("\t", 2)
        out.append({"commit": sha, "date": date, "subject": subject})
    return out


# --- balance ---------------------------------------------------------------

_SETTING_DOCS = {  # used only when the game has no SQLite balance profiles yet
    "run.start_money": ("int", "Bankroll at the start of a run"),
    "run.target_money": ("int", "Bankroll that wins the run"),
    "run.objective": ("str", "Run objective id"),
    "table.dealer_stand_on": ("int", "Dealer stands on this total or more"),
    "table.blackjack_pays_num": ("int", "Natural blackjack payout numerator (3 in 3:2)"),
    "table.blackjack_pays_den": ("int", "Natural blackjack payout denominator (2 in 3:2)"),
    "table.allow_double": ("bool", "Double down allowed on the first decision"),
    "table.allow_surrender": ("bool", "Surrender allowed on the first decision"),
    "shop.slots": ("int", "Different items on sale per restock"),
    "shop.refresh_rounds": ("int", "Rounds between restocks"),
    "bet.min": ("int", "Smallest bet"),
    "bet.max_fraction": ("float", "Largest bet as a share of the bankroll (rounded down)"),
}


def _balance() -> dict[str, Any]:
    """Settings, prices and rule tuning, from the SQLite `default` profile if the game has one."""
    try:
        data = importlib.import_module("chaos_blackjack.data")
    except ImportError:
        data = None
    if data is not None and hasattr(data, "default_balance"):
        b = data.default_balance()
        settings = _sqlite_settings(data)
        return {
            "settings": settings,
            "prices": dict(b.shop_prices),
            "item_params": dict(b.item_params),
            "rules": {r.rule_id: {"enabled": r.enabled, "params": dict(r.params),
                                  "stub_weight": r.stub_weight, "stub_params": dict(r.stub_params)}
                      for r in b.chaos_rules},
        }
    from chaos_blackjack.app import config as cfg

    rc = cfg.RunConfig()
    lo, hi, bankroll = _bet_range_at()
    values = {
        "run.start_money": rc.start_money, "run.target_money": rc.target_money, "run.objective": rc.objective,
        "table.dealer_stand_on": rc.dealer_stand_on,
        "table.blackjack_pays_num": rc.blackjack_pays[0], "table.blackjack_pays_den": rc.blackjack_pays[1],
        "table.allow_double": rc.allow_double, "table.allow_surrender": rc.allow_surrender,
        "shop.slots": rc.shop_slots, "shop.refresh_rounds": rc.shop_refresh_rounds,
        "bet.min": lo, "bet.max_fraction": round(hi / bankroll, 4),
    }
    settings = {k: {"value": v, "type": _SETTING_DOCS[k][0], "min": None, "max": None,
                    "description": _SETTING_DOCS[k][1]} for k, v in values.items()}
    return {"settings": settings, "prices": dict(rc.shop_prices), "item_params": {}, "rules": {}}


def _sqlite_settings(data: Any) -> dict[str, Any]:
    name = getattr(importlib.import_module("chaos_blackjack.data.balance"), "DEFAULT_PROFILE", "default")
    conn = data.connect(":memory:")
    try:
        rows = conn.execute(
            "SELECT s.key, s.value, s.type, s.min, s.max, s.description FROM setting s "
            "JOIN balance_profile p ON p.id = s.profile_id WHERE p.name = ? ORDER BY s.key", (name,)
        ).fetchall()
    finally:
        conn.close()
    casts = {"int": int, "float": float, "bool": lambda v: v in ("1", "true"), "str": str}
    return {k: {"value": casts.get(t, str)(v), "type": t, "min": lo, "max": hi, "description": d}
            for k, v, t, lo, hi, d in rows}


def _bet_range_at() -> tuple[int, int, int]:
    """(min bet, max bet, bankroll) at the start of a fresh run."""
    from chaos_blackjack.agent import AgentSession

    obs = AgentSession.new(seed=0).execute({"cmd": "observe"})["obs"]
    lo, hi = obs["bet_range"]
    return int(lo), int(hi), int(obs["bankroll"])


# --- rules and items -------------------------------------------------------

def _manifest() -> dict[str, Any]:
    try:
        from chaos_blackjack.gui.assets.manifest import MANIFEST
    except Exception:  # pygame missing or GUI moved: names fall back to ids
        return {}
    return MANIFEST


def _icon(root: Path, asset_id: str) -> str | None:
    hits = sorted((root / "assets").rglob(f"{asset_id}.png"))
    return hits[0].relative_to(root).as_posix() if hits else None


def _title(asset_id: str, manifest: dict[str, Any]) -> str:
    spec = manifest.get(asset_id)
    return spec.description if spec and spec.description else asset_id.replace("_", " ").title()


def _chaos_rules(root: Path, balance: dict[str, Any]) -> dict[str, Any]:
    from chaos_blackjack.registry import get_registry
    from chaos_blackjack.ui.descriptions import describe_modifier

    reg = get_registry()
    manifest = _manifest()
    profiles = _permissions(root)
    out = {}
    for rid in sorted(reg._chaos_rules):
        tuned = balance["rules"].get(rid, {})
        mod = reg.build_chaos_rule(rid, tuned.get("params") or {})
        params = {}
        if mod is not None and dataclasses.is_dataclass(mod):
            params = {k: v for k, v in dataclasses.asdict(mod).items() if k not in ("id", "chaos_flags")}
        out[rid] = {
            "name": _title(rid, manifest),
            "effect": describe_modifier(mod) if mod is not None else "",
            "params": _jsonable(params),
            "flags": sorted(getattr(mod, "chaos_flags", ()) or ()),
            "enabled": tuned.get("enabled", True),
            "stub_weight": tuned.get("stub_weight"),
            "profiles": sorted(n for n, p in profiles.items() if rid in p["allowed_rules"]),
            "icon": _icon(root, rid),
        }
    return out


def _items(root: Path, balance: dict[str, Any]) -> dict[str, Any]:
    from chaos_blackjack.app.help_text import ITEM_HELP
    from chaos_blackjack.registry import get_registry

    manifest = _manifest()
    out = {}
    for iid in sorted(get_registry()._items):
        out[iid] = {
            "name": _title(iid, manifest),
            "help": ITEM_HELP.get(iid, ""),
            "price": balance["prices"].get(iid),
            "params": _jsonable(balance["item_params"].get(iid, {})),
            "icon": _icon(root, iid),
        }
    return out


def _permissions(root: Path) -> dict[str, Any]:
    out = {}
    for f in sorted((root / "chaos_blackjack/ai/permissions").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        out[f.stem] = {
            "allowed_rules": sorted(p.get("allowed_rules", [])),
            "allowed_items": sorted(p.get("allowed_items", [])),
            "max_actions_per_turn": p.get("attempt_limits", {}).get("max_actions_per_turn"),
            "max_active_effects": p.get("attempt_limits", {}).get("max_active_effects"),
            "chaos_budget": p.get("budget", {}).get("chaos_budget"),
            "charge_per_effect": p.get("budget", {}).get("charge_per_effect"),
        }
    return out


def _assets(root: Path) -> dict[str, Any]:
    return {aid: {"name": spec.description or aid, "category": spec.category, "size": list(spec.size),
                  "file": _icon(root, aid)}
            for aid, spec in sorted(_manifest().items())}


# --- agent interface -------------------------------------------------------

def _agent(root: Path) -> dict[str, Any]:
    from chaos_blackjack.agent.observation import ACTION_HELP, OBS_SCHEMA

    main = (root / "chaos_blackjack/agent/__main__.py").read_text(encoding="utf-8")
    session = (root / "chaos_blackjack/agent/session.py").read_text(encoding="utf-8")
    commands = dict(re.findall(r'add_parser\(\s*"(\w+)",\s*help="([^"]*)"', main))
    codes = set(re.findall(r'_error\(\s*"(\w+)"', session)) | set(re.findall(r'"code":\s*"(\w+)"', main))
    return {
        "obs_schema": OBS_SCHEMA,
        "commands": commands,
        "actions": {str(getattr(k, "value", k)): v for k, v in ACTION_HELP.items()},
        "error_codes": sorted(codes),
    }


def _transcript() -> dict[str, Any]:
    """A short seeded chaos run with a simple policy; same game commit -> same transcript."""
    from chaos_blackjack.agent import AgentSession

    s = AgentSession.new(seed=TRANSCRIPT_SEED, chaos=True)
    steps = []
    reply = s.execute({"cmd": "observe"})
    rounds = 0
    while len(steps) < 40:
        obs = reply["obs"]
        if obs["phase"] == "betting":
            if rounds == TRANSCRIPT_ROUNDS:
                break
            rounds += 1
            cmd = {"cmd": "bet", "amount": TRANSCRIPT_BET}
        elif obs["phase"] == "player_turn":
            total = (obs.get("you") or {}).get("total") or 0
            cmd = {"cmd": "act", "action": "hit" if total < 17 and "hit" in obs["legal_actions"] else "stand"}
        else:
            break
        reply = s.execute(cmd)
        steps.append({"command": cmd, "ok": reply.get("ok"), "events": reply.get("events", []),
                      "obs": {k: reply["obs"].get(k) for k in _BRIEF_KEYS if reply["obs"].get(k) is not None}})
    return {"seed": TRANSCRIPT_SEED, "chaos": True, "steps": _jsonable(steps)}


def _jsonable(value: Any) -> Any:
    return json.loads(json.dumps(value, default=lambda o: getattr(o, "value", str(o))))
