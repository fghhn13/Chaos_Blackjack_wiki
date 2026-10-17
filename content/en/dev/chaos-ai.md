---
title: Dealers and Chaos AI
---
## Poker Head's offline director

The current Poker Head build Table uses an offline director that acts once before shopping and betting, scales with rounds and manages persistent or timed rules. It does not consume player items or target a player's build. See [environment mechanics](environment.html). Classic has no environment changes; J-54 runs its own program of conditions instead (see [J-54's Table](table-j54.html)).

## Legacy AI pipeline

Legacy Chaos and optional AI content packs use structured actions checked against permissions, then resolve allowed rules/items. This is distinct from the current build director. Prompt files: {{ fact: prompts }}.

{{ table: permissions }}

## Asking Chaos for advice

Clicking the host may request a text suggestion. Guidance probability is {{ fact: settings.chaos.guidance_probability.value }}; the adviser may mislead you. Advice does not play actions or modify the environment. Real-model advice may be billed, while the build director itself needs no model request. Agent has no dedicated advice command.

History is configurable: enabled {{ fact: settings.chaos.memory_enabled.value }}, limit {{ fact: settings.chaos.memory_limit.value }}. The old model pipeline, its prompts and permission budgets do not define the build director's stage pressure.
