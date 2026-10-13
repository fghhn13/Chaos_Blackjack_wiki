---
title: Player progression and Shop
---
**Bankroll** belongs to one run; **tokens** belong to the player and persist between runs. The table shop spends bankroll. Home's **Shop** spends tokens on permanent upgrades, cosmetics and starter items.

## Run rewards

Victory pays {{ fact: settings.meta.win_tokens.value }} tokens; winning with Chaos rules active adds {{ fact: settings.meta.chaos_win_bonus.value }}. Defeat pays consolation based on rounds survived and peak bankroll, capped at {{ fact: settings.meta.loss_cap.value }}. Abandoning a run pays nothing and does not return consumed starter items. Achievement rewards are paid on top of run rewards.

## Shop areas

**Upgrades**, **Cosmetics** and **Starter items** each group content by the Classic Table and dealer series. Mode-specific upgrades are tagged for their table. Starter items are grouped by the tables that sell them; Starter: Shield belongs under Poker Head.

{{ table: upgrades }}

For permanent upgrades, the price column lists successive levels. For starter items, it is the cost of one copy; the limit is how many copies can be held. Base carrying capacity is {{ fact: settings.meta.bring_kinds.value }} different kinds. Selecting items spends nothing until **Start run**. Only applicable upgrades and consumables are offered in Run setup.

See [Cosmetics](cosmetics.html), [Achievements](achievements.html) and [Profile](profile.html).
