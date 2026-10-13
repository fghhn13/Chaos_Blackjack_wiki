---
title: Poker Head environment and offline dealer
---
The official current scheme gives Poker Head an environment that persists across rounds. The nine types cover fixed values, offsets, bust limits, ordinary ties, dealer busts, profit caps, consumable bans, shop markup and a hidden player opening card. Their [cards](environment.html) show legal examples from the current director pool.

## Once before betting

After the opening core choice, the offline dealer makes one environment decision before shopping, preparation items and betting. Nothing is added after dealing. A calm result retains the existing environment. A rule publicly states its actor, exact parameters, remaining duration and removal method.

Timed rules advance on completed rounds, including naturals, pushes and surrender. Shopping, observing and saving do not advance them. Persistent rules last until removed or replaced. One rule of each type can exist; fixed values and offsets are separate types. Silence suppresses effects for the round while stored rules continue occupying slots and ageing.

## Clearing and conflicts

Clause Removal permanently removes one selected environment rule. Silence Seal suppresses all rules this round; surviving ones return next round. Paid prices and settled profits are not reversed. Item Ban instead consumes the next valid-phase consumable with no effect and ends; if that item was a remover or silence, no other rule is changed.

Clearing blocks the entire type for {{ fact: settings.mode.chaos.director.cooldown_cleared.value }} subsequent preparation phases. Natural expiry blocks its type for {{ fact: settings.mode.chaos.director.cooldown_expired.value }} phase(s). AI replacement blocks the old signature for {{ fact: settings.mode.chaos.director.cooldown_replaced.value }} phases. Cleared slots are not immediately refilled. The director replaces eligible persistent rules; timed rules are allowed to expire instead of being renewed.

Hidden Card and Item Ban never coexist. There is at most one high-pressure rule, with legal choices filtered for type conflicts, cooldowns, slot and pressure budgets.

## Values, profit and information

Printed rank → fixed value → offset → permanent player effects → soft A → whole-hand recognition → bust. Naturals still use the original starting cards. Profit caps combine positive hand and maturity profit once per round; principal, refunds, loans and buybacks are excluded, while losses and debts remain payable. Markup affects ordinary goods, including unbought stock, and combines with discounts before one rounding step.

The player hole card hides the second initial card and precise total. Later draws remain visible; ending the hand, clearing or silence reveals it. Information items retain their own scope. The danger pointer reports next-hit risk without revealing hidden exact points.

## Gradual offline pressure

{{ table: director_stages }}

The action chance applies only when a legal candidate exists. The dealer prefers adding a rule, otherwise considers legal replacement, selects a type by relative weight and then a variant. It reads round, environment and cooldown history, not the player's build, inventory, bets, cards or future deck. Independent seeded streams and saved decisions prevent shopping or reloads from rerolling the action. No model request is needed.

The [original specification](https://github.com/fghhn13/Chaos_Blackjack_wiki/blob/main/content/zh/sources/POKER_HEAD_CHAOS_RULES_AND_AGENT.md) is preserved as development history. Current runtime facts and this guide govern the wiki; balance measurements for the new build are still pending.
