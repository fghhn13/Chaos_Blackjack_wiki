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
- `--ref` picks another ref (default `main`, or `$WIKI_GAME_REF`). The site only
  ever describes `main`; other refs are for testing the adapter, so sync back to
  `main` before committing.
- The game repo is the sibling folder `../Black_jack`, or `$CHAOS_BLACKJACK_REPO`.

## Handling DRIFT.md

| Kind | Meaning | What you do |
| --- | --- | --- |
| `breaking` | extracting facts failed (game API moved) | fix `wiki/adapter.py` only; `facts.json` is left untouched until it works |
| `new` | new rule / item / setting / asset, or a rule / item without prose | write `content/en/<chaos\|items>/<id>.md` **and** `content/zh/...` (see below) |
| `removed` | id gone from the game | delete its `content/*/<folder>/<id>.md`; fix prose that mentions it |
| `stale` | prose mentions an id that was removed | rewrite that sentence |
| `auto` | a number or text changed | nothing to write; tables update themselves. Re-read the prose of that page if the change alters strategy |

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
  | `{{ table: NAME }}` on its own line | generated block: `settings`, `prices`, `permissions`, `commands`, `actions`, `errors`, `transcript`, `gallery`, `changelog`, `chaos_cards`, `item_cards` |

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
- Page list and nav groups: `wiki/i18n.py` (`PAGES`); interface strings in both
  languages: `UI` in the same file; per-language data strings (setting and error
  code descriptions): `content/<lang>/strings.json`.
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
