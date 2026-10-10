---
title: 规则
---
## 目标

你带着 **{{ fact: settings.run.start_money.value }}** 筹码进场，赚到 **{{ fact: settings.run.target_money.value }}** 就赢下这一轮。筹码输光，或者已经下不出合法的注，就算输。

## 下注

- 每局下注一个整数，范围是 {{ fact: settings.bet.min.value }} 到 当前资金 × {{ fact: settings.bet.max_fraction.value }}（向下取整）。永远不能全押。
- 下注前可以先逛[商店](shop.html)。

## 牌的点数

- 2–10 按牌面算，J、Q、K 算 10。
- A 先按大的算，快爆牌时自动减 10。在任何混沌规则下 A 都保持"软"的特性。
- [混沌规则](chaos.html)会在求和之前改变牌的点数。屏幕上显示的总点数已经算上了规则，相信它，不用自己心算。

## 一局的流程

1. 你和庄家各拿两张牌，庄家第二张扣着（*暗牌*）。
2. 混沌模式下，[混沌 AI](chaos-ai.html) 出手一次。
3. **天生 21 点**：头两张正好 21，赔率 {{ fact: settings.table.blackjack_pays_num.value }}:{{ fact: settings.table.blackjack_pays_den.value }}（向下取整）。庄家天生 21 点时，你还没出手这局就结束了；双方都是天生 21 点则算平局。
4. 轮到你：**要牌**、**停牌**、**加倍**或**投降**，也可以用[道具](items.html)。
5. 庄家翻开暗牌，一直抽到 {{ fact: settings.table.dealer_stand_on.value }} 点或以上。
6. 结算：赢 `+下注`，输 `-下注`，平局 `0`。

## 加倍和投降

两者都只能在第一次决策时用（手里正好两张牌）。用道具不算决策。

- **加倍**（启用：{{ fact: settings.table.allow_double.value }}）：下注翻倍，只再拿一张牌，然后停牌。
- **投降**（启用：{{ fact: settings.table.allow_surrender.value }}）：放弃这手牌，拿回一半下注，零头归庄家。

## 爆牌

你自己要牌或加倍时超过爆牌线（21，除非混沌规则改了它），这局立刻结束，庄家不再抽牌。
