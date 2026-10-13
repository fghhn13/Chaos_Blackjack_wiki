---
title: Poker Head build guide
---
Poker Head's Table combines a core, limited permanent equipment, consumables and financial products. Reach **{{ fact: tables.chaos.target_money }} net assets**. This is the current official scheme; product cards below show the current balance profile.

## Opening and changing your build

The Dealer's Invitation offers two fixed core choices. Choose one, or take {{ fact: settings.mode.chaos.decline_cash.value }} extra chips and play the entire run without a core. Looking or reloading cannot reroll the offer. A core does not occupy a permanent slot.

The five styles are multi-card, surrender, precision, doubling and finance. Amendment Letter offers two different new cores before betting; goods and existing financial contracts remain. A no-core run cannot use it. Leaving Private Account removes its extra shop slot and new finance eligibility, but existing positions mature normally.

Equip at most **{{ fact: settings.mode.chaos.build_slots.value }} permanent products**. One copy per name; a full build requires selecting the product to replace before payment. Old equipment is discarded without refund. Re-equipping does not reset per-round or per-stock uses.

## Cash, investment and debt

**Net assets = spendable cash + open investment principal at cost − full outstanding loan repayment.** Buying equipment reduces assets. Investing moves cash into principal; unrealised returns do not count. Borrowing adds cash and the full future debt, so it does not create a free win. Maturity settles once after the hand; actual profits, not returned principal, are subject to Withdrawal Limit.

The minimum bet grows with rounds according to {{ fact: settings.mode.chaos.min_bets.value }}, then continues by {{ fact: settings.mode.chaos.bet_step_add.value }} every {{ fact: settings.mode.chaos.bet_step_rounds.value }} rounds. You still need enough cash to bet. Victory checks after complete settlement or eligible cash actions such as buyback; open principal and debt settle without unearned interest.

## Shop and timing

Poker Head goods use fixed base chip prices. Markup and purchasing discounts combine before rounding upward once. Finance amounts are exempt; buyback returns the actual amount paid for the selected consumable instance.

One stock slot favours general consumables, while free slots increasingly offer permanents. Matching-style products have {{ fact: settings.mode.chaos.style_weight.value }} times the base selection weight. Equipped products are excluded. Initial core choice precedes the environment action; the dealer then announces the environment before shopping, preparation items and betting. See [environment mechanics](environment.html).

The panel has Build, Bag, Finance, Rules, Log and Run sections. Use the item's stated phase; use does not reopen a finished hand. Old saves without build state retain their earlier gameplay.

## Product catalog

{{ table: poker_products }}
