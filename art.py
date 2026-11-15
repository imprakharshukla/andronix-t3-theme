"""The dawn glow behind the chat, as an SVG data URL.

The Andronix halftone style: a grid of cells, each cell's brightness becomes a dot size
(dotSizes and levels from palette.json). The SVG is only the dot shapes, in one colour; theme.css
uses it as a mask over a palette gradient, so one image serves dark and light.
A dot is a zero-length line with round caps, which keeps the file to a few kilobytes.
Standard library only.

    python3 art.py     # writes build/art.svg for a look
"""
import json
import math
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent


PALETTE = json.loads((ROOT / "palette.json").read_text())

COLS, ROWS = 96, 54          # 16:9 grid; the image covers the chat column from its bottom right corner
SUN_X, SUN_Y = 0.72, 1.06    # the sun sits just under the bottom edge, right of centre
GLOW_X, GLOW_Y = 0.40, 0.46  # glow radius as a share of width and height
SEED = 7


def hash01(x: int, y: int, s: int = 0) -> float:
    h = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 4294967295


def noise(x: float, y: float) -> float:
    xi, yi = math.floor(x), math.floor(y)
    u, v = x - xi, y - yi
    u, v = u * u * (3 - 2 * u), v * v * (3 - 2 * v)
    a, b, c, d = hash01(xi, yi, SEED), hash01(xi + 1, yi, SEED), hash01(xi, yi + 1, SEED), hash01(xi + 1, yi + 1, SEED)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def brightness(col: int, row: int) -> float:
    u, v = (col + 0.5) / COLS, (row + 0.5) / ROWS
    d2 = ((u - SUN_X) / GLOW_X) ** 2 + ((v - SUN_Y) / GLOW_Y) ** 2
    glow = math.exp(-d2 * 1.6)
    haze = (0.55 * noise(col * 0.11, row * 0.34) + 0.45 * noise(col * 0.27, row * 0.8) - 0.5) * 0.22 * v
    return max(0.0, min(1.0, glow * 0.95 + haze))


def build_svg() -> str:
    levels, sizes = PALETTE["levels"], PALETTE["dotSizes"]
    paths = {}
    for row in range(ROWS):
        for col in range(COLS):
            level = sum(brightness(col, row) >= t for t in levels)
            if level:
                paths.setdefault(level, []).append((col, row))
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {COLS * 2} {ROWS * 2}' "
           f"preserveAspectRatio='xMaxYMax slice' fill='none' stroke='#000' stroke-linecap='round'>"]
    for level in sorted(paths):
        d, px, py = [], 0, 0
        for col, row in paths[level]:
            x, y = col * 2 + 1, row * 2 + 1          # cell centre, 2 units per cell
            d.append(f"m{x - px} {y - py}h0".replace(" -", "-"))
            px, py = x, y
        out.append(f"<path stroke-width='{round(sizes[level] * 4, 2):g}' d='M0 0{''.join(d)}'/>")
    out.append("</svg>")
    return "".join(out)


def build_art_data_url() -> str:
    return "data:image/svg+xml," + quote(build_svg(), safe="/:=' ")


if __name__ == "__main__":
    out = ROOT / "build" / "art.svg"
    out.parent.mkdir(exist_ok=True)
    out.write_text(build_svg())
    print(out, len(build_art_data_url()), "characters as a data URL")
