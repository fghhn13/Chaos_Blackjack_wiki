---
title: Poker Head: product and effect details (Chinese)
source_blob: 82ca8440b0fb
---
The Chinese rules reference for all 43 build entries: 5 cores, 18 permanents, 16 consumables and management items, and 4 financial products. The doc marks the first version implemented; values, prices and odds are first-pass numbers not yet simulated. Every entry has its phase, effect, limits and a short shop / Collection text.

## Shared conventions

Phases are before betting, during the player's turn, automatic, and the opening natural check. One core at most; permanents are equipped only before betting, one copy per name, and replacing or discarding one refunds nothing and cannot reset used counters. A consumable without a legal target is not spent, and nothing can rescue a hand after it busts. The doc defines actual total, recognised total (after Almost Perfect), final bet and net profit, with rewards rounded down and losses rounded up. Classic items brought into this Table settle as their new counterparts.

## Notable rules

It spells out how Almost Perfect works outside the opening check, how Borrowed Glory transfers a dealer natural, how Recovery Receipt and Comeback Ace store a one-time claim, how Original Price Receipt refunds the price actually paid and can end the run in victory, how Fate Forecast and Aces to the Top read or reorder the deck, and how financial contracts mature. A fixed evaluation order runs from printed rank through environment rewrites and offsets, Court Discount, ace choice and Almost Perfect to the bust check. A final table maps the many earlier working names to the released ones.

**2026-10-14 revision.** Cores now change what you can do: Room to Breathe (a larger bust margin), Exit Clause and Raise Permission (promoted from permanents) and the new Fresh Hand, which swaps both opening cards once per round; Graceful Retreat, Almost Perfect and High Stakes become permanents with unchanged effects, and old saves convert. Court Discount now picks 10 or 5 for each J, Q and K like an ace; Fate Forecast shows your own two opening cards; Aces to the Top moves only the next ace; a Fourfold Ticket loss beyond your cash becomes debt; the new Bust Insurance lets the dealer play on after you bust, and a dealer bust makes it a push. On 2026-10-15 the Invitation's no-core bonus was raised so that going without a core wins about as often as the stronger cores; it scales with the stake.

Current numbers are generated on [Items](items.html) and [Poker Head builds](poker-head-builds.html).
