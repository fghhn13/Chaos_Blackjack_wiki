---
title: How to play
---
## Desktop

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

On Windows, `start_game.bat` also launches the game. Create a player with **Start game**, then choose [Classic Table](table-normal.html) , [Poker Head's Table](table-chaos.html) or [J-54 *Experimental](table-j54.html) in **New run**. Review the table's goal, bets, rules, host and payout, then choose the starter items to bring. Nothing is consumed until **Start run**.

New runs begin with the host's dialogue. Enter / click advances and Escape skips. **Continue run** resumes a checkpoint without replaying the introduction.

| Phase | Mouse | Keyboard |
| --- | --- | --- |
| Betting | left-click chips to add, right-click to remove; Clear / Max; table Shop | Up / Down adjusts, Enter deals, B opens Shop |
| Your turn | Hit / Stand / Double / Surrender; inventory | H / S / D / R; I opens Bag; Tab opens the run panel |
| Round over | Next Round | Enter |
| Poker Head's Table | click the host portrait for advice | Enter closes the reply |
| Anywhere | Settings | Escape confirms leaving; F11 fullscreen; M mute; + / − volume; F5 reload art and sounds |

Home's **Shop** uses tokens for upgrades, cosmetics and starter items. The **table Shop** uses this run's bankroll. See [Player progression](progression.html). Click the player badge for [Profile](profile.html); **Switch player** manages slots.

**Collection** is grouped by Classic Table and dealer series. The Classic section contains the core table and common items; Poker Head's section introduces his character, rule pool and table-only items. Tab changes section; wheel or Page Up / Page Down scrolls. Rule/item details can show deterministic offline demos: Space pauses, R replays, Left / Right steps. Demos do not spend tokens or alter player progress.

## Browser and phones

The authenticated browser edition runs the same Pygame game in WebAssembly, with account saves. Registration requires a 16-digit invitation token. The first load may take time; loading feedback distinguishes downloading from starting. If prompted, tap **Start game** to start playback and unlock browser sound, including on iOS Safari. Browsers that allow audio automatically may skip that prompt. On touch devices, name creation and renaming use a native input field supporting composition; Save / Done confirms, Cancel keeps the existing name.

See [browser compatibility and builds](https://github.com/fghhn13/Chaos_Blackjack/blob/main/browser/README.md) and [deployment instructions](https://github.com/fghhn13/Chaos_Blackjack/blob/main/deploy/README.md).

On touch devices, swipe vertically to scroll lists, reference text and history details. A short tap selects; releasing a drag does not select an entry. Gestures inside the game scroll its content, while the surrounding web page remains scrollable.

## Text CLI and agents

```bash
python cli/main.py
python cli/main.py --enable-chaos
python -m chaos_blackjack.agent new --seed 7 --chaos
```

The text CLI retains the original hit / stand loop. The agent interface supports the controller's actions but does not apply player upgrades. Its `--chaos` flag remains for legacy play; `--mode chaos` starts the current build Table; see [Agent players](agents.html).

The default Chaos backend is offline. Enabling a real model through the game's configuration makes billed requests; details are in the game's README.

Poker Head begins with a core choice. Permanent products, consumables and finance each have their own timing. The side item slots support keys 1–9; Tab opens the run panel, Left / Right changes tabs, Escape or Tab closes it. See the [build guide](poker-head-builds.html).
