---
title: 荷官与混沌 AI
---
## 扑克头离线环境导演

当前构筑桌使用离线导演：每回合购物与下注前行动一次，按回合增强，管理持续和限时规则。它不会消耗玩家道具，也不读取玩家构筑来针对玩家，详见[环境机制](poker-head-environment-plan.html)。经典桌不改环境，J-54 *实验性使用独立牌堆规则池。

## 旧版 AI 流程

旧版混沌和可选 AI 内容包使用结构化动作，经权限校验再执行允许的规则或道具，与当前构筑导演分开。提示词文件：{{ fact: prompts }}。

{{ table: permissions }}

## 向混沌 AI 要建议

点击荷官可请求文字建议，引导概率为 {{ fact: settings.chaos.guidance_probability.value }}，可能误导玩家。建议不会出牌或改环境；真实模型建议可能计费，构筑导演本身不需要模型请求。Agent 尚无专门建议命令。

历史配置为启用 {{ fact: settings.chaos.memory_enabled.value }}，最多 {{ fact: settings.chaos.memory_limit.value }} 条。旧模型提示词和权限预算不决定新导演的阶段压力。
