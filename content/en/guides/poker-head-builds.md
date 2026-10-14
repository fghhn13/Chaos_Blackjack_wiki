---
title: Poker Head build guide
---
Poker Head's Table combines a core, limited permanent equipment, consumables and financial products. Bring {{ fact: settings.mode.chaos.stake.value }} chips from your [vault](progression.html). From **{{ fact: settings.mode.chaos.config.exit_multiple.value }} times the stake** in net assets you may take **Full Haul** before betting and leave with a win; at **{{ fact: settings.mode.chaos.config.target_multiple.value }} times** the run ends as a win, and profit beyond it is not paid. This is the current official scheme; product cards below show the current balance profile.

## Opening and changing your build

The Dealer's Invitation offers two fixed core choices. Choose one, or take {{ fact: settings.mode.chaos.decline_cash.value }} extra chips and play the entire run without a core. Looking or reloading cannot reroll the offer. A core does not occupy a permanent slot. Some cores cost or bring chips when chosen; the Invitation shows the amount.

The five styles are multi-card, surrender, precision, doubling and finance. Cores change what you can do (for example surrender or double after hitting, or redeal your opening hand); permanent products amplify the payoff. Amendment Letter offers two different new cores before betting; goods and existing financial contracts remain. A no-core run cannot use it. Leaving Private Account removes its extra shop slot and new finance eligibility, but existing positions mature normally.

Equip at most **{{ fact: settings.mode.chaos.build_slots.value }} permanent products**. One copy per name; a full build requires selecting the product to replace before payment. Old equipment is discarded without refund. Re-equipping does not reset per-round or per-stock uses.

## Cash, investment and debt

**Net assets = spendable cash + open investment principal at cost − full outstanding loan repayment.** Buying equipment reduces assets. Investing moves cash into principal; unrealised returns do not count. Borrowing adds cash and the full future debt, so it does not create a free win. A fourfold loss beyond your cash also becomes debt. Maturity settles once after the hand; actual profits, not returned principal, are subject to Withdrawal Limit.

The minimum bet grows with rounds according to {{ fact: settings.mode.chaos.min_bets.value }}, then continues by {{ fact: settings.mode.chaos.bet_step_add.value }} every {{ fact: settings.mode.chaos.bet_step_rounds.value }} rounds. You still need enough cash to bet. Victory checks after complete settlement or eligible cash actions such as buyback; open principal and debt settle without unearned interest.

## Shop and timing

Chip amounts (prices, finance, minimum bets, reroll cost, the decline bonus) are written for a reference stake of {{ fact: settings.mode.chaos.money_base.value }} and scale with the chips you bring; cards show the reference values. The paid reroll rises by {{ fact: settings.mode.chaos.reroll_step_add.value }} with each minimum-bet step. Markup and purchasing discounts combine before rounding upward once. Finance amounts are exempt; buyback returns the actual amount paid for the selected consumable instance.

One stock slot favours general consumables, while free slots increasingly offer permanents. Matching-style products have {{ fact: settings.mode.chaos.style_weight.value }} times the base selection weight. Equipped products are excluded. Initial core choice precedes the environment action; the dealer then announces the environment before shopping, preparation items and betting. See [environment mechanics](environment.html).

The panel has Build, Bag, Finance, Rules, Log and Run sections. Use the item's stated phase; use does not reopen a finished hand. Old saves without build state retain their earlier gameplay.

## Product catalog

{{ table: poker_products }}
