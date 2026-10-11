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
| Chaos Mode | click the Chaos portrait to [ask for advice](chaos-ai.html#asking-chaos-for-advice) | — |
| Anywhere | — | Esc menu (asks first), F11 fullscreen, M mute, + / − volume, F5 reload art and sounds |

The game opens on **Home**. Create a named player with **Start game**; the **Players** page lets you switch, rename or delete saves. In **New run**, choose Classic or Chaos, review permanent upgrades and select consumables. Only **Start run** consumes selected items; you may bring {{ fact: settings.meta.bring_kinds.value }} different kinds before Bag Space upgrades.

Home offers **Continue run**, **Upgrades**, **Collection** and **Run history**. Runs save automatically; leaving the table with Escape asks you to abandon the run, which pays no tokens. Wins pay {{ fact: settings.meta.win_tokens.value }} tokens, plus {{ fact: settings.meta.chaos_win_bonus.value }} in Chaos; losses receive consolation capped at {{ fact: settings.meta.loss_cap.value }}. See [Meta progression](design-meta-progression.html) for the reward formula and upgrade catalog.

**Collection** shows rules, items, modes and AI profiles with live details and offline demos. Space pauses, R replays and Left / Right steps through frames. Demos do not change player progress. Art is optional: every image has a drawn placeholder (see the [art gallery](gallery.html)).

## Browser edition

The authenticated browser edition runs the original Pygame interface in WebAssembly, including progression, upgrades and account saves. Registration requires a 16-digit invitation token. See the game's [browser compatibility and builds](https://github.com/fghhn13/Chaos_Blackjack/blob/main/browser/README.md) and [deployment guide](https://github.com/fghhn13/Chaos_Blackjack/blob/main/deploy/README.md) for access and hosting details.

## Text CLI

```bash
python cli/main.py                 # menu: new game, load game, quit
python cli/main.py --enable-chaos
python cli/main.py demo            # one automated round
```

The text CLI still runs the original hit / stand loop; double, surrender and the shop are in the window and in the agent interface.

## Real LLM (optional)

By default the Chaos AI is an offline stand-in: no network, no cost. A real model can be switched on through the git-ignored `.env` file; see the game's README, section "Real LLM". Real requests are billed.
