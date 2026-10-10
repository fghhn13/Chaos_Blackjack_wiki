---
title: How to play
---
## Pygame window

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

| Phase | Mouse | Keyboard |
| --- | --- | --- |
| Betting | left-click a chip to add, right-click to remove; Clear / Max; Shop | ↑ / ↓ ±1, Enter deals, B opens the shop (1–3 buy) |
| Your turn | Hit / Stand / Double / Surrender buttons | H / S / D / R |
| Round over | Next Round | Enter |
| Anywhere | — | Esc menu (asks first), F11 fullscreen, F5 reload art |

Toggle **Chaos Mode** on the main menu. Art is optional: every image has a drawn placeholder (see the [art gallery](gallery.html)).

## Text CLI

```bash
python cli/main.py                 # menu: new game, load game, quit
python cli/main.py --enable-chaos
python cli/main.py demo            # one automated round
```

The text CLI still runs the original hit / stand loop; double, surrender and the shop are in the window and in the agent interface.

## Real LLM (optional)

By default the Chaos AI is an offline stand-in: no network, no cost. A real model can be switched on through the git-ignored `.env` file; see the game's README, section "Real LLM". Real requests are billed.
