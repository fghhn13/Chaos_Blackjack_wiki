---
title: 首页
---
**混沌 21 点**（Chaos Blackjack）是加了料的 21 点：一个被关在沙盒里的混沌 AI 每局都可能改写规则。你带着 {{ fact: settings.run.start_money.value }} 筹码进场，在输光之前赚到 {{ fact: settings.run.target_money.value }} 就算赢。

## 开始游戏

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

在主页点 **Start game** 创建玩家，再在 **New run** 中选 Classic 或 Chaos，点 **Start run** 开始；**Continue run** 恢复未完成的一轮。喜欢命令行？看[玩法](play.html)。想写机器人或 LLM agent 来玩？看[Agent 玩家](agents.html)。

## 从哪里看起

| 我想…… | 去看 |
| --- | --- |
| 学会牌桌规则 | [规则](rules.html) |
| 知道每条混沌规则干什么 | [混沌规则](chaos.html) |
| 决定买什么 | [道具](items.html) 和 [商店与经济](shop.html) |
| 了解 AI 是怎么被管住的 | [混沌 AI](chaos-ai.html) |
| 查所有可调数值 | [平衡参数](settings.html) |

## 关于本百科

页面上的所有数值、ID、价格和命令都从游戏的 `main` 分支自动提取，只有说明文字是手写的。每页底部都写着它对应的具体提交。
