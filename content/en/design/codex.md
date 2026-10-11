---
title: Codex and demos (M4a–M4b)
source_blob: 59faeb3196e5
---
The in-game codex described in [Meta progression, saves and the codex](design-meta-progression.html) has a headless engine (M4a) and gallery/detail screens (M4b). The engine needs neither Pygame nor a player save; the screens display its entries, live texts and demo frames.

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
- **Modes** come from `chaos_blackjack.modes.modes()`; the earlier base used `normal` and `chaos` as a fallback.
- **Content packs** selected by `RunConfig.content_packs` load into the controller's scoped registry. Their items, help text, rules and AI profiles appear without leaking into other configurations. The AI provider uses `Registry.ai_ids()` and `resolve_ai()` when available; the earlier base exposed only `ai/default`.

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

Every built-in chaos rule and item ships with a demo. The Reverse Bust demo shows the current behaviour: a bust ends your hand at once as a push.

## Gallery and playback

Open **Collection** from Home, or run `python -m chaos_blackjack.gui --scene codex`. The scene entry point is `app.scenes.push("codex", config=config)`; config defaults to `app.run_config`, and an optional `kind` selects the tab.

The gallery shows tabs and an icon/name grid, with pagination for additional entries. Tab / Shift-Tab changes category; Left / Right or the wheel changes page. Select a tile to open its detail; Back / Escape preserves the gallery category and page.

Detail text and demo frames are computed from the selected config before playback. The interface animates stored frames without running further controller actions. Space pauses or plays, R replays, and Left / Right seeks one frame and pauses. Playback stops at the final frame. The description scrolls with the wheel or Page Up / Page Down. Entries without a demo, or with a demo incompatible with the settings, show readable text without playback.

Classic and Chaos use the generated mode icons in the [art gallery](gallery.html). Missing art retains procedural fallbacks.

## Status

The source document is on `main`. It calls for registry/demo tests, GUI navigation and playback tests, the full suite, and the simulator's balance check. GUI coverage includes scrolling, icon fallbacks, text-only entries, content-pack isolation and rendering built-in frames.
