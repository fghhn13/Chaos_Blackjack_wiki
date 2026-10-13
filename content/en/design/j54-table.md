---
title: J-54 — branch demo and remaining design
source_blob: 681e30decd29
---
The latest document records a v1 demo on `feat/j54-demo`. **This demo has not merged into game main.** The [original Table concept](table-j54.html) remains background; this page describes the newer branch implementation and its limits.

## Persistent deck and protocols

Deck composition persists across rounds and saves. The demo draws either Single Capture or Capital as its run protocol. Double Capture and Eradication remain proposals. Capital's demo target is 250 chips, rather than the original concept's 1000; all branch values remain provisional.

Single Capture starts with a sealed Joker. The always-stocked Start Experiment contract releases it. A player-drawn Joker during dealing, hitting or doubling immediately pushes the hand and wins the run. A dealer-drawn Joker is replaced by the next card, returned away from the top, and adds a low-card penalty. Jokers never remain in a hand and have no ordinary point value.

Each round charges a rising compute fee before betting; the minimum bet also respects that fee. Entropy adds low cards after settlement, with more after the experiment starts. Freeze suspends these injections. The demo tracks a removed-card pile, unlike the initial concept's assumption of no discard pile.

## Rules, contracts and inspection

The branch has six deck rules: Burn Protocol, Sample Injection, Redundancy Purge, Ace Injection, Layered Sort and Data Backflow. They physically add, remove, copy, move or return cards; sorting sends high cards to the bottom for the remaining round, and backflow returns removed cards.

Five contracts cover immediate low-card removal, removal after the next win, high-card injection, temporary freezing and starting the experiment. Contract offers refresh every round. Start Experiment occupies one of the shop's slots.

Hovering or pinning the shoe reveals truthful rank counts, Jokers and removed cards. Agent observations also expose composition, without revealing draw order. The side panel shows fees, entropy, the protocol, pending effects and contracts; Deck, Contracts and Run tabs provide details. See [Table UI](design-table-ui.html).

## Still being built

Misleading reports and challenges, the other protocols, targeted contracts, Joker point values, J-54-specific model prompts, collection rewards and simulator support remain outside v1. Offline play works on the branch; a model may choose actions but has no dedicated J-54 prompt.

The document's preliminary bot experiments are branch investigations, not the wiki's measured main balance. It flags early lucky Capital victories and proposes delaying eligibility, holding the target for several rounds or adding a late protocol. These alternatives are not settled rules.
