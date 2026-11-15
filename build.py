"""Andronix theme for T3 Code: palette -> andronix.json (dark, with a light variant).

    python3 build.py            # write andronix.json and print the contrast table
    python3 build.py --check    # contrast table only; exit 1 when a pair fails WCAG AA

Colours come from palette.json. Anything that is not a palette colour is a blend of two palette
colours (mix), so the theme never leaves the brand hues. The three status families (error,
warning, update) are the exception: see STATUS below.
Standard library only.
"""
import json
import re
import sys
from pathlib import Path

from art import PALETTE, build_art_data_url

ROOT = Path(__file__).parent
THEME_ID = "andronix"
THEME_NAME = "Andronix"
AUTHOR = "Andronix"
CSS_LIMIT = 20_000  # T3 accepts 50,000; the reference theme stays under 20,000 and so do we

BG = PALETTE["background"]                                   # #19120E
D = PALETTE["ramp"]["dark"]                                  # 11 steps, dark brown -> cream
L = PALETTE["ramp"]["light"]                                 # 11 steps, light sand -> deep orange
ORANGE, CREAM, MUTED, OLIVE = (PALETTE["special"][k] for k in ("orange", "cream", "muted", "olive"))

# Every role T3 Code reads (THEME_COLOR_ROLES in the app). The build fails when one is missing.
ROLES = """canvas chrome toolbar toolbarForeground toolbarBorder toolbarControl toolbarControlForeground
toolbarControlHover surface surfaceRaised surfaceOverlay text textMuted border input focus accent
accentForeground secondary secondaryForeground muted mutedForeground placeholder secondaryLabel iconMuted
error errorForeground errorSurface warning warningForeground warningSurface update updateForeground
updateSurface accentSurface accentSurfaceForeground messageSurface messageForeground messageAction
messageActionForeground messageActionHover codeBackground codeForeground searchMatchBackground
searchMatchForeground searchMatchActiveBackground searchMatchActiveForeground sidebar sidebarForeground
sidebarMutedForeground sidebarControlSurface sidebarRowHover sidebarRowActive sidebarRowSelected
sidebarBorder terminalBackground terminalForeground terminalCursor terminalSelection terminalScrollbar
terminalScrollbarHover""".split()


def rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))


def mix(a: str, b: str, t: float) -> str:
    """a at t=0, b at t=1."""
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(rgb(a), rgb(b)))


def luminance(value: str) -> float:
    channel = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c / 255) for c in rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# Status hues, the only colours from outside the palette. Error is a warm red and warning an
# amber, both picked to sit beside the browns. Update is the brand olive, so an update notice
# never looks like the orange send button. Each family is a fill, a text colour and a tint.
STATUS = {
    "dark": {
        "error": "#E5604D", "errorForeground": "#FFB4AB", "errorSurface": mix(BG, "#93000A", 0.34),
        "warning": "#E9B43C", "warningForeground": "#FBE08A", "warningSurface": mix(BG, "#8A6A0A", 0.38),
        "update": OLIVE, "updateForeground": OLIVE, "updateSurface": mix(BG, OLIVE, 0.16),
    },
    "light": {
        "error": "#BA1A1A", "errorForeground": "#93000A", "errorSurface": mix(CREAM, "#BA1A1A", 0.13),
        "warning": "#9A6A00", "warningForeground": "#6E4B00", "warningSurface": mix(CREAM, "#E9B43C", 0.30),
        "update": "#4C6320", "updateForeground": "#3D5019", "updateSurface": mix(CREAM, OLIVE, 0.45),
    },
}

DARK_MUTED = mix(MUTED, D[9], 0.42)      # #8C7A6E is 4.4:1 on the background; this is the AA step
DARK = {
    "canvas": BG, "chrome": BG,
    "toolbar": BG, "toolbarForeground": CREAM, "toolbarBorder": D[0],
    "toolbarControl": D[0], "toolbarControlForeground": D[9], "toolbarControlHover": D[1],
    "surface": D[0], "surfaceRaised": D[1], "surfaceOverlay": D[0],
    "text": CREAM, "textMuted": DARK_MUTED,
    "border": D[1], "input": D[2], "focus": D[7],
    "accent": ORANGE, "accentForeground": BG,
    "secondary": D[0], "secondaryForeground": D[9],
    "muted": D[0], "mutedForeground": DARK_MUTED,
    "placeholder": DARK_MUTED, "secondaryLabel": DARK_MUTED, "iconMuted": DARK_MUTED,
    "accentSurface": D[1], "accentSurfaceForeground": CREAM,
    "messageSurface": D[1], "messageForeground": CREAM,
    "messageAction": ORANGE, "messageActionForeground": BG, "messageActionHover": D[7],
    "codeBackground": mix(BG, "#000000", 0.35), "codeForeground": D[9],
    "searchMatchBackground": D[3], "searchMatchForeground": CREAM,
    "searchMatchActiveBackground": D[7], "searchMatchActiveForeground": BG,
    "sidebar": mix(BG, "#000000", 0.22), "sidebarForeground": D[9],
    "sidebarMutedForeground": DARK_MUTED, "sidebarControlSurface": BG,
    "sidebarRowHover": D[0], "sidebarRowActive": D[1], "sidebarRowSelected": D[1],
    "sidebarBorder": D[0],
    "terminalBackground": mix(BG, "#000000", 0.35), "terminalForeground": D[9],
    "terminalCursor": D[7], "terminalSelection": D[3],
    "terminalScrollbar": D[1], "terminalScrollbarHover": D[2],
    **STATUS["dark"],
}

INK = BG                                  # light-mode text is the dark-mode background
LIGHT_MUTED = mix(MUTED, INK, 0.38)
LIGHT_SURFACE = mix(CREAM, L[0], 0.45)
LIGHT = {
    "canvas": CREAM, "chrome": CREAM,
    "toolbar": CREAM, "toolbarForeground": INK, "toolbarBorder": L[0],
    "toolbarControl": LIGHT_SURFACE, "toolbarControlForeground": D[0], "toolbarControlHover": L[0],
    "surface": LIGHT_SURFACE, "surfaceRaised": mix(CREAM, "#FFFFFF", 0.55), "surfaceOverlay": mix(CREAM, "#FFFFFF", 0.55),
    "text": INK, "textMuted": LIGHT_MUTED,
    "border": L[0], "input": L[1], "focus": L[7],
    "accent": L[8], "accentForeground": CREAM,
    "secondary": LIGHT_SURFACE, "secondaryForeground": D[0],
    "muted": LIGHT_SURFACE, "mutedForeground": LIGHT_MUTED,
    "placeholder": LIGHT_MUTED, "secondaryLabel": LIGHT_MUTED, "iconMuted": LIGHT_MUTED,
    "accentSurface": L[0], "accentSurfaceForeground": INK,
    "messageSurface": L[0], "messageForeground": INK,
    "messageAction": L[8], "messageActionForeground": CREAM, "messageActionHover": L[9],
    "codeBackground": mix(CREAM, "#FFFFFF", 0.55), "codeForeground": D[0],
    "searchMatchBackground": D[9], "searchMatchForeground": INK,
    "searchMatchActiveBackground": ORANGE, "searchMatchActiveForeground": INK,
    "sidebar": LIGHT_SURFACE, "sidebarForeground": D[0],
    "sidebarMutedForeground": LIGHT_MUTED, "sidebarControlSurface": CREAM,
    "sidebarRowHover": L[0], "sidebarRowActive": L[1], "sidebarRowSelected": L[1],
    "sidebarBorder": L[0],
    "terminalBackground": mix(CREAM, "#FFFFFF", 0.55), "terminalForeground": D[0],
    "terminalCursor": L[7], "terminalSelection": L[1],
    "terminalScrollbar": L[1], "terminalScrollbarHover": L[2],
    **STATUS["light"],
}

# How strong the dawn glow is: at rest (an empty thread, where no text sits over it) and behind a
# conversation. The build checks text against the brightest dot at the conversation strength.
GLOW = {
    "dark": {"stops": (D[7], D[6], D[5], D[4], D[3]), "rest": 0.40, "busy": 0.12},
    "light": {"stops": (L[5], L[4], L[3], L[2], L[1]), "rest": 0.42, "busy": 0.14},
}

# (text role, background role, minimum ratio). 4.5 is AA for text; 3.0 is AA for large text and
# for non-text marks such as the cursor and the focus ring.
BODY_SURFACES = ["canvas", "chrome", "surface", "surfaceRaised", "surfaceOverlay", "muted", "secondary",
                 "accentSurface", "messageSurface", "sidebar", "sidebarControlSurface",
                 "sidebarRowHover", "sidebarRowActive", "sidebarRowSelected"]
PAIRS = (
    [("text", s, 4.5) for s in BODY_SURFACES]
    + [(t, s, 4.5) for t in ("textMuted", "mutedForeground", "secondaryLabel", "placeholder", "iconMuted")
       for s in ("canvas", "surface", "surfaceRaised", "surfaceOverlay", "muted", "messageSurface")]
    + [("sidebarForeground", s, 4.5) for s in ("sidebar", "sidebarRowHover", "sidebarRowActive", "sidebarRowSelected")]
    + [("sidebarMutedForeground", s, 4.5) for s in ("sidebar", "sidebarRowHover", "sidebarRowActive", "sidebarRowSelected")]
    + [("toolbarForeground", "toolbar", 4.5), ("toolbarControlForeground", "toolbarControl", 4.5),
       ("toolbarControlForeground", "toolbarControlHover", 4.5),
       ("secondaryForeground", "secondary", 4.5), ("accentSurfaceForeground", "accentSurface", 4.5),
       ("messageForeground", "messageSurface", 4.5),
       ("accentForeground", "accent", 4.5), ("messageActionForeground", "messageAction", 4.5),
       ("messageActionForeground", "messageActionHover", 4.5),
       ("codeForeground", "codeBackground", 4.5), ("terminalForeground", "terminalBackground", 4.5),
       ("terminalForeground", "terminalSelection", 4.5),
       ("searchMatchForeground", "searchMatchBackground", 4.5),
       ("searchMatchActiveForeground", "searchMatchActiveBackground", 4.5)]
    + [(f"{k}Foreground", s, 4.5) for k in ("error", "warning", "update")
       for s in (f"{k}Surface", "canvas", "surface", "surfaceRaised")]
    + [("accent", s, 4.5) for s in ("canvas", "surface", "surfaceRaised")]          # links
    + [(k, "canvas", 3.0) for k in ("error", "warning", "update", "focus", "messageAction")]
    + [("terminalCursor", "terminalBackground", 3.0)]
)


def check(name: str, colors: dict) -> list[str]:
    missing = [r for r in ROLES if r not in colors]
    extra = [r for r in colors if r not in ROLES]
    if missing or extra:
        sys.exit(f"{name}: missing roles {missing}, unknown roles {extra}")
    failures, rows = [], []
    for fg, bg, need in PAIRS:
        ratio = contrast(colors[fg], colors[bg])
        rows.append((ratio, fg, bg, need))
        if ratio < need:
            failures.append(f"{name}: {fg} {colors[fg]} on {bg} {colors[bg]} is {ratio:.2f}:1, needs {need}")
    glow = GLOW[name]
    for stop in glow["stops"]:                      # text over a glow dot, behind a conversation
        dot = mix(colors["canvas"], stop, glow["busy"])
        for fg in ("text", "textMuted", "accent", "errorForeground", "warningForeground"):
            ratio = contrast(colors[fg], dot)
            rows.append((ratio, fg, f"glow dot {dot}", 4.5))
            if ratio < 4.5:
                failures.append(f"{name}: {fg} {colors[fg]} over glow dot {dot} is {ratio:.2f}:1, needs 4.5")
    low = min(rows)
    text_low = min(r for r in rows if r[3] == 4.5)
    print(f"{name}: {len(rows)} pairs, {len(failures)} below AA; lowest text pair "
          f"{text_low[1]} on {text_low[2]} {text_low[0]:.2f}:1; lowest mark {low[1]} on {low[2]} {low[0]:.2f}:1")
    return failures


def minify(css: str) -> str:
    """Adapted from t3-nyx-theme (MIT)."""
    strings: list[str] = []

    def stash(match: re.Match) -> str:
        strings.append(match.group(0))
        return f"\x00{len(strings) - 1}\x00"

    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r'"[^"]*"', stash, css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    css = re.sub(r"\s*!important", "!important", css)
    css = css.replace(";}", "}")
    css = re.sub(r"\x00(\d+)\x00", lambda m: strings[int(m.group(1))], css)
    return css.strip()


def build_css() -> str:
    css = (ROOT / "theme.css").read_text()
    for placeholder, value in {
        "__ART__": build_art_data_url(),
        "__DARK_BG__": BG, "__LIGHT_BG__": CREAM,
        "__DARK_GLOW__": ", ".join(GLOW["dark"]["stops"]),
        "__LIGHT_GLOW__": ", ".join(GLOW["light"]["stops"]),
        "__DARK_REST__": str(GLOW["dark"]["rest"]), "__DARK_BUSY__": str(GLOW["dark"]["busy"]),
        "__LIGHT_REST__": str(GLOW["light"]["rest"]), "__LIGHT_BUSY__": str(GLOW["light"]["busy"]),
    }.items():
        css = css.replace(placeholder, value)
    css = minify(css)
    if len(css) > CSS_LIMIT:
        sys.exit(f"theme css is {len(css)} characters; the cap is {CSS_LIMIT}")
    return css


def build() -> dict:
    failures = check("dark", DARK) + check("light", LIGHT)
    if failures:
        sys.exit("\n".join(failures))
    return {
        "version": 1, "id": THEME_ID, "name": THEME_NAME, "appearance": "dark", "author": AUTHOR,
        "colors": {r: DARK[r] for r in ROLES},
        "variants": {"light": {r: LIGHT[r] for r in ROLES}},
        "css": build_css(),
    }


if __name__ == "__main__":
    theme = build()
    if "--check" not in sys.argv:
        out = ROOT / f"{THEME_ID}.json"
        out.write_text(json.dumps(theme, indent=2) + "\n")
        print(f"{out.name}: {len(theme['colors'])} roles x 2 appearances, {len(theme['css'])} css characters (cap {CSS_LIMIT})")
