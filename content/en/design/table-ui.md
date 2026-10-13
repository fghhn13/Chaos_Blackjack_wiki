---
title: Table UI — parts, widgets and layouts
source_blob: dc8611260ba6
---
The document marks this framework implemented, and it is now in the game's main line. It supports dealers with different mechanics while preserving the shared central play area.

## What the interface adds

Each Table chooses an ordered left/right layout. Parts that do not fit direct the player to the run panel instead. The panel opens with Tab, closes with Escape or Tab, and switches tabs with Left / Right or a tab shortcut. Most information is read-only; widgets may expose explicit actions.

Items appear as quick slots, clickable or usable with keys 1–9 during the player's turn; the Bag tab replaces the old item scene. The side feed shows recent events and errors. The full run log retains up to 400 lines and survives saves; counters keep accumulating after old lines are dropped.

The default layout (Classic and the mode-less `--chaos` run) uses the shared host, rules, feed, shoe, item slots and buttons, with Bag, Rules, Log and Run tabs. Poker Head's build Table adds its status, table actions and Build and Finance tabs, from parts that read only its public snapshot. J-54 adds deck distribution, badges, contracts and goal information, plus Deck and Contracts tabs.

## How Tables extend it

Mechanics supply state and actions. Registered parts turn that state into compact or full views built from data widgets: stats, badges, bars, progress, lists, rows, slots and logs. Shared renderers display them; layouts choose placement and panel tabs. Action descriptors route back through the controller, which runs item use, purchases, choice answers and the Table's own moves. Whether an action is enabled comes from the same move list the agent reads (see the [item architecture](design-item-architecture.html)); each item slot shows when and why it is unavailable. A command that asks a question opens one generic choice dialog, which only sends choose or cancel.

Native host and shoe interactions can open the relevant panel, pin inspection or show dialogue. A feed heading opens the full log. GUI widgets do not change the Agent observation contract. Adding a Table therefore supplies its mechanics, parts and layout rather than rewriting shared play scenes.
