#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG, lines fade in on a stagger.

Usage: python make_info_card.py
       STATIC=1 python make_info_card.py   # frozen frame for local previews
Writes: info-card.svg

Edit TITLE and FIELDS below with your own info.
"""
import os

TITLE = "you@github"
FIELDS = [
    ("Now", "Unemployed"),
    ("Prev", "Studied Finance"),
    ("Stack", "Python . SQL . C++"),
    ("Highlights", "Can do a kickflip"),
]
ACCENT = "#39d353"
LABEL_COLOR = "#8b949e"
TEXT_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
FONT_SIZE = 14
LINE_HEIGHT = 26
PADDING = 20
WIDTH = 490

OUTPUT = "info-card.svg"


def build_svg():
    static = os.environ.get("STATIC") == "1"
    height = PADDING * 2 + LINE_HEIGHT * (len(FIELDS) + 2)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}">'
    )
    parts.append(
        "<style>text{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace;"
        f"font-size:{FONT_SIZE}px;}}"
        f".label{{fill:{ACCENT};font-weight:600;}} .val{{fill:{TEXT_COLOR};}}</style>"
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="8" '
        f'fill="{BG_COLOR}" stroke="{BORDER_COLOR}"/>'
    )
    parts.append(
        f'<text x="{PADDING}" y="{PADDING+14}" style="fill:{ACCENT};font-weight:700;'
        f"font-family:'SFMono-Regular',Consolas,monospace;font-size:{FONT_SIZE}px;\">{TITLE}</text>"
    )
    parts.append(
        f'<line x1="{PADDING}" y1="{PADDING+22}" x2="{WIDTH-PADDING}" y2="{PADDING+22}" '
        f'stroke="{BORDER_COLOR}"/>'
    )

    y0 = PADDING + 22 + LINE_HEIGHT
    for i, (label, value) in enumerate(FIELDS):
        y = y0 + i * LINE_HEIGHT
        delay = i * 0.18
        opacity = "1" if static else "0"
        anim = (
            ""
            if static
            else (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.35s" fill="freeze"/>'
            )
        )
        parts.append(
            f'<g style="opacity:{opacity}">'
            f'<text x="{PADDING}" y="{y}" class="label">{label}:</text>'
            f'<text x="{PADDING+110}" y="{y}" class="val">{value}</text>'
            f"{anim}</g>"
        )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")
