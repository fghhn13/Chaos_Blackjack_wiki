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


def test_design_main_status_compares_document_contents(tmp_path, monkeypatch):
    from wiki import design

    path = "docs/design/X.md"
    shared = "docs/design/SHARED.md"

    def git(repo, *args):
        if args[0] == "for-each-ref":
            return "main\nfeat/x"
        if args[:3] == ("ls-tree", "-r", "--name-only"):
            return f"{path}\n{shared}"
        if args[0] == "ls-tree":
            return f"100644 blob {'a' * 40}\t{path}\n100644 blob {'c' * 40}\t{shared}"
        if args[0] == "log":
            return "1\tm1\t2026-10-10" if args[3] == "main" else "2\tf1\t2026-10-11"
        if args[0] == "show":
            return "# Example\nStatus: draft."
        if args[0] == "rev-parse":
            return "c" * 40 if args[1].endswith(shared) else ("a" if args[1].startswith("main:") else "b") * 40
        raise AssertionError(args)

    monkeypatch.setattr(design, "_git", git)
    docs = design.scan(tmp_path)
    assert docs["x"]["ref"] == "feat/x" and docs["x"]["on_main"] is False
    assert docs["shared"]["ref"] == "feat/x" and docs["shared"]["on_main"] is True


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
    (tmp_path / "en/proposal.md").write_text(
        "---\ntitle: J-54\nstatus: draft\nsource: user\n---\nA proposed deck.\n", encoding="utf-8")
    output = Site(FACTS, "en", []).page("proposal")
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


def test_environment_membership_has_its_own_catalog():
    from wiki.check import catalog_references

    facts = copy.deepcopy(FACTS)
    facts.update(environment_rules={"hidden": {"name": "Hidden", "effect": "Hide a card."}},
                 tables={"chaos": {"rules": [], "items": [], "environment_rules": ["hidden"]}})
    site = Site(facts, "en", [])
    assert 'table-chaos.html' in site.table_links("environment_rules", "hidden")
    assert 'environment-hidden.html' in site.expand_inline("{{ link: environment_rules.hidden }}", "test")
    assert catalog_references(facts) == []
    facts["tables"]["chaos"]["environment_rules"].append("missing")
    assert catalog_references(facts) == ["tables.chaos.environment_rules: unknown environment_rules id `missing`"]


def test_protocol_goal_and_finance_do_not_render_as_cash_price():
    facts = {**FACTS, "tables": {"j54": {"start_money": 100, "target_money": 300,
                                            "goal_text": "Draw the Joker or reach 250 chips"}}}
    site = Site(facts, "en", [])
    assert site.table_goal("j54") == "Draw the Joker or reach 250 chips"
    assert site.item_price({"kind": "core", "price": None}) == "Opening choice"
    assert site.item_price({"kind": "finance", "price": 40, "params": {"advance": 40, "repay": 50}}) == "Borrow 40 / repay 50"


def test_historical_measurements_are_not_current_item_gain():
    facts = copy.deepcopy(FACTS)
    facts["sim"] = {"measured_on": "old-version", "measured": {"items": [{"item": "peek", "ev": "+900%", "se": "0"}]}}
    assert "+900%" not in Site(facts, "en", []).entity("items", "peek")


def test_experimental_state_comes_from_facts():
    facts = {**FACTS,
             "tables": {"lab": {"experimental": True}, "classic": {"experimental": False}, "side": {}},
             "dealers": {"robot": {"tables": ["lab"]}, "host": {"tables": ["classic", "lab"]}}}
    site = Site(facts, "en", [])
    assert site.experimental("tables", "lab") and not site.experimental("tables", "side")
    assert site.experimental("dealers", "robot") and not site.experimental("dealers", "host")
    assert site.state("dealers", "robot") == "*Experimental"


def test_page_layout_rejects_shadowing_and_orphan_pages(tmp_path, monkeypatch):
    from wiki import check

    monkeypatch.setattr(F, "CONTENT", tmp_path)
    for lang in F.LANGS:
        (tmp_path / lang).mkdir()
    (tmp_path / "en/guides").mkdir()
    (tmp_path / "en/stray.md").write_text("x", encoding="utf-8")
    (tmp_path / "en/guides/lost.md").write_text("x", encoding="utf-8")
    (tmp_path / "en/guides/kept.md").write_text("x", encoding="utf-8")
    (tmp_path / "en/items").mkdir()
    (tmp_path / "en/items/peek.md").write_text("x", encoding="utf-8")
    monkeypatch.setattr(check, "PAGES", [("growth/item-peek", "g_ref"), ("guides/kept", "g_guides"),
                                         ("dev/kept", "g_inside")])
    monkeypatch.setattr(check, "REDIRECTS", {"kept": "x.html"})
    errors = check.page_layout(FACTS)
    assert any("`growth/item-peek` publishes item-peek.html, already the generated page" in e for e in errors)
    assert any("`guides/kept` publishes kept.html, already the page `dev/kept`" in e for e in errors)
    assert any("redirect `kept` would overwrite" in e for e in errors)
    assert any("en/stray.md: not in the nav" in e for e in errors)
    assert any("guides/lost.md: not in the nav" in e for e in errors)
    assert not any(("kept.md" in e or "peek.md" in e) and "not in the nav" in e for e in errors)


def test_pages_in_folders_publish_flat_and_redirects_resolve(tmp_path, monkeypatch):
    from wiki import build as B

    monkeypatch.setattr(F, "CONTENT", tmp_path)
    (tmp_path / "en/guides").mkdir(parents=True)
    (tmp_path / "en/guides/tips.md").write_text("---\ntitle: Tips\n---\nHello.\n", encoding="utf-8")
    monkeypatch.setattr(B, "PAGES", [("guides/tips", "g_guides")])
    output = Site(FACTS, "en", []).page("guides/tips")
    assert '<a href="tips.html" aria-current="page">Tips</a>' in output
    assert 'href="../zh/tips.html"' in output
    assert 'url=environment.html' in B._redirect("environment.html", "Moved to")


def test_catalog_cards_group_by_table_with_unused_last():
    facts = copy.deepcopy(FACTS)
    facts["chaos_rules"]["old_rule"] = {**facts["chaos_rules"]["fragile_bust"], "name": "Old Rule"}
    facts["items"].update(core={"name": "Core", "help": "c", "price": None, "kind": "core", "icon": None},
                          bond={"name": "Bond", "help": "b", "price": 5, "kind": "finance", "icon": None})
    facts["tables"] = {"lab": {"name": "Lab", "series": "lab", "experimental": True, "rules": ["fragile_bust"], "items": []},
                       "home": {"name": "Home", "series": "core", "rules": [], "items": ["peek"]},
                       "ph": {"name": "PH", "series": "ph", "rules": [], "items": ["bond"], "products": ["core", "bond"]}}
    site = Site(facts, "en", [])
    rules = site.t_chaos_cards()
    assert rules.index('id="pool-lab"') < rules.index('id="pool-unused"') < rules.index("rule-old_rule.html")
    assert "*Experimental" in rules and 'id="pool-home"' not in rules
    items = site.t_item_cards()
    assert items.index('id="pool-home"') < items.index('id="pool-ph"')
    assert items.index('id="pool-ph-core"') < items.index('id="pool-ph-finance"') and "pool-unused" not in items
    assert site.table_links("items", "core") == '<a href="table-ph.html">PH</a>'
    site.expand("## Intro\n\n{{ table: item_cards }}\n", "test")
    assert [h[1] for h in site._heads][:3] == ["intro", "pool-home", "pool-ph"]


UI_FACTS = {**FACTS,
            "items": {"peek": {**FACTS["items"]["peek"]},
                      "ph_core": {"name": "Fresh Hand", "help": "Redeal.", "price": None, "kind": "core", "icon": None},
                      "ph_buff": {"name": "Court Discount", "help": "Faces count low.", "price": 40, "kind": "permanent",
                                  "icon": None,
                                  "details": "Even royalty can offer a concession.\n\nEffect\nFaces count low.\n\n"
                                             "Timing\nWhile equipped\n\nLimits\nOne copy.\nNo refund.\n\n"
                                             "Related effects\nFresh Hand, Unknown Thing"}},
            "tables": {"home": {"name": "Home", "series": "core", "rules": [], "items": ["peek"]},
                       "ph": {"name": "PH", "series": "ph", "rules": [], "items": ["ph_buff"],
                              "products": ["ph_buff", "ph_core"]}}}


def test_entity_order_follows_hub_grouping():
    site = Site(UI_FACTS, "en", [])
    assert site.entity_order("items") == ["peek", "ph_core", "ph_buff"]  # table order, then core before permanent
    assert site.entity_order("tables") == ["home", "ph"]


def test_details_become_sections_with_related_links():
    site = Site(UI_FACTS, "en", [])
    tagline, block = site.details(UI_FACTS["items"]["ph_buff"])
    assert tagline == "Even royalty can offer a concession."
    assert "<dt>Effect</dt>" not in block  # same as the lead
    assert "<dt>Limits</dt><dd>One copy.<br>No refund.</dd>" in block
    assert '<a href="item-ph_core.html">Fresh Hand</a>, Unknown Thing' in block
    _, zh = Site(UI_FACTS, "zh", []).details(UI_FACTS["items"]["ph_buff"])
    assert "<dt>效果</dt>" in zh and "英文原文" in zh
    assert site.details(UI_FACTS["items"]["peek"]) == ("", "")


def test_entity_page_has_crumbs_pager_and_folded_nav():
    page = Site(UI_FACTS, "en", []).entity("items", "ph_core")
    assert '<a href="items.html#pool-ph">PH</a>' in page
    assert 'rel="prev" href="item-peek.html"' in page and 'rel="next" href="item-ph_buff.html"' in page
    assert '<details class="subs" open><summary><a href="items.html" aria-current="page">' in page
    assert '<details class="subs"><summary><a href="chaos.html"' in page


def test_search_index_lists_pages_with_keywords():
    site = Site(UI_FACTS, "zh", [], "abc")
    page = site.entity("items", "ph_buff")
    assert 'href="../style.css?v=abc"' in page and 'data-index="search.js?v=abc"' in page
    script = site.search_js()
    assert script.startswith("window.WIKI_SEARCH=[") and script.endswith("];\n")
    import json
    entry = json.loads(script[len("window.WIKI_SEARCH="):-2])[0]
    assert entry["u"] == "item-ph_buff.html" and entry["k"] == "道具"
    assert "Court Discount" in entry["w"] and "ph_buff" in entry["w"]
