# Chaos Blackjack Wiki — design (v1)

A static wiki for Chaos Blackjack, kept **outside the game** and maintained
mostly by agents. v1 is built; the day-to-day procedure is in [AGENTS.md](AGENTS.md).

## 1. Principles

1. **Independent.** Separate repository (`Black_jack_wiki/`, next to the game
   checkout `Black_jack/`). The game never imports it, and the
   wiki never writes to the game.
2. **One seam.** `wiki/adapter.py` is the only module that imports
   `chaos_blackjack`. When the game's API moves, fix the adapter, nothing else.
3. **Facts are extracted, prose is written.** Every number, id, price, param
   and command comes from the game at build time. Humans/agents write only
   explanations, strategy and lore. A hand-typed number is a bug.
4. **Built from `main`, not from working trees.** Several agents edit the game
   in parallel; the wiki reads a clean checkout of a named ref (default
   `main`) so half-finished work never leaks onto the site.
5. **Every page is stamped** with the game commit it describes. Drift is
   detected, never guessed.
6. **Static output, no runtime.** Plain HTML/CSS/(tiny JS for search), opens
   from `file://`, hostable anywhere. Python 3.10+, stdlib only to build.

## 2. What the wiki shows

Legend: **F** = generated from facts, **P** = hand-written prose, **F+P** = both.

| # | Page | Content | Kind | Source in the game |
|---|------|---------|------|--------------------|
| 1 | Home | One-paragraph pitch, how to start (GUI / CLI / agent), "describes commit `abc1234` of `main`, built 2026-10-10" | F+P | git, README |
| 2 | Rules | Bankroll, target, bet range, payouts, double / surrender, dealer rule, run end | F+P | `default` balance profile (`data/seed/default.sql` via the `Balance` loader) |
| 3 | Chaos rules (index + one card each) | Icon, id, display name, effect, tuning params, stub weight, which permission profiles allow it, enabled flag, strategy notes | F+P | registry (`register_rule`), `chaos_rule` table, `ui/descriptions.py`, `ai/permissions/*.json`, `assets/<id>.png` |
| 4 | Items (index + one card each) | Icon, id, help text, price, params, when usable, strategy notes | F+P | registry (`register_item`), `ITEM_HELP`, `shop_item` table, assets |
| 5 | Shop & economy | Slots, restock interval, purchase floor, price table | F+P | balance profile |
| 6 | The Chaos AI | Pipeline (observe → JSON → permission check → registry), budget, difficulty profiles, prompt personalities, stub vs real LLM, safety | F+P | `ai/permissions/*.json`, `ai/prompts/*.txt` (names only), README |
| 7 | Balance profile reference | Every setting: key, default, type, min/max, description | F | `setting` table |
| 8 | How to play: GUI | Controls table per phase, scenes, settings | F+P | README / `gui` key map |
| 9 | How to play: agents | Command reference, observation fields, legal actions, error codes, **live transcript** | F+P | agent CLI; transcript produced by actually running `python -m chaos_blackjack.agent` with a fixed seed |
| 10 | Content packs / modding | How to add a rule, item, prompt, pack (once `codex/content-workflow` lands on `main`) | F+P | `extensions/`, `docs/CONTENT_WORKFLOW.md` |
| 11 | Art gallery | Every manifest asset: id, category, size, final vs placeholder, thumbnail | F | `gui/assets/manifest.py`, `assets/` |
| 12 | Balance data (optional) | House edge per chaos rule, item EV, run win rate | F | latest `black-jack-sim` report (JSON), stamped with its own commit |
| 13 | Architecture | Layer diagram, module table, plugin rule | F+P | README, package tree |
| 14 | Changelog | Player-visible changes per merge to `main`, newest first | F+P | `git log` on `main` + facts diff between builds |
| 15 | Glossary | Natural, push, bust, hole card, chaos budget, restock… | P | — |

Every rule/item card has the same layout, so new content needs only a
paragraph of prose to look complete; without prose it still renders from facts
and shows a "no notes yet" badge.

## 3. Repository layout

```text
Black_jack_wiki/
├── DESIGN.md                 # this file
├── AGENTS.md                 # the update procedure below, short form
├── wiki/
│   ├── adapter.py            # ONLY module importing chaos_blackjack
│   ├── extract.py            # adapter → facts/facts.json (sorted, deterministic)
│   ├── diff.py               # old facts vs new facts → drift report
│   ├── build.py              # facts + content → site/
│   ├── check.py              # coverage, links, placeholders, stale prose
│   └── templates/            # page + card HTML, one CSS file
├── facts/
│   ├── facts.json            # committed: the snapshot the site was built from (incl. the agent transcript)
│   └── img/<id>.png          # committed: art snapshot from the same commit
├── content/                  # hand-written prose, Markdown + front matter
│   ├── en/ zh/               # same structure per language
│   │   ├── rules.md ...      # one file per page (wiki/i18n.py: PAGES)
│   │   ├── chaos/<rule_id>.md  # notes per rule (optional; missing = "no notes yet")
│   │   ├── items/<item_id>.md
│   │   └── strings.json      # setting / error-code descriptions
├── site/                     # build output (git-ignored or a gh-pages branch)
└── tests/
```

Prose pulls facts through placeholders, never copies them:

```markdown
Peek costs {{ fact: items.peek.price }} chips.
{{ table: chaos_rules }}
```

`check` fails on an unknown placeholder, so a renamed id breaks the build
instead of silently showing old text.

### `facts.json` shape (sketch)

```json
{
  "source": {"ref": "main", "commit": "729d8d1", "date": "2026-10-10"},
  "balance": {"run.start_money": {"value": 100, "type": "int", "min": 2, "max": null, "description": "..."}},
  "chaos_rules": {"fragile_bust": {"name": "Fragile Table", "effect": "...", "params": {"bust_limit": 18},
                   "stub_weight": 0, "enabled": true, "profiles": ["easy", "hard"], "icon": "fragile_bust.png"}},
  "items": {"peek": {"help": "...", "price": 10, "params": null, "icon": "peek.png"}},
  "permissions": {"easy": {"budget": 5, "max_actions_per_turn": 1}},
  "assets": {"peek": {"category": "item", "size": [128, 128], "final": true}},
  "agent_cli": {"commands": ["new", "observe", "buy", "bet", "act"], "error_codes": ["illegal_action", "..."]}
}
```

## 4. Agent update workflow

### Triggers

- A PR merges into `main` (manual: "update the wiki"; later: a scheduled run
  that checks whether `main` moved since `facts.json.source.commit`).
- A new `black-jack-sim` report (balance page only).
- Someone asks for prose on a specific page.

### Steps

```text
1. sync    python -m wiki sync   check out `main` into <game>/.agent_runs/worktrees/wiki-src (detached),
                                 extract in a subprocess, overwrite facts/facts.json + facts/img/,
                                 write DRIFT.md (old facts = the committed ones). On failure facts are
                                 left untouched and DRIFT.md has one `breaking` entry with the traceback.
2. triage  read DRIFT.md: breaking / new / removed / stale / auto
3. write   edit content/{en,zh}/ for flagged entries only
4. build   python -m wiki build  -> site/ + site/.stamp (hash of facts + content)
5. check   python -m wiki check  -> 0 errors
6. commit  in the wiki repo: "Sync wiki to game <sha>"
```

`DRIFT.md` example:

```text
Game 434396f → 729d8d1 (3 commits on main)
auto     items.peek.price            10 → 12
auto     balance.shop.refresh_rounds 2 → 3
new      items.lucky_coin            no content/items/lucky_coin.md
stale    content/rules.md:14         mentions "streak reward" (removed in 1b7a861)
```

### Agent rules

- Never edit the game repo or another agent's worktree; read-only `git` on it.
- Never hand-type a value that exists in `facts.json`; use a placeholder.
- Only touch prose that `DRIFT.md` flags, unless asked otherwise.
- `check` must pass before commit; a failing transcript replay means the
  documented commands changed, so update the page, not the transcript output.
- No billed LLM calls: the adapter forces `CHAOS_USE_LLM=0`; transcripts use the stub.
- Repository language follows the game repo convention (see open question 2).

### Checks performed by `check`

| Check | Fails when |
|-------|-----------|
| Coverage | a registered rule/item/setting has no card (prose optional, card required) |
| Placeholders | `{{ fact: x }}` names a path not in facts |
| Stale ids | prose mentions an id/command/flag absent from facts |
| Links | internal link or image target missing |
| Translations | (warning) a Chinese `effect`/`help` was made from English text that has since changed (`*_en` mismatch) |
| Stamp | `site/` built from other facts/content than the current ones |

The agent transcript is re-run on every sync, so a changed transcript shows up as an `auto` drift entry instead of a separate replay check.

## 5. Status and next steps

Done in v1: pages 1–9, 11, 13–15; bilingual content; sync / build / check; self-tests.

Next:

1. Content packs page (the content workflow is now in `main`).
2. Done: Simulator and Balance data pages from `black-jack-sim` runs on game `main`.
3. Optional scheduled sync (only runs when `main` moved past `facts.source.commit`).
4. Mention the wiki in the game's AGENTS.md.

## 6. Decisions

| Question | Decision |
| --- | --- |
| Location | separate repository `Black_jack_wiki/`, sibling of the game checkout |
| Language | bilingual: facts shared, prose per language, Chinese falls back to English |
| Hosting | local only: open `site/index.html` (works from `file://`) |
| Scope of truth | game `main` only (the local branch, which is ahead of `origin/main` today) |
