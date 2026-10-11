---
title: Shop & economy
---
The shop is open only while you are betting.

- It shows **{{ fact: settings.shop.slots.value }}** different items. Each offer can be bought once.
- It restocks every **{{ fact: settings.shop.refresh_rounds.value }}** rounds; offers you did not buy are lost.
- You may reroll each stock once for **{{ fact: settings.shop.reroll_price.value }}** chips. Rerolling keeps the restock timer; the new prices use the bankroll after paying the fee. Reroll Pass supplies a free reroll for the run.
- A purchase must leave you enough chips to still place a minimum bet.
- The same seed always shows the same shelves, and buying never changes the cards that are dealt.

## Price list

Built-in prices are percentages of the bankroll when the stock is rolled, rounded to the nearest chip with halves rounded up and a minimum of one chip. Prices stay fixed until the next stock. Classic mode does not sell {{ link: items.shield }}.

{{ table: prices }}

## Thinking about value

You start with {{ fact: settings.run.start_money.value }} chips and aim for {{ fact: settings.run.target_money.value }}, with bets capped at a fraction of your bankroll. Every purchase reduces what you can bet. Compare the displayed price with the decision the item can improve; {{ link: items.shield }} directly removes active chaos rules.
