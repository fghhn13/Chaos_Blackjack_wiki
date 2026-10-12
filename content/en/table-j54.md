---
title: J-54's Table — design draft
status: draft
source: user
source_path: docs/design/J54_TABLE.md
source_blob: ed0f3e1b0d8f
parent: tables
---
![J-54 design portrait](../img/j54.png)

**Theme: probability, calculation and rebuilding the deck.** Host: [J-54 “Joker Reshuffler”](dealer-j54.html).

Poker Head changes rules; J-54 changes the cards themselves. Build a favourable deck and chip economy first, then choose when to start the experiment and complete the protocol drawn for the run.

Based on the author's local [J54_TABLE.md source snapshot](https://github.com/fghhn13/Chaos_Blackjack_wiki/blob/main/content/sources/J54_TABLE.md), content version `ed0f3e1b0d8f`. **All numbers below are provisional design values, not simulator-validated balance.**

## 1. Persistent composition and two phases

- The standard base deck has **52 cards, no Joker**. The protocol determines when and how many Jokers enter.
- **Composition** persists for the run. Each round reshuffles and deals from the whole deck; v1 has no shoe and no discard pile.
- Every effect adds, removes or moves physical cards. Peek, Fate Oracle and Danger Radar remain truthful; a seed must replay the same process.
- Early play earns chips and cuts low cards to secure the economy. The player chooses when to begin the late experiment and pursue the protocol.
- Capture Jokers start sealed and require an expensive release contract, preventing a lucky round-one win. Eradication is the exception: its Jokers start in the deck.
- Waiting has a cost: rising compute fees and low-card injections put pressure on both the economy and the objective.

## 2. Run loop

Proposed start: standard deck, 100 chips, a random announced protocol and J-54's introduction.

1. Pay the **compute fee**, which rises with the round number.
2. Visit the **contract shop** during betting: three offers and one reroll, using the existing shop framework.
3. Optionally inspect the deck through the portrait and challenge the report.
4. Bet: minimum `max(5, compute fee)`; maximum remains half the bankroll.
5. Deal → naturals settle → J-54 Chaos rule → player turn → dealer → settlement.
6. At round end, in order: fire eligible contracts → apply burn effects → check the protocol → apply **entropy**, adding low cards.
7. Check for defeat.

All protocols lose on bankruptcy or inability to pay the next fee plus the minimum bet. Chips are life and a budget for fees and contracts; only Capital directly makes them the objective.

## 3. Random protocols: win conditions

| Protocol | Jokers | Win condition | Main approach |
| --- | --- | --- | --- |
| Single Capture | One, sealed until released | The player draws it | Shrink the deck and hit aggressively |
| Double Capture | Two, sealed until released | The player captures both across the run; captured Jokers enter a sample slot | Same approach, longer process |
| Eradication | Two in the deck from the start; wild for the dealer | No Joker remains in the deck | Targeted deletion and burn contracts |
| Capital | None | Reach 1000 chips | Deck economy |

The **Start experiment** contract, provisionally about 150 chips, releases sealed Jokers. Entropy then doubles and J-54's rules lean against the protocol. Eradication needs no release; targeted-deletion contracts fill that role.

Only a **player-drawn** Joker counts for Capture. Dealer-drawn Jokers return to the deck, with an additional 2–3-card penalty. A player-drawn Joker immediately ends the hand and wins the run in Single Capture; in Double Capture it enters the sample slot.

The same effect has different purposes by protocol: burning can shrink a Capture deck or remove a Joker under Eradication. Random deletion never removes Capture Jokers; it can remove Eradication Jokers.

**Later ideas:** Resonance, requiring both Jokers in one player hand, and a hidden protocol inferred through inspection. These are outside the first batch.

## 4. Fees, entropy and pacing

| Rounds | Provisional compute fee per round |
| --- | --- |
| 1–4 | 2 chips |
| 5–8 | 5 chips |
| 9–12 | 10 chips |
| 13 onward | Start at 20 chips, doubling every four rounds |

Proposed entropy adds one low card of rank 2–6 after each round, or two after the experiment begins. The intended pressure is to grow the deck and weaken the economy and protocol progress; this needs measurement.

Target pacing is a typical win in rounds 12–18, a fee-driven soft cap around round 25, and rare wins within eight rounds. **There is no hard round limit.** Fast-completion ratings or achievements are only a later suggestion.

The document's rough Single Capture estimate assumes about 2.8 player draws per round: `2.8 / deck size`. Decks of roughly 53, 30 and 15 cards suggest about 5%, 9% and 19% per round. **These are rough estimates, not simulation results or guaranteed win rates.**

## 5. Run contracts

This shop sells contracts, **not regular items**. Each contract has a price, trigger, effect and duration. Prices are fixed chip amounts rather than bankroll percentages, making saving for a large contract a choice.

| Contract | Provisional price | Trigger | Effect |
| --- | --- | --- | --- |
| Streamline | 100 | Next won hand | Delete four random cards |
| Targeted purge | 80 | Next won hand | Delete two cards of a chosen rank |
| Burn guarantee | 60 | Next lost hand | Burn every card drawn this round |
| Natural clause | 50 | Next natural blackjack | Delete six random cards |
| High injection | 60 | Immediate | Add two aces or ten-value cards for the economy |
| Freeze | 70 | Immediate | Prevent J-54 from adding cards for three rounds |
| Start experiment | About 150 | Immediate | Release the sealed Jokers |
| Eradication clause | 120 | Draw a Joker and win that hand | Delete that Joker; Eradication only |

Reshuffling the whole deck each round makes composition the player's edge. Adding aces and ten-value cards, and cutting low cards early, is intended to strengthen the economy and shrink the later Capture deck. Its value has not been measured.

## 6. Inspection and challenges

- Click J-54's portrait once per round for deck size, counts by rank and remaining Jokers.
- Provisionally about 15% of reports change one number. A lie is limited to information the player could compute from the starting deck, announced changes and seen cards; rare lies about Jokers remaining are allowed.
- Challenge once per report. A correct challenge grants a random regular item; a wrong challenge loses roughly 10% of the bankroll, at least five chips, intended to discourage blind accusations.
- Whether a report lies comes from seeded randomness, **not the LLM**; the LLM only voices it.
- The proposed Agent commands are `inspect` and `challenge`; observations must not reveal whether a report is true. **These commands are not implemented.**

## 7. First Chaos rule batch

Every applied rule is announced publicly and changes physical cards.

| Rule | Proposed effect |
| --- | --- |
| Burn protocol | After settlement, remove cards drawn this round; exclude Jokers under Capture |
| Sample injection | Add 2–4 cards of one rank |
| Redundancy purge | Remove X cards of one rank; quantity unresolved |
| Ace injection | Add one or two aces |

The pool primarily contains these deck rules; perhaps one existing rule may be included. Offline weights vary by protocol and alternate directions to avoid prolonged one-way drift. Capture favours injection; copying Jokers is only J-54's counter under Eradication.

The LLM can see **composition, never deck order**. Positions come from seeded randomness, so the dealer cannot stack the deck.

## 8. Expressions and implementation direction

The document proposes nine expressions: grand welcome, resting mania, card reveal, secretive trick, paranoid analysis, guarded, irritated, glitching frenzy, and obsessive lecture for the rule summary. This wiki retains the author's full portrait; mentioning an expression archive does not mean those images are displayed here or integrated into the game.

Saves, Agent state files and the simulator would need persistent composition, sealed Jokers, the sample slot and pending contracts. Protocols become objectives; targeted effects need card/rank input; numbers belong in balance profiles. See the [source document](https://github.com/fghhn13/Chaos_Blackjack_wiki/blob/main/content/sources/J54_TABLE.md) for proposed interfaces and expression mappings.

## 9. Open questions

- Immediate versus waiting contracts, and whether unfired contracts expire.
- Whether a player-drawn Eradication Joker may be used as a wild card before returning to the deck.
- Starting chips versus the first contract price, and when purchases become affordable.
- Always-random protocols versus selection after unlocking.
- Table unlock conditions and deck/table cosmetic rewards.
- Exact fee curve, entropy, lie chance, challenge penalty and contract prices.
