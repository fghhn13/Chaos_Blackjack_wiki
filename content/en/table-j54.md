---
title: J-54's Table — design draft
status: draft
source: user
parent: tables
---
Hosted by [J-54 “Harlequin Reshuffler”](dealer-j54.html). Theme: probability, calculation and deck reconstruction.

![J-54 design portrait](../img/j54.png)

J-54 is a mechanical computing device designed as a circus clown. Its theatrical movements and pixel expressions are exaggerated, yet it addresses the player in cold, precise programmatic language. Unlike other Tables, it favours changing the cards themselves over directly rewriting Blackjack's rules.

## Deck Structure

This draft proposes a 54-card deck. Items and Chaos rules can directly manipulate it:

- **Duplicate:** add cards of a specified rank or suit.
- **Remove:** take some cards out of the deck.
- **Reorder:** change the order of the remaining cards.
- **Recycle:** return discarded cards to the deck.
- **Scan:** obtain statistics about the remaining deck.

Some effects may last across rounds, gradually taking the deck away from its proposed standard structure.

## Example Chaos rules

| Rule | Proposed effect |
| --- | --- |
| Sample Proliferation | Choose a rank at random and duplicate its remaining cards |
| Redundancy Removal | Randomly remove some remaining cards of one rank |
| Layered Ordering | Arrange high-rank and low-rank cards in groups |
| Data Reflow | Shuffle some discarded cards back into the deck |
| Distribution Bias | Change how often a specified rank appears in the next several cards |

## Example exclusive items

| Item | Proposed effect |
| --- | --- |
| Sample Duplicator | Add a copy of a chosen card in the player's hand to the deck |
| Data Shredder | Delete cards of a specified rank from the remaining deck |
| Distribution Scanner | View the rank distribution of the remaining deck |
| Local Shuffler | Shuffle the remaining cards again |
| Recycling Module | Return a chosen discarded card to the deck |

## Open definitions

The released game's base deck has {{ fact: deck.cards }} cards and is rebuilt each round. This draft's 54-card structure and persistent changes require definitions for Jokers, a discard area, the reset schedule and what happens when the deck runs out.

Quantities, duration, stacking and the visibility of deck information remain open. These are design questions, not additional established mechanics. There are no prices or simulator measurements yet.
