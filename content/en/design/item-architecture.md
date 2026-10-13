---
title: Products, choices and moves
source_blob: f3b0e948f744
---
The contract for every Table that sells or applies its own goods. It is implemented for Poker Head's build Table (`chaos_blackjack/poker_head/`); J-54's contracts and the classic item plugins still use their older paths, and moving them over is listed as planned, optional work.

## Goals and layers

A new product should be one catalog row plus one small handler, never a branch in the controller or the GUI. The GUI and the agent show the same legal moves with the same reasons, a choice changes nothing until it is confirmed, and public views carry only what a player at the table may see. Classic play, J-54 and the mode-less `--chaos` run behave as before.

The layers, from the bottom: a catalog of `ProductDef` rows (names, kinds, phases and targets; every number lives in the balance profile), ownership (`Holdings` for owned consumables with the price actually paid, `Loadout` for the core and equipped permanents, `Ledger` for cash postings and open positions), passive effects and active item handlers, pending choices, and the controller as the only entry point. Effects implement only the hooks they need from a fixed list (bust limit, card value, recognition, naturals, settlement, surrender rate, prices and so on) and are folded in a fixed order: core, permanents in slot order, then this round's preparations. Handlers change the round only through a narrow context object.

## Choices, moves and views

A command that needs a decision asks a `Choice` and returns without changing anything; while it is pending, only choosing, cancelling (when allowed) and saving are possible, and the choice is saved with the run. `GameController.moves()` is the single source of legality: shop buttons, item slots, choice buttons and the agent's legal actions all read it, and a test checks the GUI and the moves agree. Views expose `moves`, `choice` and a frozen, table-specific public snapshot; a test checks that no undealt card or private financial outcome leaks.

## Extending and saving

The doc lists what to add for a consumable, permanent, core, financial product, table action, non-bankroll goal, panel or question, and notes that Poker Head's environment rules are data handled by the offline director. Every object saves with a version, and random draws use named, counter-seeded streams so shopping, rerolling, saving and loading do not shift the deal or a private result. Current products are on [Items](items.html).
