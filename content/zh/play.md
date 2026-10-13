---
title: 玩法
---
## 桌面版

```bash
pip install -e ".[gui]"
python -m chaos_blackjack.gui
```

Windows 也可运行 `start_game.bat`。点 **Start game** 创建玩家，再在 **New run** 选择[经典牌桌](table-normal.html)、[扑克头的牌桌](table-chaos.html)或[J-54 *实验性](table-j54.html)。检查目标、下注范围、规则、荷官和赔率，再勾选开局物品；只有点 **Start run** 才消耗物品。

新一轮先播放荷官台词，Enter／点击翻页，Escape 跳过。**Continue run** 恢复检查点，不重复播放开场。

| 阶段 | 鼠标 | 键盘 |
| --- | --- | --- |
| 下注 | 左键筹码加注、右键减注；Clear / Max；局内 Shop | 上下键微调，Enter 发牌，B 打开商店 |
| 你的回合 | 要牌／停牌／加倍／投降；背包 | H / S / D / R；I 打开 Bag；Tab 打开局内面板 |
| 回合结束 | Next Round | Enter |
| 扑克头的牌桌 | 点荷官头像问建议 | Enter 关闭回复 |
| 任何时候 | Settings | Escape 确认离开；F11 全屏；M 静音；+ / − 音量；F5 重新载入美术和音效 |

主页 **Shop** 花代币买升级、装扮和开局物品；**局内 Shop** 花本轮筹码。详见[玩家成长](progression.html)。点击玩家信息打开[个人资料](profile.html)，**Switch player** 管理槽位。

**Collection** 按经典牌桌和荷官系列分组。经典区展示基础牌桌和通用道具；扑克头区介绍角色、规则池和专属道具。Tab 切换，滚轮或 Page Up / Page Down 滚动。规则和道具详情可播放固定发牌的离线演示：空格暂停、R 重播、左右键逐帧查看，不花代币、不改变进度。

## 浏览器与手机

需要登录的浏览器版通过 WebAssembly 运行同一套 Pygame 游戏，支持账号存档。注册需要 16 位数字邀请码。首次加载可能较慢，提示会区分下载与启动阶段；出现提示时点击 **Start game** 启动并启用音效，iOS Safari 也使用这个触摸入口。允许自动播放音效的浏览器可能跳过提示。触屏设备新建或改名使用支持输入法组合输入的原生文本框，Save／完成按钮确认，Cancel 保留原名。

访问和部署说明见[浏览器兼容性与构建](https://github.com/fghhn13/Chaos_Blackjack/blob/main/browser/README.md)和[部署指南](https://github.com/fghhn13/Chaos_Blackjack/blob/main/deploy/README.md)。

触屏设备可上下滑动列表、参考说明和历史详情。短按选择，拖动后松手不会误选条目。游戏区域内的手势滚动游戏内容，外围网页仍可正常滚动。

## 文字命令行与 Agent

```bash
python cli/main.py
python cli/main.py --enable-chaos
python -m chaos_blackjack.agent new --seed 7 --chaos
```

文字命令行保留原来的要牌／停牌循环。Agent 支持控制器动作，但不应用玩家的局外升级；`--chaos` 保留旧玩法兼容，`--mode chaos` 启动当前构筑桌，详见[Agent 玩家](agents.html)。

默认混沌后端离线。按游戏配置接入真实模型时，请求会计费；具体设置见游戏 README。

扑克头新局先选核心；永久商品、消耗品与金融产品各有阶段。侧栏道具槽支持 1～9，Tab 打开局内面板，左右键换标签，Escape 或 Tab 关闭。详见[构筑指南](poker-head-builds.html)。
