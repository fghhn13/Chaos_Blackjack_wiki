---
title: 架构
---
游戏把**事实**（游戏状态）和**法则**（规则引擎 + 注册的混沌规则插件）分开。

```text
        GUI (gui/)       text CLI (ui/, cli/)      agent CLI (agent/)
              \                  |                       /
               └──────── GameController (app/) ─────────┘
                                 │
                     GameLoop + GameState (core/)
               ┌─────────────────┼─────────────────┐
         RuleEngine (rules/)   items/        ChaosPipeline (ai/)
               │                                   │
         rules/plugins/*        prompts · permissions · LLM backend
               └──────────── Registry (registry/) ─┘
```

- **插件**（混沌规则和道具）按名字自行注册，彼此从不 import；核心代码通过注册表按名字找到行为。
- **前端从不决定规则**：它们只渲染控制器的视图并调用它的命令。
- **混沌 AI** 只输出结构化 JSON，并按权限校验。

## 本百科是怎么生成的

百科是一个独立的仓库。只有一个 adapter 模块会从 `main` 的干净 checkout 导入游戏，把事实（ID、数值、帮助文字、美术、一局重放的 agent 录像）提取到 `facts/facts.json`。网站由这些事实加上手写的说明文字渲染而成。
