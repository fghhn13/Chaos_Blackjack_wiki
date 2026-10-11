---
title: 局外成长、存档与图鉴
source_blob: 61b37b6dc12c
---
每轮游戏之间你有一个**玩家**：一个存档位，里面有代币、永久升级和消耗品。每一轮都会记录，**图鉴**讲解规则、道具、模式和 AI，有演示的条目还会播放动画。Agent 命令行不加入局外成长，保证 agent 对局公平、可复现。

本页概述共享设计约定。下方奖励引用自动提取的默认值；设计中的 balance v1 商品目录以 `seed/default.sql` 的价格和参数为准。

## 决定

| 主题 | 决定 |
| --- | --- |
| 代币 | 赢一轮发代币。输了按存活局数和资金峰值发一点安慰奖。 |
| 临时升级 | 消耗品：在局外商店购买，叠放在背包里；开新一轮时，每种选中的消耗品用掉一件。 |
| 玩家存档 | 3 个可命名的存档位。 |
| 图鉴 | 所有条目都正常显示（图标 + 名称），暂时不做锁定或剪影；"见过"的数据先收集起来以后用。 |
| 游戏模式 | 开新一轮时选择。目前只有 `normal` 和 `chaos`，都已解锁。 |
| Agent / 模拟器 | Agent 命令行没有局外成长。模拟器会加入升级和代币经济的实验。 |
| 数值 | 价格、奖励和升级数值都放在平衡配置里，不写进代码。 |

命名约定：**玩家**（player）是局外存档（存档位）；**平衡配置**（balance profile）是一组数值。玩家永远不叫"profile"。

## 整体关系

```text
player (slot 1-3) ── tokens, permanent upgrades (with level), consumables (with count)
   │
   ├─ start run(mode) ─► RunConfig = balance profile + mode + permanent upgrades
   │                                  + one use of each selected consumable
   │                       └─ game logic unchanged; the run's fingerprint shows the upgrades
   └─ finish run ──────► tokens (win or consolation), run history row, codex "seen" updates
```

即：玩家（3 个存档位之一）拥有代币、带等级的永久升级和带数量的消耗品。开一轮时，运行配置 = 平衡配置 + 模式 + 永久升级 + 选中的消耗品各一件，游戏逻辑本身不变；一轮结束时，结算代币（胜利奖励或安慰奖），写入对局记录，更新图鉴的"见过"数据。

## 代币

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `meta.win_tokens` | {{ fact: settings.meta.win_tokens.value }} | 胜利获得的代币 |
| `meta.chaos_win_bonus` | {{ fact: settings.meta.chaos_win_bonus.value }} | 混沌模式胜利额外获得的代币 |
| `meta.loss_per_round` | {{ fact: settings.meta.loss_per_round.value }} | 每存活一局的安慰奖 |
| `meta.loss_per_peak_gain` | {{ fact: settings.meta.loss_per_peak_gain.value }} | 资金峰值每比开局资金多 100% 的安慰奖 |
| `meta.loss_cap` | {{ fact: settings.meta.loss_cap.value }} | 安慰奖上限 |

```text
安慰奖 = min(loss_cap, floor(局数 × loss_per_round
                            + max(0, 峰值 − 开局) / 开局 × loss_per_peak_gain))
```

放弃一轮不发代币。

## 局外商店：balance v1 商品目录

| 升级 | 类型 | 效果 | 价格 | 最高等级 |
| --- | --- | --- | --- | --- |
| `start_money` | 永久 | 每级开局资金 +10 | 20，每级 +10 | 3 |
| `bag_space` | 永久 | 多带一种消耗品 | 25，每级 +15 | 2 |
| `reroll_pass` | 永久 | 每轮一次免费商店刷新 | 30 | 1 |
| `start_<道具>` | 消耗品 | 下一轮开局就带着这件道具（每种商店道具一个条目） | 设计建议约为开局商店价的一半，实际以商品显示为准 | 3 |

升级的第 *n* 级价格为 `cost + (n − 1) × cost_step`。一个升级可以要求先拥有另一个升级。

每轮基础携带上限为 {{ fact: settings.meta.bring_kinds.value }} 种消耗品。`shop.slots_add` 和 `shop.discount_pct` 效果仍可用于自定义配置，但默认商店不再出售；设计文档说明它们的实测价值很低。

## 游戏模式

模式就是 `GameMode(id, name, description, icon, overrides, unlocked_by)`：一组对运行配置的覆盖。首批只有 `normal` 和 `chaos`；为以后的模式预留了 `unlock_mode` 升级效果，但目前商店里还没有对应商品。

## 对局记录

每一轮会记录：模式、平衡配置及其指纹、种子、结果（`victory` 胜利、`defeat` 失败、`abandoned` 放弃）、局数、最终和峰值资金、获得的代币、用到的升级，以及一份摘要：

```json
{"rules_seen": {"great_crash": 2}, "items_used": {"peek": 3}, "items_bought": {"swap": 1},
 "rounds": 23, "peak_money": 260, "blackjacks": 2, "doubles": 4, "surrenders": 1,
 "chaos_ai": "default"}
```

中途退出记为 `abandoned`，不发代币。

## 图鉴

- 按类别分页：规则、模式、道具、AI。每个条目有图标、名称、简介，以及引用当前平衡配置实时数值的详细说明。
- 条目由 **provider** 从规则、道具、模式和 AI 的注册表里读取，所以插件和内容包会自动出现在图鉴里，不用改图鉴代码。
- **演示**是一段短脚本（指定发牌，再加上 `apply_rule`、`use_item`、`hit`、`dealer`、`caption` 等步骤），在真正的游戏控制器上运行，所以演示永远不会和规则不一致。没有演示的条目显示大图标和文字。

## 界面

| 界面 | 内容 |
| --- | --- |
| 主页 | 当前玩家；带摘要的 Continue run / New run / Start game；升级、图鉴、对局记录、设置、退出 |
| 玩家 | 3 个存档位：游玩、新建、改名、删除（需确认） |
| 开局准备 | 模式选择、规则展示、生效的永久升级、要带的消耗品、Start run |
| 升级 | 按类型分页展示永久升级（等级点、下一级价格）和消耗品（已拥有数量） |
| 一轮结算 | 胜利或失败、代币明细、返回主页 |
| 对局记录 | 历史对局列表；详情里显示摘要 |
| 图鉴 | 按类别分页，图标 + 名称的网格；详情里有动画演示和文字 |

游戏从**主页**开始，不再提供快速游戏或游戏内美术素材图鉴。

## 开发者参考

### 数据模型

迁移 `0004_meta_progression.sql`（0003 已被混沌 AI 设置占用）在游戏数据库里新增这些表：`player`（存档位 1–3、名字、代币）、`player_upgrade`（永久升级存等级，消耗品存数量）、`run_history`、`codex_seen`（按玩家、类别、条目记录首次见到时间和次数）。平衡配置一侧新增 `meta_upgrade` 商品目录：类型、效果 ID 和 JSON 参数、价格和每级加价、最高等级、是否启用、前置升级。局内存档会关联玩家和对局 ID。

### 扩展点

| 注册表 | 怎么加内容 |
| --- | --- |
| 升级效果：`register_effect(id, fn(config, amount, params) -> RunConfig)` | 新效果要写代码；用已有效果的新升级只需加一行 `meta_upgrade` |
| 游戏模式：`register_mode(GameMode)` | 一个带覆盖项的 `GameMode` |
| 图鉴 provider：`register_codex_provider(kind, fn(config) -> list[CodexEntry])` | 插件不用做任何事：provider 会读注册表 |

### 局外 API（`chaos_blackjack/meta/`）

```python
list_slots() -> list[PlayerSlot]                 # always 3
create_player(slot, name) / rename_player(player_id, name) / delete_player(player_id)
get_player(player_id) -> Player                  # tokens, upgrades, stats
meta_shop(player_id, profile=None) -> list[UpgradeOffer]
buy_upgrade(player_id, upgrade_id) -> Player
modes(player_id=None) -> list[ModeOption]        # mode + unlocked
start_run(player_id, mode_id, *, consumables=(), profile=None, seed=None, loop_factory=None) -> RunStart
    # RunStart(run_id, mode, config, applied, controller); the controller saves into the player's run
resume_run(player_id, *, loop_factory=None) -> RunStart | None   # unfinished run with a save
pending_run(player_id) -> PendingRun | None       # saved run summary without loading it
finish_run(run_id, controller) -> RunReward      # tokens + breakdown + result; only once the run is over
abandon_run(run_id) -> None
history(player_id, limit=50) -> list[RunRecord]
codex_seen(player_id) -> dict[(kind, entry_id), times]
```

错误统一为 `MetaError`（一种 `ValueError`），附带玩家能看懂的提示。做界面时可以用 `chaos_blackjack.meta.fake.install_fake()`：它在内存数据库上运行真正的服务，并带有演示数据（1 号位"Ace"有代币、升级和三条历史对局；2 号位"Rookie"；3 号位为空）；`chaos_blackjack.meta.use_service(None)` 切回 `data/game.db`。命令行工具：`python -m chaos_blackjack.data players | history SLOT | grant SLOT TOKENS`。控制器新增 `add_listener(fn)`，每条通知都会调用它但不会消耗通知；局外层用它来生成对局摘要。

### 图鉴 API（`chaos_blackjack/codex/`）

```python
codex_kinds() -> list[CodexKind]                  # rule, mode, item, ai
codex_entries(kind=None, config=None) -> list[CodexEntry]
run_demo(script, config) -> list[DemoFrame]       # frames for the GUI to play
```

### 工作计划

| 步骤 | 负责 | 分支 |
| --- | --- | --- |
| 0. 把未合并的功能分支并入 `main`（混沌互动、带内容包和音效的牌桌界面、动画、音效） | B | `integration/main` |
| M1–M2 数据、局外逻辑、模式、效果、控制器钩子、假实现 | A | `feat/meta-core` |
| M4a 图鉴注册表、provider、演示脚本、`run_demo`（无界面、有测试） | C | `feat/codex-core` |
| M3 GUI 界面 | B | `feat/meta-gui` |
| M4b 图鉴 GUI | C | `feat/codex-gui` |
| M5 模拟器：升级、代币经济、首次定价 | A | `black-jack-sim` |

每一步的共同规则：仓库内容用英文（中文玩家指南保持同步）；测试里不产生计费调用；游戏逻辑从不读数据库；新数值放进平衡配置；"完成"意味着功能测试、全量测试和模拟器的平衡检查都通过，并且文档已更新。
