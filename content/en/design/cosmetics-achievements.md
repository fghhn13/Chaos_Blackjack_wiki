---
title: Cosmetics, achievements and Profile
source_blob: 29b8dc2f41ba
---
Cosmetics change art only and are owned per player. Default looks are implicit; other looks come from token purchases, achievements or admin grants. Slots cover decks, tables, chip sets and avatars. Asset aliases apply the equipped look while a missing asset falls back to the base art.

Profile opens from the Home badge. Overview shows lifetime stats; Wardrobe equips owned looks and previews them; Achievements shows progress; Switch player opens the existing player slots. Purchasing is now in Shop's Cosmetics area, while Wardrobe only equips owned content.

At run settlement, tracked stats update and locked achievements are checked in the same transaction; rewards pay once. Abandoned runs do not count. An older player's settled history is backfilled once, treating missing counters as zero. Achievement tokens are separate from the run's base rewards. Hidden entries are concealed until unlocked. Some achievements reward multiple looks.

The balance setting `meta.unlock_all_cosmetics` (currently {{ fact: settings.meta.unlock_all_cosmetics.value }} in the shipped profile, where 1 means on) makes every player own every look, hidden ones included, in the wardrobe, shop and loadout. It writes nothing to ownership, so turning it off in a cloned profile restores each player's real collection.

Migration `0006_cosmetics_achievements.sql` adds ownership, equipped looks, lifetime/best stats, unlocks, cosmetic prices and achievement rewards; migration 0007 extends decks and multiple rewards. Prices and rewards are balance-profile data. Registries declare looks, stats and achievements without a GUI dependency. Content validation checks references and obtainability.

The design leaves pricing balance and mid-run toasts open; current catalogs are on [Cosmetics](cosmetics.html) and [Achievements](achievements.html).

**Chip economy (2026-10-14).** "Tokens" in this design now means chips from the player's [vault](design-meta-progression.html). Looks are bought with chips again (looks a player was wearing were kept) and count towards lifetime spend; from membership level 4 the Shop takes a discount. Achievement rewards are paid in chips, rescaled for the vault, and seven new achievements cover the build Table and risky play: To the Brim, In and Out, All In, Saved by the Bell, Fresh Start, Back from Broke and Five Ways to Win. Current rewards are on [Achievements](achievements.html).

**Prices by wins (2026-10-15).** Look prices are now set against what a win earns, so Classic looks cost a few hundred chips and J-54's a few thousand. A dealer's looks go on sale once that dealer is beaten, and a dealer whose Table is not listed yet has no looks in the Shop. Current prices are on [Cosmetics](cosmetics.html).
