---
title: J-54 v2 specification
source_blob: 68f9249e13ef
---
The implementation specification of J-54's current table, scope frozen and built on 2026-10-17; it replaces the v1 demo at the table `j54`. Every number in it is a first value in the balance profile, to be tuned by play. The player-facing result is on [J-54's Table](table-j54.html).

It defines the run (a fixed number of rounds, a chip target counted only from a late round, or a Joker capture), the compute budget and its three paid moves (Cut, Hot Purge, Release), J-54's program of seven conditions in three camps with seeded segments and a camp announcement, the exact evaluator behind the win-chance meter and the heat map, the Joker rules, the firmware menu, the sample bounty, the public snapshot shared by the GUI and the agent, and the balance keys added and removed. It also lists the engine hooks the table needed (per-side card values, a per-round dealer stand threshold, the player's bust line), the tests and the three work packages it was built in.

Its notes explain choices: capture counts only from the late round because counting it from any round handed a non-shaping player a large lucky advantage in the lab, and nothing is ever inserted by the player because the lab dropped those operations.
