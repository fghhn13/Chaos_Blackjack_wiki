---
title: Poker Head: build design overview (Chinese)
source_blob: 93cd443761fe
---
The Chinese overview of the in-run build system for Poker Head's Table. The doc marks the first version implemented; its numbers and odds still await simulation. Detailed effects are in the [effects spec](design-poker-head-effects.zh-cn.html), the environment in the [chaos rules and offline agent](design-poker-head-chaos-rules-and-agent.zh-cn.html) doc, and pricing in the [implementation plan](design-poker-head-implementation-plan.zh-cn.html).

A run is shaped by a core, a limited number of permanent slots, consumables and financial products, toward a net-assets goal while the minimum bet rises and the dealer's environment grows. Five styles are described: multi-card, surrender, precision, doubling and finance.

The doc covers the Dealer's Invitation (two cores, or extra starting chips and no core for the whole run), the Amendment Letter for changing core, fixed candidates that reloading cannot reroll, permanent-slot replacement and discarding without refund, shop odds that favour the current core's style, a testing switch that shelves every product, and the interface: category colours, a cash line with a goal bar, build icons and one shared choice dialog. Current values are on [Poker Head builds](poker-head-builds.html).
