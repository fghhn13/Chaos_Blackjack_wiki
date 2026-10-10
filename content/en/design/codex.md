---
title: Codex and demos (headless, M4a)
source_blob: 4b483e5d3ec0
---
The engine behind the in-game codex described in [Meta progression, saves and the codex](design-meta-progression.html): the entries, their live texts and animated demos, without any GUI. It needs neither Pygame nor a player save; the codex screen (M4b) only displays what this layer produces.

## What the codex shows

- **Tabs** (`CodexKind`): rules, items, modes and AIs. A new kind gets its own tab.
- **Entries** (`CodexEntry`): kind, id, name, icon, summary, a detail text, an optional demo, and an order. Nothing is locked or hidden, not even rules the AI may not pick or items the current shop does not sell.
- **Live details**: every detail text is computed from the current `RunConfig`, so prices, restocking, the Fate Oracle card count, payouts, bet limits, dealer rule, mode overrides and Chaos advice settings always match the selected balance profile. Summaries and demo captions never state tunable numbers.

```python
from chaos_blackjack.app.config import RunConfig
from chaos_blackjack.codex import codex_entries, codex_kinds, run_demo

config = RunConfig()                      # or RunConfig.from_balance(profile)
tabs = codex_kinds()
entry = next(e for e in codex_entries("rule", config) if e.id == "great_crash")
text = entry.detail(config)
frames = run_demo(entry.demo, config)
```

## Where entries come from

- **Providers**: `register_codex_provider(kind, fn)` adds a function that receives the config and returns entries. A later provider can override an existing entry or add new ones.
- **Rules and items** are read from the live plugin registries on every query, so new plugins and content packs appear automatically (with a readable fallback name and no demo). A plugin can describe itself with optional `codex_name`, `codex_icon`, `codex_summary`, `codex_detail`, `codex_demo` and `codex_order` attributes.
- **Modes** come from the meta layer's mode list once it lands; until then the codex lists `normal` and `chaos`.
- **AIs**: the game has one Chaos AI pipeline, shown as `ai/default`; content packs can add more.

## Demos

A demo is a short script: two starting cards per hand, the rest of the deck in draw order, and a list of steps.

| Step | Effect |
| --- | --- |
| `deal` | rig the starting deal and place a real bet (exactly one per script) |
| `apply_rule` | show a registered chaos rule with the profile's live tuning (fixed profile values win) |
| `use_item` | use a real item |
| `hit`, `stand`, `double`, `surrender` | the normal player actions, with their usual permissions |
| `dealer` | play the dealer to the end, one frame per draw and decision |
| `caption`, `pause` | capture the current table with a caption |

`run_demo` plays the script on a **real game controller** with only the deal rigged, and returns frames (table view, caption, notices) for the GUI to animate. Because the real rules run, a demo can never contradict the game. Demos:

- never change the caller's config, balance numbers, saves, history or tokens;
- are always offline: no model is called and no credentials are loaded, even when the real LLM is enabled;
- fail loudly on a bad card, unknown step or illegal action instead of faking an effect;
- keep the dealer's hole card hidden until the game or an item reveals it.

All seven built-in chaos rules and all six items ship with a demo. The Reverse Bust demo shows the current behaviour: a bust ends your hand at once, but the settlement can still pay you.

## Status

Branch `feat/codex-core`. Validation: the codex tests, the full test suite, and the simulator's balance check against this checkout (balance must not move).
