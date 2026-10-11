---
title: The Chaos AI
---
The Chaos AI never touches the cards. It returns a small structured JSON action, and the game checks it before anything happens.

## Pipeline

1. The game builds an observation of the table for the AI.
2. The AI answers with JSON: apply a rule (with parameters), use one of the player's items, or do nothing.
3. A **permission validator** checks the action against the active difficulty profile: allowed rules and items, actions per turn, and the chaos budget.
4. Accepted actions are resolved by name through the registry into a rule modifier or an item use. Rejected actions are reported as events and have no effect.
5. If the model fails or times out, the action becomes a no-op and the game continues.

## Difficulty profiles

{{ table: permissions }}

## Personalities

Prompt files shipped with the game: {{ fact: prompts }}.

The default dealer appearance is **Poker Head**, with expressions and dialogue reacting to table events. This visual default keeps the usual Chaos rule weights. The separately selectable `poker_head` content pack supplies its own AI profile; do not confuse that profile with the default portrait.

For a direct offline content-pack game, run `python -m chaos_blackjack.content play poker_head`, or use `python -m chaos_blackjack.agent new --pack poker_head --ai poker_head --chaos`. Its persona is polite and hostile to the player, favours small rule changes and calm rounds, and does not use the player's items.

## Asking Chaos for advice

In Chaos Mode you can click the Chaos portrait while betting, during your turn, after a round, or with the shop open, to ask for a suggestion. Each time, Chaos secretly decides whether to **guide** you or **mislead** you: it guides with probability {{ fact: settings.chaos.guidance_probability.value }} and never tells you which it chose. Even "guiding" advice is not guaranteed to be right.

Chaos sees more than you do when it answers (hidden cards and the deck order included), but its reply is text only: it cannot buy, play or change rules. Agents have no command for this yet. With a real model each poke is one billed request.

## Memory

Chaos can keep a run-local history of what happened and use it in later prompts. It is off by default (enabled: {{ fact: settings.chaos.memory_enabled.value }}); when switched on in a balance profile it keeps at most {{ fact: settings.chaos.memory_limit.value }} events, and saves restore it.

## Offline vs real model

Without an API key the AI is a deterministic offline stand-in; tests, CI and the agent interface use it by default. With a real model each chaos phase is one chat request, plus at most one repair request when the JSON is invalid.

The default offline draw combines each rule's weight with a calm-round weight of {{ fact: settings.chaos.stub_calm_weight.value }}. These are relative weights, not percentages; a calm draw leaves the rules unchanged.
