"""facts/facts.json + content/ -> site/ (static HTML, opens from file://)."""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any, Callable

from wiki import facts as F
from wiki.i18n import PAGES, REDIRECTS, UI, page_slug
from wiki.md import front_matter, inline, render

SITE = F.ROOT / "site"
STATIC = F.ROOT / "wiki" / "static"
IMG = F.ROOT / "facts" / "img"
STAMP = SITE / ".stamp"

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*(?::\s*([^}]*?))?\s*\}\}")
ENTITY = {"chaos_rules": ("rule", "chaos"), "items": ("item", "items"),
          "environment_rules": ("environment", "environment"),
          "tables": ("table", "tables"), "dealers": ("dealer", "dealers")}
# Catalog page -> (collection, page prefix) whose entries are listed under it in the nav.
# Table fields listing what a table offers, per collection.
POOL_FIELDS = {"chaos_rules": ("rules",), "environment_rules": ("environment_rules",), "items": ("items", "products")}
KIND_ORDER = ["core", "permanent", "item", "finance", "contract", None]
# Section headings of a game `details` text -> UI string key.
DETAIL_KEYS = {"Effect": "d_effect", "Timing": "d_timing", "Limits": "d_limits", "Example": "d_example",
               "Acquisition": "d_acquisition", "Related effects": "d_related"}
# Generated page prefix -> search result label (UI key); anything else is a page.
SEARCH_KINDS = {"item": "k_item", "rule": "k_rule", "environment": "k_environment", "table": "k_table",
                "dealer": "k_dealer", "design": "k_design"}
NAV_SUBS = {"chaos": ("chaos_rules", "rule"), "items": ("items", "item"), "design": ("design_docs", "design"),
            "environment": ("environment_rules", "environment"),
            "tables": ("tables", "table"), "dealers": ("dealers", "dealer")}


def input_hash() -> str:
    """Hash of everything a build reads; check compares it with the stamp."""
    h = hashlib.sha256()
    for p in sorted([F.FACTS, *F.CONTENT.rglob("*"), *IMG.glob("*")]):
        if p.is_file():
            h.update(p.relative_to(F.ROOT).as_posix().encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def build(out: Path = SITE) -> list[str]:
    facts = F.load()
    if not facts:
        return ["facts/facts.json is missing; run `python -m wiki sync` first"]
    errors: list[str] = []
    if out.exists():
        shutil.rmtree(out)
    (out / "img").mkdir(parents=True)
    for f in STATIC.iterdir():
        shutil.copy2(f, out / f.name)
    for f in IMG.glob("*.png"):
        shutil.copy2(f, out / "img" / f.name)
    # Editorial portraits stay separate from game snapshots removed by sync.
    for f in (F.CONTENT / "img").glob("*.png"):
        shutil.copy2(f, out / "img" / f.name)
    (out / "index.html").write_text(_landing(facts), encoding="utf-8")
    # Cache-busting query for style.css, wiki.js and search.js: changes with code or content.
    static = b"".join(f.read_bytes() for f in sorted(STATIC.iterdir()) if f.is_file())
    version = hashlib.sha256(input_hash().encode() + static).hexdigest()[:10]
    for lang in F.LANGS:
        site = Site(facts, lang, errors, version)
        (out / lang).mkdir()
        for page, _ in PAGES:
            (out / lang / f"{page_slug(page)}.html").write_text(site.page(page), encoding="utf-8")
        for old, target in REDIRECTS.items():
            (out / lang / f"{old}.html").write_text(_redirect(target, UI[lang]["moved"]), encoding="utf-8")
        for coll, (prefix, _) in ENTITY.items():
            for eid in facts.get(coll, {}):
                (out / lang / f"{prefix}-{eid}.html").write_text(site.entity(coll, eid), encoding="utf-8")
        for d in facts.get("design_docs", {}):
            (out / lang / f"design-{d}.html").write_text(site.design_doc(d), encoding="utf-8")
        (out / lang / "search.js").write_text(site.search_js(), encoding="utf-8")
    if out == SITE:
        STAMP.write_text(input_hash() + "\n", encoding="utf-8")
    return sorted(set(errors))


class Site:
    def __init__(self, facts: dict[str, Any], lang: str, errors: list[str], version: str = "") -> None:
        self.facts, self.lang, self.errors = facts, lang, errors
        self.v = f"?v={version}" if version else ""
        self.t = UI[lang]
        self._heads: list[tuple[int, str, str]] = []
        self.index: list[dict[str, str]] = []

    # --- content ----------------------------------------------------------

    def _read(self, rel: str) -> tuple[dict[str, str], str, bool]:
        """(meta, body, translated). Falls back to English."""
        for lang in (self.lang, "en"):
            p = F.CONTENT / lang / rel
            if p.exists():
                meta, body = front_matter(p.read_text(encoding="utf-8"))
                return meta, body, lang == self.lang
        return {}, "", False

    def entity_text(self, coll: str, eid: str) -> tuple[dict[str, str], str, bool]:
        return self._read(f"{F.PROSE_FOLDERS[coll]}/{eid}.md")

    def name(self, coll: str, eid: str) -> str:
        meta, _, ok = self.entity_text(coll, eid)
        own = meta.get("name") or meta.get("title")
        e = self.facts[coll][eid]
        return own if ok and own else e.get("name") or e.get("title") or eid

    def blurb(self, coll: str, eid: str) -> tuple[str, bool]:
        """Localized effect / help text and whether it is translated."""
        key = "help" if coll == "items" else "effect"
        current = self.facts[coll][eid][key]
        if self.lang != "en":
            meta, _, ok = self.entity_text(coll, eid)
            # `<key>_en` records the English text the translation was made from.
            if ok and meta.get(key) and meta.get(f"{key}_en") == current:
                return self.expand_inline(meta[key], f"{coll}.{eid}"), True
        return current, self.lang == "en"

    def catalog_text(self, coll: str, eid: str, key: str = "name") -> str:
        entry = self.facts[coll][eid]
        if coll in ("tables", "dealers") and key == "name":
            return self.name(coll, eid)
        text = str(entry.get(key) or "")
        translated = self._strings().get("catalog", {}).get(coll, {}).get(eid, {})
        if self.lang != "en" and translated.get(f"{key}_en") == text:
            return self.expand_inline(translated.get(key) or text, f"{coll}.{eid}.{key}")
        return text

    def entity_link(self, coll: str, eid: str) -> str:
        return f'<a href="{ENTITY[coll][0]}-{eid}.html">{html.escape(self.name(coll, eid))}</a>'

    def pool(self, tid: str, coll: str) -> list[str]:
        """Ids of `coll` a table offers: its chaos rules, environment rules, or sold items and products."""
        table = self.facts.get("tables", {}).get(tid, {})
        fields = POOL_FIELDS.get(coll, ())
        return sorted({eid for field in fields for eid in table.get(field) or []})

    def table_order(self) -> list[str]:
        """Released tables first (core series leading), experimental ones last."""
        tables = self.facts.get("tables", {})
        return sorted(tables, key=lambda tid: (self.experimental("tables", tid), tables[tid].get("series") != "core", tid))

    def table_links(self, coll: str, eid: str) -> str:
        return ", ".join(self.entity_link("tables", tid) for tid in self.table_order()
                         if eid in self.pool(tid, coll)) or self.t["none"]

    # --- placeholders ------------------------------------------------------

    def expand_inline(self, text: str, where: str) -> str:
        def sub(m: re.Match[str]) -> str:
            kind, arg = m.group(1), (m.group(2) or "").strip()
            if kind == "fact":
                try:
                    return self.fmt(F.lookup(self.facts, arg))
                except KeyError:
                    self.errors.append(f"{where}: unknown fact `{arg}`")
                    return "??"
            if kind == "link":
                coll, _, eid = arg.partition(".")
                if coll in ENTITY and eid in self.facts.get(coll, {}):
                    return f"[{self.name(coll, eid)}]({ENTITY[coll][0]}-{eid}.html)"
                self.errors.append(f"{where}: unknown link `{arg}`")
                return arg
            return m.group(0)
        return PLACEHOLDER.sub(sub, text)

    def expand(self, body: str, where: str) -> str:
        raws: list[str] = []

        def block(m: re.Match[str]) -> str:
            kind, arg = m.group(1), (m.group(2) or "").strip()
            fn: Callable[[], str] | None = getattr(self, f"t_{arg.replace('-', '_')}", None) if kind == "table" else None
            if fn is None:
                self.errors.append(f"{where}: unknown block `{m.group(0).strip()}`")
                return ""
            raws.append(fn())
            return f"\n\x00{len(raws) - 1}\x00\n"

        body = re.sub(r"^[ \t]*\{\{\s*(table)\s*:\s*([\w-]+)\s*\}\}[ \t]*$", block, body, flags=re.M)
        body = self.expand_inline(body, where)
        for m in PLACEHOLDER.finditer(body):
            self.errors.append(f"{where}: unknown placeholder `{m.group(0)}`")
        rendered, _ = render(body)
        rendered = re.sub(r"\x00(\d+)\x00", lambda m: raws[int(m.group(1))], rendered)
        self._heads = [(int(lvl), hid, html.unescape(re.sub(r"<[^>]+>", "", text)))
                       for lvl, hid, text in re.findall(r'<h(\d) id="([^"]+)">(.*?)</h\1>', rendered)]
        return rendered

    def fmt(self, v: Any) -> str:
        if isinstance(v, bool):
            return self.t["yes"] if v else self.t["no"]
        if v is None or v == {} or v == []:
            return "—"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        if isinstance(v, list):
            return ", ".join(self.fmt(x) for x in v)
        if isinstance(v, dict):
            return ", ".join(f"{k}={self.fmt(x)}" for k, x in v.items())
        return str(v)

    # --- generated blocks (t_<name> = {{ table: name }}) ---------------------

    def _table(self, head: list[str], rows: list[list[str]], cls: str = "") -> str:
        th = "".join(f"<th>{self.t.get(h, h)}</th>" for h in head)
        trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f'<div class="table-wrap"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

    def _icon(self, eid: str, label: str, size: str = "") -> str:
        if (IMG / f"{eid}.png").exists():
            return f'<img class="icon {size}" src="../img/{eid}.png" alt="">'
        initials = "".join(w[0] for w in re.findall(r"[A-Za-z]+", label)[:2]).upper() or "?"
        return f'<span class="icon ph {size}" aria-hidden="true">{html.escape(initials)}</span>'

    def _cards(self, coll: str, selected: list[str] | None = None) -> str:
        prefix = ENTITY[coll][0]
        cards = []
        for eid, e in self.facts.get(coll, {}).items():
            if selected is not None and eid not in selected:
                continue
            name = self.name(coll, eid)
            text, ok = self.blurb(coll, eid)
            extra = ""
            if coll == "items":
                extra = f'<span class="pill">{self.item_price(e)}</span>'
            cards.append(
                f'<a class="card {prefix}" href="{prefix}-{eid}.html">{self._icon(eid, e["name"])}'
                f'<span class="card-body"><strong>{html.escape(name)}</strong>{extra}'
                f'<span class="muted{"" if ok else " en"}">{inline(text)}</span></span></a>')
        return f'<div class="cards">{"".join(cards)}</div>'

    def pool_groups(self, coll: str) -> tuple[list[tuple[str, list[str]]], list[str], bool]:
        """(per-table groups, unused ids, whether the hub page shows them as headed sections)."""
        entries = self.facts.get(coll, {})
        groups = [(tid, [eid for eid in entries if eid in self.pool(tid, coll)]) for tid in self.table_order()]
        groups = [(tid, ids) for tid, ids in groups if ids]
        offered = {eid for _, ids in groups for eid in ids}
        unused = [eid for eid in entries if eid not in offered]
        return groups, unused, bool(groups) and (len(groups) > 1 or bool(unused))

    def entity_order(self, coll: str) -> list[str]:
        """Reading order of a collection: the hub page's order (by table, then kind), each id once."""
        entries = self.facts.get(coll, {})
        if coll == "tables":
            return [tid for tid in self.table_order() if tid in entries]
        if coll not in POOL_FIELDS:
            return list(entries)
        groups, unused, _ = self.pool_groups(coll)
        order: list[str] = []
        for _, ids in groups:
            if coll == "items":
                ids = sorted(ids, key=lambda eid: KIND_ORDER.index(entries[eid].get("kind"))
                             if entries[eid].get("kind") in KIND_ORDER else len(KIND_ORDER))
            order += [eid for eid in ids if eid not in order]
        return order + unused

    def _by_table(self, coll: str) -> str:
        """Cards grouped by the table that offers them; ids no table offers come last as unused.

        An id offered by several tables is listed under each. With a single group there are
        no headings. Items of one table with several kinds get a sub-heading per kind."""
        groups, unused, headed = self.pool_groups(coll)
        if not headed:
            return self._cards(coll)
        out = []
        for tid, ids in groups:
            label = f'*{self.t["experimental"]}'
            pill = (f' <span class="pill">{label}</span>'
                    if self.experimental("tables", tid) and label not in self.name("tables", tid) else "")
            out.append(f'<h2 id="pool-{tid}">{self.entity_link("tables", tid)}{pill}</h2>' + self._kinds(coll, tid, ids))
        if unused:
            out.append(f'<h2 id="pool-unused">{self.t["unused_pool"]}</h2>'
                       f'<p class="muted">{self.t["unused_note"]}</p>' + self._cards(coll, unused))
        return "".join(out)

    def _kinds(self, coll: str, tid: str, ids: list[str]) -> str:
        entries = self.facts[coll]
        kinds = list(dict.fromkeys(entries[eid].get("kind") for eid in ids))
        if coll != "items" or len(kinds) < 2:
            return self._cards(coll, ids)
        kinds.sort(key=lambda k: KIND_ORDER.index(k) if k in KIND_ORDER else len(KIND_ORDER))
        return "".join(f'<h3 id="pool-{tid}-{kind or "classic"}">{self.t[kind] if kind else self.t["classic_items"]}</h3>'
                       + self._cards(coll, [eid for eid in ids if entries[eid].get("kind") == kind]) for kind in kinds)

    def t_chaos_cards(self) -> str:
        return self._by_table("chaos_rules")

    def t_item_cards(self) -> str:
        return self._by_table("items")

    def t_poker_products(self) -> str:
        """Build-product catalog of every table that has one, by kind."""
        return "".join(self._kinds("items", tid, sorted(table["products"], key=list(self.facts["items"]).index))
                       for tid, table in self.facts.get("tables", {}).items() if table.get("products"))

    def t_environment_cards(self) -> str:
        return self._by_table("environment_rules")

    def t_director_stages(self) -> str:
        import json
        stages = json.loads(self.facts["settings"]["mode.chaos.director.stages"]["value"])
        rows = []
        for index, (start, chance, slots, budget) in enumerate(stages):
            end = f"–{stages[index + 1][0] - 1}" if index + 1 < len(stages) else "+"
            rows.append([f"{start}{end}", f"{chance * 100:g}%", str(slots), str(budget)])
        return self._table(["rounds", "action_chance", "rule_slots", "pressure_budget"], rows)

    def table_goal(self, tid: str) -> str:
        entry = self.facts["tables"][tid]
        return html.escape(self.catalog_text("tables", tid, "goal_text")) if entry.get("goal_text") else f'{entry["start_money"]} → {entry["target_money"]}'

    def t_tables(self) -> str:
        rows = []
        for tid, table in sorted(self.facts.get("tables", {}).items(), key=lambda pair: (pair[1]["series"] != "core", pair[0])):
            rows.append([self.entity_link("tables", tid), self.entity_link("dealers", table["host"]),
                         html.escape(self.catalog_text("tables", tid, "description")),
                         self.table_goal(tid),
                         str(len(table.get("environment_rules", table["rules"]))), str(len(table.get("products", table["items"])))])
        return self._table(["name", "host", "description", "goal", "rule_count", "item_count"], rows, "catalog")

    def experimental(self, coll: str, eid: str) -> bool:
        """A table is experimental when the game says so; a dealer when all its tables are."""
        if coll == "tables":
            return bool(self.facts.get("tables", {}).get(eid, {}).get("experimental"))
        tables = self.facts.get("dealers", {}).get(eid, {}).get("tables") or []
        return bool(tables) and all(self.experimental("tables", tid) for tid in tables)

    def state(self, coll: str, eid: str) -> str:
        return f'*{self.t["experimental"]}' if self.experimental(coll, eid) else self.t["released"]

    def t_dealers(self) -> str:
        rows = [[self.entity_link("dealers", did), self.state("dealers", did),
                 ", ".join(self.entity_link("tables", tid) for tid in dealer["tables"])]
                for did, dealer in self.facts.get("dealers", {}).items()]
        return self._table(["name", "state", "tables"], rows)

    def t_upgrades(self) -> str:
        rows = []
        for uid, entry in self.facts.get("upgrades", {}).items():
            cost = " / ".join(str(entry["cost"] + level * entry["cost_step"])
                              for level in range(entry["max_level"])) if entry["kind"] == "permanent" else str(entry["cost"])
            scope = self.entity_link("tables", entry["mode"]) if entry["mode"] else self.t["all_tables"]
            rows.append([html.escape(self.catalog_text("upgrades", uid)), self.t[entry["kind"]],
                         html.escape(self.catalog_text("upgrades", uid, "description")), cost,
                         str(entry["max_level"]), scope])
        return self._table(["name", "kind", "effect", "token_cost", "max_level", "tables"], rows, "catalog")

    def t_cosmetics(self) -> str:
        rows, hidden = [], []
        for cid, entry in self.facts.get("cosmetics", {}).items():
            sources = []
            if entry["default"]:
                sources.append(self.t["default_owned"])
            if entry["price"] is not None:
                sources.append(f'{entry["price"]} {self.t["tokens"]}')
            sources += [html.escape(self.catalog_text("achievements", aid)) for aid in entry["achievements"]]
            row = [html.escape(self.catalog_text("cosmetics", cid)), self.t[entry["slot"]],
                   html.escape(self.catalog_text("cosmetics", cid, "description")), ", ".join(sources) or self.t["not_sold"]]
            (hidden if entry["hidden"] else rows).append(row)
        head = ["name", "slot", "description", "obtain"]
        return self._table(head, rows, "catalog") + (f'<details><summary>{self.t["spoilers"]}</summary>{self._table(head, hidden, "catalog")}</details>' if hidden else "")

    def t_achievements(self) -> str:
        rows, hidden = [], []
        for aid, entry in self.facts.get("achievements", {}).items():
            reward = [f'{entry["tokens"]} {self.t["tokens"]}'] if entry["tokens"] else []
            reward += [html.escape(self.catalog_text("cosmetics", cid)) for cid in entry["cosmetics"]]
            row = [html.escape(self.catalog_text("achievements", aid)),
                   html.escape(self.catalog_text("achievements", aid, "description")),
                   str(entry["goal"]), self.t[entry["scope"]], ", ".join(reward) or self.t["none"]]
            (hidden if entry["hidden"] else rows).append(row)
        head = ["name", "condition", "goal", "scope", "reward"]
        return self._table(head, rows, "catalog") + (f'<details><summary>{self.t["spoilers"]}</summary>{self._table(head, hidden, "catalog")}</details>' if hidden else "")

    def t_settings(self) -> str:
        zh = self._strings().get("settings", {})
        rows = []
        for k, s in self.facts.get("settings", {}).items():
            rng = "" if s.get("min") is None and s.get("max") is None else f"{self.fmt(s.get('min'))} – {self.fmt(s.get('max'))}"
            desc = zh.get(k) if self.lang != "en" and zh.get(k) else s.get("description") or ""
            rows.append([f"<code>{k}</code>", f"<strong>{html.escape(self.fmt(s['value']))}</strong>",
                         s.get("type", ""), rng, html.escape(desc)])
        return self._table(["key", "value", "type", "range", "description"], rows)

    def item_price(self, item: dict[str, Any]) -> str:
        if item.get("kind") == "core":
            return self.t["core_choice"]
        if item.get("kind") == "finance" and "advance" in item.get("params", {}):
            return self.t["loan_price"].format(**item["params"])
        price = item.get("price")
        if price is None:
            return self.t["not_sold"]
        if item.get("price_mode") == "bankroll_pct":
            return self.t["bankroll_price"].format(price=self.fmt(price))
        return f"{self.fmt(price)} {self.t['chips']}"

    def t_prices(self) -> str:
        rows = []
        for eid, e in sorted(self.facts.get("items", {}).items(), key=lambda kv: (kv[1].get("price") is None, kv[1].get("price") or 0)):
            text, _ = self.blurb("items", eid)
            rows.append([f'<a href="item-{eid}.html">{html.escape(self.name("items", eid))}</a>',
                         self.item_price(e), inline(text)])
        return self._table(["name", "price", "help"], rows)

    def t_permissions(self) -> str:
        rows = []
        for name, p in self.facts.get("permissions", {}).items():
            rules = len(p["allowed_rules"])
            items = ", ".join(self.name("items", i) for i in p["allowed_items"] if i in self.facts["items"]) or self.t["none"]
            rows.append([f"<code>{name}</code>", self.fmt(p.get("chaos_budget")), self.fmt(p.get("charge_per_effect")),
                         self.fmt(p.get("max_actions_per_turn")), self.fmt(p.get("max_active_effects")),
                         f"{rules} / {len(self.facts['chaos_rules'])}", html.escape(items)])
        return self._table(["profile", "budget", "per_effect", "actions_turn", "active_effects",
                            "allowed_rules", "allowed_items"], rows)

    def t_commands(self) -> str:
        rows = [[f"<code>{c}</code>", html.escape(h)] for c, h in sorted(self.facts["agent"]["commands"].items())]
        return self._table(["command", "meaning"], rows)

    def t_actions(self) -> str:
        rows = [[f"<code>{a}</code>", html.escape(h)] for a, h in self.facts["agent"]["actions"].items()]
        return self._table(["action", "meaning"], rows)

    def t_errors(self) -> str:
        zh = self._strings().get("error_codes", {})
        en = self._strings("en").get("error_codes", {})
        rows = [[f"<code>{c}</code>", html.escape((zh if self.lang != "en" else en).get(c) or en.get(c, ""))]
                for c in self.facts["agent"]["error_codes"]]
        return self._table(["code", "meaning"], rows)

    def t_transcript(self) -> str:
        tr = self.facts.get("transcript") or {}
        rows = []
        for n, s in enumerate(tr.get("steps", []), 1):
            c = s["command"]
            cmd = " ".join(str(c[k]) for k in ("cmd", "action", "item", "amount") if k in c)
            ev = "<br>".join(html.escape(e) for e in s.get("events", []))
            obs = s.get("obs", {})
            lr = obs.get("last_round")
            res = html.escape(obs.get("summary", ""))
            if lr:
                res += f'<br><span class="pill">{html.escape(str(lr.get("outcome")))} {lr.get("delta", 0):+}</span>'
            rows.append([str(n), f"<code>{html.escape(cmd)}</code>", ev, res])
        head = f'<p class="muted"><code>python -m chaos_blackjack.agent new --seed {tr.get("seed")} --chaos</code></p>'
        return head + self._table(["step", "you_send", "events", "result"], rows, "transcript")

    def t_gallery(self) -> str:
        groups: dict[str, list[str]] = {}
        for aid, a in self.facts.get("assets", {}).items():
            final = (IMG / f"{aid}.png").exists()
            tag = f'<span class="pill {"ok" if final else "warn"}">{self.t["final" if final else "placeholder"]}</span>'
            groups.setdefault(a["category"], []).append(
                f'<figure class="art">{self._icon(aid, a["name"], "big")}<figcaption><strong>{html.escape(a["name"])}</strong>'
                f'<code>{aid}</code><span class="muted">{a["size"][0]}×{a["size"][1]}</span>{tag}</figcaption></figure>')
        return "".join(f'<h3 id="art-{c}">{html.escape(c)}</h3><div class="gallery">{"".join(v)}</div>'
                       for c, v in groups.items())

    def t_changelog(self) -> str:
        rows = [[c["date"], f"<code>{c['commit']}</code>", html.escape(c["subject"])]
                for c in self.facts.get("changelog", [])]
        return self._table(["date", "commit", "change"], rows)

    def _strings(self, lang: str | None = None) -> dict[str, Any]:
        p = F.CONTENT / (lang or self.lang) / "strings.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    # --- pages -------------------------------------------------------------

    def page(self, path: str) -> str:
        slug = page_slug(path)
        meta, body, ok = self._read(f"{path}.md")
        if not body and not meta:
            self.errors.append(f"content/en/{path}.md is missing")
        article = self.expand(body, f"{self.lang}/{path}.md")
        if meta.get("status") == "draft":
            article = f'<div class="banner planned">{self.t["editorial_draft"]}</div>' + article
        if not ok:
            article = f'<p class="notice">{self.t["untranslated"]}</p>' + article
        title = meta.get("title", slug)
        return self.layout(slug, title, f"<h1>{html.escape(title)}</h1>{article}", self._heads)

    def entity(self, coll: str, eid: str) -> str:
        if coll in ("tables", "dealers"):
            return self.catalog_entity(coll, eid)
        prefix, _ = ENTITY[coll]
        e = self.facts[coll][eid]
        meta, body, ok = self.entity_text(coll, eid)
        where = f"{self.lang}/{ENTITY[coll][1]}/{eid}.md"
        name = self.name(coll, eid)
        text, text_ok = self.blurb(coll, eid)
        rows = [["id", f"<code>{eid}</code>"]]
        if coll in ("chaos_rules", "environment_rules"):
            rows += [["params", html.escape(self.fmt(e.get("params")))],
                     ["flags", html.escape(self.fmt(e.get("flags")))],
                     ["profiles", html.escape(self.fmt(e.get("profiles")))],
                     ["enabled", self.fmt(e.get("enabled"))]]
            if e.get("stub_weight") is not None:
                rows.append(["stub_weight", self.fmt(e["stub_weight"])])
            ev = self.sim_rule_rows(eid) if self._sim().get("measured_on") == self.facts["source"]["commit"] else []
            if ev:
                rows.append(["sim_rule_ev", "<br>".join(ev) + f' · <a href="balance.html">{self.t["sim_more"]}</a>'])
        else:
            rows += [["price", self.item_price(e)]]
            if e.get("kind"):
                rows.append(["kind", self.t[e["kind"]]])
            if e.get("timing"):
                meta_timing = meta.get("timing") if ok else None
                rows.append(["timing", html.escape(meta_timing or e["timing"])])
            if e.get("params"):
                rows.append(["params", html.escape(self.fmt(e["params"]))])
            gain = next((r for r in self._measured("items") if r["item"] == eid), None)
            if gain and self._sim().get("measured_on") == self.facts["source"]["commit"]:
                rows.append(["sim_item_gain", f'{self._ev_pill(gain["ev"])} <span class="muted">{html.escape(gain["se"])}</span>'
                                              f' · <a href="balance.html">{self.t["sim_more"]}</a>'])
        if self.facts.get("tables"):
            rows.append(["tables", self.table_links(coll, eid)])
        facts_tbl = "".join(f"<tr><th>{self.t[k]}</th><td>{v}</td></tr>" for k, v in rows)
        note = "" if text_ok else f' <span class="badge" title="{self.t["untranslated"]}">EN</span>'
        prose = self.expand(body, where) if body.strip() else f'<p class="muted">{self.t["no_notes"]}</p>'
        if body.strip() and not ok:
            prose = f'<p class="notice">{self.t["untranslated"]}</p>' + prose
        back = "environment" if coll == "environment_rules" else "chaos" if coll == "chaos_rules" else "items"
        tagline, details = self.details(e)
        if tagline and self.lang == "en":
            note += f'</p><p class="tagline">{html.escape(tagline)}'
        html_ = (self.crumbs(back, self.pool_crumb(coll, eid, back), name)
                 + f'<div class="hero {prefix}">{self._icon(eid, e["name"], "big")}<div><h1>{html.escape(name)}</h1>'
                 f'<p class="lead">{inline(text)}{note}</p></div></div>'
                 f'<div class="table-wrap"><table class="facts">{facts_tbl}</table></div>{details}{prose}'
                 + self.pager(coll, eid))
        keywords = " ".join(dict.fromkeys([e["name"], eid]))
        return self.layout(f"{prefix}-{eid}", name, html_, _heads_of(html_), active=back,
                           keywords=keywords, icon=eid, snippet=_plain(inline(text)))

    def details(self, e: dict[str, Any]) -> tuple[str, str]:
        """(tagline, rendered sections) from the game's `details` text: a tagline, then blocks
        headed Effect / Timing / Limits / Example / Acquisition / Related effects. The text is
        English; other languages label it as the original."""
        blocks = [b.strip() for b in (e.get("details") or "").split("\n\n") if b.strip()]
        if not blocks:
            return "", ""
        tagline = blocks.pop(0) if blocks[0].split("\n", 1)[0] not in DETAIL_KEYS else ""
        rows = []
        for block in blocks:
            head, _, body = block.partition("\n")
            key = DETAIL_KEYS.get(head)
            if key == "d_effect" and self.lang == "en" and body.strip() == e.get("help"):
                continue  # already the lead
            value = (self.related_links(body) if key == "d_related"
                     else "<br>".join(html.escape(line) for line in body.splitlines()))
            rows.append(f'<dt>{self.t[key] if key else html.escape(head)}</dt><dd>{value}</dd>')
        if not rows:
            return tagline, ""
        note = f'<p class="muted">{self.t["details_original"]}</p>' if self.lang != "en" else ""
        return tagline, f'<h2 id="details">{self.t["details"]}</h2>{note}<dl class="details">{"".join(rows)}</dl>'

    def related_links(self, text: str) -> str:
        """Comma-separated English names -> links to those entries, in this language."""
        if not hasattr(self, "_by_name"):
            self._by_name = {e["name"]: (coll, eid) for coll in ("items", "chaos_rules", "environment_rules")
                             for eid, e in self.facts.get(coll, {}).items() if e.get("name")}
        out = []
        for name in (n.strip() for n in text.replace("\n", ",").split(",")):
            if name:
                hit = self._by_name.get(name)
                out.append(self.entity_link(*hit) if hit else html.escape(name))
        return ", ".join(out)

    def hub_title(self, hub: str) -> str:
        path = next((p for p, _ in PAGES if page_slug(p) == hub), hub)
        return self._read(f"{path}.md")[0].get("title", hub)

    def crumbs(self, hub: str, middle: str, name: str) -> str:
        """Nav group › hub page › (section) › this page."""
        group = next((g for p, g in PAGES if page_slug(p) == hub), None)
        parts = ([html.escape(self.t[group])] if group else []) + [
            f'<a href="{hub}.html">{html.escape(self.hub_title(hub))}</a>'] + ([middle] if middle else [])
        parts.append(f'<span aria-current="page">{html.escape(name)}</span>')
        return f'<nav class="crumbs" aria-label="{self.t["breadcrumb"]}">{" <span class=sep>›</span> ".join(parts)}</nav>'

    def pool_crumb(self, coll: str, eid: str, hub: str) -> str:
        """Link to the hub section that lists this id (first table offering it, or unused)."""
        groups, unused, headed = self.pool_groups(coll)
        if not headed:
            return ""
        tid = next((t for t, ids in groups if eid in ids), None)
        if tid is None:
            return f'<a href="{hub}.html#pool-unused">{html.escape(self.t["unused_pool"])}</a>'
        return f'<a href="{hub}.html#pool-{tid}">{html.escape(self.name("tables", tid))}</a>'

    def pager(self, coll: str, eid: str) -> str:
        """Previous / next entry in the collection's reading order."""
        order = self.entity_order(coll)
        if eid not in order or len(order) < 2:
            return ""
        i = order.index(eid)
        prefix = ENTITY[coll][0] if coll in ENTITY else "design"
        links = []
        if i > 0:
            links.append(f'<a rel="prev" href="{prefix}-{order[i - 1]}.html"><small>{self.t["prev"]}</small>'
                         f'{html.escape(self.name(coll, order[i - 1]))}</a>')
        if i + 1 < len(order):
            links.append(f'<a rel="next" href="{prefix}-{order[i + 1]}.html"><small>{self.t["next"]}</small>'
                         f'{html.escape(self.name(coll, order[i + 1]))}</a>')
        return f'<nav class="pager">{"".join(links)}</nav>'

    def catalog_entity(self, coll: str, eid: str) -> str:
        entry = self.facts[coll][eid]
        _, body, ok = self.entity_text(coll, eid)
        name = self.name(coll, eid)
        rows = []
        if coll == "tables":
            rows = [["host", self.entity_link("dealers", entry["host"])],
                    ["goal", self.table_goal(eid)],
                    ["bet_limits", f'{entry["min_bet"]} – {entry["max_bet_fraction"]} × {self.t["bankroll"]}'],
                    ["payout", ":".join(map(str, entry["blackjack_pays"]))],
                    ["rules", ", ".join(self.entity_link("environment_rules" if entry.get("environment_rules") else "chaos_rules", rid) for rid in entry.get("environment_rules", entry["rules"])) or self.t["none"]],
                    ["items", ", ".join(self.entity_link("items", iid) for iid in entry.get("products", entry["items"])) or self.t["none"]]]
        else:
            rows = [["tables", ", ".join(self.entity_link("tables", tid) for tid in entry["tables"])]]
        table = self._table(["key", "value"], [[self.t[key], value] for key, value in rows])
        prose = self.expand(body, f"{self.lang}/{coll}/{eid}.md")
        if not ok:
            prose = f'<p class="notice">{self.t["untranslated"]}</p>' + prose
        article = (self.crumbs(coll, "", name)
                   + f'<h1>{html.escape(name)}</h1><span class="pill ok">{self.state(coll, eid)}</span>{table}{prose}'
                   + self.pager(coll, eid))
        return self.layout(f"{ENTITY[coll][0]}-{eid}", name, article, self._heads, active=coll,
                           keywords=" ".join(dict.fromkeys([entry.get("name", ""), eid])))

    def design_doc(self, d: str) -> str:
        doc = self.facts["design_docs"][d]
        meta, body, ok = self.entity_text("design_docs", d)
        title = self.name("design_docs", d)
        where = f"{self.lang}/design/{d}.md"
        state = self.t["design_on_main"] if doc["on_main"] else self.t["design_planned"]
        if meta.get("status") == "experimental":
            state = "*" + self.t["experimental"]
        banner = self.t["design_banner"].format(
            state=state, path=html.escape(doc["path"]), ref=html.escape(doc["ref"]), commit=doc["commit"],
            date=doc["date"], status=html.escape(doc.get("status") or "—"))
        notes = ""
        if body and meta.get("source_blob") != doc["blob"]:
            notes += f'<p class="notice">{self.t["design_stale"]}</p>'
        if body and not ok:
            notes += f'<p class="notice">{self.t["untranslated"]}</p>'
        prose = self.expand(body, where) if body.strip() else f'<p class="muted">{self.t["design_no_summary"]}</p>'
        html_ = (self.crumbs("design", "", title)
                 + f'<h1>{html.escape(title)}</h1><div class="banner {"" if doc["on_main"] else "planned"}">{banner}</div>'
                 f'{notes}{prose}' + self.pager("design_docs", d))
        return self.layout(f"design-{d}", title, html_, self._heads if body.strip() else [], active="design",
                           keywords=" ".join([doc.get("title") or "", doc["path"]]))

    # --- search ------------------------------------------------------------

    def _index(self, slug: str, title: str, article: str, keywords: str, icon: str, snippet: str) -> None:
        prefix = slug.split("-", 1)[0] if "-" in slug else ""
        entry = {"u": f"{slug}.html", "t": title, "k": self.t[SEARCH_KINDS.get(prefix, "k_page")],
                 "w": keywords, "s": snippet, "x": _plain(article)[:4000]}
        if icon and (IMG / f"{icon}.png").exists():
            entry["i"] = f"../img/{icon}.png"
        self.index.append({k: v for k, v in entry.items() if v})

    def search_js(self) -> str:
        """The page index as a script (not JSON: pages opened from file:// cannot fetch)."""
        data = json.dumps(self.index, ensure_ascii=False, separators=(",", ":"))
        return f"window.WIKI_SEARCH={data};\n"

    # --- simulator ----------------------------------------------------------

    def _sim(self) -> dict[str, Any]:
        return self.facts.get("sim") or {}

    def _measured(self, key: str) -> list[dict[str, Any]]:
        return (self._sim().get("measured") or {}).get(key, [])

    def _ev_pill(self, ev: str) -> str:
        cls = "ok" if ev.startswith("+") and ev.strip("+%0.") else ("warn" if ev.startswith("-") else "")
        return f'<span class="pill {cls}">{html.escape(ev)}</span>'

    def sim_rule_rows(self, rid: str) -> list[str]:
        """EV rows for one game rule (a rule can have several simulated variants)."""
        from wiki.sim import game_rule

        rules = set(self.facts.get("chaos_rules", {}))
        return [f"{self._ev_pill(r['ev'])} <span class=\"muted\">{html.escape(r['se'])} · <code>{html.escape(r['rule'])}</code></span>"
                for r in self._measured("edge") if game_rule(r["rule"], rules) == rid]

    def t_sim_edge(self) -> str:
        from wiki.sim import game_rule

        rules = set(self.facts.get("chaos_rules", {}))
        rows = []
        for r in self._measured("edge"):
            gid = game_rule(r["rule"], rules)
            name = (f'<a href="rule-{gid}.html">{html.escape(self.name("chaos_rules", gid))}</a>'
                    if gid else self.t["sim_no_rule"])
            rows.append([f"<code>{html.escape(r['rule'])}</code>", name, self._ev_pill(r["ev"]), html.escape(r["se"])])
        return self._sim_meta("edge") + self._table(["sim_variant", "name", "sim_ev", "sim_se"], rows)

    def t_sim_items(self) -> str:
        rows = []
        for r in self._measured("items"):
            known = r["item"] in self.facts.get("items", {})
            name = f'<a href="item-{r["item"]}.html">{html.escape(self.name("items", r["item"]))}</a>' if known else r["item"]
            rows.append([name, self._ev_pill(r["ev"]), html.escape(r["se"])])
        return self._sim_meta("items") + self._table(["name", "sim_gain", "sim_se"], rows)

    def t_sim_bands(self) -> str:
        defs = {d["name"]: d for d in self._sim().get("band_defs", [])}
        rows = []
        for b in self._measured("bands"):
            d = defs.get(b["metric"], {})
            size = f"{d['rounds']} {self.t['sim_rounds']}" if "rounds" in d else (
                f"{d['runs']} {self.t['sim_runs']}" if "runs" in d else "")
            ok = b.get("ok") == "yes"
            rows.append([html.escape(b["metric"]), html.escape(size), f"<strong>{html.escape(b['value'])}</strong>",
                         html.escape(b["band"]),
                         f'<span class="pill {"ok" if ok else "warn"}">{self.t["yes" if ok else "no"]}</span>'])
        return self._sim_meta("bands") + self._table(["sim_metric", "sim_size", "sim_value", "sim_band", "sim_in_band"], rows)

    def t_sim_commands(self) -> str:
        rows = [[f"<code>{html.escape(c)}</code>", f"<code>{html.escape(u)}</code>"]
                for c, u in self._sim().get("commands", {}).items()]
        return self._table(["command", "sim_usage"], rows)

    def t_sim_options(self) -> str:
        s = self._sim()
        fmt = lambda xs: ", ".join(f"<code>{html.escape(x)}</code>" for x in xs)  # noqa: E731
        rows = [["<code>--chaos</code>", fmt(["off", "stub", "mix", "mix:a+b", *s.get("rules", [])])],
                ["<code>--bet</code>", fmt(s.get("bet_policies", []))],
                ["<code>--shop</code>", fmt(s.get("shop_policies", []))],
                ["<code>--prices</code>", fmt(["game", "fixed:<factor>", "scaled:<pct>"])]]
        return self._table(["sim_option", "sim_values"], rows)

    def _sim_meta(self, key: str) -> str:
        s = self._sim()
        run = (s.get("measured") or {}).get("runs", {}).get(key)
        if not run:
            return f'<p class="notice">{self.t["sim_missing"]}</p>'
        stale = s.get("measured_on") != self.facts["source"].get("commit")
        text = self.t["sim_meta"].format(args=html.escape(f"python -m bjsim {run['args']}"), seed=run["seed"],
                                         balance=html.escape(str(run["balance"])), game=s.get("measured_on"),
                                         sim=s.get("source", {}).get("commit"), title=html.escape(run["title"]))
        return f'<p class="muted">{text}</p>' + (f'<p class="notice">{self.t["sim_stale"]}</p>' if stale else "")

    def t_design_docs(self) -> str:
        rows = []
        for d, doc in self.facts.get("design_docs", {}).items():
            state = self.t["design_on_main"] if doc["on_main"] else self.t["design_planned"]
            rows.append([f'<a href="design-{d}.html">{html.escape(self.name("design_docs", d))}</a>',
                         f'<span class="pill {"ok" if doc["on_main"] else "warn"}">{state}</span>',
                         html.escape(doc.get("status") or "—"),
                         f'<code>{html.escape(doc["ref"])}</code> @ <code>{doc["commit"]}</code>', doc["date"]])
        if not rows:
            return f'<p class="muted">{self.t["none"]}</p>'
        return self._table(["name", "state", "doc_status", "source", "date"], rows)

    def layout(self, slug: str, title: str, article: str, heads: list[tuple[int, str, str]],
               active: str | None = None, keywords: str = "", icon: str = "", snippet: str = "") -> str:
        t, src = self.t, self.facts["source"]
        active = active or slug
        self._index(slug, title, article, keywords, icon, snippet)
        groups: dict[str, list[str]] = {}
        for path, group in PAGES:
            page = page_slug(path)
            meta, _, _ = self._read(f"{path}.md")
            cur = ' aria-current="page"' if page == active else ""
            sub = ' class="sub"' if meta.get("parent") else ""
            link = f'<a href="{page}.html"{sub}{cur}>{html.escape(meta.get("title", page))}</a>'
            if page not in NAV_SUBS:
                groups.setdefault(group, []).append(link)
                continue
            # A hub's entries fold under it; only the section you are in starts open.
            coll, prefix = NAV_SUBS[page]
            order = self.entity_order(coll)
            subs = "".join(f'<a class="sub" href="{prefix}-{eid}.html"'
                           f'{" aria-current=page" if slug == f"{prefix}-{eid}" else ""}>{html.escape(self.name(coll, eid))}</a>'
                           for eid in order)
            opened = " open" if page == active else ""
            groups.setdefault(group, []).append(
                f'<details class="subs"{opened}><summary>{link}<span class="count">{len(order)}</span></summary>{subs}</details>')
        nav = "".join(f'<div class="group"><p>{t[g]}</p>{"".join(links)}</div>' for g, links in groups.items())
        toc = "".join(f'<a class="l{lvl}" href="#{hid}">{html.escape(txt)}</a>' for lvl, hid, txt in heads if lvl in (2, 3))
        other = "zh" if self.lang == "en" else "en"
        stamp = t["stamp"].format(ref=html.escape(src.get("ref", "")), commit=src.get("commit", ""),
                                  date=src.get("date", ""), version=src.get("version", "?"))
        site_name = "Chaos Blackjack " + t["wiki"]
        return f"""<!doctype html>
<html lang="{'zh-CN' if self.lang == 'zh' else 'en'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · {site_name}</title>
<link rel="stylesheet" href="../style.css{self.v}">
<script>try{{localStorage.setItem("wiki-lang","{self.lang}")}}catch(e){{}}</script>
</head>
<body>
<header class="top">
  <button class="menu" aria-label="{t['menu']}" aria-expanded="false">☰</button>
  <a class="brand" href="index.html" aria-label="Chaos Blackjack"><span class="suit">♠</span> <span class="name">Chaos Blackjack</span> <span class="tag">{t['wiki']}</span></a>
  <div class="search-wrap">
    <input class="filter" type="search" placeholder="{t['filter']}" aria-label="{t['filter']}" autocomplete="off"
      role="combobox" aria-expanded="false" aria-controls="search-results" data-empty="{t['no_results']}" data-index="search.js{self.v}">
    <div class="results" id="search-results" role="listbox" hidden></div>
  </div>
  <a class="lang" href="../{other}/{slug}.html" hreflang="{other}">{UI[other]['lang_name']}</a>
</header>
<div class="layout">
  <nav class="side">{nav}</nav>
  <main><article>{article}</article><footer class="stamp">{stamp}</footer></main>
  <aside class="toc">{f'<p>{t["on_this_page"]}</p>{toc}' if toc else ''}</aside>
</div>
<script src="../wiki.js{self.v}"></script>
</body>
</html>
"""


def _plain(fragment: str) -> str:
    """Text of an HTML fragment, whitespace collapsed."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _heads_of(fragment: str) -> list[tuple[int, str, str]]:
    """(level, id, text) of every heading with an id, for the page TOC."""
    return [(int(lvl), hid, _plain(text)) for lvl, hid, text in re.findall(r'<h(\d) id="([^"]+)">(.*?)</h\1>', fragment)]


def _redirect(target: str, moved: str) -> str:
    t = html.escape(target)
    return (f'<!doctype html>\n<html><head><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={t}">'
            f'<link rel="canonical" href="{t}"><title>{moved}</title></head>'
            f'<body><p>{moved} <a href="{t}">{t}</a></p></body></html>\n')


def _landing(facts: dict[str, Any]) -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chaos Blackjack Wiki</title><link rel="stylesheet" href="style.css">
<script>
var l = null; try { l = localStorage.getItem("wiki-lang"); } catch (e) {}
if (!l) l = /^zh/i.test(navigator.language || "") ? "zh" : "en";
location.replace(l + "/index.html");
</script></head>
<body class="landing"><main><h1><span class="suit">♠</span> Chaos Blackjack Wiki</h1>
<p><a href="en/index.html">English</a> · <a href="zh/index.html">中文</a></p></main></body></html>
"""
