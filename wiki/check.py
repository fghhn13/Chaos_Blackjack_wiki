"""Consistency checks. Errors fail (exit 1); warnings are listed for the next writer."""

from __future__ import annotations

import re
import json
import shutil
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

from wiki import facts as F
from wiki.build import SITE, STAMP, build, input_hash
from wiki.i18n import PAGES
from wiki.md import front_matter


def problems() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    facts = F.load()
    if not facts:
        return ["facts/facts.json is missing; run `python -m wiki sync`"], []
    errors += catalog_references(facts)

    # Placeholders and missing pages: a scratch build reports them.
    tmp = Path(tempfile.mkdtemp(prefix="wiki-check-"))
    try:
        errors += build(tmp / "site")
        errors += _links(tmp / "site")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # Orphans: prose for an id the game no longer has.
    for coll, folder in F.PROSE_FOLDERS.items():
        for lang in F.LANGS:
            for p in sorted((F.CONTENT / lang / folder).glob("*.md")):
                if p.stem not in facts.get(coll, {}):
                    errors.append(f"{p.relative_to(F.ROOT).as_posix()}: `{p.stem}` is not in the game any more")

    # Coverage: prose and translations (warnings unless --strict).
    for page, _ in PAGES:
        for lang in F.LANGS:
            if not (F.CONTENT / lang / f"{page}.md").exists():
                warnings.append(f"content/{lang}/{page}.md missing (falls back to English)")
    warnings += [f"{w}: {d}" for _, w, d in F.missing_prose(facts)]
    for d, doc in facts.get("design_docs", {}).items():
        for lang in F.LANGS:
            p = F.CONTENT / lang / "design" / f"{d}.md"
            meta = front_matter(p.read_text(encoding="utf-8"))[0] if p.exists() else {}
            if p.exists() and meta.get("source_blob") != doc["blob"]:
                warnings.append(f"{lang}: design page {d} was written from blob {meta.get('source_blob')}, "
                                f"the doc is now {doc['blob']} ({doc['ref']}); update it and `source_blob`")
    for coll, folder in F.PROSE_FOLDERS.items():
        if coll not in ("chaos_rules", "environment_rules", "items"):
            continue
        key = "help" if coll == "items" else "effect"
        for eid, e in facts.get(coll, {}).items():
            for lang in F.LANGS[1:]:
                p = F.CONTENT / lang / folder / f"{eid}.md"
                meta = front_matter(p.read_text(encoding="utf-8"))[0] if p.exists() else {}
                if not meta.get("name") or not meta.get(key):
                    warnings.append(f"{lang}: {coll}.{eid} has no translated name / {key}")
                elif meta.get(f"{key}_en") != e[key]:
                    warnings.append(f"{lang}: {coll}.{eid} translation is stale; English is now: {e[key]!r} "
                                    f"(update `{key}` and set `{key}_en` to it)")

    # Stamp: site/ must be built from the current facts + content.
    for lang in F.LANGS[1:]:
        path = F.CONTENT / lang / "strings.json"
        translations = json.loads(path.read_text(encoding="utf-8")).get("catalog", {}) if path.exists() else {}
        for coll in ("tables", "upgrades", "cosmetics", "achievements"):
            for eid, entry in facts.get(coll, {}).items():
                for key in (("description",) if coll == "tables" else ("name", "description")):
                    text = translations.get(coll, {}).get(eid, {})
                    if not text.get(key) or text.get(f"{key}_en") != entry.get(key):
                        warnings.append(f"{lang}: {coll}.{eid} {key} translation missing or stale")
    if not STAMP.exists():
        errors.append("site/ was never built; run `python -m wiki build`")
    elif STAMP.read_text(encoding="utf-8").strip() != input_hash():
        errors.append("site/ is out of date with facts/content; run `python -m wiki build`")
    return errors, warnings


def catalog_references(facts: dict) -> list[str]:
    """Reject broken graph edges before rendering tables or rewards."""
    errors = []
    edges = {"tables": {"host": "dealers", "series": "series", "rules": "chaos_rules", "items": "items",
                        "products": "items", "environment_rules": "environment_rules"},
             "dealers": {"tables": "tables"}, "upgrades": {"mode": "tables", "requires": "upgrades"},
             "cosmetics": {"series": "series", "achievements": "achievements"},
             "achievements": {"cosmetics": "cosmetics"}}
    for coll, fields in edges.items():
        for eid, entry in facts.get(coll, {}).items():
            for field, target in fields.items():
                values = entry.get(field)
                values = values if isinstance(values, list) else [values] if values is not None else []
                for value in values:
                    if value not in facts.get(target, {}):
                        errors.append(f"{coll}.{eid}.{field}: unknown {target} id `{value}`")
    return errors


def _links(site: Path) -> list[str]:
    errors = []
    for page in site.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for target in re.findall(r'(?:href|src)="([^"]+)"', text):
            url = urlparse(target)
            if url.scheme or target.startswith("#"):
                continue
            path = (page.parent / unquote(url.path)).resolve()
            if not path.exists():
                errors.append(f"{page.relative_to(site).as_posix()}: broken link {target}")
            elif url.fragment and path.suffix == ".html":
                if f'id="{url.fragment}"' not in path.read_text(encoding="utf-8"):
                    errors.append(f"{page.relative_to(site).as_posix()}: missing anchor {target}")
    return errors


def check(strict: bool = False) -> int:
    errors, warnings = problems()
    if strict:
        errors, warnings = errors + warnings, []
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"check: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0
