# Chaos Blackjack Wiki

[![CI](https://github.com/fghhn13/Chaos_Blackjack_wiki/actions/workflows/ci.yml/badge.svg)](https://github.com/fghhn13/Chaos_Blackjack_wiki/actions/workflows/ci.yml)

A static, bilingual (English / 中文) wiki for
[Chaos Blackjack](https://github.com/fghhn13/Chaos_Blackjack), generated from the
game's `main` branch and maintained mostly by agents.

```bash
python -m wiki all         # sync facts from game main, build site/, check
# then open site/index.html
```

- **Separate repository.** The game never imports it. It sits next to the game
  checkout (`../Black_jack`, or `$CHAOS_BLACKJACK_REPO`).
- **Facts are extracted, prose is written.** `wiki/adapter.py` (the only module
  that imports the game) reads ids, numbers, help text, art and a replayed agent
  transcript into `facts/facts.json`; pages combine those facts with Markdown in
  `content/<lang>/`.
- **Balance numbers are measured.** When the balance simulator
  (`black-jack-sim`) is present, `sync` runs it on game `main` and stores the
  results: player EV per chaos rule, item value and the regression bands.
- **Drift is reported, not guessed.** `sync` writes `DRIFT.md`, which lists what
  changed in the game and what prose needs writing.

Update procedure for agents: [AGENTS.md](AGENTS.md). Design and rationale:
[DESIGN.md](DESIGN.md).

## Layout

```text
wiki/          adapter (game seam), facts/diff, Markdown renderer, build, check, static CSS/JS
facts/         facts.json + img/ (committed snapshot of what the site describes)
content/en/    English pages; chaos/<rule>.md, items/<item>.md notes; strings.json
content/zh/    Chinese pages, same structure
tests/         self-tests (no game checkout needed)
site/          build output (git-ignored)
```

Python 3.10+, standard library only; `pytest` for the tests.

CI (`.github/workflows/ci.yml`) runs the self-tests, builds the site from the
committed facts and runs `check --strict` (missing translations fail) on
Ubuntu (3.10, 3.12) and Windows (3.12). The built site is attached to each run
as the `wiki-site` artifact. CI never touches the game repository.

## GitHub Pages

The `pages.yml` workflow tests, builds and validates the committed snapshot,
then publishes `site/` on every push to `main`. It does not sync the game.

For the initial setup, open repository **Settings > Pages** and select
**GitHub Actions** as the build source. Private repositories require a GitHub
plan that supports Pages; keep this repository private unless publication of
its source is intended. A published Pages site may be publicly accessible even
when the source repository is private.

After enabling Pages, run **Deploy Wiki to GitHub Pages** from the Actions tab
(or push a commit to `main`). The deployment environment shows the final site URL.
