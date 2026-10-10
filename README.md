# Chaos Blackjack Wiki

A static, bilingual (English / 中文) wiki for
[Chaos Blackjack](https://github.com/fghhn13/Chaos_Blackjack), generated from the
game's `main` branch and maintained mostly by agents.

```bash
python -m wiki all         # sync facts from game main, build site/, check
# then open site/index.html
```

- **Separate repository.** The game never imports it. It normally sits inside the
  game checkout as `black-jack-wiki/` (excluded there), like `black-jack-sim/`.
- **Facts are extracted, prose is written.** `wiki/adapter.py` (the only module
  that imports the game) reads ids, numbers, help text, art and a replayed agent
  transcript into `facts/facts.json`; pages combine those facts with Markdown in
  `content/<lang>/`.
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
