"""The colibri palette and the iridescent colormaps. Usage: colibri.py OUTDIR  (writes colibri.pdf)"""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rhdt_mpl import oklab
from rhdt_mpl.palettes import PALETTES

out = sys.argv[1] if len(sys.argv) > 1 else "."
pal = PALETTES["colibri"]
rng = np.random.default_rng(4)
rhdt_mpl.set_cycle("colibri")

fig = plt.figure(figsize=(rhdt_mpl.TWO_COLUMN, 7.4))
gs = fig.add_gridspec(3, 1, height_ratios=[0.62, 2.0, 3.3], hspace=0.25)

# --- swatches with names and hex codes
ax = fig.add_subplot(gs[0]); ax.set_xlim(0, len(pal)); ax.set_ylim(0, 1); ax.axis("off")
for i, (name, hexv) in enumerate(pal.items()):
    ax.add_patch(Rectangle((i + 0.03, 0.3), 0.94, 0.7, color=hexv, lw=0))
    ink = "white" if oklab.lightness(hexv) < 0.68 else "black"
    ax.text(i + 0.5, 0.65, name, ha="center", va="center", fontsize=7.5, fontweight="bold", color=ink)
    ax.text(i + 0.5, 0.12, hexv, ha="center", va="center", fontsize=6, family="Noto Sans Mono", color="0.3")
ax.set_title('rhdt_mpl.set_cycle("colibri")        color="rhdt:colibri:ruby"', fontsize=7, family="Noto Sans Mono", color="0.25", loc="left", pad=4)

# --- the cycle in use
sub = gs[1].subgridspec(1, 3, wspace=0.25)
x = np.linspace(0, 10, 200)
a1, a2, a3 = (fig.add_subplot(sub[0, k]) for k in range(3))
for a in (a1, a2, a3):
    a.set_prop_cycle(rhdt_mpl.cycle("colibri"))
for i in range(8):
    a1.plot(x, np.sin(x / 1.7 + 0.5 * i) * np.exp(-x / 18), label=list(pal)[i])
a1.set(title="8 lines")
for i in range(8):
    a2.scatter(*(rng.uniform(-2.4, 2.4, 2) + 0.5 * rng.standard_normal((30, 2))).T, s=9, lw=0)
a2.set(title="clusters")
h = rng.uniform(1, 3, (8, 4)); b = np.zeros(4)
for i in range(8):
    a3.bar(range(4), h[i], bottom=b, width=0.8, edgecolor="white", lw=0.4); b += h[i]
a3.set(title="stacked bars", xticks=range(4))

# --- the iridescent colormaps: gradient, greyscale lightness, and a sample field
g = np.linspace(-2, 2, 220); X, Y = np.meshgrid(g, g)
Z = np.sin(3 * X) * np.cos(3 * Y) * np.exp(-(X**2 + Y**2) / 2)
sub = gs[2].subgridspec(3, 2, height_ratios=[0.25, 0.25, 3], hspace=0.12, wspace=0.18)
for j, n in enumerate(["ok_colibri", "ok_gorget"]):
    cm = plt.get_cmap(n)
    grad = fig.add_subplot(sub[0, j]); grad.imshow(np.linspace(0, 1, 256)[None], aspect="auto", cmap=n)
    grey = fig.add_subplot(sub[1, j])
    L = np.array([oklab.lightness(c) for c in cm(np.linspace(0, 1, 256))])
    grey.imshow(np.array([[int(oklab.oklab(l, 0, 0)[k:k + 2], 16) / 255 for k in (1, 3, 5)] for l in L])[None], aspect="auto")
    for a in (grad, grey):
        a.set_xticks([]); a.set_yticks([])
    grad.set_title(f'cmap="{n}"   ("{n}_r")', fontsize=7, family="Noto Sans Mono", color="0.25", loc="left")
    fld = fig.add_subplot(sub[2, j]); fld.pcolormesh(X, Y, Z, cmap=n, rasterized=True); fld.set_aspect("equal")
    fld.set(xlabel="$x$", ylabel="$y$" if j == 0 else "")
rhdt_mpl.panel_labels([a1, a2, a3])
fig.savefig(f"{out}/colibri.pdf")
rhdt_mpl.use(backend=False)
