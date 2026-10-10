---
title: Architecture
---
The game separates **facts** (game state) from **laws** (the rule engine plus registered chaos rule plugins).

```text
        GUI (gui/)       text CLI (ui/, cli/)      agent CLI (agent/)
              \                  |                       /
               └──────── GameController (app/) ─────────┘
                                 │
                     GameLoop + GameState (core/)
               ┌─────────────────┼─────────────────┐
         RuleEngine (rules/)   items/        ChaosPipeline (ai/)
               │                                   │
         rules/plugins/*        prompts · permissions · LLM backend
               └──────────── Registry (registry/) ─┘
```

- **Plugins** (chaos rules and items) register themselves by name and never import each other; core code resolves behaviour by name through the registry.
- **Front-ends never decide rules**: they render the controller's view and call its commands.
- **The Chaos AI** only emits structured JSON that is validated against permissions.

## How this wiki is built

The wiki is a separate repository. One adapter module imports the game from a clean checkout of `main` and extracts facts (ids, numbers, help text, art, a replayed agent transcript) into `facts/facts.json`. The site is rendered from those facts plus hand-written prose.
