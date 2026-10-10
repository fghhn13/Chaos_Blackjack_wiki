"""A small Markdown subset, stdlib only.

Blocks: front matter, #-headings, paragraphs, - / 1. lists (one level), > quotes,
``` fences, | tables |, --- rules, and raw-HTML tokens (a line that is exactly
`\\x00N\\x00`, filled in by the caller). Inline: `code`, **bold**, *em*,
[text](url), ![alt](src).
"""

from __future__ import annotations

import html
import re

RAW = re.compile(r"^\x00(\d+)\x00$")


def front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, text[end + 5:]


def slug(text: str) -> str:
    s = re.sub(r"<[^>]+>", "", text).strip().lower()
    s = re.sub(r"[^\w一-鿿]+", "-", s).strip("-")
    return s or "section"


def inline(text: str) -> str:
    codes: list[str] = []

    def keep(m: re.Match[str]) -> str:
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x01{len(codes) - 1}\x01"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", r'<img src="\2" alt="\1">', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x01(\d+)\x01", lambda m: codes[int(m.group(1))], text)


def render(text: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Markdown -> (html, headings[(level, id, text)])."""
    lines = text.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    heads: list[tuple[int, str, str]] = []
    para: list[str] = []
    i = 0

    def flush() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            flush()
            i += 1
        elif RAW.match(s):
            flush()
            out.append(s)
            i += 1
        elif s.startswith("```"):
            flush()
            lang = s[3:].strip()
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>")
        elif m := re.match(r"^(#{1,4})\s+(.*)$", s):
            flush()
            level, title = len(m.group(1)), inline(m.group(2))
            hid = slug(title)
            heads.append((level, hid, re.sub(r"<[^>]+>", "", title)))
            out.append(f'<h{level} id="{hid}">{title}</h{level}>')
            i += 1
        elif re.match(r"^(-{3,}|\*{3,})$", s):
            flush()
            out.append("<hr>")
            i += 1
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append(_table(rows))
        elif s.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{render(chr(10).join(quote))[0]}</blockquote>")
        elif re.match(r"^([-*]|\d+\.)\s+", s):
            flush()
            ordered = bool(re.match(r"^\d+\.", s))
            items: list[str] = []
            while i < len(lines):
                t = lines[i].strip()
                if m := re.match(r"^([-*]|\d+\.)\s+(.*)$", t):
                    items.append(m.group(2))
                elif t and items and lines[i].startswith((" ", "\t")):
                    items[-1] += " " + t
                else:
                    break
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        else:
            para.append(s)
            i += 1
    flush()
    return "\n".join(out), heads


def _table(rows: list[list[str]]) -> str:
    head, body = rows[0], rows[1:]
    if body and all(re.match(r"^:?-+:?$", c) for c in body[0]):
        body = body[1:]
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'
