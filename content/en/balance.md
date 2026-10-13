---
title: Balance data
---
Historical measurements by the [balance simulator](simulator.html) on the older main snapshot; they do not measure current Poker Head builds or J-54. Each table names the command, seed, balance profile and commits it comes from.

## Reading the numbers

- **Player EV / bet**: the average bankroll change per round divided by the bet, for a basic-strategy player. `+10%` means the player gains a tenth of the bet per round on average; negative numbers favour the house.
- **Std. error**: the measurement's uncertainty. Differences smaller than about two standard errors are noise.
- **EV gain per use**: EV with the item used once per hand minus EV without it, on the same deals.
- Bots do not exploit chaos rules beyond moving their bust line, so a skilled player can do better than these numbers under chaos.

## Player EV under each chaos rule

The first row is plain blackjack. Rules with parameters are simulated with specific values, shown in the variant name.

{{ table: sim_edge }}

## Item value

Measured without chaos. A {{ link: items.shield }} only helps while a rule is active, so it measures nothing here; an information item shows no gain when the bots' item policy cannot act on what it reveals.

The current bot policy does not act on {{ link: items.danger_radar }}'s next-hit warning. Its zero here measures that policy's limitation, not the item's usefulness to a player.

{{ table: sim_items }}

## Regression bands

{{ table: sim_bands }}
