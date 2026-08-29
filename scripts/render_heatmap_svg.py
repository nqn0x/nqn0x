#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53-week x 7-day heatmap SVG.

Usage: python render_heatmap_svg.py
Reads:  data/contributions.json
Writes: contrib-heatmap.svg
"""
import json

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 11
GAP = 3
COLS = 53
ROWS = 7
MARGIN_LEFT = 30
MARGIN_TOP = 20
FOOTER_H = 34

INPUT = "data/contributions.json"
OUTPUT = "contrib-heatmap.svg"


def load_data():
    with open(INPUT) as f:
        return json.load(f)


def build_svg(data):
    days = data["days"]
    stats = data["stats"]

    width = MARGIN_LEFT + COLS * (CELL + GAP)
    height = MARGIN_TOP + ROWS * (CELL + GAP) + FOOTER_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )
    parts.append('<rect width="100%" height="100%" fill="transparent"/>')
    parts.append(
        "<style>text{font-family:'SFMono-Regular',Consolas,monospace;font-size:10px;"
        "fill:#8b949e;}</style>"
    )

    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    weeks = weeks[-COLS:]  # keep the most recent 53 weeks

    for col, week in enumerate(weeks):
        for row, day in enumerate(week):
            level = max(0, min(day.get("level") or 0, len(PALETTE) - 1))
            color = PALETTE[level]
            x = MARGIN_LEFT + col * (CELL + GAP)
            y = MARGIN_TOP + row * (CELL + GAP)
            delay = (col + row * 0.3) * 0.012
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0" transform="translate(-8,-8)">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8 -8" to="0 0" begin="{delay:.3f}s" dur="0.4s" fill="freeze" '
                f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/></rect>'
            )

    legend_y = MARGIN_TOP + ROWS * (CELL + GAP) + 14
    parts.append(f'<text x="{MARGIN_LEFT}" y="{legend_y}">Less</text>')
    lx = MARGIN_LEFT + 34
    for color in PALETTE:
        parts.append(
            f'<rect x="{lx}" y="{legend_y-9}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y}">More</text>')

    total = stats.get("total_active_days", 0)
    footer_y = legend_y + 16
    parts.append(
        f'<text x="{MARGIN_LEFT}" y="{footer_y}" style="fill:#c9d1d9;">'
        f'{total} contributions in the last year &#183; '
        f'streak {stats.get("current_streak", 0)} (best {stats.get("longest_streak", 0)})'
        f"</text>"
    )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    data = load_data()
    svg = build_svg(data)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT}")
