---
title: Agent 玩家
---
机器人和 LLM agent 通过一次一条的 shell 命令来玩。每次调用之间，对局保存在一个状态文件里，每条回复都是 JSON（观察数据 schema {{ fact: agent.obs_schema }}）。

```bash
python -m chaos_blackjack.agent new --seed 7 --chaos
python -m chaos_blackjack.agent --brief bet 10
python -m chaos_blackjack.agent --brief act hit
```

## 循环

1. 读 `obs.hint` 和 `obs.legal_actions`。
2. 发送恰好一个合法动作。
3. 读 `events`（刚发生了什么）和新的 `obs`。
4. 重复，直到 `obs.phase` 变成 `run_over`。

观察数据只包含坐在牌桌前能看到的信息。不要解码状态文件。

## 命令

{{ table: commands }}

## 动作

{{ table: actions }}

## 错误

被拒绝的命令不会改变任何状态；读 `error.legal_actions` 后重试。

{{ table: errors }}

## 一局录像

每次更新百科时都会重放这一局：种子 {{ fact: transcript.seed }}，开启混沌，固定下注，"低于 17 就要牌"的策略。游戏一变，这张表就跟着变。

{{ table: transcript }}

完整指南（观察字段、流式模式、Python API）在游戏仓库的 `docs/AGENT_GUIDE.md`（英文）。
