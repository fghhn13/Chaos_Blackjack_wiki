---
title: Carried chips: the vault, two tiers and Full Haul (Chinese)
source_blob: 0d9389a48444
---
A Chinese design for making chips persist between runs, discussed and agreed with the author. Until now each run's chips were free, so losing cost nothing and an all-in restart was often the rational play; this design makes the chips you bring your own.

## Principles

One currency: tokens are replaced by chips everywhere. No play style is forbidden (all-in gambling, relief then all-in, farming the low Table, spending for membership), but each must be less efficient than playing well. In a fair game, chips can only come from three sources: player advantage from items and builds, explicit rewards (relief, achievements, a Full Haul bonus), and discounts. The meta shop sells no power, only discounts.

## Tables and endings

Classic is the low tier with a small stake and an automatic win at a multiple of it; Poker Head's Table takes a larger stake, lets you leave with a **Full Haul** inside a window of multiples and caps profit at the top, reusing the profit-cap logic of the Withdrawal Limit rule. Below the window you cannot leave. A run ends in a Full Haul, going broke, or a debt bankruptcy charged to the vault; abandoning counts as broke. Poker Head always tops up a vault too small for Classic with a relief that grows after each bankruptcy. Strong items are allowed if they are rare, rerolls grow costlier, and the intended order of efficiency is: serious Poker Head play, then farming Classic, then the relief-and-all-in loop.

## Progress (2026-10-14)

Implemented: chip amounts scale with the stake, the multiple-based goals and Full Haul action, the vault replacing tokens, stakes chosen in New run, relief, early-bust insurance (revised so it is not a chip source), membership levels by lifetime spend with badges, chip rewards and seven new achievements, halved Classic item prices; meta upgrades are off. Simulations on a test profile found the intended order inverted for now: the environment rules are Poker Head's main source of losses, rising minimum bets favour all-in over steady play, and relief is always income. Open questions include a Full Haul bonus, the relief cap, membership perks and further tiers. Current values are on [Chip vault and progression](progression.html).
