---
title: Balance simulator
---
`bjsim` plays thousands of rounds and whole runs with scripted bots to measure house edge, the impact of each chaos rule, item value, shop pricing and run length. It lives in its own repository (`black-jack-sim`); the game never imports it and it never changes the game. Measured results are on the [Balance data](balance.html) page.

## How it stays honest

- **One seam.** Only the simulator's `bjsim/adapter.py` imports the game. When the game's API changes, that file is updated and nothing else.
- **Visible state only.** Bots see what a player sees, with two documented exceptions: the cards an information item has just revealed, and rewritten shop prices for pricing experiments.
- **No billing.** The Chaos AI is always a scripted stand-in; no real model is called.
- **Reproducible.** Same seed, same results, whatever the number of worker processes. By default it simulates the game's shipped balance values, not your local database.

## Running it

Python 3.10+, no extra packages. Run inside `black-jack-sim/`, next to a game checkout.

{{ table: sim_commands }}

Common options: `--profile NAME` (simulate a balance profile from the game's database), `--rounds N`, `--runs N`, `--seed N`, `--jobs N` (processes; never changes results), `--out FILE` (`.md` or `.json`).

{{ table: sim_options }}

- `--chaos stub` is the game's own offline Chaos AI as the balance profile sets it; `mix` picks uniformly from all rules.
- `--shop eager` buys anything useful (keeping a reserve); `--shop value` buys one item when it is worth it at a maximum bet.
- `--prices fixed:<factor>` multiplies the game's prices; `scaled:<pct>` makes peek cost that share of the bankroll and the others proportionally.
- `upgrades` measures upgrade levels on matched deals, reporting changes in win rate and tokens per run, plus token payback time.
- `career` simulates repeated runs and meta purchases with `--policy none|permanent|consumable|mixed`, `--careers N` and `--length N`; comma-separated policies can be compared in one report.

## Bots

Bots play classic basic strategy without splitting, shifted when a rule moves the bust line, but they do not otherwise adapt to chaos rules. Results under chaos are therefore a "naive player" view: someone who exploits a rule does better.

## Regression bands

The simulator keeps a list of key metrics with allowed ranges (`bands.json`). `python -m bjsim check` measures them; a value outside its band means a game change moved the balance. When that is intended, the band is re-measured and updated in the same change.

The current report has out-of-band measurements, shown below. The wiki preserves them; updating the simulator's regression bands belongs in its separate repository. The stub metric's label still describes the earlier value-shift-only setup, while the current profile draws a weighted mix including calm rounds.

{{ table: sim_bands }}

## How the wiki uses it

On every `python -m wiki sync` the wiki runs the simulator from a clean checkout of its `main` against a clean checkout of the game's `main`, and stores the results as facts. Results are reused while neither commit changes, so the numbers on this wiki always say which game and simulator commits they come from.
