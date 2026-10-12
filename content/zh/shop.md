---
title: 局内商店与筹码
---
本页介绍花本轮筹码的**局内商店**；主页花代币的 [Shop](progression.html)另见玩家成长。

商店只在下注阶段开放。

- 每次上架 **{{ fact: settings.shop.slots.value }}** 种不同的道具，每件只能买一次。
- 每 **{{ fact: settings.shop.refresh_rounds.value }}** 局换一批货，没买的就没了。
- 每批货可花 **{{ fact: settings.shop.reroll_price.value }}** 筹码刷新一次。刷新不重置补货计时，新价格按扣费后的资金计算；Reroll Pass 提供本轮的一次免费刷新。
- 买完之后，剩下的筹码必须还够下最小注。
- 同一个种子的货架永远一样，买东西也不会改变发到的牌。

## 价目表

内置道具按生成货架时资金的百分比定价，四舍五入，最低一个筹码；下一批货生成之前价格不变。经典模式不出售{{ link: items.shield }}。

{{ table: prices }}

## 怎么算值不值

你从 {{ fact: settings.run.start_money.value }} 筹码开始，目标是 {{ fact: settings.run.target_money.value }}，下注额又受当前资金比例限制。每次购买都会减少可下注的资金。比较界面价格和道具能改善的决策；{{ link: items.shield }} 可以直接清除当前生效的混沌规则。
