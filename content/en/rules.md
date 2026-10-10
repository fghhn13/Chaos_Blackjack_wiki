---
title: Rules
---
## Goal

You enter with **{{ fact: settings.run.start_money.value }}** chips. Reach **{{ fact: settings.run.target_money.value }}** to win the run. You lose when you run out of chips or can no longer place a legal bet.

## Betting

- Each round you bet a whole number from {{ fact: settings.bet.min.value }} up to {{ fact: settings.bet.max_fraction.value }} × your bankroll, rounded down. You can never go all-in.
- Before betting you may visit the [shop](shop.html).

## Card values

- 2–10 are worth their face value; J, Q and K are worth 10.
- An Ace counts high, but drops by 10 whenever the hand would otherwise bust. Aces stay "soft" under every chaos rule.
- [Chaos rules](chaos.html) change card values before the total is summed. The total shown on screen always includes them: trust it over mental arithmetic.

## A round

1. You and the dealer get two cards each; the dealer's second card is face down (the *hole card*).
2. In chaos mode, the [Chaos AI](chaos-ai.html) acts once.
3. **Naturals**: a two-card 21 is a natural blackjack and pays {{ fact: settings.table.blackjack_pays_num.value }}:{{ fact: settings.table.blackjack_pays_den.value }}, rounded down. If the dealer has a natural the round ends before you act; two naturals push.
4. Your turn: **hit**, **stand**, **double** or **surrender**, or use an [item](items.html).
5. The dealer reveals the hole card and draws until reaching {{ fact: settings.table.dealer_stand_on.value }} or more.
6. Settlement: win `+bet`, lose `-bet`, push `0`.

## Double and surrender

Both are allowed only on your first decision (exactly two cards). Using an item does not count as a decision.

- **Double** (enabled: {{ fact: settings.table.allow_double.value }}): the bet doubles, you get exactly one card, then you stand.
- **Surrender** (enabled: {{ fact: settings.table.allow_surrender.value }}): you give up the hand and get half the bet back, rounded in the house's favour.

## Bust

Going over the bust limit (21, unless a chaos rule changes it) on your own hit or double ends the round at once; the dealer does not draw.
