---
title: 图鉴与演示（M4a–M4b）
source_blob: 59faeb3196e5
---
这是[局外成长、存档与图鉴](design-meta-progression.html)里游戏内图鉴的无界面引擎（M4a）和列表、详情界面（M4b）。引擎不需要 Pygame 或玩家存档；界面展示它生成的条目、实时说明和演示帧。

## 图鉴里有什么

- **分页**（`CodexKind`）：规则、道具、模式、AI。新增的类别会有自己的分页。
- **条目**（`CodexEntry`）：类别、ID、名称、图标、简介、详细说明、可选的演示，以及排序。什么都不锁定、不隐藏，包括 AI 不能选的规则和当前商店不卖的道具。
- **实时说明**：每条详细说明都根据当前的 `RunConfig` 计算，所以价格、补货、命运神谕看牌数、赔率、下注范围、庄家规则、模式覆盖项和混沌 AI 建议设置，永远和所选的平衡配置一致。简介和演示字幕从不写可调的数值。

```python
from chaos_blackjack.app.config import RunConfig
from chaos_blackjack.codex import codex_entries, codex_kinds, run_demo

config = RunConfig()                      # or RunConfig.from_balance(profile)
tabs = codex_kinds()
entry = next(e for e in codex_entries("rule", config) if e.id == "great_crash")
text = entry.detail(config)
frames = run_demo(entry.demo, config)
```

## 条目从哪里来

- **Provider**：`register_codex_provider(kind, fn)` 注册一个函数，它接收配置并返回条目。后注册的 provider 可以覆盖已有条目，也可以新增条目。
- **规则和道具**在每次查询时从实时的插件注册表读取，所以新插件和内容包会自动出现（带一个可读的默认名称，没有演示）。插件可以用可选属性 `codex_name`、`codex_icon`、`codex_summary`、`codex_detail`、`codex_demo`、`codex_order` 描述自己。
- **模式**从 `chaos_blackjack.modes.modes()` 读取；较早的基础版本以 `normal` 和 `chaos` 作为回退。
- **内容包**由 `RunConfig.content_packs` 选择，载入控制器的独立注册表。道具、说明、规则和 AI 档案会自动出现，不会影响其他配置。AI provider 在可用时使用 `Registry.ai_ids()` 和 `resolve_ai()`；较早版本只展示 `ai/default`。

## 演示

演示是一段短脚本：每手两张起手牌、按抽牌顺序排好的其余牌堆，以及一串步骤。

| 步骤 | 作用 |
| --- | --- |
| `deal` | 指定起手牌并真正下注（每个脚本恰好一次） |
| `apply_rule` | 按平衡配置的实时参数展示一条已注册的混沌规则（配置里固定的值优先） |
| `use_item` | 真正使用一件道具 |
| `hit`、`stand`、`double`、`surrender` | 普通的玩家动作，权限规则照常 |
| `dealer` | 让庄家打到结束，每次抽牌和决定各一帧 |
| `caption`、`pause` | 带字幕截取当前牌桌 |

`run_demo` 在**真正的游戏控制器**上播放脚本，只有发牌是指定的，返回一组帧（牌桌视图、字幕、通知）交给界面去播放动画。因为跑的是真规则，演示永远不会和游戏矛盾。演示：

- 从不改动调用方的配置、平衡数值、存档、对局记录或代币；
- 永远离线：即使开启了真实大模型，也不会调用模型、不会读取密钥；
- 遇到错误的牌、未知步骤或非法动作会直接报错，而不是假装生效；
- 庄家的暗牌在游戏或道具揭示之前一直扣着。

每条内置混沌规则和每件道具都带有演示。反转爆牌的演示展示当前行为：爆牌会立刻结束这手牌，按平局结算。

## 列表与播放

从主页打开 **Collection**，或运行 `python -m chaos_blackjack.gui --scene codex`。界面入口为 `app.scenes.push("codex", config=config)`；默认配置是 `app.run_config`，可选的 `kind` 指定初始分页。

列表按类别展示图标和名称，条目多时自动分成多页。Tab / Shift-Tab 切换类别，左右键或滚轮翻页。选择条目打开详情；Back / Escape 返回后保留类别和页码。

详情文字和演示帧先按所选配置计算，再播放已存的帧；播放期间不再执行控制器动作。空格暂停或播放，R 重播，左右键逐帧定位并暂停，最后一帧停住。说明可用滚轮或 Page Up / Page Down 滚动。没有演示或演示与当前设置不兼容的条目会展示文字，关闭播放。

经典和混沌模式使用[美术图鉴](gallery.html)里的模式图标；缺失美术时保留程序绘制的占位图。

## 状态

来源文档已在 `main`。它要求注册表和演示测试、界面导航和播放测试、全量测试，以及模拟器平衡检查。界面测试还覆盖滚动、图标回退、纯文字条目、内容包隔离和内置演示帧渲染。
