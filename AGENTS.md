# Updating the wiki (agent procedure)

This repository is the Chaos Blackjack wiki. It is **separate from the game**:
never edit the game repository or another agent's worktree from here.
Python 3.10+, stdlib only (pytest for the self-tests). Run everything from this folder.

## The update loop

```bash
python -m wiki sync            # check out game `main`, extract facts, write DRIFT.md
#   ... handle DRIFT.md (below) ...
python -m wiki build           # render site/
python -m wiki check           # must end with 0 error(s)
python -m pytest -q            # only if you touched wiki/*.py
git add -A && git commit       # message: "Sync wiki to game <sha>" + DRIFT summary
```

`python -m wiki all` runs sync, build and check in one go (use it when you expect no drift).

- `sync` reads the game from its own throw-away worktree
  `<game>/.agent_runs/worktrees/wiki-src` (detached, read-only for you). It never
  uses the shared checkout, so other agents' unmerged work cannot leak in.
- `--ref` picks another ref (default `main`, or `$WIKI_GAME_REF`). By default the
  site describes `main`; other refs are for testing the adapter, so sync back to
  `main` before committing, unless the user explicitly selects the current development version.
  On 2026-10-14 the author selected the committed branch `feat/poker-head-builds`
  (`python -m wiki sync --ref feat/poker-head-builds`): the Poker Head and J-54
  work that game `main` merged, plus new art that is not in `main` yet. Document its
  Poker Head products and environment as the official current scheme and mark
  J-54 experimental. Do not replace it with older `main` facts merely because
  the art has not merged; switch back to `main` once `main` contains it. Never
  modify the shared game checkout.
- The game repo is the sibling folder `../Black_jack`, or `$CHAOS_BLACKJACK_REPO`.

## Handling DRIFT.md

| Kind | Meaning | What you do |
| --- | --- | --- |
| `breaking` | extracting facts failed (game API moved) | fix `wiki/adapter.py` only; `facts.json` is left untouched until it works |
| `new` | new rule / item / setting / asset / design doc, or one without prose | write `content/en/<chaos\|items>/<id>.md` **and** `content/zh/...` (see below) |
| `removed` | id gone from the game | delete its `content/*/<folder>/<id>.md`; fix prose that mentions it |
| `stale` | prose mentions an id that was removed | rewrite that sentence |
| `auto` | a number or text changed | nothing to write; tables update themselves. Re-read the prose of that page if the change alters strategy |

Design docs: `sync` also scans `docs/design/*.md` on **every local branch** of the
game (newest version wins). They are plans, not facts, so they get their own
"Design" section with a "planned / in main" banner. A `new` design doc needs
`content/{en,zh}/design/<slug>.md` (`META_PROGRESSION.md` -> `meta-progression`)
with `title:` and `source_blob:` (the doc's `blob` from `facts.json`); a `stale`
one means the doc changed: read the `git diff` named in DRIFT.md, update both
languages and `source_blob`. Summarise faithfully; do not invent details the
doc does not state.

Simulator: when the balance simulator repo exists (`black-jack-sim/` in the game
checkout, or `$BJSIM_REPO`), `sync` checks out its `main` into
`<game>/.agent_runs/worktrees/wiki-sim` and runs `bjsim check`, `edge` and
`items` against the game worktree (about a minute; results are reused while
neither commit moves). Results feed the Balance data and Simulator pages and
the rule / item cards. `--no-sim` skips measuring and reports `stale`. A
`breaking` entry on `sim` means the simulator itself failed against game main:
that fix belongs in `black-jack-sim`, never in this repo. `OUT OF BAND` in an
`auto` entry means a game change moved balance; report it, do not hide it.

`check` also warns about stale translations: when the English effect/help of a
rule or item changes, the Chinese page falls back to English until you update
its `effect`/`help` **and** copy the new English text into `effect_en`/`help_en`.

## Writing content

- Two languages, same structure: `content/en/` and `content/zh/`. A missing
  Chinese page falls back to English with a notice; `check --strict` turns
  missing translations into errors.
- **Never hand-type a value that is in `facts/facts.json`.** Use placeholders:

  | Placeholder | Renders |
  | --- | --- |
  | `{{ fact: settings.run.start_money.value }}` | the value (dotted keys work) |
  | `{{ link: items.peek }}` | link to the item / rule page, localized name |
  | `{{ table: NAME }}` on its own line | generated block: `settings`, `prices`, `permissions`, `commands`, `actions`, `errors`, `transcript`, `gallery`, `changelog`, `chaos_cards`, `item_cards`, `environment_cards`, `poker_products` |

  Card blocks group themselves by the table that offers each id (the table's
  `rules`, `environment_rules`, `items` + `products` in facts), released tables
  first, then experimental ones, then "Not used at any table". Never sort cards
  by id prefix (`ph_`, `j54_`) in `wiki/*.py`.

  An unknown placeholder fails the build, so renamed ids cannot go unnoticed.
- Rule / item pages: the card (icon, effect, params, price) is generated; the
  Markdown body is optional strategy notes. Chinese front matter:

  ```markdown
  ---
  name: 偷看
  help: 查看牌堆下一张牌的点数。
  help_en: Reveal the rank of the next card in the deck.
  ---
  ```

  (rules use `effect` / `effect_en`; `*_en` must equal the current English text
  in `facts.json`).
- Page list and nav groups: `wiki/i18n.py` (`PAGES`). Sources are grouped in
  folders (`guides/`, `growth/`, `dev/`, `reference/`; catalog hubs such as
  `chaos.md` stay top-level next to their entity folders), but every page is
  published flat as `site/<lang>/<name>.html`, so moving a source never breaks
  links. When a page is merged or retired, add `old-name -> new target` to
  `REDIRECTS` in the same file and point prose links at the new target. Interface strings in both
  languages: `UI` in the same file; per-language data strings (setting and error
  code descriptions): `content/<lang>/strings.json`.
- Dealer and Table pages use `content/<lang>/{dealers,tables}/<game-id>.md`.
  Their relationships, goals and effective rule/item pools come from facts.
  Progression, cosmetic and achievement catalogs are generated too; Chinese
  `strings.json` catalog entries retain `name_en` / `description_en` for drift checks.
- Navigation is generated: a new table or dealer in facts appears under "Tables
  and dealers" by itself; just write its `{tables,dealers}/<id>.md`. The
  "Experimental" label comes from the game's `tables.<id>.experimental` (a dealer
  is experimental when all its tables are); never hard-code ids in `wiki/*.py`.
  `check` rejects top-level pages missing from `PAGES` and `PAGES` entries that
  shadow a generated page (`table-<id>`, `dealer-<id>`, `item-<id>`...).
- Author-supplied designs that are not in the game yet are editorial top-level
  pages with `status: draft` and `source: user` (added to `PAGES`). J-54 is in
  the game now, so its pages are `tables/j54.md` and `dealers/j54.md`.
  The author now requests current J-54 pages with an experimental label, while
  preserving early concept documents as historical background. Do not invent game ids, prices or measured
  results. Editorial portraits live in `content/img/`, which sync never prunes.
- Repository language: code, comments and commits in English; Chinese only in
  `content/zh/` and the `zh` interface strings.

## Rules

- Only `wiki/adapter.py` may import `chaos_blackjack`. Facts must be JSON-safe
  and deterministic (sorted, no timestamps) so `git diff facts/` is the history.
- The adapter forces `CHAOS_USE_LLM=0` and an in-memory database: no billed
  calls, no writes to the game's `data/game.db`.
- Only write prose that DRIFT.md or the user asks for; do not restyle pages
  on the side.
- `site/` and `DRIFT.md` are build output and git-ignored. `facts/facts.json`
  and `facts/img/` are committed.

## Viewing

Open `site/index.html` in a browser (it picks English or Chinese and remembers
the choice). Everything works from `file://`.
