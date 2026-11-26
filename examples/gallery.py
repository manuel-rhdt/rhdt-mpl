"""Example figures; needs an umbruch binary on $UMBRUCH or PATH and pdftoppm for PNGs."""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from umbruch_matplotlib import rich

out = sys.argv[1] if len(sys.argv) > 1 else "."
rng = np.random.default_rng(1)

# 1. Four panels with the default cycle
fig, axs = plt.subplots(2, 2, figsize=(7.5, 5.2))
ax = axs[0, 0]
x = np.linspace(0, 10, 300)
for k in range(5):
    ax.plot(x, np.exp(-x / 6) * np.cos(x + k * 0.6), label=f"$\\varphi={k*0.6:.1f}$")
ax.set(xlabel=rich("time <i>t</i> (s)"), ylabel=r"$e^{-t/\tau}\cos(t+\varphi)$", title="Damped oscillations")
ax.legend(ncols=2, loc="upper right")

ax = axs[0, 1]
cats = ["A", "B", "C", "D"]
w = 0.2
for k in range(4):
    ax.bar(np.arange(4) + (k - 1.5) * w, rng.uniform(1, 5, 4), w, label=f"group {k+1}")
ax.set_xticks(range(4), cats)
ax.set(ylabel="counts", title="Grouped bars")

ax = axs[1, 0]
n = np.logspace(1, 4, 12)
ax.loglog(n, 3 / n, "o-", label=r"$\propto N^{-1}$")
ax.loglog(n, 2 / np.sqrt(n), "s-", label=r"$\propto N^{-1/2}$")
ax.loglog(n, 5 / n**2, "^-", label=r"$\propto N^{-2}$")
ax.set(xlabel="samples $N$", ylabel="error", title="Convergence")
ax.legend()

ax = axs[1, 1]
g = np.linspace(-2, 2, 120)
X, Y = np.meshgrid(g, g)
Z = np.sin(3 * X) * np.cos(3 * Y) * np.exp(-(X**2 + Y**2) / 2)
im = ax.pcolormesh(X, Y, Z, rasterized=True)
fig.colorbar(im, ax=ax, label=r"$\psi(x,y)$")
ax.set(xlabel="$x$", ylabel="$y$", title="Heatmap", aspect="equal")
fig.savefig(f"{out}/gallery.pdf")

# 2. All palettes
fig, ax = plt.subplots(figsize=(7.5, 3.6), constrained_layout=True)
for row, (name, pal) in enumerate(reversed(list(rhdt_mpl.PALETTES.items()))):
    for col, (cname, hexv) in enumerate(pal.items()):
        ax.barh(row, 1, left=col, height=0.8, color=hexv, edgecolor="none")
        lum = sum(int(hexv[i:i+2], 16) * f for i, f in zip((1, 3, 5), (.299, .587, .114)))
        ax.text(col + .5, row, cname, ha="center", va="center", fontsize=6.5,
                color="white" if lum < 140 else "black")
ax.set_yticks(range(len(rhdt_mpl.PALETTES)), list(reversed(list(rhdt_mpl.PALETTES))))
ax.set_xticks([]); ax.set_xlim(0, 10)
for s in ("left", "bottom"): ax.spines[s].set_visible(False)
ax.tick_params(left=False)
ax.set_title("Palettes (rhdt_mpl.PALETTES)")
fig.savefig(f"{out}/palettes.pdf")
