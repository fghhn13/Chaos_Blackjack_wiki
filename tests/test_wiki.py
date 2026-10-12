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


def test_sim_rule_variants_map_to_game_rules(tmp_path):
    from wiki.sim import _dict_keys, game_rule

    rules = {"modify_card_value", "tiebreaker_shift", "great_crash"}
    assert game_rule("modify_card_value-1", rules) == "modify_card_value"
    assert game_rule("tiebreaker_dealer", rules) == "tiebreaker_shift"
    assert game_rule("great_crash", rules) == "great_crash"
    assert game_rule("none", rules) is None
    src = tmp_path / "bots.py"
    src.write_text('X: dict[str, int] = {"a": 1, "b": 2}\nY = {"c": 3}\n', encoding="utf-8")
    assert _dict_keys(src, "X") == ["a", "b"] and _dict_keys(src, "Y") == ["c"]


def test_out_of_band_is_reported():
    sim = {"source": {"commit": "s1"}, "measured_on": "g1",
           "measured": {"bands": [{"metric": "EV", "value": "+0.5", "band": "[0, 0.1]", "ok": "no"}]}}
    entries = F.diff({**FACTS, "sim": {}}, {**FACTS, "sim": sim})
    assert any(k == "auto" and "OUT OF BAND" in d for k, _, d in entries)


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_percentage_prices_on_all_item_surfaces(lang):
    from wiki.i18n import UI

    expected = UI[lang]["bankroll_price"].format(price=4)
    facts = copy.deepcopy(FACTS)
    facts["items"]["peek"].update(price=4, price_mode="bankroll_pct")
    site = Site(facts, lang, [])
    for output in (site.t_prices(), site.t_item_cards(), site.entity("items", "peek")):
        assert expected in output
    facts["items"]["peek"].pop("price_mode")
    assert f"4 {site.t['chips']}" in site.t_prices()
    facts["items"]["peek"]["price"] = None
    assert site.t["not_sold"] in site.t_prices()


def test_sim_measure_uses_requested_game_over_inherited_import(tmp_path, monkeypatch):
    from wiki.sim import measure

    game, decoy, simulator = (tmp_path / name for name in ("game", "decoy", "simulator"))
    for root, value in ((game, "requested"), (decoy, "wrong")):
        package = root / "chaos_blackjack"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(f"VALUE = {value!r}\n", encoding="utf-8")
    package = simulator / "bjsim"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "__main__.py").write_text(
        "import json, sys\nfrom pathlib import Path\nimport chaos_blackjack\n"
        "output = Path(sys.argv[sys.argv.index('--out') + 1])\n"
        "output.write_text(json.dumps({'tables': [{'title': 'fixture', "
        "'rows': [['fixture', chaos_blackjack.VALUE, 'band', 'yes']]}]}), encoding='utf-8')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTHONPATH", str(decoy))
    results = measure(simulator, game, jobs=1)
    assert results["bands"][0]["value"] == "requested"
    assert results["edge"][0]["ev"] == "requested"
    assert results["items"][0]["ev"] == "requested"


def test_table_membership_and_graph_references():
    from wiki.check import catalog_references

    facts = copy.deepcopy(FACTS)
    facts.update(series={"core": {}, "host": {}}, dealers={"host": {"name": "Host", "tables": ["normal", "chaos"]}},
                 tables={"normal": {"name": "Classic", "host": "host", "series": "core", "rules": [], "items": ["peek"]},
                         "chaos": {"name": "Host table", "host": "host", "series": "host",
                                   "rules": ["fragile_bust"], "items": ["peek"]}})
    site = Site(facts, "en", [])
    assert 'table-chaos.html' in site.table_links("chaos_rules", "fragile_bust")
    assert 'table-normal.html' not in site.table_links("chaos_rules", "fragile_bust")
    assert 'table-normal.html' in site.table_links("items", "peek")
    assert catalog_references(facts) == []
    facts["tables"]["chaos"]["items"].append("removed_item")
    assert catalog_references(facts) == ["tables.chaos.items: unknown items id `removed_item`"]


def test_author_draft_banner_without_game_entity(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "CONTENT", tmp_path)
    (tmp_path / "en").mkdir()
    (tmp_path / "en/table-j54.md").write_text(
        "---\ntitle: J-54\nstatus: draft\nsource: user\n---\nA proposed deck.\n", encoding="utf-8")
    output = Site(FACTS, "en", []).page("table-j54")
    assert "Design draft" in output and "not implemented in game main" in output
    assert '<span class="pill ok">' not in output
    assert "tables" not in FACTS


def test_multiple_cosmetic_rewards_and_hidden_spoilers():
    facts = {**FACTS,
             "cosmetics": {"deck": {"name": "Reward deck"}, "table": {"name": "Reward table"}},
             "achievements": {
                 "win": {"name": "Table win", "description": "Win.", "goal": 1, "scope": "total",
                         "tokens": 4, "cosmetics": ["deck", "table"], "hidden": False},
                 "secret": {"name": "Secret", "description": "Hidden goal.", "goal": 3, "scope": "run",
                            "tokens": 0, "cosmetics": [], "hidden": True}}}
    output = Site(facts, "en", []).t_achievements()
    visible, hidden = output.split("<details>", 1)
    assert "Reward deck" in visible and "Reward table" in visible
    assert "Secret" not in visible and "Secret" in hidden
