---
title: Poker Head: environment rules and the offline agent (Chinese)
source_blob: 37085682a512
---
The Chinese design for Poker Head's environment and the offline dealer that grows stronger over a run. The doc marks it integrated into the game; values, weights and durations are first-pass and not yet simulated. Only the offline director changes the build Table's environment; `--llm` affects dealer dialogue only. Classic, J-54 and old Chaos saves are unchanged.

## Rules

A 2026-10-15 revision, based on simulator measurements of each variant, allows at most two rules at once and sorts them into light, medium and heavy tiers by their effect on expected value: heavy rules wait until a later round and only one can be active, and the most extreme card rewrites were removed; the rule list, announcements and the agent observation show each rule's tier. The original design allowed up to three rules, one per type, and a full board can still be replaced. Nine generic types replace the old fixed rules: fixed card values, value offsets, bust limits, tie outcomes, bust outcomes, a profit cap, an item ban, shop markup and a hidden player card. Each rule shows its name, full effect, target, remaining duration and how it goes away; persistent rules last until removed, timed ones count completed rounds. Clause Removal deletes a chosen rule, Silence Seal suppresses all of them for one round, and an item ban is lifted by sacrificing a consumable with no effect. The doc maps every old rule to its new type.

## The offline dealer

It acts at most once per round, before shopping and betting, and grows by round only: more simultaneous rules, stronger variants and a higher action chance across four stages, limited by a pressure budget with at most one high-pressure rule and no hidden card together with an item ban. It reads only the seed, round, current rules and cooldown history, never the player's build, bets or cards. It prefers adding a rule, picks a type by weight and then a variant, keeps rules at least two rounds, and puts a cleared or expired type on cooldown. All draws are reproducible and saved, and no model is called.

How this plays today is on [Environment](environment.html).
