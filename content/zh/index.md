---
title: 首页
---
**混沌 21 点**是一段穿行于不同荷官牌桌的旅程。每张 Table 把荷官、目标、规则和道具组合成一种玩法。先在经典牌桌学习游戏，再到[扑克头](dealer-poker_head.html)的专属牌桌坐下。

## 开始游戏

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

主页 **Start game** 创建玩家，**New run** 选择经典牌桌或扑克头的牌桌、查看升级并勾选开局物品；**Continue run** 恢复未完成的一轮。[玩法](play.html)说明桌面、浏览器和手机操作。

## 选择牌桌

{{ table: tables }}

## 继续探索

- [荷官](dealers.html)：角色和他们的牌桌。[J-54](dealer-j54.html)是以概率、计算和牌堆重构为主题的**设计草案**。
- [混沌规则](chaos.html)与[道具](items.html)：具体效果及适用牌桌。
- [玩家成长](progression.html)、[装扮](cosmetics.html)、[成就](achievements.html)和[个人资料](profile.html)：跨轮保留的内容。
- [Agent 玩家](agents.html)、[平衡数据](balance.html)和[混沌 AI](chaos-ai.html)：技术参考。

已实现机制和数值来自游戏 main，作者提供的草案另有状态标记，不代表已上线的玩法。每页页脚注明游戏数据快照；草案提示说明提案的独立来源。
