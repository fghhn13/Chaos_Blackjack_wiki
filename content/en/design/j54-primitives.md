---
title: J-54 game primitives
source_blob: f08808fef186
---
A research document (framework agreed 2026-10-15, v2 decisions 2026-10-16) that replaced "design a level" with "design the parts levels are made of". J-54 acts by a fixed algorithm, the player changes a shared deck with a limited budget, and each side follows its own card-value rules, so changing the deck shifts the advantage.

It catalogues the primitives (the table's shuffle and replacement sub-mode, draw policies, deck operations, effect rules, J-54's advantage, goals) and records ten rounds of a rule lab that measured them. The lab's findings shaped v2: a chip target counted from a late round with a betting meter in bands, removal as the player's move, a heat map computed exactly for the active rules, the camp announcement as the difficulty dial, rules sorted into camps by the way they point, and a firmware with a price. A later round widened the goal to a **build space** judged by strategy diversity rather than one tuned configuration; Round 10 kept the Joker release (with a late capture), J-54's most valued rank, two more firmwares and a size-3 Hot Purge, and dropped purchasable information, the Sample card and schedule balancing as a mechanism.

The document ends with open questions (a human-feasible shaping policy, random schedules, injection size, double and surrender) and the verification roadmap. The implemented result is the [v2 specification](design-j54-v2-spec.html).
