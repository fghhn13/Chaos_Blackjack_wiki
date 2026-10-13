---
title: Cosmetics, achievements and Profile
source_blob: 235ca1cbf918
---
Cosmetics change art only and are owned per player. Default looks are implicit; other looks come from token purchases, achievements or admin grants. Slots cover decks, tables, chip sets and avatars. Asset aliases apply the equipped look while a missing asset falls back to the base art.

Profile opens from the Home badge. Overview shows lifetime stats; Wardrobe equips owned looks and previews them; Achievements shows progress; Switch player opens the existing player slots. Purchasing is now in Shop's Cosmetics area, while Wardrobe only equips owned content.

At run settlement, tracked stats update and locked achievements are checked in the same transaction; rewards pay once. Abandoned runs do not count. An older player's settled history is backfilled once, treating missing counters as zero. Achievement tokens are separate from the run's base rewards. Hidden entries are concealed until unlocked. Some achievements reward multiple looks.

The balance setting `meta.unlock_all_cosmetics` (currently {{ fact: settings.meta.unlock_all_cosmetics.value }} in the shipped profile, where 1 means on) makes every player own every look, hidden ones included, in the wardrobe, shop and loadout. It writes nothing to ownership, so turning it off in a cloned profile restores each player's real collection.

Migration `0006_cosmetics_achievements.sql` adds ownership, equipped looks, lifetime/best stats, unlocks, cosmetic prices and achievement rewards; migration 0007 extends decks and multiple rewards. Prices and rewards are balance-profile data. Registries declare looks, stats and achievements without a GUI dependency. Content validation checks references and obtainability.

The design leaves pricing balance and mid-run toasts open; current catalogs are on [Cosmetics](cosmetics.html) and [Achievements](achievements.html).
