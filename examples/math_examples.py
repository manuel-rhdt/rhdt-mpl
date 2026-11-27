"""Typeset math in a figure. Usage: math_examples.py OUTDIR  (writes math.pdf)

Formulas are ordinary Matplotlib mathtext ($...$); umbruch lays them out as MathML in Fira Math.
"""
import sys

import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from umbruch_matplotlib import rich

out = sys.argv[1] if len(sys.argv) > 1 else "."
fig = plt.figure(figsize=(rhdt_mpl.TWO_COLUMN, 4.3), layout="constrained")
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.62], hspace=0.08)
ax1, ax2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
axf = fig.add_subplot(gs[1, :])

# a  Planck's law, with Wien's displacement law marked
h, kB, c = 6.62607015e-34, 1.380649e-23, 2.99792458e8
nu = np.linspace(0.02, 3.2, 400) * 1e15
temps = (4000, 5000, 6000, 7000)
peaks = []
for T, col in zip(temps, rhdt_mpl.palette("colibri", ["ruby", "amber", "emerald", "sapphire"])):
    B = 2 * h * nu**3 / c**2 / np.expm1(h * nu / (kB * T))
    ax1.plot(nu / 1e15, B * 1e9, color=col, label=rf"$T={T}\,\mathrm{{K}}$")
    peaks.append((2.821439 * kB * T / h / 1e15, B.max() * 1e9))
ax1.plot(*zip(*peaks), "o--", color="0.3", ms=3, lw=0.8)
ax1.annotate(r"$\nu_{\max}=\dfrac{2.82\,k_B T}{h}$", xy=peaks[1], xytext=(1.25, 32), textcoords="data",
             arrowprops=dict(arrowstyle="-", color="0.3", lw=0.6, shrinkA=2, shrinkB=2), fontsize=8.5)
ax1.set(xlabel=r"$\nu\ (10^{15}\,\mathrm{Hz})$", ylabel=r"$B_\nu(T)\ (10^{-9}\,\mathrm{W\,m^{-2}\,Hz^{-1}\,sr^{-1}})$",
        xlim=(0, 3.2), title="blackbody radiation")
ax1.legend(loc="upper right")

# b  damped Rabi oscillations
t = np.linspace(0, 12, 500)
Omega = 2.0
for gam, col in zip((0.1, 0.4, 1.0), rhdt_mpl.palette("colibri", ["sapphire", "emerald", "ruby"])):
    ax2.plot(t, 0.5 * (1 - np.exp(-gam * t / 2) * np.cos(Omega * t)), color=col,
             label=rf"$\gamma={gam}\,\Omega/2$")
ax2.set(xlabel=r"$\Omega t$ (rad)", ylabel=r"$P_e(t)=\langle e|\rho(t)|e\rangle$", xlim=(0, 12), ylim=(0, 1.3),
        title=rich("damped Rabi oscillations"))
ax2.legend(loc="upper right", ncols=3, columnspacing=1.0, handlelength=1.4)
rhdt_mpl.panel_labels([ax1, ax2], y=1.03)

# c  the equations behind them, set as text
axf.axis("off")
eqs = [
    (r"Lindblad master equation", r"$\dot\rho=-\dfrac{i}{\hbar}\,[H,\rho]+\sum_k \gamma_k\left(L_k\rho L_k^\dagger"
                                   r"-\dfrac{1}{2}\{L_k^\dagger L_k,\rho\}\right)$"),
    (r"two-level Hamiltonian", r"$H=\dfrac{\hbar}{2}\begin{pmatrix}\Delta & \Omega\\ \Omega^{*} & -\Delta\end{pmatrix},"
                                r"\qquad P_e(t)=\dfrac{1}{2}\left[1-e^{-\gamma t/2}\cos\Omega t\right]$"),
    (r"Planck's law", r"$B_\nu(T)=\dfrac{2h\nu^{3}}{c^{2}}\,\dfrac{1}{e^{h\nu/k_B T}-1},\qquad"
                       r"\displaystyle\int_0^\infty B_\nu\,d\nu=\dfrac{2\pi^{4}k_B^{4}}{15\,h^{3}c^{2}}\,T^{4}$"),
]
for i, (name, eq) in enumerate(eqs):
    y = 0.84 - 0.36 * i
    axf.text(0.0, y, name, fontsize=7, color="0.35", va="center", transform=axf.transAxes)
    axf.text(0.2, y, eq, fontsize=10, va="center", transform=axf.transAxes)
fig.savefig(f"{out}/math.pdf")
