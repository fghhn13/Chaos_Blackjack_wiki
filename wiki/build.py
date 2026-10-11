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
from wiki.i18n import PAGES, UI
from wiki.md import front_matter, inline, render

SITE = F.ROOT / "site"
STATIC = F.ROOT / "wiki" / "static"
IMG = F.ROOT / "facts" / "img"
STAMP = SITE / ".stamp"

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*(?::\s*([^}]*?))?\s*\}\}")
ENTITY = {"chaos_rules": ("rule", "chaos"), "items": ("item", "items")}  # collection -> (page prefix, folder)
# Catalog page -> (collection, page prefix) whose entries are listed under it in the nav.
NAV_SUBS = {"chaos": ("chaos_rules", "rule"), "items": ("items", "item"), "design": ("design_docs", "design")}


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
    (out / "index.html").write_text(_landing(facts), encoding="utf-8")
    for lang in F.LANGS:
        site = Site(facts, lang, errors)
        (out / lang).mkdir()
        for page, _ in PAGES:
            (out / lang / f"{page}.html").write_text(site.page(page), encoding="utf-8")
        for coll, (prefix, _) in ENTITY.items():
            for eid in facts.get(coll, {}):
                (out / lang / f"{prefix}-{eid}.html").write_text(site.entity(coll, eid), encoding="utf-8")
        for d in facts.get("design_docs", {}):
            (out / lang / f"design-{d}.html").write_text(site.design_doc(d), encoding="utf-8")
    if out == SITE:
        STAMP.write_text(input_hash() + "\n", encoding="utf-8")
    return sorted(set(errors))


class Site:
    def __init__(self, facts: dict[str, Any], lang: str, errors: list[str]) -> None:
        self.facts, self.lang, self.errors = facts, lang, errors
        self.t = UI[lang]
        self._heads: list[tuple[int, str, str]] = []

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
        key = "effect" if coll == "chaos_rules" else "help"
        current = self.facts[coll][eid][key]
        if self.lang != "en":
            meta, _, ok = self.entity_text(coll, eid)
            # `<key>_en` records the English text the translation was made from.
            if ok and meta.get(key) and meta.get(f"{key}_en") == current:
                return self.expand_inline(meta[key], f"{coll}.{eid}"), True
        return current, self.lang == "en"

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
        rendered, heads = render(body)
        rendered = re.sub(r"\x00(\d+)\x00", lambda m: raws[int(m.group(1))], rendered)
        self._heads = heads
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

    def _cards(self, coll: str) -> str:
        prefix = ENTITY[coll][0]
        cards = []
        for eid, e in self.facts.get(coll, {}).items():
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

    def t_chaos_cards(self) -> str:
        return self._cards("chaos_rules")

    def t_item_cards(self) -> str:
        return self._cards("items")

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

    def page(self, slug: str) -> str:
        meta, body, ok = self._read(f"{slug}.md")
        if not body and not meta:
            self.errors.append(f"content/en/{slug}.md is missing")
        article = self.expand(body, f"{self.lang}/{slug}.md")
        if not ok:
            article = f'<p class="notice">{self.t["untranslated"]}</p>' + article
        title = meta.get("title", slug)
        return self.layout(slug, title, f"<h1>{html.escape(title)}</h1>{article}", self._heads)

    def entity(self, coll: str, eid: str) -> str:
        prefix, _ = ENTITY[coll]
        e = self.facts[coll][eid]
        meta, body, ok = self.entity_text(coll, eid)
        where = f"{self.lang}/{ENTITY[coll][1]}/{eid}.md"
        name = self.name(coll, eid)
        text, text_ok = self.blurb(coll, eid)
        rows = [["id", f"<code>{eid}</code>"]]
        if coll == "chaos_rules":
            rows += [["params", html.escape(self.fmt(e.get("params")))],
                     ["flags", html.escape(self.fmt(e.get("flags")))],
                     ["profiles", html.escape(self.fmt(e.get("profiles")))],
                     ["enabled", self.fmt(e.get("enabled"))]]
            if e.get("stub_weight") is not None:
                rows.append(["stub_weight", self.fmt(e["stub_weight"])])
            ev = self.sim_rule_rows(eid)
            if ev:
                rows.append(["sim_rule_ev", "<br>".join(ev) + f' · <a href="balance.html">{self.t["sim_more"]}</a>'])
        else:
            rows += [["price", self.item_price(e)]]
            if e.get("params"):
                rows.append(["params", html.escape(self.fmt(e["params"]))])
            gain = next((r for r in self._measured("items") if r["item"] == eid), None)
            if gain:
                rows.append(["sim_item_gain", f'{self._ev_pill(gain["ev"])} <span class="muted">{html.escape(gain["se"])}</span>'
                                              f' · <a href="balance.html">{self.t["sim_more"]}</a>'])
        facts_tbl = "".join(f"<tr><th>{self.t[k]}</th><td>{v}</td></tr>" for k, v in rows)
        note = "" if text_ok else f' <span class="badge" title="{self.t["untranslated"]}">EN</span>'
        prose = self.expand(body, where) if body.strip() else f'<p class="muted">{self.t["no_notes"]}</p>'
        if body.strip() and not ok:
            prose = f'<p class="notice">{self.t["untranslated"]}</p>' + prose
        back = "chaos" if coll == "chaos_rules" else "items"
        html_ = (f'<p class="crumb"><a href="{back}.html">← {self.t["all_rules" if back == "chaos" else "all_items"]}</a></p>'
                 f'<div class="hero {prefix}">{self._icon(eid, e["name"], "big")}<div><h1>{html.escape(name)}</h1>'
                 f'<p class="lead">{inline(text)}{note}</p></div></div>'
                 f'<div class="table-wrap"><table class="facts">{facts_tbl}</table></div>{prose}')
        return self.layout(f"{prefix}-{eid}", name, html_, self._heads if body.strip() else [], active=back)

    def design_doc(self, d: str) -> str:
        doc = self.facts["design_docs"][d]
        meta, body, ok = self.entity_text("design_docs", d)
        title = self.name("design_docs", d)
        where = f"{self.lang}/design/{d}.md"
        state = self.t["design_on_main"] if doc["on_main"] else self.t["design_planned"]
        banner = self.t["design_banner"].format(
            state=state, path=html.escape(doc["path"]), ref=html.escape(doc["ref"]), commit=doc["commit"],
            date=doc["date"], status=html.escape(doc.get("status") or "—"))
        notes = ""
        if body and meta.get("source_blob") != doc["blob"]:
            notes += f'<p class="notice">{self.t["design_stale"]}</p>'
        if body and not ok:
            notes += f'<p class="notice">{self.t["untranslated"]}</p>'
        prose = self.expand(body, where) if body.strip() else f'<p class="muted">{self.t["design_no_summary"]}</p>'
        html_ = (f'<p class="crumb"><a href="design.html">← {self.t["all_design"]}</a></p>'
                 f'<h1>{html.escape(title)}</h1><div class="banner {"" if doc["on_main"] else "planned"}">{banner}</div>'
                 f'{notes}{prose}')
        return self.layout(f"design-{d}", title, html_, self._heads if body.strip() else [], active="design")

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
               active: str | None = None) -> str:
        t, src = self.t, self.facts["source"]
        active = active or slug
        groups: dict[str, list[str]] = {}
        for page, group in PAGES:
            meta, _, _ = self._read(f"{page}.md")
            cur = ' aria-current="page"' if page == active else ""
            groups.setdefault(group, []).append(f'<a href="{page}.html"{cur}>{html.escape(meta.get("title", page))}</a>')
            if page in NAV_SUBS:
                coll, prefix = NAV_SUBS[page]
                for eid in self.facts.get(coll, {}):
                    cur = ' aria-current="page"' if slug == f"{prefix}-{eid}" else ""
                    groups[group].append(f'<a class="sub" href="{prefix}-{eid}.html"{cur}>{html.escape(self.name(coll, eid))}</a>')
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
<link rel="stylesheet" href="../style.css">
<script>try{{localStorage.setItem("wiki-lang","{self.lang}")}}catch(e){{}}</script>
</head>
<body>
<header class="top">
  <button class="menu" aria-label="{t['menu']}" aria-expanded="false">☰</button>
  <a class="brand" href="index.html"><span class="suit">♠</span> Chaos Blackjack <span class="tag">{t['wiki']}</span></a>
  <input class="filter" type="search" placeholder="{t['filter']}" aria-label="{t['filter']}">
  <a class="lang" href="../{other}/{slug}.html" hreflang="{other}">{UI[other]['lang_name']}</a>
</header>
<div class="layout">
  <nav class="side">{nav}</nav>
  <main><article>{article}</article><footer class="stamp">{stamp}</footer></main>
  <aside class="toc">{f'<p>{t["on_this_page"]}</p>{toc}' if toc else ''}</aside>
</div>
<script src="../wiki.js"></script>
</body>
</html>
"""


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
