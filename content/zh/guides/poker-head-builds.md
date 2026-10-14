---
title: 扑克头构筑指南
---
扑克头牌桌由核心、有限永久商品位、消耗品和金融产品组成，从[金库](progression.html)带入 {{ fact: settings.mode.chaos.stake.value }} 筹码。净资产达到**带入额的 {{ fact: settings.mode.chaos.config.exit_multiple.value }} 倍**起，可在下注前选择**满载而归**以胜利离场；达到 **{{ fact: settings.mode.chaos.config.target_multiple.value }} 倍**时直接胜利结束，超出部分的盈利不支付。本页按当前正式方案介绍，以下卡片读取当前平衡配置。

## 开局与转型

「庄家的见面礼」提供两个固定核心候选。可以选一个，也可额外取得 {{ fact: settings.mode.chaos.decline_cash.value }} 筹码、整局无核心。查看或读档不会重抽；核心不占永久商品位。部分核心在选择时会花费或带来筹码，见见面礼上的说明。

五种方向为多牌、投降、控点、双倍和金融。核心改变你能做什么（例如要牌后仍可投降或加倍、重开起手牌），永久商品负责放大收益。「改约函」可在下注前提供两个不同的新核心；已购商品与已有金融合同保留。无核心局不能使用改约函。退出贵宾账户会撤去额外商店格、停止新购金融产品，已有投资与贷款继续结算。

当前最多装备 **{{ fact: settings.mode.chaos.build_slots.value }} 件永久商品**，同名最多一件。满位购买先选旧商品，确认后扣款替换；旧商品不退款，也不进入备用仓库。重新装备不重置本回合或本批货已用次数。

## 现金、投资与债务

**净资产 = 可用现金 + 未到期投资的投入本金 − 未偿贷款的全部应还金额。**购买装备降低净资产；投资将现金换为本金，未实现收益不提前计入。借款同时增加现金和未来应还债务，不能凭借钱直接创造胜利。四倍押注输超现金的部分同样记为债务。到期在完整回合后结算一次；提现阻挠只约束实际正收益，不截留返还本金。

最低下注按 {{ fact: settings.mode.chaos.min_bets.value }} 随回合提高，之后每 {{ fact: settings.mode.chaos.bet_step_rounds.value }} 回合再加 {{ fact: settings.mode.chaos.bet_step_add.value }}。下注仍须有足够现金。完整结算或回购等合法现金动作后检查胜利；胜利时清算未到期本金与已记债务，不支付未赚到的利息。

## 商店与使用阶段

筹码金额（价格、金融产品、最低下注、刷新费、放弃核心的补偿）按 {{ fact: settings.mode.chaos.money_base.value }} 筹码的参考带入额编写，并随实际带入额等比缩放；卡片显示参考值。付费刷新价格随最低下注每升一档增加 {{ fact: settings.mode.chaos.reroll_step_add.value }}。涨价与采购折扣合并后只向上取整一次；金融金额不套折扣，原价回购按选中消耗品的实际支付价退款。

每批一格优先提供泛用消耗品，其他格随回合增加永久商品概率。当前核心对应流派的商品选择权重为基础的 {{ fact: settings.mode.chaos.style_weight.value }} 倍；已装备商品不再上架。开局先选核心，再由荷官公布环境，然后开放购物、准备道具和下注。详见[混沌环境机制](environment.html)。

局内面板含 Build、Bag、Finance、Rules、Log、Run。按道具注明的阶段使用，不能在已经结算后补救。没有构筑状态的旧存档保留原玩法。

## 商品目录

{{ table: poker_products }}
