"""Same data under several property cycles. Usage: compare_cycles.py OUTDIR"""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from cycler import cycler

out = sys.argv[1] if len(sys.argv) > 1 else "."
rows = [("colibri-dark (default)", rhdt_mpl.cycle("colibri-dark")), ("colibri", rhdt_mpl.cycle("colibri")),
        ("ok8", rhdt_mpl.cycle("ok8")),
        ("Tol Vibrant", cycler(color=rhdt_mpl.palette("tol-vibrant", ["orange", "blue", "cyan", "magenta", "red", "teal"])))]
rng = np.random.default_rng(3)
x = np.linspace(0, 10, 200)
centers = rng.uniform(-2.2, 2.2, (8, 2))
pts = [c + 0.45 * rng.standard_normal((40, 2)) for c in centers]
heights = rng.uniform(1, 3, (8, 5))

fig, axs = plt.subplots(len(rows), 4, figsize=(rhdt_mpl.TWO_COLUMN, 2.1 * len(rows)))
for r, (name, cyc) in enumerate(rows):
    a1, a2, a3, a4 = axs[r]
    for ax in axs[r]:
        ax.set_prop_cycle(cyc)
    for i in range(6):   # 6 series
        a1.plot(x, np.sin(x / 1.6 + 0.55 * i) * np.exp(-x / 14) + 0.0)
    for i in range(8):   # 8 series: Tol Vibrant wraps around
        a2.plot(x, 0.45 * i + 0.3 * np.sin(x / 1.8 + 0.5 * i))
    for i in range(8):
        a3.scatter(*pts[i].T, s=10, lw=0)
    bottom = np.zeros(5)
    for i in range(8):
        a4.bar(range(5), heights[i], bottom=bottom, width=0.8, lw=0.4, edgecolor="white")
        bottom += heights[i]
    a1.set_ylabel(name, fontsize=8, fontweight="bold")
    if r == 0:
        for ax, t in zip(axs[0], ["6 lines", "8 lines", "8 clusters", "8 stacked bars"]):
            ax.set_title(t)
    for ax in axs[r, 2:]:
        ax.set_xticks([]); ax.set_yticks([])
fig.align_ylabels(axs[:, 0])
fig.savefig(f"{out}/compare_cycles.pdf")
