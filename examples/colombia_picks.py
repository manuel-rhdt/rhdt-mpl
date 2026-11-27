"""The chosen Colombian species as colors from reflectance spectra. Usage: colombia_picks.py DATA_DIR OUTDIR
(writes colombia_picks.pdf)"""
import os
import sys

import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rhdt_mpl import oklab

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import colombia_spectra as cs                  # noqa: E402

SPECIES = [("Heliangelus_exortis", "tourmaline sunangel"), ("Chrysolampis_mosquitus", "ruby-topaz"),
           ("Coeligena_bonapartei", "golden-bellied starfrontlet"), ("Chrysuronia_oenone", "golden-tailed sapphire")]
data, out = sys.argv[1], sys.argv[2]
meta, spec = cs.load(os.path.join(data, "refcolC.txt"))
W, SW, RH = rhdt_mpl.TWO_COLUMN, 0.78, 0.78
H = 0.55 + RH * len(SPECIES)
fig = plt.figure(figsize=(W, H), layout="none")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.text(0.1, H - 0.2, "four Colombian hummingbirds, males, from reflectance spectra", fontsize=9, fontweight="bold", va="center")
for i, name in enumerate(cs.PATCHES.values()):
    ax.text(2.6 + i * (SW + 0.04) + SW / 2, H - 0.45, name, fontsize=6.5, ha="center", color="0.4")
for r, (sp, common) in enumerate(SPECIES):
    y = H - 0.55 - RH * (r + 1) + 0.12
    ax.text(0.1, y + 0.45, common, fontsize=8, fontweight="bold", va="center")
    ax.text(0.1, y + 0.27, sp.replace("_", " "), fontsize=6.5, style="italic", color="0.35", va="center")
    for i, (code, name) in enumerate(cs.PATCHES.items()):
        idx = [k for k, m in enumerate(meta) if m["Species"] == sp and m["Sex"] == "Males" and m["Feather_type"] == code]
        hexv, ing = cs.linear_rgb_to_hex(cs.spectrum_to_linear_rgb(np.median(spec[idx], axis=0)))
        x = 2.6 + i * (SW + 0.04)
        ax.add_patch(Rectangle((x, y + 0.14), SW, 0.46, color=hexv, lw=0))
        ink = "white" if oklab.lightness(hexv) < 0.68 else "black"
        ax.text(x + SW / 2, y + 0.37, hexv + ("" if ing else " ∘"), fontsize=5.8, ha="center", va="center",
                family="Fira Mono", color=ink)
        ax.text(x + SW / 2, y + 0.06, f"n={len(idx)}", fontsize=5, ha="center", va="center", color="0.45")
fig.savefig(os.path.join(out, "colombia_picks.pdf"))
