---
title: 筹码金库与局外成长
---
游戏只有一种货币：**筹码**。每位玩家有一个跨局保留的**筹码金库**，新玩家初始为 {{ fact: settings.meta.vault_start.value }}。开局时从金库取出本轮带入的筹码作为起始现金，结束后能带回多少取决于结局。局内商店和主页 **Shop** 都花筹码。

## 带入资金与目标

在 **New run** 用滑条选择带入额，目标随带入额变化。

| 牌桌 | 从金库带入 | 获胜方式 |
| --- | --- | --- |
| [经典牌桌](table-normal.html) | {{ fact: settings.mode.normal.stake.value }} | 达到带入额的 {{ fact: settings.mode.normal.config.target_multiple.value }} 倍，这同时是上限 |
| [扑克头的牌桌](table-chaos.html) | {{ fact: settings.mode.chaos.stake.value }} | 达到带入额的 {{ fact: settings.mode.chaos.config.exit_multiple.value }} 倍起可选择**满载而归**，以胜利离场；达到 {{ fact: settings.mode.chaos.config.target_multiple.value }} 倍时直接胜利结束，超出部分的盈利不支付 |

未达到离场线时不能离开：一局只能以胜利或破产结束。[J-54 *实验性](table-j54.html)是免费演示桌，不需要带入。金库不足最低带入额时不能开始。

## 一局如何结算

- **胜利**：本轮最终现金存回金库；未到期投资按成本清算，债务先行还清。
- **失败**：不带回任何筹码。结束时仍欠的债务（四倍押注输超现金、未还贷款）从金库扣除，最低扣到 0。
- **放弃**：按失败处理，带入的筹码亏掉。

本版胜利没有额外奖金（由金库结算）；成就仍另外发放筹码奖励。

## 救济、保险与会员

**救济**：金库不够经典牌桌的最低带入时，扑克头会补足，保证总能开局。首次 {{ fact: settings.meta.relief_base.value }} 筹码，自上次获胜以来每多救济一次加 {{ fact: settings.meta.relief_step.value }}，单次最多 {{ fact: settings.meta.relief_cap.value }}；赢一局后重置。

**早期破产险**在 New run 与带入额一起购买，保费为带入额的 {{ fact: settings.meta.insurance_premium_pct.value }}%；若在 {{ fact: settings.meta.insurance_rounds.value }} 回合内失败，退还带入额的 {{ fact: settings.meta.insurance_refund_pct.value }}%。中途放弃不赔付。

**会员等级**按累计消费升级（局内与主页商店购物、保费；下注和输掉的筹码不算），各级起点为累计消费 {{ fact: settings.meta.membership_spend.value }}。每级在个人资料页有称号和徽章；3 级起救济上限增加 {{ fact: settings.meta.membership_relief_bonus.value }}，4 级起主页商店优惠 {{ fact: settings.meta.membership_shop_discount_pct.value }}%。

## 商店

主页 **Shop** 用筹码出售[装扮](cosmetics.html)。本版关闭了永久升级和开局物品，Shop 与 New run 不再提供它们。

继续查看[成就](achievements.html)和[个人资料](profile.html)。
