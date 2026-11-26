#!/usr/bin/env python3
# Layout adapted from https://github.com/santana-iago/santana-iago (MIT).
# See LICENSE.profile-template in this directory.
from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from urllib.parse import urldefrag


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "assets" / "generated"
DESKTOP_WIDTH = 880
MOBILE_WIDTH = 336
DESKTOP_BREAKPOINT = 1280
SECTIONS = (
    ("featured", "Featured work", 3),
    ("websites", "Institutional websites", 2),
    ("other_work", "Other work", 2),
)
THEMES = {
    "light": {
        "text": "#1f2328",
        "muted": "#57606a",
        "line": "#d0d7de",
        "soft_line": "#eaeef2",
        "card": "#f6f8fa",
        "mark": "#ffffff",
    },
    "dark": {
        "text": "#f0f6fc",
        "muted": "#9aa4b2",
        "line": "#30363d",
        "soft_line": "#21262d",
        "card": "#161b22",
        "mark": "#0d1117",
    },
}


def svg_open(width: int, height: int, theme: str) -> list[str]:
    colors = THEMES[theme]
    styles = f"""
.line{{stroke:{colors["line"]}}}.soft-line{{stroke:{colors["soft_line"]}}}
.card{{fill:{colors["card"]};stroke:{colors["line"]}}}
.mark{{fill:{colors["mark"]};stroke:{colors["line"]}}}
.linkedin{{fill:#0a66c2}}.linkedin-text{{fill:#fff}}
.arrow{{stroke:{colors["muted"]};fill:none}}
text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;fill:{colors["text"]}}}
.mono,.label,.status,.intro,.mark-text{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}
.hero{{font-family:Georgia,'Times New Roman',serif;font-weight:600;font-style:italic;font-size:34px}}
.hero-mobile{{font-size:24px}}
.intro,.status{{font-size:13px}}
.label{{font-size:10px;font-weight:700;letter-spacing:1.1px}}
.mark-text{{font-size:12px;font-weight:700}}
.section{{font-size:15px;font-weight:500}}.section-mobile{{font-size:18px;font-weight:600}}
.title{{font-size:14px;font-weight:700}}.title-mobile{{font-size:17px}}
.description{{font-size:12px}}.description-mobile{{font-size:14.5px}}
.label,.intro,.description{{fill:{colors["muted"]}}}
"""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<style>{styles}</style>",
    ]


def add_text(parts: list[str], x: float, y: float, value: str, css: str, *, center: bool = False) -> None:
    anchor = ' text-anchor="middle"' if center else ""
    parts.append(f'<text x="{x}" y="{y}" class="{css}"{anchor}>{html.escape(value)}</text>')


def add_lines(parts: list[str], x: int, y: int, lines: list[str], css: str, line_height: int) -> None:
    for index, line in enumerate(lines):
        add_text(parts, x, y + index * line_height, line, css)


def line(parts: list[str], x1: float, y1: float, x2: float, y2: float, css: str = "line") -> None:
    parts.append(f'<line class="{css}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')


def mark(parts: list[str], x: int, y: int, size: int, label: str, *, linkedin: bool = False) -> None:
    css = "linkedin" if linkedin else "mark"
    text_css = "mark-text linkedin-text" if linkedin else "mark-text"
    parts.append(f'<rect class="{css}" x="{x}" y="{y}" width="{size}" height="{size}" rx="8"/>')
    add_text(parts, x + size / 2, y + size / 2 + 4, label, text_css, center=True)


def thumbnail(parts: list[str], x: int, y: int, width: int, height: int, path: str) -> None:
    encoded = base64.b64encode((ROOT / path).read_bytes()).decode("ascii")
    frame = f'x="{x}" y="{y}" width="{width}" height="{height}"'
    parts.append(f'<clipPath id="thumbnail"><rect {frame} rx="8"/></clipPath>')
    parts.append(f'<rect class="mark" {frame} rx="8"/>')
    parts.append(
        f'<image {frame} href="data:image/png;base64,{encoded}" '
        'preserveAspectRatio="xMidYMid meet" clip-path="url(#thumbnail)"/>'
    )


def arrow(parts: list[str], x: int, y: int) -> None:
    parts.append(
        f'<path d="M{x-4} {y+4} L{x+4} {y-4} M{x-1} {y-4} H{x+4} V{y+1}" '
        'class="arrow" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def wrap_words(value: str, max_chars: int) -> list[str]:
    lines = []
    current = ""
    for word in value.split():
        candidate = f"{current} {word}" if current else word
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def svg_close(parts: list[str]) -> str:
    return "\n".join([*parts, "</svg>", ""])


def hero(meta: dict, mobile: bool, theme: str) -> str:
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    left, name_y, intro_y = (16, 36, 62) if mobile else (3, 58, 91)
    intro = wrap_words(meta["introduction"], 36 if mobile else 94)
    bottom = intro_y + (len(intro) - 1) * 18 + 17
    parts = svg_open(width, bottom + 8, theme)
    line(parts, left, 6, width - left, 6)
    add_text(parts, left, name_y, meta["name"], "hero hero-mobile" if mobile else "hero")
    add_lines(parts, left, intro_y, intro, "intro", 18)
    line(parts, left, bottom, width - left, bottom)
    return svg_close(parts)


def status(items: list[dict], mobile: bool, theme: str) -> str:
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    height = 60 * len(items) + 6 if mobile else 72
    parts = svg_open(width, height, theme)
    if mobile:
        for index, item in enumerate(items):
            y = 60 * index
            add_text(parts, 16, y + 21, item["label"], "label mono")
            add_text(parts, 16, y + 43, item["value"], "status")
            line(parts, 16, y + 55, width - 16, y + 55)
    else:
        column_width = width / len(items)
        for index, item in enumerate(items):
            x = round(column_width * index)
            if index:
                line(parts, x, 16, x, height - 16)
            add_text(parts, x + 14, 26, item["label"], "label mono")
            add_text(parts, x + 14, 48, item["value"], "status")
        line(parts, 0, height - 1, width, height - 1)
    return svg_close(parts)


def contact(item: dict, mobile: bool, theme: str) -> str:
    width, height = (MOBILE_WIDTH, 76) if mobile else (265, 76)
    parts = svg_open(width, height, theme)
    parts.append(f'<rect class="card" x=".5" y="3.5" width="{width - 1}" height="68" rx="10"/>')
    if item.get("image"):
        thumbnail(parts, 20, 23, 28, 28, item["image"])
    else:
        mark(parts, 20, 23, 28, item["mark"], linkedin=item["label"] == "LinkedIn")
    add_text(parts, 60, 28, item["label"].upper(), "label mono")
    values = wrap_words(item["value"], 30 if mobile else 22)
    add_lines(parts, 60, 51 if len(values) == 1 else 45, values, "status", 15)
    arrow(parts, width - 20, 38)
    return svg_close(parts)


def heading(title: str, mobile: bool, theme: str) -> str:
    width, height, left = (MOBILE_WIDTH, 52, 16) if mobile else (DESKTOP_WIDTH, 42, 3)
    parts = svg_open(width, height, theme)
    add_text(parts, left, height - 20, title, "section section-mobile" if mobile else "section")
    line(parts, left, height - 7, width - left, height - 7)
    return svg_close(parts)


def mobile_card(item: dict, theme: str) -> str:
    titles = wrap_words(item["title"], 25)
    categories = wrap_words(item["category"], 36)
    descriptions = wrap_words(item["description"], 39)
    title_y = 37 if len(titles) == 1 else 27
    category_y = max(69, title_y + 20 * (len(titles) - 1) + 21)
    description_y = category_y + 14 * (len(categories) - 1) + 23
    bottom = description_y + 20 * (len(descriptions) - 1) + 17
    parts = svg_open(MOBILE_WIDTH, bottom + 7, theme)
    thumbnail(parts, 16, 12, 54, 44, item["image"])
    add_lines(parts, 76, title_y, titles, "title title-mobile", 20)
    add_lines(parts, 16, category_y, categories, "label mono", 14)
    add_lines(parts, 16, description_y, descriptions, "description description-mobile", 20)
    if item.get("url"):
        arrow(parts, MOBILE_WIDTH - 20, 24)
    line(parts, 16, bottom, MOBILE_WIDTH - 16, bottom)
    return svg_close(parts)


def desktop_cards(items: list[dict], theme: str, *, featured: bool) -> list[str]:
    width = 276 if featured else 390
    title_x, title_y = (72, 24) if featured else (82, 26)
    description_x = 8 if featured else title_x
    titles = [wrap_words(item["title"], 20 if featured else 33) for item in items]
    categories = [wrap_words(item["category"], 23 if featured else 37) for item in items]
    descriptions = [wrap_words(item["description"], 40 if featured else 44) for item in items]
    category_y = max(62 if featured else 53, title_y + (max(map(len, titles)) - 1) * 17 + 22)
    description_y = category_y + (max(map(len, categories)) - 1) * 13 + (28 if featured else 21)
    bottom = description_y + (max(map(len, descriptions)) - 1) * 17 + 15
    slides = []
    for index, item in enumerate(items):
        parts = svg_open(width, bottom + 7, theme)
        thumbnail(parts, 8 if featured else 12, 10 if featured else 28, 54, 44, item["image"])
        add_lines(parts, title_x, title_y, titles[index], "title", 17)
        add_lines(parts, title_x, category_y, categories[index], "label mono", 13)
        add_lines(parts, description_x, description_y, descriptions[index], "description", 17)
        if item.get("url"):
            arrow(parts, width - 18, 17)
        if index + 1 < len(items):
            line(parts, width - 1, 1, width - 1, bottom, "soft-line")
        line(parts, 2, bottom, width - 2, bottom)
        slides.append(svg_close(parts))
    return slides


def picture(name: str, alt: str, url: str | None = None) -> str:
    base = f"./assets/generated/{name}"
    images = []
    for theme in THEMES:
        marker = f"#gh-{theme}-mode-only"
        href = html.escape(urldefrag(url).url + marker, quote=True) if url else marker
        tab = "" if url else ' tabindex="-1"'
        images.append(
            f'<a href="{href}"{tab}><picture>'
            f'<source media="(min-width: {DESKTOP_BREAKPOINT}px)" srcset="{base}-desktop-{theme}.svg{marker}">'
            f'<img src="{base}-mobile-{theme}.svg{marker}" alt="{html.escape(alt, quote=True)}">'
            '</picture></a>'
        )
    return "".join(images)


def card_picture(item: dict) -> str:
    alt = f'{item["title"]}. {item["description"]}'
    return picture(f'work-{item["id"]}', alt, item.get("url"))


def readme(profile: dict) -> str:
    meta = profile["meta"]
    contacts = profile["contacts"]
    status_alt = ". ".join(item["value"].replace(" @ ", " at ") for item in profile["status"])
    lines = [
        '<div align="center">',
        picture("hero", f'{meta["full_name"]}. {meta["introduction"]}'),
        picture("status", status_alt),
        "</div>",
        "",
        '<p align="center">',
        "&#8195;".join(picture(f'contact-{item["label"].lower()}', item["label"], item["url"]) for item in contacts),
        "</p>",
        "",
        '<p align="center">',
        " · ".join(f'<a href="#section-{key.replace("_", "-")}">{title}</a>' for key, title, _ in SECTIONS),
        "</p>",
        "",
    ]
    for key, title, row_size in SECTIONS:
        slug = key.replace("_", "-")
        entries = profile[key]
        lines.extend([
            f'<a name="section-{slug}"></a>',
            "",
            '<div align="center">',
            picture(f"{slug}-heading", title),
        ])
        for start in range(0, len(entries), row_size):
            cards = "".join(card_picture(item) for item in entries[start:start + row_size])
            lines.append(f'<div align="center">{cards}</div>')
        lines.extend(["</div>", ""])
    lines.extend([
        "<details>",
        "<summary>Accessible text version</summary>",
        "",
        f'# {meta["full_name"]}',
        "",
        meta["introduction"],
        "",
        " · ".join(f'[{item["label"]}]({item["url"]})' for item in contacts),
        "",
    ])
    for key, title, _ in SECTIONS:
        lines.extend([f"## {title}", ""])
        for item in profile[key]:
            lines.extend([f'### {item["title"]}', "", f'*{item["category"]}*', "", item["description"], ""])
            if item.get("details"):
                lines.extend([item["details"], ""])
            if item.get("code_url"):
                lines.extend([f'[Live site]({item["url"]}) · [Source code]({item["code_url"]})', ""])
            elif item.get("url"):
                lines.extend([f'[Open {item["title"]}]({item["url"]})', ""])
    lines.extend(["## Coursework and practice", ""])
    for item in profile["practice"]:
        lines.append(f'- [{item["title"]}]({item["url"]}) — {item["description"]}')
    lines.extend(["", "## Technical toolkit", ""])
    for group in profile["toolkit"]:
        lines.append(f'- **{group["label"]}** · {", ".join(group["items"])}')
    lines.extend([
        "",
        "</details>",
        "",
        "<!-- Layout adapted from github.com/santana-iago/santana-iago under MIT.",
        "Edit profile.json and run python scripts/build_profile.py to regenerate. -->",
        "",
    ])
    return "\n".join(lines)


def save_generated(profile: dict) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for layout, mobile in (("desktop", False), ("mobile", True)):
            assets = {
                "hero": hero(profile["meta"], mobile, theme),
                "status": status(profile["status"], mobile, theme),
            }
            for item in profile["contacts"]:
                assets[f'contact-{item["label"].lower()}'] = contact(item, mobile, theme)
            for key, title, row_size in SECTIONS:
                assets[f'{key.replace("_", "-")}-heading'] = heading(title, mobile, theme)
                entries = profile[key]
                for start in range(0, len(entries), row_size):
                    items = entries[start:start + row_size]
                    if mobile:
                        cards = [mobile_card(item, theme) for item in items]
                    else:
                        cards = desktop_cards(items, theme, featured=key == "featured")
                    for item, card in zip(items, cards):
                        assets[f'work-{item["id"]}'] = card
            for name, content in assets.items():
                (GENERATED / f"{name}-{layout}-{theme}.svg").write_text(content, encoding="utf-8", newline="\n")
    (ROOT / "README.md").write_text(readme(profile), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    save_generated(json.loads((ROOT / "profile.json").read_text(encoding="utf-8")))
