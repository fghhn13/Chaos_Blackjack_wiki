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
    },
}

# (slug, nav group). Page text lives in content/<lang>/<slug>.md.
PAGES: list[tuple[str, str]] = [
    ("index", "g_start"), ("rules", "g_start"), ("shop", "g_start"), ("play", "g_start"), ("agents", "g_start"),
    ("chaos", "g_catalog"), ("items", "g_catalog"),
    ("chaos-ai", "g_inside"), ("settings", "g_inside"), ("architecture", "g_inside"),
    ("gallery", "g_ref"), ("changelog", "g_ref"), ("glossary", "g_ref"),
]
