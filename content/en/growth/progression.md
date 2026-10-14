---
title: Chip vault and progression
---
There is one currency: **chips**. Each player has a **chip vault** that persists between runs; a new player starts with {{ fact: settings.meta.vault_start.value }}. A run's cash is taken out of the vault when it starts, and what comes back depends on how the run ends. The table shop and Home's **Shop** both spend chips.

## Stakes and goals

In **New run** you choose how much to bring with a slider; the goal follows the stake.

| Table | Stake from the vault | How a run is won |
| --- | --- | --- |
| [Classic Table](table-normal.html) | {{ fact: settings.mode.normal.stake.value }} | Reach {{ fact: settings.mode.normal.config.target_multiple.value }} times the stake; that is also the ceiling |
| [Poker Head's Table](table-chaos.html) | {{ fact: settings.mode.chaos.stake.value }} | From {{ fact: settings.mode.chaos.config.exit_multiple.value }} times the stake you may take **Full Haul** and leave with a win; at {{ fact: settings.mode.chaos.config.target_multiple.value }} times the run ends as a win, and profit beyond it is not paid |

Below the exit point you cannot leave: a run ends in a win or in going broke. [J-54 *Experimental](table-j54.html) is a free demo and takes no stake. Start is disabled when the vault cannot cover the minimum stake.

## Settling a run

- **Win**: the run's final cash goes back to the vault; open investments are settled at cost and debts are paid first.
- **Defeat**: nothing comes back. Debt still owed at the end (a fourfold loss beyond your cash, open loans) is taken from the vault, never below 0.
- **Abandon**: counts as a defeat; the stake is lost.

Winning pays no separate bonus in this version (the vault pays); achievements still pay their chip rewards on top.

## Relief, insurance and membership

**Relief.** When the vault cannot cover Classic's minimum stake, Poker Head tops it up so you can always play: {{ fact: settings.meta.relief_base.value }} chips at first, {{ fact: settings.meta.relief_step.value }} more for each earlier relief since your last won run, at most {{ fact: settings.meta.relief_cap.value }}. A won run resets it.

**Early-bust insurance** is bought in New run together with the stake. It costs {{ fact: settings.meta.insurance_premium_pct.value }}% of the stake; if the run is lost within {{ fact: settings.meta.insurance_rounds.value }} rounds it refunds {{ fact: settings.meta.insurance_refund_pct.value }}% of the stake. Abandoning does not pay.

**Membership** levels follow lifetime spend on goods (in-run and Home shop purchases and insurance premiums; bets and losses do not count). The levels start at {{ fact: settings.meta.membership_spend.value }} chips spent. Each level has a title and badge on Profile; from level 3 the relief cap rises by {{ fact: settings.meta.membership_relief_bonus.value }}, and from level 4 Home's Shop takes {{ fact: settings.meta.membership_shop_discount_pct.value }}% off.

## Shop

Home's **Shop** sells [Cosmetics](cosmetics.html) for chips. Permanent upgrades and starter items are switched off in this version, so the Shop and New run do not offer them.

See [Achievements](achievements.html) and [Profile](profile.html).
