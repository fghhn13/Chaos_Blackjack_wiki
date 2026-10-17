---
title: J-54 concept and v1 demo (history)
source_blob: 000dbfcd84a8
---
The original J-54 design document, now kept for reference: since 2026-10-17 the table follows the [v2 specification](design-j54-v2-spec.html), documented on [J-54's Table](table-j54.html).

## The v1 demo

The first J-54 table (implemented 2026-10-13) rebuilt a deck that lasted the run. Each run drew a protocol: **Single Capture**, where a sealed Joker could be released and drawing it pushed the hand and won the run, or **Capital**, a chip target. A compute fee rose in steps every few rounds, entropy added low cards after each settlement, and the shop sold five contracts (Low Purge, Streamline, High Injection, Freeze and Start Experiment) that acted immediately or when their trigger was met. J-54's own rules were deck operations: {{ link: chaos_rules.j54_ace_injection }}, {{ link: chaos_rules.j54_burn }}, {{ link: chaos_rules.j54_data_backflow }}, {{ link: chaos_rules.j54_layered_sort }}, {{ link: chaos_rules.j54_redundancy_purge }}, {{ link: chaos_rules.j54_sample_injection }}. These rules are still registered in the game but no longer part of J-54's program; the contracts are gone.

## Why it changed

On 2026-10-15 the design moved to composable primitives (deck operations, per-side card rules, goals), recorded in [J-54: game primitives](design-j54-primitives.html), where the Joker hunt became one goal among several. The rule lab's findings led to v2: conditions that change only J-54's cards, a compute budget for removing cards, a heat map and meter, a firmware pick and a late Joker capture. The document's later sections still describe the original concept and its unbuilt ideas, such as further protocols.
