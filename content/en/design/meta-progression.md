---
title: Meta progression, saves and run history
source_blob: 00513f4ac45e
---
A player is a named save slot holding tokens, permanent upgrades and starter items. Starting a run combines a balance profile, table mode, applicable permanent upgrades and selected consumables. Finishing records rewards, history and codex encounters. Abandoning pays no tokens. The agent CLI stays independent of player progression.

The service supports slot creation, renaming, deletion, mode selection, buying upgrades, starting/resuming a run, reading a pending checkpoint, finishing/abandoning and history. Migration 0004 added players, owned upgrades, run history, codex sightings and the upgrade catalog. A controller listener accumulates run statistics without consuming GUI notices; fake services support in-memory GUI development.

Home, Profile, Run setup, Shop, Collection, results and history form the player flow. There is no quick-play flow. Modes can have their own upgrade restrictions. The later [AI modes](design-ai-modes.html) and [Cosmetics and achievements](design-cosmetics-achievements.html) extend this contract with hosts, series, wardrobe, stats and unlocks.

The codex contract gains `build` and `environment` kinds and optional browser metadata on each entry (category, style, timing, price, related entries). Collection uses series tabs, a compact host / category sidebar, type- and style-filtered cards and an inline reference; details are animated demos or compact text references with live numbers and the adopted product icons.

Reward formulas and the original catalog are defined by the contract; shipped prices and current entries are generated on [Player progression](progression.html). Cosmetics never affect run rules or the balance fingerprint. Simulator upgrade/career experiments use the same configuration and reward helpers.

## 2026-10-14: upgrades off, chip vault

Meta upgrades and starter items are switched off in this version (`meta.upgrades_enabled`): nothing is sold or applied and the GUI hides those areas; a development switch turns the dormant system back on. Their planned replacement is the [carried-chips economy](design-carried-chips.zh-cn.html).

The player's tokens are now a **chip vault** (every screen says chips). A Table with a stake setting takes its starting cash from the vault within a range; a free Table, such as J-54's demo, takes none. A win brings the final cash home; a defeat brings nothing and remaining debt comes out of the vault, never below zero; abandoning loses the stake. Victory and consolation payouts are off, and achievements pay chips. When the vault cannot cover Classic's minimum stake, Poker Head pays a growing relief that a won run resets. Lifetime spend counts chips spent on goods, not bets, and drives membership. Run history records the stake and chips brought back, and every run writes its table notices to a local JSON-lines log. Current values are on [Chip vault and progression](progression.html).

**Onboarding (2026-10-15).** A guided player reaches milestones that open the tables one by one, and a settled run lists the milestones it reached; players from before onboarding are not guided. See [Onboarding](design-tutorial.html).
