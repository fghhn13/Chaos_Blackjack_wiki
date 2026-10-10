---
title: Home
---
**Chaos Blackjack** is blackjack with a twist: a sandboxed Chaos AI may bend the rules every round. Start with {{ fact: settings.run.start_money.value }} chips and reach {{ fact: settings.run.target_money.value }} before you go broke.

## Start playing

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

Turn on **Chaos Mode** in the main menu to meet the Chaos AI. Prefer the terminal? See [How to play](play.html). Writing a bot or an LLM agent? See [Agent players](agents.html).

## Where to look

| If you want to… | Read |
| --- | --- |
| learn the table rules | [Rules](rules.html) |
| know what each chaos rule does | [Chaos rules](chaos.html) |
| decide what to buy | [Items](items.html) and [Shop & economy](shop.html) |
| understand how the AI is kept in check | [The Chaos AI](chaos-ai.html) |
| look up every tunable number | [Balance settings](settings.html) |

## About this wiki

Every number, id, price and command on these pages is extracted from the game's `main` branch; only the explanations are written by hand. The footer of each page names the exact commit it describes.
