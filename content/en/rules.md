---
title: Rules
---
These are Classic Blackjack baseline rules. Poker Head's [builds](poker-head-builds.html) and [environment](environment.html), and [J-54 *Experimental](table-j54.html), override the applicable parts.

## Goal

At the Classic Table you bring {{ fact: settings.mode.normal.stake.value }} chips from your [vault](progression.html) and win the run at **{{ fact: settings.mode.normal.config.target_multiple.value }} times** what you brought. (Without a vault, for example the agent CLI, a run starts with **{{ fact: settings.run.start_money.value }}** chips and the goal is **{{ fact: settings.run.target_money.value }}**.) You lose when you run out of chips or can no longer place a legal bet.

## Betting

- Each round you bet a whole number from {{ fact: settings.bet.min.value }} up to {{ fact: settings.bet.max_fraction.value }} × your bankroll, rounded down. You can never go all-in.
- Before betting you may visit the [shop](shop.html).

## Card values

- 2–10 are worth their face value; J, Q and K are worth 10.
- An Ace counts high, but drops by 10 whenever the hand would otherwise bust. A fixed-value environment rule can disable this choice; read its declared effect.
- [Chaos rules](chaos.html) change card values before the total is summed. The total shown on screen always includes them: trust it over mental arithmetic.

## A round

1. You and the dealer get two cards each; the dealer's second card is face down (the *hole card*).
2. **Naturals** settle before player actions: an original Ace plus a ten-value card pays {{ fact: settings.table.blackjack_pays_num.value }}:{{ fact: settings.table.blackjack_pays_den.value }}, rounded down. The dealer's natural ends the round before you act; two naturals push.
3. In legacy Chaos compatibility, otherwise the [Chaos AI](chaos-ai.html) acts once. A rule can immediately bust a starting hand; {{ link: chaos_rules.reverse_bust }} changes a player bust to a push. A hand changed to 21 by a rule does not gain the natural payout.
4. Your turn: **hit**, **stand**, **double** or **surrender**, or use an [item](items.html).
5. The dealer reveals the hole card and draws until reaching {{ fact: settings.table.dealer_stand_on.value }} or more.
6. Settlement: win `+bet`, lose `-bet`, push `0`.

## Double and surrender

Both are allowed only on your first decision (exactly two cards). Using an item does not count as a decision.

- **Double** (enabled: {{ fact: settings.table.allow_double.value }}): the bet doubles, you get exactly one card, then you stand.
- **Surrender** (enabled: {{ fact: settings.table.allow_surrender.value }}): you give up the hand and get half the bet back, rounded in the house's favour.

## Bust

Going over the bust limit (21, unless a chaos rule changes it) on your own hit or double ends the round at once; the dealer does not draw.
