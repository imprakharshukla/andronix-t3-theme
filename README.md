# Andronix theme for T3 Code

The [Andronix](https://andronix.app) look as a [T3 Code](https://t3.codes) theme: warm browns, an
orange accent, and a halftone "dawn glow" behind the chat. One file, `andronix.json`, holds a dark
theme and a light variant.

![The dawn glow in dark mode](previews/dark.png)
![The dawn glow in light mode](previews/light.png)

The previews show the background glow on an empty thread, cropped from the app.

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/AndronixApp/andronix-t3-theme/main/andronix.json -o andronix.json
t3 theme set andronix.json
```

The desktop app and the browser switch right away. Dark or light follows T3's appearance setting.
To go back to the default:

```sh
t3 theme set t3-chat
```

Needs a T3 Code build with custom themes (November 2026 or later). The phone app does not use themes.

### Instructions for agents

1. Download `https://raw.githubusercontent.com/AndronixApp/andronix-t3-theme/main/andronix.json`.
2. If the `t3` command is available, run `t3 theme set <path to andronix.json>`.
3. Otherwise call the `t3_theme_set` tool with `themeId: "andronix"` and the file's JSON as `theme`.
4. Do not edit `andronix.json`. Change `build.py` and rebuild instead.

## Palette

| | Colours |
|---|---|
| Background | `#19120E` |
| Ramp, dark to light | `#2A1F18` `#3A2D24` `#4E3423` `#6E3408` `#954611` `#C25F14` `#E8791E` `#F59A4E` `#FFB689` `#FFD9BF` `#FFF3EA` |
| Accents | orange `#E8791E`, cream `#FFF3EA`, muted `#8C7A6E`, olive `#BFD39A` |

The light variant puts the same browns and oranges on the cream.

## Rebuild

Python 3.9 or later, standard library only.

```sh
python3 build.py            # writes andronix.json and prints the contrast summary
python3 build.py --check    # contrast check only
python3 art.py              # writes build/art.svg, to look at the glow on its own
```

| File | What it is |
|---|---|
| `andronix.json` | The theme. Built; do not edit by hand. |
| `palette.json` | The colours, and the dot sizes of the halftone. |
| `build.py` | Palette to colour roles, the contrast check, and the JSON. |
| `art.py` | Draws the dawn glow as a small SVG of dots. |
| `theme.css` | Places the glow behind the chat column. |

## Rules the build keeps

- **Palette only.** Every colour is in `palette.json` or is a blend of two of its colours. The
  exceptions are the error red and the warning amber; the update colour is the palette's olive.
- **All 61 colour roles are set**, for dark and for light. The build stops if one is missing.
- **WCAG AA.** 112 text and background pairs per appearance are checked: 4.5:1 for text, 3:1 for
  marks such as the cursor and the focus ring. The build stops on a failure.
- **The glow stays out of the way.** It is strongest on an empty thread, where no text sits on it,
  and fades once a conversation has messages. Text over the brightest dot is part of the check.
- **Size.** The CSS is about 10,000 characters. T3 accepts 50,000; the build caps it at 20,000.

## What the theme cannot change

T3 fixes these itself: the terminal's 16 ANSI colours, the red and green of diffs, and the green
"done" marks. The theme sets the terminal background, text, cursor and selection around them.

If a future T3 update renames the chat column's hook, the glow stops showing and the colours stay.

## Credit

The approach (a colour table and a CSS background packed into one theme file by a small build
script) follows [t3-nyx-theme](https://github.com/Deepusleepy/t3-nyx-theme) by Deepusleepy, MIT.
`minify` in `build.py` is adapted from it.

## License

[MIT](LICENSE)
