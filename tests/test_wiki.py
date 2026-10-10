"""Wiki self-tests: no game checkout needed."""

from __future__ import annotations

import copy

import pytest

from wiki import facts as F
from wiki.build import Site
from wiki.md import front_matter, render

FACTS = {
    "source": {"ref": "main", "commit": "abc1234", "date": "2026-10-10", "version": "0.2.0"},
    "settings": {"run.start_money": {"value": 100, "type": "int", "min": 2, "max": None, "description": "Start"}},
    "chaos_rules": {"fragile_bust": {"name": "Fragile Bust", "effect": "Bust at 18.", "params": {}, "flags": [],
                                     "enabled": True, "stub_weight": None, "profiles": ["easy"], "icon": None}},
    "items": {"peek": {"name": "Peek", "help": "See the next card.", "price": 10, "params": {}, "icon": None}},
    "permissions": {"easy": {"allowed_rules": ["fragile_bust"], "allowed_items": ["peek"], "chaos_budget": 5,
                             "charge_per_effect": 1, "max_actions_per_turn": 1, "max_active_effects": 1}},
    "prompts": ["chaotic"],
    "assets": {},
    "agent": {"obs_schema": 2, "commands": {"bet": "place a bet"}, "actions": {"hit": "one more card"},
              "error_codes": ["usage"]},
    "transcript": {"seed": 7, "steps": []},
    "changelog": [],
}


def test_lookup_handles_dotted_keys():
    assert F.lookup(FACTS, "settings.run.start_money.value") == 100
    assert F.lookup(FACTS, "items.peek.price") == 10
    with pytest.raises(KeyError):
        F.lookup(FACTS, "items.nope.price")


def test_markdown_basics():
    out, heads = render("## Hi *there*\n\n- a `x<y`\n- b\n\n| A | B |\n| - | - |\n| 1 | **2** |\n")
    assert '<h2 id="hi-there">Hi <em>there</em></h2>' in out
    assert "<code>x&lt;y</code>" in out
    assert "<td><strong>2</strong></td>" in out
    assert heads == [(2, "hi-there", "Hi there")]
    meta, body = front_matter("---\ntitle: X\n---\nbody")
    assert meta == {"title": "X"} and body == "body"


def test_placeholders_resolve_and_report_unknown():
    errors: list[str] = []
    site = Site(FACTS, "en", errors)
    html = site.expand("Start with {{ fact: settings.run.start_money.value }}. {{ link: items.peek }}\n\n"
                       "{{ table: prices }}\n\n{{ fact: items.nope }}", "test.md")
    assert "Start with 100." in html
    assert 'href="item-peek.html"' in html
    assert "<table" in html
    assert errors == ["test.md: unknown fact `items.nope`"]


def test_diff_classifies_changes():
    new = copy.deepcopy(FACTS)
    new["items"]["peek"]["price"] = 12
    new["items"]["lucky"] = {"name": "Lucky", "help": "?", "price": 5, "params": {}, "icon": None}
    del new["chaos_rules"]["fragile_bust"]
    kinds = {(k, w) for k, w, _ in F.diff(FACTS, new)}
    assert ("auto", "items.peek.price") in kinds
    assert ("new", "items.lucky") in kinds
    assert ("removed", "chaos_rules.fragile_bust") in kinds
    # Nested changes under a removed id are not repeated as `auto`.
    assert not any(k == "auto" and w.startswith("chaos_rules.fragile_bust") for k, w in kinds)


def test_stale_translation_falls_back_to_english(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "CONTENT", tmp_path)
    (tmp_path / "zh" / "items").mkdir(parents=True)
    p = tmp_path / "zh" / "items" / "peek.md"
    p.write_text("---\nname: 偷看\nhelp: 看下一张\nhelp_en: See the next card.\n---\n", encoding="utf-8")
    site = Site(FACTS, "zh", [])
    assert site.blurb("items", "peek") == ("看下一张", True)
    p.write_text("---\nname: 偷看\nhelp: 看下一张\nhelp_en: Old English text.\n---\n", encoding="utf-8")
    assert site.blurb("items", "peek") == ("See the next card.", False)
    assert site.name("items", "peek") == "偷看"


def test_changed_design_doc_is_stale():
    doc = {"path": "docs/design/X.md", "ref": "feat/x", "commit": "aaa", "date": "2026-10-10",
           "blob": "111", "title": "X", "status": "plan", "on_main": False}
    old = {**FACTS, "design_docs": {"x": doc}}
    new = {**FACTS, "design_docs": {"x": {**doc, "blob": "222", "commit": "bbb"}}}
    assert [(k, w) for k, w, _ in F.diff(old, new)] == [("stale", "design_docs.x")]
    merged = {**FACTS, "design_docs": {"x": {**doc, "ref": "main", "on_main": True}}}
    assert [(k, w) for k, w, _ in F.diff(old, merged)] == [("auto", "design_docs.x")]


def test_design_status_takes_the_bold_part():
    from wiki.design import _status, slug

    assert _status("Status: **agreed plan**, 2026-10-10. Shared contract") == "agreed plan"
    assert _status("Status: draft. More text") == "draft"
    assert slug("docs/design/META_PROGRESSION.md") == "meta-progression"
