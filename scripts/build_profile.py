#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "assets" / "generated"
DESKTOP_WIDTH = 880
MOBILE_WIDTH = 360


def load_profile() -> dict[str, Any]:
    return json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def wrap_words(value: str, max_chars: int, max_lines: int) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > max_chars:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines or [""]


def theme_css() -> str:
    light = """
.line{stroke:#d0d7de}.soft-line{stroke:#eaeef2}.card{fill:#fffafb;stroke:#e4c8ce}
.card-neutral{fill:#f6f8fa;stroke:#d0d7de}.text{fill:#1f2328}.muted{fill:#57606a}
.label{fill:#6e5a60}.accent{fill:#c45168}.accent-stroke{stroke:#d4687b}.accent-soft{fill:#fbe7eb}
.chip{fill:#ffffff;stroke:#e0bec6}.chip-text{fill:#713c48}.arrow{stroke:#c45168;fill:none}
"""
    dark = """
.line{stroke:#30363d}.soft-line{stroke:#21262d}.card{fill:#181316;stroke:#51313a}
.card-neutral{fill:#161b22;stroke:#30363d}.text{fill:#f0f6fc}.muted{fill:#9aa4b2}
.label{fill:#b8a0a6}.accent{fill:#ed9092}.accent-stroke{stroke:#ed9092}.accent-soft{fill:#352126}
.chip{fill:#20191c;stroke:#633d47}.chip-text{fill:#f0b6bb}.arrow{stroke:#ed9092;fill:none}
"""
    typography = """
.ui{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
"""
    return typography + light + f"@media (prefers-color-scheme:dark){{{dark}}}"


def svg_open(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<style>{theme_css()}</style>",
    ]


def svg_close(parts: list[str]) -> str:
    parts.append("</svg>")
    return "".join(parts)


def add_text(
    parts: list[str],
    x: float,
    y: float,
    value: str,
    cls: str,
    size: float,
    weight: int = 400,
    anchor: str | None = None,
    letter_spacing: float | None = None,
    italic: bool = False,
) -> None:
    attrs = [
        f'x="{x}"',
        f'y="{y}"',
        f'class="{cls}"',
        f'font-size="{size}"',
        f'font-weight="{weight}"',
    ]
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{letter_spacing}"')
    if italic:
        attrs.append('font-style="italic"')
    parts.append(f"<text {' '.join(attrs)}>{esc(value)}</text>")


def add_multiline(
    parts: list[str],
    x: float,
    y: float,
    lines: list[str],
    cls: str,
    size: float,
    weight: int,
    line_height: float,
    letter_spacing: float | None = None,
) -> None:
    letter_attr = f' letter-spacing="{letter_spacing}"' if letter_spacing is not None else ""
    parts.append(
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" '
        f'font-weight="{weight}"{letter_attr}>'
    )
    for index, line in enumerate(lines):
        parts.append(f'<tspan x="{x}" dy="{0 if index == 0 else line_height}">{esc(line)}</tspan>')
    parts.append("</text>")


def add_round_rect(
    parts: list[str], x: float, y: float, width: float, height: float, radius: float, cls: str
) -> None:
    parts.append(
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" class="{cls}"/>'
    )


def add_arrow(parts: list[str], x: float, y: float) -> None:
    parts.append(
        f'<path d="M{x-5} {y+5} L{x+5} {y-5} M{x} {y-5} H{x+5} V{y}" '
        'class="arrow" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def generate_hero(profile: dict[str, Any], mobile: bool) -> str:
    meta = profile["meta"]
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    height = 208 if mobile else 170
    parts = svg_open(width, height)
    margin = 18 if mobile else 4
    parts.append(f'<line x1="{margin}" y1="8" x2="{width-margin}" y2="8" class="line"/>')

    if mobile:
        add_text(parts, 18, 41, meta["eyebrow"], "mono accent", 8.2, 700, letter_spacing=1.0)
        add_text(parts, 18, 80, meta["name"], "ui text", 31, 750, letter_spacing=-0.8)
        headline = wrap_words(meta["headline"], 31, 2)
        add_multiline(parts, 18, 112, headline, "ui text", 17.5, 650, 23)
        summary = wrap_words(meta["summary"], 46, 3)
        add_multiline(parts, 18, 166, summary, "mono muted", 9.2, 400, 14)
        parts.append('<circle cx="326" cy="43" r="17" class="accent-soft"/>')
        parts.append('<circle cx="326" cy="43" r="5" class="accent"/>')
    else:
        add_text(parts, 6, 38, meta["eyebrow"], "mono accent", 9.5, 700, letter_spacing=1.45)
        add_text(parts, 6, 83, meta["name"], "ui text", 39, 750, letter_spacing=-1.1)
        add_text(parts, 6, 119, meta["headline"], "ui text", 22, 650, letter_spacing=-0.35)
        add_text(parts, 8, 146, meta["summary"], "mono muted", 11.4, 400)
        parts.append('<circle cx="825" cy="55" r="27" class="accent-soft"/>')
        parts.append('<circle cx="825" cy="55" r="8" class="accent"/>')
        parts.append('<path d="M760 104 H848 M782 118 H862" class="accent-stroke" stroke-width="1.2" opacity="0.7"/>')

    parts.append(f'<line x1="{margin}" y1="{height-8}" x2="{width-margin}" y2="{height-8}" class="line"/>')
    return svg_close(parts)


def generate_status(profile: dict[str, Any], mobile: bool) -> str:
    items = profile["status"]
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    height = 278 if mobile else 174
    parts = svg_open(width, height)
    margin = 18 if mobile else 4
    add_text(parts, margin, 27, "RIGHT NOW", "mono label", 8.5, 700, letter_spacing=1.5)
    parts.append(f'<line x1="{margin}" y1="42" x2="{width-margin}" y2="42" class="line"/>')

    if mobile:
        for i, item in enumerate(items):
            y = 68 + i * 51
            add_text(parts, margin, y, item["label"], "mono accent", 8.3, 700, letter_spacing=1.25)
            add_text(parts, margin, y + 21, item["value"], "ui text", 13.2, 600)
            if i < len(items) - 1:
                parts.append(f'<line x1="{margin}" y1="{y+33}" x2="{width-margin}" y2="{y+33}" class="soft-line"/>')
    else:
        cell_width = (width - 8) / 2
        for i, item in enumerate(items):
            row, col = divmod(i, 2)
            x = 8 + col * cell_width
            y = 72 + row * 54
            if col == 1:
                parts.append(f'<line x1="{x-16}" y1="56" x2="{x-16}" y2="158" class="soft-line"/>')
            add_text(parts, x, y, item["label"], "mono accent", 8.5, 700, letter_spacing=1.35)
            add_text(parts, x, y + 22, item["value"], "ui text", 14.2, 600)
        parts.append('<line x1="4" y1="112" x2="876" y2="112" class="soft-line"/>')
    parts.append(f'<line x1="{margin}" y1="{height-6}" x2="{width-margin}" y2="{height-6}" class="line"/>')
    return svg_close(parts)


def generate_header(title: str, mobile: bool) -> str:
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    height = 58 if mobile else 52
    parts = svg_open(width, height)
    margin = 18 if mobile else 4
    add_text(parts, margin, 29, title.lower(), "ui text", 18 if mobile else 15, 650, letter_spacing=-0.2)
    parts.append(f'<line x1="{margin}" y1="{height-6}" x2="{width-margin}" y2="{height-6}" class="line"/>')
    return svg_close(parts)


def generate_focus_card(item: dict[str, Any], mobile: bool) -> str:
    width, height = (328, 210) if mobile else (284, 246)
    parts = svg_open(width, height)
    add_round_rect(parts, 2, 2, width - 4, height - 4, 14, "card")
    parts.append(f'<rect x="2" y="2" width="{width-4}" height="5" rx="3" class="accent"/>')
    add_round_rect(parts, 18, 20, 40, 40, 20, "accent-soft")
    add_text(parts, 38, 46, item["mark"], "mono accent", 11, 800, anchor="middle", letter_spacing=0.8)

    if mobile:
        title_lines = wrap_words(item["title"], 30, 2)
        add_multiline(parts, 18, 88, title_lines, "ui text", 18, 720, 22)
        category_y = 88 + (len(title_lines) - 1) * 22 + 27
        cat_lines = wrap_words(item["category"], 42, 2)
        add_multiline(parts, 18, category_y, cat_lines, "mono accent", 8.2, 700, 12, 0.65)
        desc_y = category_y + (len(cat_lines) - 1) * 12 + 28
        desc_lines = wrap_words(item["description"], 48, 3)
        add_multiline(parts, 18, desc_y, desc_lines, "ui muted", 11.5, 400, 16)
    else:
        title_lines = wrap_words(item["title"], 26, 2)
        add_multiline(parts, 18, 92, title_lines, "ui text", 17, 720, 22)
        category_y = 92 + (len(title_lines) - 1) * 22 + 27
        cat_lines = wrap_words(item["category"], 34, 2)
        add_multiline(parts, 18, category_y, cat_lines, "mono accent", 7.8, 700, 12, 0.6)
        desc_y = category_y + (len(cat_lines) - 1) * 12 + 31
        desc_lines = wrap_words(item["description"], 38, 4)
        add_multiline(parts, 18, desc_y, desc_lines, "ui muted", 11.3, 400, 17)
    return svg_close(parts)


def generate_experience_card(item: dict[str, Any], mobile: bool) -> str:
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    height = 184 if mobile else 150
    margin = 18 if mobile else 4
    parts = svg_open(width, height)
    add_round_rect(parts, margin, 2, width - 2 * margin, height - 8, 14, "card-neutral")
    parts.append(f'<rect x="{margin}" y="2" width="5" height="{height-8}" rx="3" class="accent"/>')
    if mobile:
        add_text(parts, 38, 35, "PREVIOUS EXPERIENCE", "mono accent", 8.2, 700, letter_spacing=1.2)
        title_lines = wrap_words(item["title"], 38, 2)
        add_multiline(parts, 38, 64, title_lines, "ui text", 16.5, 720, 21)
        cat_y = 64 + (len(title_lines) - 1) * 21 + 26
        cat_lines = wrap_words(item["category"], 43, 2)
        add_multiline(parts, 38, cat_y, cat_lines, "mono label", 7.8, 700, 11, 0.65)
        desc_y = cat_y + (len(cat_lines) - 1) * 11 + 27
        desc_lines = wrap_words(item["description"], 48, 3)
        add_multiline(parts, 38, desc_y, desc_lines, "ui muted", 10.7, 400, 15)
    else:
        add_text(parts, 28, 34, "PREVIOUS EXPERIENCE", "mono accent", 8.4, 700, letter_spacing=1.3)
        add_text(parts, 28, 67, item["title"], "ui text", 19, 720, letter_spacing=-0.2)
        add_text(parts, 28, 93, item["category"], "mono label", 8.2, 700, letter_spacing=0.85)
        desc_lines = wrap_words(item["description"], 106, 2)
        add_multiline(parts, 28, 122, desc_lines, "ui muted", 11.4, 400, 17)
    return svg_close(parts)


def generate_project_card(item: dict[str, Any], mobile: bool) -> str:
    width, height = (328, 194) if mobile else (284, 226)
    parts = svg_open(width, height)
    add_round_rect(parts, 2, 2, width - 4, height - 4, 14, "card-neutral")
    add_text(parts, 18, 34, item["number"], "mono accent", 9, 800, letter_spacing=1.25)
    add_arrow(parts, width - 24, 27)

    if mobile:
        add_text(parts, 18, 68, item["title"], "ui text", 18, 720, letter_spacing=-0.2)
        cat_lines = wrap_words(item["category"], 43, 2)
        add_multiline(parts, 18, 96, cat_lines, "mono accent", 8.1, 700, 12, 0.6)
        desc_y = 96 + (len(cat_lines) - 1) * 12 + 30
        desc_lines = wrap_words(item["description"], 48, 3)
        add_multiline(parts, 18, desc_y, desc_lines, "ui muted", 11.2, 400, 16)
    else:
        title_lines = wrap_words(item["title"], 27, 2)
        add_multiline(parts, 18, 72, title_lines, "ui text", 17.5, 720, 22)
        cat_y = 72 + (len(title_lines) - 1) * 22 + 27
        cat_lines = wrap_words(item["category"], 34, 2)
        add_multiline(parts, 18, cat_y, cat_lines, "mono accent", 7.7, 700, 12, 0.55)
        desc_y = cat_y + (len(cat_lines) - 1) * 12 + 30
        desc_lines = wrap_words(item["description"], 38, 4)
        add_multiline(parts, 18, desc_y, desc_lines, "ui muted", 11.1, 400, 16)
    return svg_close(parts)


def generate_stack(profile: dict[str, Any], mobile: bool) -> str:
    groups = profile["stack"]
    width = MOBILE_WIDTH if mobile else DESKTOP_WIDTH
    height = 370 if mobile else 230
    parts = svg_open(width, height)
    margin = 18 if mobile else 4

    if mobile:
        for i, group in enumerate(groups):
            y = 8 + i * 88
            add_round_rect(parts, margin, y, width - 2 * margin, 76, 12, "card-neutral")
            add_text(parts, margin + 16, y + 25, group["label"], "mono accent", 8.2, 700, letter_spacing=1.2)
            items = "  ·  ".join(group["items"])
            lines = wrap_words(items, 44, 2)
            add_multiline(parts, margin + 16, y + 51, lines, "ui text", 12, 600, 16)
    else:
        card_width = (width - 24) / 2
        for i, group in enumerate(groups):
            row, col = divmod(i, 2)
            x = 4 + col * (card_width + 16)
            y = 4 + row * 108
            add_round_rect(parts, x, y, card_width, 94, 12, "card-neutral")
            add_text(parts, x + 18, y + 29, group["label"], "mono accent", 8.4, 700, letter_spacing=1.25)
            items = "  ·  ".join(group["items"])
            lines = wrap_words(items, 54, 2)
            add_multiline(parts, x + 18, y + 59, lines, "ui text", 12.5, 600, 18)
    return svg_close(parts)


def generate_contact_card(item: dict[str, Any], mobile: bool) -> str:
    width, height = (328, 78) if mobile else (430, 78)
    parts = svg_open(width, height)
    add_round_rect(parts, 2, 2, width - 4, height - 4, 13, "card")
    add_round_rect(parts, 16, 17, 42, 42, 21, "accent-soft")
    initials = "in" if item["label"] == "LINKEDIN" else "GH"
    add_text(parts, 37, 44, initials, "mono accent", 12, 800, anchor="middle")
    add_text(parts, 72, 28, item["label"], "mono label", 7.8, 700, letter_spacing=1.25)
    value = item["value"]
    max_chars = 31 if mobile else 48
    if len(value) > max_chars:
        value = value[: max_chars - 1] + "…"
    add_text(parts, 72, 52, value, "ui text", 12.3 if mobile else 13, 650)
    add_arrow(parts, width - 24, 39)
    return svg_close(parts)


def responsive_picture(base: str, alt: str, width: str | None = None) -> str:
    width_attr = f' width="{width}"' if width else ""
    return (
        f'<picture><source media="(max-width: 480px)" '
        f'srcset="./assets/generated/{base}-mobile.svg">'
        f'<img src="./assets/generated/{base}-desktop.svg"{width_attr} alt="{esc(alt)}"></picture>'
    )


def generate_readme(profile: dict[str, Any]) -> str:
    meta = profile["meta"]
    lines: list[str] = [
        '<div align="center">',
        responsive_picture("hero", f'{meta["name"]}. {meta["headline"]}', "100%"),
        responsive_picture("status", "Current roles and areas of focus.", "100%"),
        "</div>",
        "",
        "<br>",
        "",
        responsive_picture("current-header", "Current focus.", "100%"),
        '<p align="center">',
    ]

    for index, item in enumerate(profile["focus"]):
        lines.append(responsive_picture(f"focus-{index}", item["title"]))
    lines.extend([
        "</p>",
        "",
        responsive_picture("experience-header", "Previous experience.", "100%"),
        responsive_picture("experience", profile["experience"]["title"], "100%"),
        "",
        responsive_picture("projects-header", "Selected projects.", "100%"),
        '<p align="center">',
    ])
    for index, item in enumerate(profile["projects"]):
        card = responsive_picture(f"project-{index}", item["title"])
        lines.append(f'<a href="{esc(item["url"])}">{card}</a>')
    lines.extend([
        "</p>",
        "",
        responsive_picture("stack-header", "Technical toolkit.", "100%"),
        responsive_picture("stack", "Languages, web technologies, data tools, research tools, and workflow practices.", "100%"),
        "",
        responsive_picture("contact-header", "Contact.", "100%"),
        '<p align="center">',
    ])
    for index, item in enumerate(profile["contacts"]):
        card = responsive_picture(f"contact-{index}", f'{item["label"]}: {item["value"]}')
        lines.append(f'<a href="{esc(item["url"])}">{card}</a>')
    lines.extend([
        "</p>",
        "",
        responsive_picture("stats-header", "GitHub profile statistics.", "100%"),
        '<picture>',
        '  <source media="(prefers-color-scheme: dark)" srcset="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=gabrielgdrbandeira&theme=github_dark">',
        '  <img src="https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=gabrielgdrbandeira&theme=github" width="100%" alt="Gabriel Galvão GitHub profile statistics">',
        '</picture>',
        "",
        "<details>",
        "<summary>Accessible text version</summary>",
        "",
        f'# {meta["name"]}',
        f'**{meta["headline"]}**',
        "",
        meta["summary"],
        "",
        "## Current focus",
    ])
    for item in profile["focus"]:
        lines.extend([
            f'### {item["title"]}',
            f'*{item["category"]}*',
            "",
            item["description"],
            "",
        ])
    exp = profile["experience"]
    lines.extend([
        "## Previous experience",
        f'### {exp["title"]}',
        f'*{exp["category"]}*',
        "",
        exp["description"],
        "",
        "## Selected projects",
    ])
    for item in profile["projects"]:
        lines.extend([
            f'### [{item["title"]}]({item["url"]})',
            f'*{item["category"]}*',
            "",
            item["description"],
            "",
        ])
    lines.append("## Technical toolkit")
    for group in profile["stack"]:
        lines.append(f'- **{group["label"].title()}**: {", ".join(group["items"])}')
    lines.extend([
        "",
        "## Contact",
    ])
    for item in profile["contacts"]:
        lines.append(f'- [{item["label"].title()}]({item["url"]})')
    lines.extend([
        "",
        "</details>",
        "",
        "<!-- Generated from profile.json with scripts/build_profile.py. -->",
        "",
    ])
    return "\n".join(lines)


def save_generated(profile: dict[str, Any]) -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    for old_file in GENERATED.glob("*.svg"):
        old_file.unlink()

    outputs: dict[str, str] = {}
    for mobile, suffix in ((False, "desktop"), (True, "mobile")):
        outputs[f"hero-{suffix}.svg"] = generate_hero(profile, mobile)
        outputs[f"status-{suffix}.svg"] = generate_status(profile, mobile)
        outputs[f"current-header-{suffix}.svg"] = generate_header("current focus", mobile)
        outputs[f"experience-header-{suffix}.svg"] = generate_header("previous experience", mobile)
        outputs[f"projects-header-{suffix}.svg"] = generate_header("selected projects", mobile)
        outputs[f"stack-header-{suffix}.svg"] = generate_header("technical toolkit", mobile)
        outputs[f"contact-header-{suffix}.svg"] = generate_header("let's connect", mobile)
        outputs[f"stats-header-{suffix}.svg"] = generate_header("github profile statistics", mobile)
        outputs[f"experience-{suffix}.svg"] = generate_experience_card(profile["experience"], mobile)
        outputs[f"stack-{suffix}.svg"] = generate_stack(profile, mobile)
        for index, item in enumerate(profile["focus"]):
            outputs[f"focus-{index}-{suffix}.svg"] = generate_focus_card(item, mobile)
        for index, item in enumerate(profile["projects"]):
            outputs[f"project-{index}-{suffix}.svg"] = generate_project_card(item, mobile)
        for index, item in enumerate(profile["contacts"]):
            outputs[f"contact-{index}-{suffix}.svg"] = generate_contact_card(item, mobile)

    for name, content in outputs.items():
        (GENERATED / name).write_text(content, encoding="utf-8")
    (ROOT / "README.md").write_text(generate_readme(profile), encoding="utf-8")


def main() -> None:
    profile = load_profile()
    save_generated(profile)
    print(f"Generated profile README and {len(list(GENERATED.glob('*.svg')))} SVG assets.")


if __name__ == "__main__":
    main()
