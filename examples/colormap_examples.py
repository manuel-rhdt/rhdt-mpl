"""Example plots of the colormaps.  Usage: colormap_examples.py OUTDIR  (writes cmap_wigner.pdf, cmap_fields.pdf,
cmap_curves.pdf)

    cmap_wigner   diverging maps on a signed quantity: the Wigner function of an even cat state
    cmap_fields   the sequential maps on one smooth random field
    cmap_curves   a map as a color scale for a family of curves, and a single-hue map for a density
"""
import sys

import numpy as np
import rhdt_mpl
import matplotlib as mpl
import matplotlib.pyplot as plt
from umbruch_matplotlib import rich

out = sys.argv[1] if len(sys.argv) > 1 else "."
W = rhdt_mpl.TWO_COLUMN


def truncated(name, hi):
    """The first *hi* of a colormap, for lines on a white background (the pale end would vanish)."""
    return mpl.colors.ListedColormap(mpl.colormaps[name](np.linspace(0, hi, 256)), name=f"{name}[0:{hi}]")


# ------------------------------------------------------------------ the Wigner function of a cat state: diverging
# W(x, p) of the even cat state with the two coherent components at x = +-x0 (hbar = 1): two Gaussians and, between them, an
# interference term that oscillates in p and makes W negative.
x0 = 2.1
x = np.linspace(-3.6, 3.6, 480)
X, P = np.meshgrid(x, x)
G = lambda x_, p_: np.exp(-(x_**2 + p_**2))
Wig = (G(X - x0, P) + G(X + x0, P) + 2 * G(X, P) * np.cos(2 * x0 * P)) / (np.pi * 2 * (1 + np.exp(-2 * x0**2)))
m = np.abs(Wig).max()

fig, axs = plt.subplots(1, 2, figsize=(W, 3.15), layout="constrained")
for ax, name in zip(axs, ("ok_ruby_sapphire", "ok_green_magenta")):
    im = ax.imshow(Wig, extent=(x[0], x[-1], x[0], x[-1]), origin="lower", cmap=name, vmin=-m, vmax=m,
                   interpolation="bilinear")
    ax.contour(X, P, np.where(np.abs(P) < 1.3, Wig, np.nan), levels=[0], colors="0.2", linewidths=0.45)  # sign changes
    ax.set(xlabel=r"$x$", ylabel=r"$p$", title=name, aspect="equal")
    cb = fig.colorbar(im, ax=ax, shrink=0.82, pad=0.02, label=r"$W(x,p)$")
    cb.set_ticks([-m, 0, m])
    cb.set_ticklabels([f"{-m:.2f}", "0", f"{m:.2f}"])
rhdt_mpl.panel_labels(axs, y=1.04)
fig.suptitle(rich("Wigner function of an even cat state: diverging maps centered on zero"), fontsize=8.8, x=0.5)
fig.savefig(f"{out}/cmap_wigner.pdf")
plt.close(fig)

# ------------------------------------------------------------------ one random field, three sequential maps
rng = np.random.default_rng(11)
n = 256
k = np.hypot(*np.meshgrid(np.fft.fftfreq(n), np.fft.fftfreq(n)))
spectrum = np.exp(-(k / 0.035) ** 2) / (k + 0.01)          # smooth, with large and small scales
field = np.fft.ifft2(np.fft.fft2(rng.standard_normal((n, n))) * spectrum).real
field = (field - field.min()) / (field.max() - field.min())

fig, axs = plt.subplots(1, 3, figsize=(W, 2.75), layout="constrained")
for ax, name in zip(axs, ("ok_orchid", "ok_ember", "ok_lagoon")):
    im = ax.imshow(field, cmap=name, interpolation="bilinear")
    ax.contour(field, levels=np.linspace(0.1, 0.9, 5), colors="white", linewidths=0.3, alpha=0.55)
    ax.set(title=name, xticks=[], yticks=[])
    fig.colorbar(im, ax=ax, orientation="horizontal", shrink=0.9, pad=0.03, aspect=22, ticks=[0, 0.5, 1])
rhdt_mpl.panel_labels(axs, y=1.03)
fig.suptitle(rich("One smooth random field in three sequential maps: lightness orders the values, hue tells them apart"),
             fontsize=8.8)
fig.savefig(f"{out}/cmap_fields.pdf")
plt.close(fig)

# ------------------------------------------------------------------ a map as a color scale for curves; a single-hue map for a density
fig, axs = plt.subplots(1, 2, figsize=(W, 2.9), layout="constrained")

ax = axs[0]
gammas = np.linspace(0.03, 0.55, 18)
cmap = truncated("ok_lagoon", 0.8)
norm = mpl.colors.Normalize(gammas[0], gammas[-1])
t = np.linspace(0, 14, 600)
for g in gammas:
    ax.plot(t, np.exp(-g * t) * np.cos(2.2 * t), color=cmap(norm(g)), lw=1.1)
ax.set(xlabel=rich("time <i>t</i>"), ylabel=r"$x(t)$", xlim=(0, 14), title="curves colored by damping")
fig.colorbar(mpl.cm.ScalarMappable(norm, cmap), ax=ax, label=r"damping $\gamma$", pad=0.02)

ax = axs[1]
# a "banana" distribution, as in a posterior with a curved degeneracy: a single-hue map for a density on white
rng = np.random.default_rng(5)
q = rng.standard_normal((400_000, 2))
bx, by = 1.6 * q[:, 0], 0.55 * q[:, 1] + 0.45 * (1.6 * q[:, 0]) ** 2 - 1.2
hb = ax.hexbin(bx, by, gridsize=48, bins="log", mincnt=1, cmap="ok_blue_r", linewidths=0.1, edgecolors="face",
               extent=(-5, 5, -2.5, 8))
ax.set(xlabel=r"$\theta_1$", ylabel=r"$\theta_2$", title="density in ok_blue_r", xlim=(-5, 5), ylim=(-2.5, 8))
fig.colorbar(hb, ax=ax, label="samples per cell", pad=0.02)

rhdt_mpl.panel_labels(axs, y=1.03)
fig.savefig(f"{out}/cmap_curves.pdf")
plt.close(fig)
