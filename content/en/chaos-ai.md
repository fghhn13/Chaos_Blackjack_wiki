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

## Offline vs real model

Without an API key the AI is a deterministic offline stand-in; tests, CI and the agent interface use it by default. With a real model each chaos phase is one chat request, plus at most one repair request when the JSON is invalid.
