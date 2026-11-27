"""Showcase of rhdt_mpl colors and colormaps. Usage: showcase_colors.py OUTDIR
Writes colors.pdf and colormaps.pdf."""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rhdt_mpl import oklab, okmaps
from rhdt_mpl.palettes import PALETTES, OK_PRINT_LINESTYLES

out = sys.argv[1] if len(sys.argv) > 1 else "."
W = rhdt_mpl.TWO_COLUMN
LABEL_W, SW, GAP = 2.25, 0.44, 0.03
MONO = "Fira Mono"


def ink(color):
    return "white" if oklab.lightness(color) < 0.68 else "black"


def wrap(name):
    return name.replace(" ", "\n")


def section(ax, y, text):
    ax.text(0.08, y, text, fontsize=8.5, fontweight="bold", va="center")
    ax.plot([0.08, W - 0.08], [y - 0.14, y - 0.14], color="0.75", lw=0.6)


def row(ax, y, title, code, swatches, lines=False, h=0.43):
    ax.text(0.1, y + h * 0.72, title, fontsize=7.5, fontweight="bold", va="center")
    ax.text(0.1, y + h * 0.28, code, fontsize=5.6, family=MONO, va="center", color="0.25")
    x0 = LABEL_W
    for i, (label, col) in enumerate(swatches):
        x = x0 + i * (SW + GAP)
        if col is None:
            continue
        if lines:
            ax.plot([x, x + SW], [y + h / 2] * 2, color=col, lw=1.8,
                    ls=OK_PRINT_LINESTYLES[i], solid_capstyle="butt")
            ax.text(x + SW / 2, y + h / 2 - 0.1, str(i + 1), fontsize=5, ha="center", va="top", color="0.4")
        else:
            ax.add_patch(Rectangle((x, y), SW, h, color=col, lw=0))
            if label:
                fs = 4.8 if max(len(w) for w in label.split()) <= 10 else 3.9
                ax.text(x + SW / 2, y + h / 2, wrap(label), fontsize=fs, ha="center", va="center",
                        color=ink(col), linespacing=0.95)


# ---------------------------------------------------------------- figure 1: colors
default = ["orange", "blue", "cyan", "magenta", "red", "teal"]
rows = [
    ("sec", "Palettes   rhdt_mpl.palette(name, names=None)  returns a list of hex   |   rhdt_mpl.set_palette(name, names=None)"),
    ("colibri   (default cycle)", 'rhdt_mpl.palette("colibri")', list(PALETTES["colibri"].items())),
    ("colibri-dark   (darker partners)", 'rhdt_mpl.palette("colibri-dark")', list(PALETTES["colibri-dark"].items())),
    ("okabe-ito", 'rhdt_mpl.palette("okabe-ito")', list(PALETTES["okabe-ito"].items())),
    ("sec", "Cycles   rhdt_mpl.set_cycle(name)   |   ax.set_prop_cycle(rhdt_mpl.cycle(name))   |   first k are most separated"),
    ("ok6", 'rhdt_mpl.set_cycle("ok6")', list(PALETTES["ok6"].items())),
    ("ok8", 'rhdt_mpl.set_cycle("ok8")', list(PALETTES["ok8"].items())),
    ("ok-print   (ok6 + line styles)", 'rhdt_mpl.set_cycle("ok-print")', list(PALETTES["ok6"].items())),
    ("sec", "Individual colors by name   \"rhdt:palette:name\", accepted wherever Matplotlib takes a color"),
    ("default palette, short", 'color="rhdt:emerald"',
     [("emerald", PALETTES["colibri"]["emerald"])]),
    ("full form", 'color="rhdt:colibri:ruby"',
     [("ruby", PALETTES["colibri"]["ruby"])]),
    ("other palettes", 'color="rhdt:okabe-ito:sky blue"',
     [("sky blue", PALETTES["okabe-ito"]["sky blue"])]),
    ("same name, other palette", 'color="rhdt:ok6:navy"   "rhdt:ok8:navy"',
     [("ok6:navy", PALETTES["ok6"]["navy"]), ("ok8:navy", PALETTES["ok8"]["navy"])]),
    ("with helpers", 'oklab.muted("rhdt:colibri:amber")',
     [("amber", PALETTES["colibri"]["amber"]), ("muted", oklab.muted("rhdt:colibri:amber"))]),
    ("sec", "OKLab helpers   from rhdt_mpl import oklab   all return \"#rrggbb\""),
    ("muted   (chroma x 0.5, lighter)", 'oklab.muted("rhdt:amber")',
     [("rhdt:amber", "rhdt:amber"), ("muted", oklab.muted("rhdt:amber")),
      ("rhdt:sapphire", "rhdt:sapphire"), ("muted", oklab.muted("rhdt:sapphire")),
      ("rhdt:jade", "rhdt:jade"), ("muted", oklab.muted("rhdt:jade"))]),
    ("family   (lightness steps)", 'oklab.family("rhdt:sapphire", 4)', [(f"{i+1}", c) for i, c in enumerate(oklab.family("rhdt:sapphire", 4))]
     + [("", None)] + [(f"{i+1}", c) for i, c in enumerate(oklab.family("rhdt:amber", 4))]),
    ("lighten / darken", 'oklab.lighten(c, .12) / .darken(c, .12)',
     [("dark", oklab.darken("rhdt:sapphire", .12)), ("c", "rhdt:sapphire"), ("light", oklab.lighten("rhdt:sapphire", .12)),
      ("", None), ("dark", oklab.darken("rhdt:amber", .12)), ("c", "rhdt:amber"), ("light", oklab.lighten("rhdt:amber", .12))]),
    ("rotate_hue / mix", 'oklab.rotate_hue(c, 25)   oklab.mix(a, b, t)',
     [("−25°", oklab.rotate_hue("rhdt:jade", -25)), ("c", "rhdt:jade"), ("+25°", oklab.rotate_hue("rhdt:jade", 25)), ("", None)]
     + [(f"t={t:.2f}".rstrip("0").rstrip("."), oklab.mix("rhdt:amber", "rhdt:sapphire", t)) for t in (0, .25, .5, .75, 1)]),
]
RH = 0.62
H = 0.55 + sum(0.5 if r[0] == "sec" else RH for r in rows)
fig = plt.figure(figsize=(W, H), layout=None)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.text(0.08, H - 0.2, "rhdt_mpl colors", fontsize=11, fontweight="bold", va="center")
ax.text(W - 0.08, H - 0.2, "import rhdt_mpl     # applies style, Fira fonts, umbruch backend", fontsize=6, family=MONO,
        ha="right", va="center", color="0.25")
y = H - 0.62
for r in rows:
    if r[0] == "sec":
        y -= 0.12
        section(ax, y, r[1]); y -= 0.38
    else:
        title, code, sw = r
        row(ax, y - 0.4, title, code, sw, lines=title.startswith("ok-print"))
        y -= RH
fig.savefig(f"{out}/colors.pdf")
plt.close(fig)

# ---------------------------------------------------------------- figure 2: colormaps
names = list(okmaps.COLORMAPS)
H2 = 0.9 + 0.7 * len(names)
fig = plt.figure(figsize=(W, H2), layout=None)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H2); ax.axis("off")
ax.text(0.08, H2 - 0.2, "rhdt_mpl colormaps", fontsize=11, fontweight="bold", va="center")
ax.text(W - 0.08, H2 - 0.2, 'plt.imshow(z, cmap="ok_orchid")   # default     append "_r" to reverse',
        fontsize=6, family=MONO, ha="right", va="center", color="0.25")
ax.text(LABEL_W, H2 - 0.55, "colour", fontsize=6, color="0.4", va="bottom")
ax.text(W - 0.08, H2 - 0.55, "OKLab lightness L (0 to 1)", fontsize=6, color="0.4", va="bottom", ha="right")
grad = np.linspace(0, 1, 256)
bar_x, bar_w = LABEL_W, W - LABEL_W - 0.1
for i, n in enumerate(names):
    y = H2 - 0.7 - 0.7 * (i + 1) + 0.2
    cm = okmaps.COLORMAPS[n]
    ax.text(0.1, y + 0.36, n + ("   (default)" if n == "ok_orchid" else ""), fontsize=7.5, fontweight="bold", va="bottom")
    ax.text(0.1, y + 0.31, f'cmap="{n}"', fontsize=5.6, family=MONO, va="top", color="0.25")
    ax.text(0.1, y + 0.22, f'cmap="{n}_r"', fontsize=5.6, family=MONO, va="top", color="0.45")
    ax.imshow(grad[None], extent=(bar_x, bar_x + bar_w, y + 0.18, y + 0.44), cmap=cm, aspect="auto")
    Ls = np.array([oklab.lightness(c) for c in cm.colors])
    greys = np.array([[int(oklab.oklab(L, 0, 0)[k:k + 2], 16) / 255 for k in (1, 3, 5)] for L in Ls])
    ax.imshow(greys[None], extent=(bar_x, bar_x + bar_w, y - 0.04, y + 0.18), aspect="auto")
    ax.text(bar_x + 0.04, y - 0.06, f"L = {Ls[0]:.2f}", fontsize=5, va="top", color="0.4")
    ax.text(bar_x + bar_w - 0.04, y - 0.06, f"{Ls[-1]:.2f}", fontsize=5, va="top", ha="right", color="0.4")
ax.set_xlim(0, W); ax.set_ylim(0, H2)
fig.savefig(f"{out}/colormaps.pdf")
