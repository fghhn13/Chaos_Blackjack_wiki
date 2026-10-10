---
title: Agent players
---
Bots and LLM agents play through one-shot shell commands. The run is saved to a state file between calls, and every reply is JSON (observation schema {{ fact: agent.obs_schema }}).

```bash
python -m chaos_blackjack.agent new --seed 7 --chaos
python -m chaos_blackjack.agent --brief bet 10
python -m chaos_blackjack.agent --brief act hit
```

## The loop

1. Read `obs.hint` and `obs.legal_actions`.
2. Send exactly one legal action.
3. Read `events` (what just happened) and the new `obs`.
4. Repeat until `obs.phase` is `run_over`.

Observations contain only what a player at the table can see. Do not decode the state file.

## Commands

{{ table: commands }}

## Actions

{{ table: actions }}

## Errors

A rejected command changes nothing; read `error.legal_actions` and retry.

{{ table: errors }}

## A recorded run

This run is replayed on every wiki update with seed {{ fact: transcript.seed }}, chaos on, a flat bet and a "hit below 17" policy. If the game changes, this table changes with it.

{{ table: transcript }}

The full guide (observation fields, streaming mode, Python API) is `docs/AGENT_GUIDE.md` in the game repository.
