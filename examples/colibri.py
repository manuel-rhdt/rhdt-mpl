"""The colibri palette and the hummingbird species palettes. Usage: colibri.py OUTDIR  (writes colibri.pdf)"""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rhdt_mpl import oklab
from rhdt_mpl.palettes import PALETTES

SPECIES = {"sunangel": "Heliangelus exortis", "ruby-topaz": "Chrysolampis mosquitus",
           "starfrontlet": "Coeligena bonapartei", "sapphire": "Chrysuronia oenone",
           "violet-crowned": "Ramosomyia violiceps", "broad-billed": "Cynanthus latirostris"}

out = sys.argv[1] if len(sys.argv) > 1 else "."
LABEL_W, SW, GAP, RH = 2.1, 0.58, 0.035, 0.62
rows = [("colibri", "bright, from the data", PALETTES["colibri"]),
        ("colibri-dark", "darker partners", PALETTES["colibri-dark"])] + [(k, latin, PALETTES[k]) for k, latin in SPECIES.items()]
H_SW = 0.75 + RH * len(rows)
W = rhdt_mpl.TWO_COLUMN

fig = plt.figure(figsize=(W, H_SW + 2.9), layout="none")
ax = fig.add_axes([0, 2.9 / (H_SW + 2.9), 1, H_SW / (H_SW + 2.9)])
ax.set_xlim(0, W); ax.set_ylim(0, H_SW); ax.axis("off")
ax.text(0.08, H_SW - 0.2, "hummingbird palettes", fontsize=11, fontweight="bold", va="center")
ax.text(W - 0.08, H_SW - 0.2, 'rhdt_mpl.palette("ruby-topaz")     color="rhdt:colibri:mosquitus crown"', fontsize=6,
        family="Noto Sans Mono", ha="right", va="center", color="0.25")
ax.text(0.1, 0.1, "∘ the exact color lies outside sRGB; the swatch shows its nearest sRGB color", fontsize=5.6, color="0.35",
        va="center")
for r, (key, sub, pal) in enumerate(rows):
    y = H_SW - 0.5 - RH * (r + 1) + 0.12
    ax.text(0.1, y + 0.30, key, fontsize=8, fontweight="bold", va="center")
    ax.text(0.1, y + 0.13, sub, fontsize=6.5, style="italic" if r else "normal", color="0.35", va="center")
    for i, (name, hexv) in enumerate(pal.items()):
        x = LABEL_W + i * (SW + GAP)
        ax.add_patch(Rectangle((x, y + 0.12), SW, 0.40, color=hexv, lw=0))
        ink = "white" if oklab.lightness(hexv) < 0.68 else "black"
        ax.text(x + SW / 2, y + 0.32, name.replace(" ", "\n"), fontsize=5.0 if key.startswith("colibri") else 5.8, ha="center",
                va="center", color=ink, linespacing=0.95)
        if rhdt_mpl.wide_css(key, name):                       # the exact color lies outside sRGB
            ax.plot([x + SW - 0.06], [y + 0.46], "o", ms=2.2, mfc="none", mec=ink, mew=0.6)
        ax.text(x + SW / 2, y + 0.04, hexv, fontsize=4.8, ha="center", va="center", family="Noto Sans Mono", color="0.4")

# --- the pattern in use: a dark part for the theory, bright gorget as the accent, quieter plumage colors for the rest
gs = fig.add_gridspec(1, 3, left=0.07, right=0.98, bottom=0.07, top=2.45 / (H_SW + 2.9), wspace=0.28)
x = np.linspace(0, 10, 60)
theory = 30 * (1 - np.exp(-x / 4))
demos = [("sunangel", "gorget", "crown", "mantle", "belly"), ("ruby-topaz", "gorget", "crown", "rump", "mantle"),
         ("violet-crowned", "crown", "bill", "back", "tail")]
axs = []
for k, (key, hi, c1, c2, dark) in enumerate(demos):
    a = fig.add_subplot(gs[0, k]); axs.append(a)
    P = f"rhdt:{key}:"
    a.plot(x, 0.30 * theory, color=P + c1, lw=1.3, label=c1)
    a.plot(x, 0.18 * theory, color=P + c2, lw=1.3, label=c2)
    a.plot(x, theory, color=P + dark, lw=2, zorder=10, label=dark)
    a.plot(x, theory * (1 - 0.05 * np.sin(x)), color=P + hi, lw=1.6, marker="o", markevery=6, markersize=3.5, label=hi)
    a.set(title=key, xlabel="x", ylabel="y" if k == 0 else "")
    a.legend(fontsize=6, loc="upper left")
rhdt_mpl.panel_labels(axs)
fig.savefig(f"{out}/colibri.pdf")
