---
title: Meta progression, saves and the codex
source_blob: dbc1dc45c09c
---
Between runs you will keep a **player**: a save slot with tokens, permanent upgrades and consumables. Every run is recorded, and a **codex** explains every rule, item, mode and AI with an animated demo. The agent CLI stays without meta progression so agent runs remain fair and reproducible.

All numbers below are **placeholders** from the design; the real values will live in the balance profile.

## Decisions

| Topic | Decision |
| --- | --- |
| Tokens | A win pays tokens. A loss pays a small consolation based on rounds survived and peak bankroll. |
| Temporary upgrades | Consumables: bought in the meta shop, stacked in the inventory; one of each selected is used up at the start of the next run. |
| Player saves | 3 named slots. |
| Codex | Every entry is shown normally (icon + name), no locks or silhouettes for now; "seen" data is collected for later. |
| Game modes | Chosen when starting a run. For now only `normal` and `chaos`, both unlocked. |
| Agents / simulator | The agent CLI has no meta progression. The simulator gets upgrade and token-economy experiments. |
| Numbers | Prices, rewards and upgrade values live in the balance profile, not in code. |

Naming: a **player** is a meta save (slot); a **balance profile** is a set of numbers. A player is never called a "profile".

## How it fits together

```text
player (slot 1-3) ── tokens, permanent upgrades (with level), consumables (with count)
   │
   ├─ start run(mode) ─► RunConfig = balance profile + mode + permanent upgrades
   │                                  + one use of each selected consumable
   │                       └─ game logic unchanged; the run's fingerprint shows the upgrades
   └─ finish run ──────► tokens (win or consolation), run history row, codex "seen" updates
```

## Tokens

| Setting | Default | Meaning |
| --- | --- | --- |
| `meta.win_tokens` | 10 | tokens for a victory |
| `meta.loss_per_round` | 0.2 | consolation per round survived |
| `meta.loss_per_peak_gain` | 4 | consolation per 100 % of the start bankroll gained at the peak |
| `meta.loss_cap` | 5 | consolation maximum |

```text
consolation = min(loss_cap, floor(rounds × loss_per_round
                                  + max(0, peak − start) / start × loss_per_peak_gain))
```

Example: a defeat after 20 rounds with a peak of 150 from a start of 100 pays min(5, floor(4 + 2)) = 5 tokens.

## Meta shop: first catalog

| Upgrade | Kind | Effect | Cost | Max level |
| --- | --- | --- | --- | --- |
| `start_money` | permanent | +10 starting bankroll per level | 15, +10 per level | 3 |
| `shop_slot` | permanent | +1 item on the run shop's shelf | 40 | 1 |
| `shop_discount` | permanent | −10 % run shop prices per level | 25, +15 per level | 2 |
| `start_<item>` | consumable | start the next run holding that item (one per shop item) | about half the item's shop price | — |

Level *n* of an upgrade costs `cost + (n − 1) × cost_step`. An upgrade can require another one to be owned first.

## Game modes

A mode is `GameMode(id, name, description, icon, overrides, unlocked_by)`: a set of `RunConfig` overrides. `normal` and `chaos` ship first; an `unlock_mode` upgrade effect exists for later modes but has no catalog entry yet.

## Run history

Each run stores its mode, balance profile and fingerprint, seed, result (`victory`, `defeat`, `abandoned`), rounds, final and peak bankroll, tokens earned, upgrades used, and a summary:

```json
{"rules_seen": {"great_crash": 2}, "items_used": {"peek": 3}, "items_bought": {"swap": 1},
 "rounds": 23, "peak_money": 260, "blackjacks": 2, "doubles": 4, "surrenders": 1,
 "chaos_ai": "default"}
```

Quitting mid-run records `abandoned` and pays no tokens.

## Codex

- Tabs per kind: rules, modes, items, AIs. Each entry has an icon, a name, a summary and a detail text that uses the live numbers of the current balance profile.
- Entries come from **providers** that read the rule, item, mode and AI registries, so plugins and content packs appear without codex changes.
- A **demo** is a short script (rigged deal plus steps such as `apply_rule`, `use_item`, `hit`, `dealer`, `caption`) played on a real game controller, so a demo can never disagree with the rules. Entries without a demo show a large icon and the text.

## Screens

| Screen | Content |
| --- | --- |
| Player select | 3 slots: create, continue, rename, delete (with confirmation) |
| Hub | tokens; Start run (mode picker and consumables to bring); Meta shop; History; Codex; Settings |
| Meta shop | permanent upgrades (level pips, next cost) and consumables (owned count) |
| Run result | victory or defeat, token breakdown, back to the hub |
| History | list of runs; detail with the summary |
| Codex | tabs per kind, grid of icon + name; detail with animated demo and text |

The main menu keeps **Quick play** (no player, as today) and the developer asset gallery.

## For developers

### Data model

New tables in the game database: `player` (slot 1–3, name, tokens), `player_upgrade` (level for permanent upgrades, count for consumables), `run_history`, `codex_seen` (per player, kind, entry; first seen, times). On the balance-profile side, `meta_upgrade` holds the catalog: kind, effect id and JSON params, cost and cost step, max level, enabled, requirement. Saved runs gain a player and run id.

### Extension points

| Registry | Adding content |
| --- | --- |
| Upgrade effects: `register_effect(id, fn(config, amount, params) -> RunConfig)` | a new effect is code; a new upgrade using an existing effect is one `meta_upgrade` row |
| Game modes: `register_mode(GameMode)` | one `GameMode` with its overrides |
| Codex providers: `register_codex_provider(kind, fn(config) -> list[CodexEntry])` | none for plugins: providers read the registries |

### Meta API (`chaos_blackjack/meta/`)

```python
list_slots() -> list[PlayerSlot]                 # always 3
create_player(slot, name) / rename_player(player_id, name) / delete_player(player_id)
get_player(player_id) -> Player                  # tokens, upgrades, stats
meta_shop(player_id, profile=None) -> list[UpgradeOffer]
buy_upgrade(player_id, upgrade_id) -> Player
modes() -> list[GameMode]
start_run(player_id, mode_id, *, consumables=(), profile=None, seed=None) -> RunStart
finish_run(run_id, controller) -> RunReward      # tokens + breakdown
abandon_run(run_id) -> None
history(player_id, limit=50) -> list[RunRecord]
```

An in-memory fake with the same behaviour ships first so the screens can be built before the real store. The controller gains `add_listener(fn)`, called for every notice without consuming it; the meta layer uses it to build the run summary.

### Codex API (`chaos_blackjack/codex/`)

```python
codex_kinds() -> list[CodexKind]                  # rule, mode, item, ai
codex_entries(kind=None, config=None) -> list[CodexEntry]
run_demo(script, config) -> list[DemoFrame]       # frames for the GUI to play
```

### Work plan

| Step | Owner | Branch |
| --- | --- | --- |
| 0. Integrate open feature branches into `main` (chaos poke, table UI with content packs and audio, animations, sound) | B | `integration/main` |
| M1–M2 data, meta logic, modes, effects, controller hook, fake | A | `feat/meta-core` |
| M4a codex registry, providers, demo scripts, `run_demo` (headless, tested) | C | `feat/codex-core` |
| M3 GUI screens | B | `feat/meta-gui` |
| M4b codex GUI | C | `feat/codex-gui` |
| M5 simulator: upgrades, token economy, first pricing | A | `black-jack-sim` |

Ground rules for every step: repository content in English (the Chinese player guide stays in sync), no billed calls in tests, game logic never reads the database, new numbers go into the balance profile, and "done" means feature tests, the full suite and the simulator's balance check all pass with docs updated.
