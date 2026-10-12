---
title: Meta progression, saves and run history
source_blob: b4f8ce97dc79
---
A player is a named save slot holding tokens, permanent upgrades and starter items. Starting a run combines a balance profile, table mode, applicable permanent upgrades and selected consumables. Finishing records rewards, history and codex encounters. Abandoning pays no tokens. The agent CLI stays independent of player progression.

The service supports slot creation, renaming, deletion, mode selection, buying upgrades, starting/resuming a run, reading a pending checkpoint, finishing/abandoning and history. Migration 0004 added players, owned upgrades, run history, codex sightings and the upgrade catalog. A controller listener accumulates run statistics without consuming GUI notices; fake services support in-memory GUI development.

Home, Profile, Run setup, Shop, Collection, results and history form the player flow. There is no quick-play flow. Modes can have their own upgrade restrictions. The later [AI modes](design-ai-modes.html) and [Cosmetics and achievements](design-cosmetics-achievements.html) extend this contract with hosts, series, wardrobe, stats and unlocks.

Reward formulas and the original catalog are defined by the contract; shipped prices and current entries are generated on [Player progression](progression.html). Cosmetics never affect run rules or the balance fingerprint. Simulator upgrade/career experiments use the same configuration and reward helpers.
