---
title: 规则
---
本页是经典 Blackjack 的基础规则；扑克头的[构筑](poker-head-builds.html)与[环境](environment.html)、[J-54 的牌桌](table-j54.html)分别覆盖相关机制。

## 目标

在经典牌桌，你从[金库](progression.html)带入 {{ fact: settings.mode.normal.stake.value }} 筹码，涨到带入额的 **{{ fact: settings.mode.normal.config.target_multiple.value }} 倍**就赢下这一轮。（不使用金库时，例如 Agent 命令行，一轮从 **{{ fact: settings.run.start_money.value }}** 筹码开始，目标是 **{{ fact: settings.run.target_money.value }}**。）筹码输光，或者已经下不出合法的注，就算输。

## 下注

- 每局下注一个整数，范围是 {{ fact: settings.bet.min.value }} 到 当前资金 × {{ fact: settings.bet.max_fraction.value }}（向下取整）。永远不能全押。
- 下注前可以先逛[商店](shop.html)。

## 牌的点数

- 2–10 按牌面算，J、Q、K 算 10。
- A 先按大的算，快爆牌时自动减 10。固定牌点环境可以撤去大小切换，须按公布效果计算。
- [混沌规则](chaos.html)会在求和之前改变牌的点数。屏幕上显示的总点数已经算上了规则，相信它，不用自己心算。

## 一局的流程

1. 你和庄家各拿两张牌，庄家第二张扣着（*暗牌*）。
2. **天生 21 点**在玩家行动前结算：原始牌面的 A 加一张 10 点牌，赔率 {{ fact: settings.table.blackjack_pays_num.value }}:{{ fact: settings.table.blackjack_pays_den.value }}（向下取整）。庄家天生 21 点时，你还没出手这局就结束；双方都是天生 21 点则算平局。
3. 旧版混沌兼容玩法中，否则[混沌 AI](chaos-ai.html) 出手一次。规则可能让起手牌立即爆牌；{{ link: chaos_rules.reverse_bust }} 会把玩家爆牌改为平局。规则改出的 21 点不享受天生 21 点赔付。
4. 轮到你：**要牌**、**停牌**、**加倍**或**投降**，也可以用[道具](items.html)。
5. 庄家翻开暗牌，一直抽到 {{ fact: settings.table.dealer_stand_on.value }} 点或以上。
6. 结算：赢 `+下注`，输 `-下注`，平局 `0`。

## 加倍和投降

两者都只能在第一次决策时用（手里正好两张牌）。用道具不算决策。

- **加倍**（启用：{{ fact: settings.table.allow_double.value }}）：下注翻倍，只再拿一张牌，然后停牌。
- **投降**（启用：{{ fact: settings.table.allow_surrender.value }}）：放弃这手牌，拿回一半下注，零头归庄家。

## 爆牌

你自己要牌或加倍时超过爆牌线（21，除非混沌规则改了它），这局立刻结束，庄家不再抽牌。
