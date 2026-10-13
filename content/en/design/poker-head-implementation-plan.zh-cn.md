---
title: Poker Head: implementation plan and first pricing (Chinese)
source_blob: b68348a5b8fa
---
The Chinese plan for building Poker Head's build Table, kept as a record after it was carried out. A table at the top lists where the result differs from the plan: fewer permanent slots than planned plus the option to discard one, the early chaos-stacking draft replaced by the [environment rules and offline agent](design-poker-head-chaos-rules-and-agent.zh-cn.html) design, a higher stock payout, and the module split now described in the [item architecture](design-item-architecture.html). Simulation of the new prices has not been done yet.

The plan defines net assets as cash plus invested principal minus all debt still owed, with unrealised profit never counted, victory checked only after a full settlement or a legal cash action, and open positions settled at cost on victory. It sets a stepped minimum-bet curve, shop restocks, weighted shelves, a paid and a free reroll, and fixed chip prices for the build Table only, explaining the price tiers and why the stock payout was raised above the deposit's.

Implementation ran in phases A to F (state and ledger, cores and shop, hand effects, consumables and persistent rules, finance and public views, regression and pricing), each with acceptance checks. Current prices are generated on [Items](items.html).
