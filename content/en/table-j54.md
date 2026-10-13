---
title: J-54's Table *Experimental
status: experimental
parent: tables
---
![J-54 portrait](../img/j54.png)

J-54 *Experimental rebuilds the physical deck across rounds. Every round reshuffles the retained composition; removed cards are tracked. Inspection is truthful and reveals rank distribution, not draw order.

## Protocol and economy

Single Capture starts with a sealed Joker. Buy {{ link: items.j54_start_experiment }} to release it; drawing it as the player immediately pushes the hand and wins the run. The dealer returns it away from the top and adds a low-card penalty. Capital instead targets {{ fact: settings.mode.j54.capital_target.value }} chips.

Compute fees rise according to {{ fact: settings.mode.j54.fee_steps.value }}, every {{ fact: settings.mode.j54.fee_step_rounds.value }} rounds. The minimum bet respects the fee. Entropy adds {{ fact: settings.mode.j54.entropy.value }} low card(s) after settlement, or {{ fact: settings.mode.j54.entropy_experiment.value }} after starting the experiment. Freeze suspends injections.

## Contracts and rules

The shop restocks every {{ fact: settings.mode.j54.config.shop_refresh_rounds.value }} round(s). Low Purge, Streamline, High Injection, Freeze and Start Experiment act immediately or when their trigger is met; purchases sign contracts rather than stocking inventory. The rule and contract cards above show exact configured effects and prices.

Hover or pin the shoe to inspect composition. Deck and Contracts tabs show details; the chart compares the deck with a standard one. Double Capture, Eradication, misleading reports and challenges remain future ideas; current play has Single Capture and Capital. The [early concept](https://github.com/fghhn13/Chaos_Blackjack_wiki/blob/main/content/sources/J54_TABLE.md) is historical background, including older placeholder values.
