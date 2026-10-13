"""Interface strings for the site chrome and generated tables."""

from __future__ import annotations

UI: dict[str, dict[str, str]] = {
    "en": {
        "lang_name": "English", "wiki": "Wiki", "filter": "Filter pages…", "on_this_page": "On this page",
        "menu": "Menu",
        "g_start": "Start", "g_catalog": "Catalog", "g_inside": "Under the hood", "g_ref": "Reference",
        "stamp": "Describes <code>{ref}</code> @ <code>{commit}</code> ({date}) · game v{version}",
        "untranslated": "This text has not been translated yet; showing English.",
        "no_notes": "No notes yet. The card above is generated from the game.",
        "yes": "yes", "no": "no",
        "id": "Id", "name": "Name", "effect": "Effect (default parameters)", "help": "Effect",
        "price": "Price", "params": "Parameters", "flags": "Flags", "profiles": "Allowed by",
        "bankroll_price": "{price}% of bankroll at restock",
        "enabled": "Enabled", "stub_weight": "Offline AI weight", "not_sold": "not sold",
        "key": "Key", "value": "Default", "type": "Type", "range": "Range", "description": "Description",
        "profile": "Profile", "budget": "Chaos budget", "per_effect": "Cost per effect",
        "actions_turn": "Actions per turn", "active_effects": "Active effects", "allowed_rules": "Rules",
        "allowed_items": "Items", "none": "none",
        "command": "Command", "action": "Action", "code": "Error code", "meaning": "Meaning",
        "category": "Category", "size": "Size", "art": "Art", "final": "final", "placeholder": "placeholder",
        "date": "Date", "commit": "Commit", "change": "Change",
        "step": "Step", "you_send": "You send", "events": "Events", "result": "Table after",
        "chips": "chips", "all_rules": "All chaos rules", "all_items": "All items", "back": "Back",
        "g_design": "Design", "all_design": "All design docs", "state": "State", "doc_status": "Doc status",
        "source": "Source", "design_planned": "planned", "design_on_main": "in main",
        "design_banner": "<strong>{state}</strong> · design doc <code>{path}</code> on <code>{ref}</code> @ "
                         "<code>{commit}</code> ({date}) · status: {status}. Plans can change before they ship; "
                         "current player guides describe the version named in their footer.",
        "design_stale": "The design doc has changed since this page was written; it may be out of date.",
        "design_no_summary": "No wiki summary yet. Read the source design doc in the game repository.",
        "sim_rule_ev": "Player EV (simulator)", "sim_item_gain": "EV gain per use (simulator)",
        "sim_more": "all results", "sim_variant": "Simulated rule", "sim_ev": "Player EV / bet", "sim_se": "Std. error",
        "sim_gain": "EV gain / bet", "sim_no_rule": "no chaos rule", "sim_metric": "Metric", "sim_size": "Sample",
        "sim_value": "Measured", "sim_band": "Allowed band", "sim_in_band": "In band", "sim_rounds": "rounds",
        "sim_runs": "runs", "sim_usage": "Usage", "sim_option": "Option", "sim_values": "Values",
        "sim_meta": "<code>{args}</code> · seed {seed} · balance <code>{balance}</code> · game <code>{game}</code> · "
                    "simulator <code>{sim}</code> · {title}",
        "sim_stale": "These results were measured on an older game commit than the rest of this wiki.",
        "sim_missing": "No simulator results yet: run <code>python -m wiki sync</code> with the simulator present.",
    },
    "zh": {
        "lang_name": "中文", "wiki": "百科", "filter": "筛选页面…", "on_this_page": "本页目录",
        "menu": "菜单",
        "g_start": "入门", "g_catalog": "图鉴", "g_inside": "机制", "g_ref": "参考",
        "stamp": "对应 <code>{ref}</code> @ <code>{commit}</code>（{date}）· 游戏 v{version}",
        "untranslated": "本段尚未翻译，暂时显示英文。",
        "no_notes": "暂无说明。上方卡片由游戏数据自动生成。",
        "yes": "是", "no": "否",
        "id": "ID", "name": "名称", "effect": "效果（默认参数）", "help": "效果",
        "price": "价格", "params": "参数", "flags": "标记", "profiles": "允许的难度",
        "bankroll_price": "补货时资金的 {price}%",
        "enabled": "启用", "stub_weight": "离线 AI 权重", "not_sold": "不出售",
        "key": "键", "value": "默认值", "type": "类型", "range": "范围", "description": "说明",
        "profile": "难度档", "budget": "混沌预算", "per_effect": "每次效果消耗",
        "actions_turn": "每回合动作数", "active_effects": "同时生效数", "allowed_rules": "规则",
        "allowed_items": "道具", "none": "无",
        "command": "命令", "action": "动作", "code": "错误码", "meaning": "含义",
        "category": "类别", "size": "尺寸", "art": "美术", "final": "正式", "placeholder": "占位",
        "date": "日期", "commit": "提交", "change": "变更",
        "step": "步", "you_send": "发送", "events": "事件", "result": "之后的牌桌",
        "chips": "筹码", "all_rules": "全部混沌规则", "all_items": "全部道具", "back": "返回",
        "g_design": "设计", "all_design": "全部设计文档", "state": "状态", "doc_status": "文档状态",
        "source": "来源", "design_planned": "计划中", "design_on_main": "已进 main",
        "design_banner": "<strong>{state}</strong> · 设计文档 <code>{path}</code>，位于 <code>{ref}</code> @ "
                         "<code>{commit}</code>（{date}）· 状态：{status}。计划在上线前仍可能变化；"
                         "当前玩法页面以页脚注明的版本为准。",
        "design_stale": "设计文档在本页写成之后有过改动，本页可能已过时。",
        "design_no_summary": "还没有百科摘要，请阅读游戏仓库里的原始设计文档。",
        "sim_rule_ev": "玩家期望值（模拟器）", "sim_item_gain": "每次使用的期望值增益（模拟器）",
        "sim_more": "全部结果", "sim_variant": "模拟的规则", "sim_ev": "玩家期望值 / 下注", "sim_se": "标准误",
        "sim_gain": "期望值增益 / 下注", "sim_no_rule": "无混沌规则", "sim_metric": "指标", "sim_size": "样本",
        "sim_value": "实测值", "sim_band": "允许区间", "sim_in_band": "在区间内", "sim_rounds": "局",
        "sim_runs": "轮", "sim_usage": "用法", "sim_option": "选项", "sim_values": "可选值",
        "sim_meta": "<code>{args}</code> · 种子 {seed} · 平衡配置 <code>{balance}</code> · 游戏 <code>{game}</code> · "
                    "模拟器 <code>{sim}</code> · {title}",
        "sim_stale": "这些结果测量自比本百科其余部分更旧的游戏提交。",
        "sim_missing": "还没有模拟器结果：在模拟器存在时运行 <code>python -m wiki sync</code>。",
    },
}

UI["en"].update({
    "rounds": "Rounds", "action_chance": "Action chance", "rule_slots": "Rule slots", "pressure_budget": "Pressure budget",
    "released": "Current version", "experimental": "Experimental", "core": "Core", "item": "Consumables",
    "finance": "Financial products", "contract": "Contract", "timing": "Timing",
    "classic_items": "Classic items", "core_choice": "Opening choice", "loan_price": "Borrow {advance} / repay {repay}",
    "g_tables": "Tables and dealers", "g_growth": "Progression and collection", "g_guides": "Guides",
    "moved": "This page has moved to",
    "host": "Dealer", "tables": "Tables", "goal": "Goal", "rule_count": "Rules", "item_count": "Items",
    "released": "Current version", "rules": "Chaos rules", "items": "Items", "bet_limits": "Bet range",
    "bankroll": "bankroll", "payout": "Natural payout", "tokens": "tokens", "token_cost": "Token cost",
    "max_level": "Max level / copies", "kind": "Kind", "permanent": "Permanent", "consumable": "Starter item",
    "all_tables": "All tables", "deck": "Deck", "table": "Table", "chips": "chips", "avatar": "Avatar",
    "slot": "Slot", "obtain": "How to obtain", "default_owned": "Owned by default",
    "condition": "Condition", "scope": "Scope", "total": "Lifetime", "run": "Single run", "reward": "Reward",
    "spoilers": "Hidden content — reveal spoilers",
    "editorial_draft": "Design draft · supplied by the author for this wiki · not implemented in game main. "
                       "Mechanics and numbers are provisional proposals, with no simulator-validated balance yet.",
})
UI["zh"].update({
    "rounds": "回合", "action_chance": "行动概率", "rule_slots": "同时规则上限", "pressure_budget": "总压力预算",
    "released": "当前版本", "experimental": "实验性", "core": "核心", "item": "消耗与管理道具",
    "finance": "金融产品", "contract": "契约", "timing": "使用阶段",
    "classic_items": "经典道具", "core_choice": "开局选择", "loan_price": "借入 {advance}／偿还 {repay}",
    "g_tables": "牌桌与荷官", "g_growth": "成长与收藏", "g_guides": "攻略",
    "moved": "本页已移至",
    "host": "荷官", "tables": "适用牌桌", "goal": "目标", "rule_count": "规则数", "item_count": "道具数",
    "released": "当前版本", "rules": "混沌规则", "items": "道具", "bet_limits": "下注范围",
    "bankroll": "当前资金", "payout": "天生 21 点赔率", "tokens": "代币", "token_cost": "代币价格",
    "max_level": "最高等级／持有上限", "kind": "类型", "permanent": "永久升级", "consumable": "开局物品",
    "all_tables": "所有牌桌", "deck": "牌组", "table": "牌桌", "avatar": "头像",
    "slot": "装扮部位", "obtain": "获取方式", "default_owned": "默认拥有",
    "condition": "条件", "scope": "统计范围", "total": "累计", "run": "单轮", "reward": "奖励",
    "spoilers": "隐藏内容 — 展开查看剧透",
    "editorial_draft": "设计草案 · 作者提供给本 Wiki · 尚未在游戏 main 实现。"
                       "文中机制与数值均为暂定设计，尚无经过模拟器验证的平衡结果。",
})

# (path, nav group), in nav order. Page text lives in content/<lang>/<path>.md; the folder
# only groups the sources (guides/, growth/, dev/, reference/), every page is published
# flat as site/<lang>/<last path segment>.html so links and bookmarks never move.
# Catalog hubs stay top-level next to their entity folders. Entity pages (one per table,
# dealer, rule, item...) are generated from facts and listed under their hub (NAV_SUBS in
# build.py); never add them here.
PAGES: list[tuple[str, str]] = [
    ("index", "g_start"), ("play", "g_start"), ("rules", "g_start"),
    ("tables", "g_tables"), ("dealers", "g_tables"),
    ("environment", "g_catalog"), ("chaos", "g_catalog"), ("items", "g_catalog"),
    ("guides/poker-head-builds", "g_guides"),
    ("growth/progression", "g_growth"), ("growth/profile", "g_growth"), ("growth/shop", "g_growth"),
    ("growth/cosmetics", "g_growth"), ("growth/achievements", "g_growth"),
    ("dev/agents", "g_inside"), ("dev/chaos-ai", "g_inside"), ("dev/settings", "g_inside"),
    ("dev/balance", "g_inside"), ("dev/simulator", "g_inside"), ("dev/architecture", "g_inside"),
    ("design", "g_design"),
    ("reference/gallery", "g_ref"), ("reference/changelog", "g_ref"), ("reference/glossary", "g_ref"),
]

# Retired page slug -> where it lives now. Each gets a small redirect page so old links keep working.
REDIRECTS: dict[str, str] = {
    "poker-head-environment-plan": "environment.html",
}


def page_slug(path: str) -> str:
    """Published name of a page: its last path segment."""
    return path.rsplit("/", 1)[-1]
