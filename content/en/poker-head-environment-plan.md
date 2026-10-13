---
title: Poker Head — persistent Chaos and a growing offline Agent
status: draft
source: user
source_path: docs/design/POKER_HEAD_CHAOS_RULES_AND_AGENT.zh-CN.md
source_blob: baa29fbcb40cddd1353198b6cb0398e1d01bbd8a
parent: design
---
**In development; not merged into game main.** This summary follows the author's local design dated 2026-10-13. The [Chinese source snapshot](https://github.com/fghhn13/Chaos_Blackjack_wiki/blob/main/content/zh/sources/POKER_HEAD_CHAOS_RULES_AND_AGENT.md) preserves the full proposal. Numbers, weights, durations and timing below are draft settings, not measured balance.

The scope is the new Poker Head build Table. Classic, J-54 and legacy Chaos saves are outside this proposal. It leaves that build's cores, product prices, permanent slots and proposed 500-net-asset goal intact. **That 500 target belongs to the unmerged build, not the current main Table.** Current gameplay remains on [Poker Head's Table](table-chaos.html).

## A persistent environment, announced before betting

Up to three environment rules coexist. Poker Head may add, strengthen or replace one per round; a calm result keeps existing rules. After the initial free core choice, the proposed action occurs **before shopping, preparation items and betting**, with no further change after dealing. This differs from main's action after dealing and natural settlement.

Every rule publicly states its target, exact effect, remaining duration or persistence, and how to remove it. Persistent rules stay until cleared, replaced or the run ends. Timed rules count completed rounds, including naturals, pushes and surrender; shopping, observation and saves do not advance timers. One rule of each type is allowed; fixed values and value offsets are separate types. Silence still occupies slots and advances timers.

## Nine rule types

| Type | Proposed effect and boundary | Duration |
| --- | --- | --- |
| Fixed card value | Player, dealer or both count a named card group as Y. Groups use printed ranks, suits or colours. Fixing A disables its 1/11 choice and must say so; the first offline pool excludes A and fixing every card to one value. Printed-card natural detection is preserved. | Persistent |
| Card-value offset | Add/subtract per-card points for the same target/group options. A +1 becomes 2/12 unless fixed; final values cannot fall below 1. Odd/even groups use original printed ranks. | Persistent |
| Bust limit | Change one party's limit. Player upgrades/items can add to it; dealer stand behaviour and natural payout stay unchanged. Non-bust dealer totals above 21 compare normally. | Initially 2 rounds |
| Ordinary tie result | Assign an ordinary tied hand to player, dealer or push; initially only dealer wins. Does not override bust, surrender, two naturals or the existing special item exception. | Persistent |
| Bust result | Initially, dealer bust pushes if the player is still alive. Player-bust-to-push remains a template outside the initial offline pool. Push profit is zero and triggers no win-only effects. | 2 rounds |
| Profit cap | Cap combined positive hand and financial-maturity profit once per round. Principal refunds, loans, buybacks and surrender refunds are excluded. Losses and debts remain payable; purchases do not reduce the counted profit. | 3 rounds; draft caps 50, 40 or 30 |
| Item ban | The next valid-phase consumable is sacrificed without its effect, then the ban ends; alternatively wait. Effect prerequisites are ignored for this sacrifice. Passives, permanent swaps, existing contracts, purchases and initial free core choices continue. | 2 or 3 rounds |
| Shop markup | Raise ordinary consumable and permanent-product prices, including unbought current stock. Combine markup and discounts before rounding up once, minimum 1; buybacks use the actual paid price. Excludes financial amounts, loans, refresh fees and gifts. | 3 rounds |
| Player hole card | Hide the second initial card, exact total and near-21 hints; later draws stay visible. Reveal on stand, double, surrender, bust or other terminal result. Exchanges retain the mask; logs must not leak cards. | Initially 2, later 3 rounds |

The proposed scoring order is printed value → fixed value → offset → permanent player value effects → soft-A choice → whole-hand recognitions → bust. Naturals use the original starting cards, although their positive profit still counts toward the cap.

Hidden-card rules do not falsify the hand used for settlement. Clearing or silencing reveals the card immediately. Existing next-card information, dealer inspection and the danger pointer keep their stated scopes; the danger pointer may report a next-hit bust boolean without exposing exact hidden points.

## Clearing, silence and replacement

Clearing permanently removes **one selected rule**. Silence suppresses all environment effects for the current round; stored rules continue ageing and surviving rules return next round. Unbought stock reprices while markup is suppressed; paid costs and settled profit are never refunded retroactively. If a ban consumes the clearing or silence item, only the ban ends.

Rules cannot be renewed by replacing a timed rule with identical parameters. Before AI replacement, each rule must have remained for at least two full rounds; timed rules cannot be replaced early merely to extend their duration. Persistent replacement favours lower pressure, then older rules, then stable type order. A replacement removes one rule and adds one atomically.

After player clearing or consumable countering, the entire type is unavailable for the next two environment phases. Natural expiry blocks its type for the next phase. AI replacement instead blocks the old parameter signature for two phases. Clearing in round 5 therefore blocks that type in rounds 6 and 7, allowing it again in round 8. No rule immediately refills a cleared slot.

## A gradually stronger offline Agent

The Agent scales with round number and current environment, without targeting a player's build, inventory, decisions, bets, win rate, hidden cards or future deck. It uses an independent seeded Chaos RNG, separate from shops, decks and cores. Sorted candidates and saved decisions prevent observing, shopping or reloading from rerolling an action; actual clearing history can legitimately change later choices.

| Rounds | Action chance | Active-rule cap | Total pressure budget |
| --- | --- | --- | --- |
| 1–3 | 60% | 1 | 2 |
| 4–6 | 75% | 2 | 4 |
| 7–9 | 85% | 3 | 7 |
| 10+ | 95% | 3 | 8 |

These are chances to attempt a legal action, not guarantees. Legal additions take priority; otherwise the Agent considers eligible replacements, filters conflicts, cooldowns and pressure, then chooses a type by relative weight and a legal variant uniformly. It announces one result per preparation phase and makes no network/model request.

Early pools emphasise local card changes and modest markup; later pools add bust limits, ties, dealer-bust pushes, profit caps, bans and hidden cards. Pressure is a draft heuristic: small local changes cost 1, broader changes often 2, and severe bust/profit effects 3–4. At most one pressure-3/4 rule may coexist. **Player hole card and item ban can never coexist.** Multiple limits for the same party are also excluded. The full source lists stage-specific variants, pressure costs and type weights; weights are relative and are renormalised after illegal choices are removed.

## What still needs implementation and measurement

The source proposes validation of build/no-core win rates, run length and bankruptcy, late-round activity, three-rule occupancy and clearing gaps, profit caps with investments, sacrifice/wait/clear/silence decisions, hidden-information behaviour, affordability under markup, and combined-rule EV. Its example round sequence is illustrative, not a fixed script or a simulator result. Invitations, challenges, opportunities and trap events are outside this draft.
