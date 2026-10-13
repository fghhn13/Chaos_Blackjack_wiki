---
title: J-54 的牌桌 *实验性
status: experimental
parent: tables
---
![J-54 立绘](../img/j54.png)

J-54 *实验性会真实重构牌堆，组成跨回合保留，每回合重洗；删除的牌另有记录。检查始终提供真实牌面分布，不公开牌序。

## 协议与经济

单次捕获开局封存 Joker。购买{{ link: items.j54_start_experiment }}释放后，玩家抽到即将本手判为平局并赢下整轮；庄家抽到则放回、避开牌顶，另加低牌惩罚。资本协议改以 {{ fact: settings.mode.j54.capital_target.value }} 筹码为目标。

算力费按 {{ fact: settings.mode.j54.fee_steps.value }} 递增，每 {{ fact: settings.mode.j54.fee_step_rounds.value }} 回合进一档，最低注也受费用约束。结算后熵增加入 {{ fact: settings.mode.j54.entropy.value }} 张低牌，启动实验后为 {{ fact: settings.mode.j54.entropy_experiment.value }} 张；冻结暂停注入。

## 契约与规则

商店每 {{ fact: settings.mode.j54.config.shop_refresh_rounds.value }} 回合补货，包含低牌剔除、精简、高牌注入、冻结与启动实验。购买即签约，不进入消耗品背包，按立即或约定条件执行。上方规则与契约卡片显示当前实际效果和价格。

悬停或固定牌堆信息可以检查组成，Deck 与 Contracts 标签显示详情，图表与标准牌堆对比。当前只含单次捕获与资本；双重捕获、清除、虚假报告与质疑留待后续。[早期构思快照](https://github.com/fghhn13/Chaos_Blackjack_wiki/blob/main/content/sources/J54_TABLE.md)只作历史背景，包含旧占位值。
