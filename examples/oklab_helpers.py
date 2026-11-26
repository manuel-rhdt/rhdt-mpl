"""Demo of rhdt_mpl.oklab. Usage: oklab_helpers.py OUTDIR"""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from rhdt_mpl import oklab

out = sys.argv[1] if len(sys.argv) > 1 else "."
base = rhdt_mpl.palette("tol-vibrant", ["orange", "blue", "cyan", "magenta", "red", "teal"])
cols = [
    ("original", lambda c: c),
    ("muted", oklab.muted),
    ("muted, more", lambda c: oklab.muted(c, chroma=0.25, lighten=0.3)),
    ("lighten 0.12", lambda c: oklab.lighten(c, 0.12)),
    ("darken 0.12", lambda c: oklab.darken(c, 0.12)),
    ("hue +25°", lambda c: oklab.rotate_hue(c, 25)),
    ("hue −25°", lambda c: oklab.rotate_hue(c, -25)),
    ("mix with black 30%", lambda c: oklab.mix(c, "#000000", 0.3)),
]
fig = plt.figure(figsize=(rhdt_mpl.TWO_COLUMN, 3.6), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1])
ax = fig.add_subplot(gs[0])
for r, (name, f) in enumerate(cols):
    for k, c in enumerate(base):
        ax.add_patch(plt.Rectangle((k, -r), 0.94, 0.86, color=f(c), lw=0))
ax.set_xlim(0, 6); ax.set_ylim(-len(cols) + 0.1, 1)
ax.set_yticks([-r + 0.43 for r in range(len(cols))], [n for n, _ in cols])
ax.set_xticks([]); ax.tick_params(left=False)
for s in ax.spines.values(): s.set_visible(False)
ax.set_title("Tol Vibrant under each helper")

ax = fig.add_subplot(gs[1])
x = np.linspace(0, 10, 60)
theory = 30 * (1 - np.exp(-x / 4))
sec = oklab.family("#33BBEE", 3)
for i, (c, name, k) in enumerate(zip(sec, ["InfoNCE", "MINE", "SMILE"], [0.30, 0.22, 0.15])):
    ax.plot(x, k * theory + 1.5 * i, color=c, lw=1.2, marker="^v<"[i], markevery=6, markersize=3.5, label=name)
ax.plot(x, 0.6 * theory + 0.4 * x, color=oklab.muted("#EE7733"), lw=1.2, ls="--", label="baseline (muted)")
ax.plot(x, theory, color="k", lw=2, zorder=10, label="theory")
ax.plot(x, theory * (1 - 0.04 * np.sin(x)), color="#EE7733", lw=1.6, marker="o", markevery=6, markersize=3.5, label="highlight")
ax.set(title="black / bright / muted", xlabel="x", ylabel="y")
ax.legend(fontsize=6.5, loc="upper left", bbox_to_anchor=(0.0, 1.0))
fig.savefig(f"{out}/oklab_helpers.pdf")
