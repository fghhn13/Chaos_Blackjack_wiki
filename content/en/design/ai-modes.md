---
title: Dealer-hosted Tables and series
source_blob: ee62c586a618
---
Each mode is hosted by a dealer and has its own goal, rule pool and item pool. Classic remains the core Table, hosted by Poker Head without rule changes. The former Chaos display becomes Poker Head's Table; the internal `chaos` id is retained for saves and stats.

Collection and Shop group content by the core series and dealer expansions. Collection presents a character profile and signature line; table numbers are shown separately. Shop has Upgrades, Cosmetics and Starter items; mode-specific upgrades are tagged, and starters belong to series according to where their items are sold.

New runs play a host introduction generated from the goal and pools, with expressions and random lines. Resumed runs skip it. Victory and defeat scripts precede results. Enter advances, Escape skips. Host scripts live in JSON and can have mode-specific variants.

Migration `0007_ai_modes.sql` adds upgrade mode restrictions, moves the cosmetic slot from card back to deck (card back plus optional face), and permits multiple cosmetic rewards. Poker Face rewards Poker Head's deck and table. New modes can register a series, host, pools and goal; Collection and Shop then add their sections.

Current player-facing details are on [Tables](tables.html), [Dealers](dealers.html), [Progression](progression.html) and [Cosmetics](cosmetics.html).

## Unmerged extension

The newest document also describes J-54's branch demo, with its own deck rules and contracts. Exclusive mode pools prevent J-54 content from leaking into unrestricted or Poker Head modes. Per-mode balance overrides inherit other defaults; J-54 can restock every round. Tables register their own mechanics through a shared dispatcher. These additions remain on `feat/j54-demo`, not main; see [J-54's branch design](design-j54-table.html).
