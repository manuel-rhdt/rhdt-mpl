"""One figure that exercises the features of rhdt_mpl. Usage: features.py OUTDIR  (writes features.pdf)"""
import sys
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from rhdt_mpl import oklab
from umbruch_matplotlib import rich

out = sys.argv[1] if len(sys.argv) > 1 else "."
rng = np.random.default_rng(2)
fig, axs = plt.subplots(2, 3, figsize=(rhdt_mpl.TWO_COLUMN, 5.0))
x = np.linspace(0, 10, 300)

# a  default style and cycle, Noto Sans, rich text and math through umbruch
ax = axs[0, 0]
for k in range(5):
    ax.plot(x, np.exp(-x / 6) * np.cos(x + 0.6 * k), label=rf"$\varphi={0.6 * k:.1f}$")
ax.set(xlabel=rich("time <i>t</i> (ms)"), ylabel=r"$\hat\rho_{ij}(t)$", title="default cycle")
ax.set_ylim(-1, 2.0)
ax.legend(ncols=2, fontsize=6.5, loc="upper right", columnspacing=1.0, handlelength=1.6)

# b  the print cycle: ok6 colors with line styles
ax = axs[0, 1]
rhdt_mpl.set_cycle("ok-print")
ax.set_prop_cycle(rhdt_mpl.cycle("ok-print"))
for k in range(6):
    ax.plot(x, np.sin(x / 1.7 + 0.5 * k), label=str(k + 1))
ax.set(xlabel="x", title="ok-print cycle")
ax.set_ylim(-1.8, 1.1)
ax.legend(ncols=3, fontsize=6.5, loc="lower center", columnspacing=1.0, handlelength=2.2)
rhdt_mpl.use(backend=False)          # back to the default cycle

# c  default colormap
ax = axs[0, 2]
g = np.linspace(-2, 2, 160)
X, Y = np.meshgrid(g, g)
Z = np.sin(3 * X) * np.cos(3 * Y) * np.exp(-(X**2 + Y**2) / 2)
im = ax.pcolormesh(X, Y, Z, rasterized=True)
fig.colorbar(im, ax=ax, label=r"$\psi(x,y)$")
ax.set(title="ok_orchid", aspect="equal", xlabel="$x$", ylabel="$y$")

# d  single-hue colormap, reversed for a white background
ax = axs[1, 0]
pts = rng.standard_normal((300, 2))
sc = ax.scatter(*pts.T, c=np.hypot(*pts.T), cmap="ok_blue_r", s=14, edgecolor="rhdt:tol-dark:dark grey", lw=0.3)
fig.colorbar(sc, ax=ax, label="distance")
ax.set(title="ok_blue_r", xlabel="x", ylabel="y")

# e  roles: black theory, bright highlight, muted family and baseline, by name and via OKLab
ax = axs[1, 1]
xs = np.linspace(0, 10, 40)
theory = 30 * (1 - np.exp(-xs / 4))
for c, name, k, m in zip(oklab.family("rhdt:tol-vibrant:cyan", 3), ["InfoNCE", "MINE", "SMILE"],
                         [0.30, 0.22, 0.15], "^v<"):
    ax.plot(xs, k * theory, color=c, lw=1.2, marker=m, markevery=6, markersize=3.5, label=name)
ax.plot(xs, 0.6 * theory, color=oklab.muted("rhdt:tol-vibrant:orange"), ls="--", lw=1.2, label="baseline")
ax.plot(xs, theory, color="black", lw=2, zorder=10, label="theory")
ax.plot(xs, theory * (1 - 0.04 * np.sin(xs)), color="rhdt:tol-vibrant:orange", marker="o", markevery=6, markersize=3.5,
        label="ML-PWS")
ax.set(title="named colors", xlabel="x", ylabel="MI (bit)", xlim=(0, 16.5))
ax.legend(fontsize=6.5, loc="center right")

# f  the 8-color cycle on stacked bars, named fill and edge colors
ax = axs[1, 2]
rhdt_mpl.set_cycle("ok8")
ax.set_prop_cycle(rhdt_mpl.cycle("ok8"))
h = rng.uniform(1, 3, (8, 4)); bottom = np.zeros(4)
for i in range(8):
    ax.bar(range(4), h[i], bottom=bottom, width=0.8, edgecolor="white", lw=0.4, label=f"{i + 1}")
    bottom += h[i]
ax.set(title="ok8 cycle", xlabel="group", ylabel="counts", xticks=range(4))
rhdt_mpl.use(backend=False)

rhdt_mpl.panel_labels(axs)           # bold a, b, c, ... at the top left of each axes
fig.savefig(f"{out}/features.pdf")
