"""Write the table of all named colors into the README (between the named-colors markers) and the swatch images it uses
(docs/swatches/<hex>.svg).  Everything comes from the package, so the table cannot drift from it.

    python examples/make_color_table.py
"""
import os
import re

import rhdt_mpl
from rhdt_mpl import oklab
from rhdt_mpl.palettes import PALETTES, NATIVE_SPACE, DEFAULT_PALETTE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
SWATCHES = os.path.join(ROOT, "docs", "swatches")
BEGIN, END = "<!-- named-colors:begin -->", "<!-- named-colors:end -->"
PATCH_NOTE = {"gorget": "gorget", "crown": "crown", "belly": "belly", "mantle": "mantle", "rump": "rump"}


def swatch(hexv, space):
    """A swatch file in the native color space of the palette (CSS ``color(display-p3 ...)`` where that is Display P3;
    a browser that cannot show P3 falls back to the sRGB it makes of it)."""
    name = ("p3-" if space == "display-p3" else "") + hexv.lstrip("#").lower() + ".svg"
    fill = hexv
    if space == "display-p3":
        r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
        fill = f"color(display-p3 {r:.4f} {g:.4f} {b:.4f})"
    os.makedirs(SWATCHES, exist_ok=True)
    with open(os.path.join(SWATCHES, name), "w") as fh:
        fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="16" viewBox="0 0 40 16">'
                 f'<rect x="0.5" y="0.5" width="39" height="15" rx="2.5" fill="{fill}" stroke="#8888" stroke-width="1"/></svg>\n')
    return f'<img src="docs/swatches/{name}" width="40" height="16" alt="{hexv}">'


def notes(palette, name):
    out = []
    if palette == DEFAULT_PALETTE:
        out.append(f"also `rhdt:{name}`")
    if palette in rhdt_mpl.SOURCES and name in rhdt_mpl.SOURCES[palette]:
        sp, sex, patch, n = rhdt_mpl.SOURCES[palette][name]
        out.append(f"{sp.replace('_', ' ')} {'♂' if sex == 'Males' else '♀'} {patch}, {n} specimens")
    if palette == "colibri-dark":
        out.append(f"darker partner of `{rhdt_mpl.PARTNERS[name]}`")
    w = rhdt_mpl.wide_css(palette, name)
    if w:
        out.append(f"exact color outside Display P3: `{w}`")
    return "; ".join(out)


def table():
    rows = ["| | name | hex | notes |", "|---|---|---|---|"]
    for palette, colors in PALETTES.items():
        space = NATIVE_SPACE.get(palette, "srgb")
        for name, hexv in colors.items():
            note = "; ".join(x for x in (f"Display P3" if space == "display-p3" else "sRGB", notes(palette, name)) if x)
            rows.append(f"| {swatch(hexv, space)} | `rhdt:{palette}:{name}` | `{hexv.lower()}` | {note} |")
    return "\n".join(rows)


def block():
    n = len(rhdt_mpl.named_colors())
    return (f"{BEGIN}\n<details>\n<summary>All {n} named colors (click to expand)</summary>\n\n"
            f"The full name of every color is `rhdt:<palette>:<name>`; the colors of the default palette (`{DEFAULT_PALETTE}`) also "
            f"have the short form `rhdt:<name>`. The hex values are the numbers of the palette in its own color space, Display P3 for the hummingbird palettes and sRGB for `okabe-ito`, `ok6` and `ok8` (the notes say which); the colors a figure uses are converted to its color space. For the few colors outside Display P3 the hex is the nearest Display P3 color.\n\n"
            f"{table()}\n\n</details>\n{END}")


if __name__ == "__main__":
    if os.path.isdir(SWATCHES):                      # start clean, so swatches of removed colors disappear
        for f in os.listdir(SWATCHES):
            if f.endswith(".svg"):
                os.remove(os.path.join(SWATCHES, f))
    s = open(README).read()
    if BEGIN in s:
        s = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda m: block(), s, flags=re.S)
    else:
        anchor = "## Colormaps"
        s = s.replace(anchor, block() + "\n\n" + anchor, 1)
    open(README, "w").write(s)
    print("wrote the table of", len(rhdt_mpl.named_colors()), "named colors;", len(os.listdir(SWATCHES)), "swatches")
