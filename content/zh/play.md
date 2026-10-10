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

在主菜单切换 **Chaos Mode**。美术是可选的：每张图都有程序绘制的占位图（见[美术图鉴](gallery.html)）。

## 文字命令行

```bash
python cli/main.py                 # 菜单：新游戏、读档、退出
python cli/main.py --enable-chaos
python cli/main.py demo            # 自动打一局
```

文字命令行还是最初的要牌 / 停牌玩法；加倍、投降和商店只在窗口版和 agent 接口里有。

## 接入真实大模型（可选）

默认情况下混沌 AI 是离线替身：不联网、不花钱。可以在 git 忽略的 `.env` 文件里开启真实模型，详见游戏 README 的 "Real LLM" 一节。真实请求会计费。
