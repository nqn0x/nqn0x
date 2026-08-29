#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing, monochrome ASCII SVG.

Usage: python make_ascii_svg.py
Reads:  source-prepped.png
Writes: avi-ascii.svg
"""
from PIL import Image, ImageOps

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 53
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
FILL_COLOR = "#c9d1d9"  # single light-gray fill -- monochrome only, no rainbow coloring

INPUT = "source-prepped.png"
OUTPUT = "avi-ascii.svg"


def image_to_ascii_grid(path, cols, rows):
    img = Image.open(path).convert("L")

    # Preserve the photo's real proportions instead of stretching it to
    # exactly cols x rows -- pad with white (blank glyph) to fill the rest.
    fitted = ImageOps.pad(
        img, (cols, rows), color=255,
        centering=(0.5, 0.35),  # bias slightly upward, portraits have headroom
    )

    pixels = list(fitted.getdata())
    grid = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0 dark -> 255 bright
            idx = int((255 - brightness) / 255 * (len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        grid.append("".join(row_chars))
    return grid


def build_svg(grid):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}">'
    )
    parts.append('<rect width="100%" height="100%" fill="transparent"/>')
    parts.append(
        "<style>text{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace;"
        f"font-size:{FONT_SIZE}px;fill:{FILL_COLOR};white-space:pre;}}</style>"
    )

    row_duration = 0.9
    stagger = 0.045

    defs = ["<defs>"]
    for r in range(ROWS):
        y = r * CHAR_H
        defs.append(
            f'<clipPath id="clip{r}"><rect x="0" y="{y:.1f}" width="0" height="{CHAR_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{width:.0f}" '
            f'begin="{r * stagger:.3f}s" dur="{row_duration}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/></rect></clipPath>'
        )
    defs.append("</defs>")
    parts.append("".join(defs))

    for r, row in enumerate(grid):
        y = (r + 1) * CHAR_H - CHAR_H * 0.2
        escaped = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(
            f'<g clip-path="url(#clip{r})"><text x="0" y="{y:.1f}">{escaped}</text></g>'
        )

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    grid = image_to_ascii_grid(INPUT, COLS, ROWS)
    svg = build_svg(grid)
    with open(OUTPUT, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT} ({COLS}x{ROWS} chars)")
