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
The nav groups below are `PAGES` in `wiki/i18n.py`, in order; the source path
is `content/<lang>/<path>.md`. Every page publishes flat as
`site/<lang>/<last segment>.html`, so moving a source never changes its URL.

| Nav group | Page (source path) | Content | Kind | Source in the game |
|-----------|--------------------|---------|------|--------------------|
| Start | Home (`index`) | Pitch, how to start (GUI / CLI / agent), the commit the site describes | F+P | git, README |
| Start | Play (`play`) | GUI controls per phase, scenes, choosing a table | F+P | README / `gui` key map |
| Start | Rules (`rules`) | Classic baseline: bankroll, target, bets, payouts, double / surrender, dealer rule | F+P | `default` balance profile |
| Tables and dealers | Tables (`tables`) + one page per table | Host, goal, bet range, payout, rule / item pools, experimental state | F+P | game modes (`tables` in facts) |
| Tables and dealers | Dealers (`dealers`) + one page per dealer | Character, quote, tables hosted | F+P | host profiles (`dealers` in facts) |
| Catalog | Environment (`environment`) + one card each | Environment cards and how the offline director uses them | F+P | Poker Head environment registry, director settings |
| Catalog | Chaos rules (`chaos`) + one card each | Icon, effect, params, stub weight, permission profiles, tables, strategy notes | F+P | registry (`register_rule`), `chaos_rule` table, `ai/permissions/*.json` |
| Catalog | Items (`items`) + one card each | Icon, help, price / kind, timing, params, tables, strategy notes | F+P | registry (`register_item`), shop tables, Poker Head catalog |
| Guides | Poker Head builds (`guides/poker-head-builds`) | Cores, slots, cash / debt, product catalog by kind | F+P | Poker Head catalog, mode settings |
| Progression and collection | `growth/progression`, `profile`, `shop`, `cosmetics`, `achievements` | Upgrades, profile and saves, in-run shop, cosmetic and achievement catalogs | F+P | meta progression catalogs, balance profile |
| Under the hood | `dev/agents` | Command reference, observation fields, actions, error codes, **live transcript** | F+P | agent CLI run with a fixed seed |
| Under the hood | `dev/chaos-ai` | Director / AI pipeline, budgets, difficulty profiles, stub vs real LLM | F+P | `ai/permissions/*.json`, `ai/prompts/*.txt` (names only) |
| Under the hood | `dev/settings` | Every setting: key, default, type, min/max, description | F | `setting` table |
| Under the hood | `dev/balance`, `dev/simulator` | House edge per rule, item gain, win rates, bands; how to run the simulator | F+P | latest `black-jack-sim` results, stamped with their commit |
| Under the hood | `dev/architecture` | Layer diagram, module table, plugin rule | F+P | README, package tree |
| Design | Design (`design`) + one page per doc | Branch design docs with a "planned / in main" banner; early concepts as history | F+P | `docs/design/*.md` on every local branch |
| Reference | `reference/gallery`, `changelog`, `glossary` | Every art asset; player-visible changes; terms | F / F+P / P | asset manifest, `git log`, — |

Catalog pages group their cards by the table that offers each id (the table's
`rules`, `environment_rules`, `items` + `products`), released tables first,
then experimental ones, then "Not used at any table". The "Experimental" label
comes from `tables.<id>.experimental`; nothing in `wiki/*.py` names a game id.

Every rule/item card has the same layout, so new content needs only a
paragraph of prose to look complete; without prose it still renders from facts
and shows a "no notes yet" badge. Adding a table or dealer to the game adds its
nav entry and catalog section by itself; the wiki only needs its
`{tables,dealers}/<id>.md`.

## 3. Repository layout

```text
Black_jack_wiki/
├── DESIGN.md                 # this file
├── AGENTS.md                 # the update procedure below, short form
├── wiki/
│   ├── __main__.py           # CLI: sync / build / check / all
│   ├── adapter.py            # ONLY module importing chaos_blackjack → facts (sorted, deterministic)
│   ├── facts.py              # load / save / diff facts.json → drift report
│   ├── design.py             # docs/design/*.md from every local game branch
│   ├── sim.py                # balance simulator results (bjsim CLI in a subprocess)
│   ├── build.py              # facts + content → site/
│   ├── check.py              # links, placeholders, page layout, stale prose and translations
│   ├── i18n.py               # PAGES (nav), REDIRECTS, interface strings
│   ├── md.py                 # small Markdown subset
│   └── static/               # style.css, wiki.js
├── facts/
│   ├── facts.json            # committed: the snapshot the site was built from (incl. the agent transcript)
│   └── img/<id>.png          # committed: art snapshot from the same commit
├── content/                  # hand-written prose, Markdown + front matter
│   ├── en/ zh/               # same structure per language
│   │   ├── index.md play.md rules.md                   # Start
│   │   ├── tables.md dealers.md environment.md chaos.md items.md design.md
│   │   │                     # catalog hubs, beside their entity folders:
│   │   ├── tables/ dealers/ environment/ chaos/ items/ design/  # <id>.md notes per entity
│   │   ├── guides/ growth/ dev/ reference/              # other pages, grouped by nav group
│   │   └── strings.json      # setting / error-code / catalog descriptions
│   ├── img/                  # editorial portraits (never pruned by sync)
│   └── sources/              # author-supplied source documents, kept as history
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
| Links | internal link, anchor or image target missing |
| Page layout | a page source outside the entity folders is not in `PAGES`, or two pages / entity pages / redirects publish the same file name |
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
