"""Overview of the colors of all species of the Colombian hummingbird reflectance database.
Usage: colombia_overview.py DATA_DIR OUTDIR   (writes colombia.pdf)"""
import sys
import os
import numpy as np
import rhdt_mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import colombia_spectra as cs                  # noqa: E402

data, out = sys.argv[1], sys.argv[2]
meta, spec = cs.load(os.path.join(data, "refcolC.txt"))
species = cs.species_list(meta)
rows = []
for sp in species:
    sex = "Males" if any(m["Species"] == sp and m["Sex"] == "Males" for m in meta) else "Females"
    cols, ing = {}, {}
    for code, name in cs.PATCHES.items():
        idx = [i for i, m in enumerate(meta) if m["Species"] == sp and m["Sex"] == sex and m["Feather_type"] == code]
        if idx:
            cols[name], ing[name] = cs.linear_rgb_to_hex(cs.spectrum_to_linear_rgb(np.median(spec[idx], axis=0)))
    rows.append((sp, sex, cols, ing))

NC, per = 3, int(np.ceil(len(rows) / 3))
RH, SW, NAMEW = 0.158, 0.20, 1.18
colw = NAMEW + 5 * (SW + 0.01) + 0.12
W, H = NC * colw + 0.2, per * RH + 0.75
fig = plt.figure(figsize=(W, H), layout="none")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.text(0.1, H - 0.2, "Colombian hummingbirds: plumage colors from reflectance spectra", fontsize=9, fontweight="bold", va="center")
ax.text(W - 0.1, H - 0.2, "males where measured (f = females); ∘ = gamut-mapped", fontsize=5.6, ha="right", va="center", color="0.35")
for c in range(NC):
    x0 = 0.1 + c * colw
    for i, name in enumerate(cs.PATCHES.values()):
        ax.text(x0 + NAMEW + i * (SW + 0.01) + SW / 2, H - 0.45, name, fontsize=4.6, ha="center", va="center", color="0.4")
for k, (sp, sex, cols, ing) in enumerate(rows):
    c, r = divmod(k, per)
    x0, y = 0.1 + c * colw, H - 0.62 - r * RH
    ax.text(x0, y + RH / 2 - 0.01, sp.replace("_", " ") + ("" if sex == "Males" else " (f)"), fontsize=5, style="italic",
            va="center")
    for i, name in enumerate(cs.PATCHES.values()):
        if name in cols:
            x = x0 + NAMEW + i * (SW + 0.01)
            ax.add_patch(Rectangle((x, y + 0.012), SW, RH - 0.024, color=cols[name], lw=0))
            if not ing[name]:
                ax.plot([x + SW / 2], [y + RH / 2], "o", ms=1.4, mfc="none", mec="white", mew=0.5)
fig.savefig(os.path.join(out, "colombia.pdf"))
