---
title: 玩法
---
## Pygame 窗口

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

| 阶段 | 鼠标 | 键盘 |
| --- | --- | --- |
| 下注 | 左键点筹码加注，右键减注；Clear / Max；Shop | ↑ / ↓ ±1，Enter 发牌，B 打开商店（1–3 购买） |
| 你的回合 | Hit / Stand / Double / Surrender 按钮 | H / S / D / R |
| 一局结束 | Next Round | Enter |
| 混沌模式 | 点击混沌 AI 头像[要建议](chaos-ai.html#向混沌-ai-要建议) | — |
| 任何时候 | — | Esc 回主菜单（会先确认），F11 全屏，M 静音，+ / − 调音量，F5 重新加载美术和音效 |

游戏打开后进入**主页**。点 **Start game** 创建有名字的玩家；**Players** 页面可切换、改名或删除存档。在 **New run** 中选 Classic 或 Chaos，查看永久升级并勾选消耗品。只有点 **Start run** 才消耗所选道具；升级 Bag Space 前最多带 {{ fact: settings.meta.bring_kinds.value }} 种。

主页提供 **Continue run**、**Upgrades**、**Collection** 和 **Run history**。游戏自动保存；牌桌按 Escape 离开时会确认放弃，本轮不发代币。胜利获得 {{ fact: settings.meta.win_tokens.value }} 代币，混沌模式额外加 {{ fact: settings.meta.chaos_win_bonus.value }}；失败的安慰奖上限为 {{ fact: settings.meta.loss_cap.value }}。奖励公式和升级目录见[局外成长](design-meta-progression.html)。

**Collection** 按规则、道具、模式和 AI 展示实时说明与离线演示。空格暂停、R 重播、左右键逐帧查看，演示不影响玩家进度。美术是可选的，每张图都有程序绘制的占位图（见[美术图鉴](gallery.html)）。

## 浏览器版

需要登录的浏览器版通过 WebAssembly 运行原来的 Pygame 界面，包含局外成长、升级和账号存档。注册需要 16 位数字邀请码。访问和部署说明见游戏的[浏览器兼容性与构建文档](https://github.com/fghhn13/Chaos_Blackjack/blob/main/browser/README.md)和[部署指南](https://github.com/fghhn13/Chaos_Blackjack/blob/main/deploy/README.md)。

## 文字命令行

```bash
python cli/main.py                 # 菜单：新游戏、读档、退出
python cli/main.py --enable-chaos
python cli/main.py demo            # 自动打一局
```

文字命令行还是最初的要牌 / 停牌玩法；加倍、投降和商店只在窗口版和 agent 接口里有。

## 接入真实大模型（可选）

默认情况下混沌 AI 是离线替身：不联网、不花钱。可以在 git 忽略的 `.env` 文件里开启真实模型，详见游戏 README 的 "Real LLM" 一节。真实请求会计费。
