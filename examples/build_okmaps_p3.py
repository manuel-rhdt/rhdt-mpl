"""Build src/rhdt_mpl/okmaps.py: the nine colormaps as 256-entry tables in Display P3.

The maps were designed in OKLab as sRGB tables, each at a fixed fraction of the largest chroma the sRGB gamut allows at
its lightness and hue (0.9 for the single-hue maps, less for the quieter ones).  The Display P3 tables keep the lightness
and hue of every entry and the same *fraction* of the largest chroma of the Display P3 gamut, so they are as saturated
relative to their gamut as the originals and use the room P3 has: the chroma grows by 1.0 to 1.4 times.

    git show 312d922:src/rhdt_mpl/okmaps.py > okmaps_srgb.py      # the last version with sRGB tables
    python examples/build_okmaps_p3.py okmaps_srgb.py             # rewrites src/rhdt_mpl/okmaps.py
"""
import importlib.util
import os
import sys

import numpy as np

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "rhdt_mpl")
OUT = os.path.join(SRC, "okmaps.py")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cs = _load("colorspace", os.path.join(SRC, "colorspace.py"))      # not through the package: it imports okmaps
NAMES = ["ok_dusk", "ok_orchid", "ok_blue", "ok_teal", "ok_green", "ok_orange", "ok_red", "ok_purple", "ok_pink"]

HEADER = '''"""Personal colormaps (256-entry tables in Display P3, designed in OKLab).

Multi-hue:   ok_dusk, ok_orchid
Single-hue:  ok_blue, ok_teal, ok_green, ok_orange, ok_red, ok_purple, ok_pink
All run dark -> light; append _r for light -> dark (usual for single-hue maps
on a white background). Only needs matplotlib.

The tables (``COLORMAPS``) are Display P3 numbers.  ``register(space)`` registers the maps with Matplotlib for figures
whose numbers are in *space*: for ``"display-p3"`` as they are, for ``"srgb"`` converted, with chroma reduced where a
color lies outside sRGB.  ``rhdt_mpl.use()`` does this.

    import rhdt_mpl
    plt.imshow(z, cmap="ok_blue_r")
"""
import matplotlib as mpl
import numpy as np
from matplotlib.colors import ListedColormap

from . import colorspace

'''
FOOTER = '''
#: name -> ListedColormap with the tables above, in Display P3
COLORMAPS = {}
for _n, _t in [%s]:
    COLORMAPS[_n] = globals()[_n] = ListedColormap(_t, name=_n)


def register(space="display-p3"):
    """Register the maps and their ``_r`` versions with Matplotlib for figures whose numbers are in *space*."""
    for name, cmap in COLORMAPS.items():
        table = colorspace.convert(np.array(cmap.colors), "display-p3", space)
        for c in (ListedColormap(table, name=name), ListedColormap(table[::-1], name=name + "_r")):
            if c.name in mpl.colormaps:         # registered by an earlier call, in another color space
                mpl.colormaps.unregister(c.name)
            mpl.colormaps.register(c)
'''


def max_chroma(L, h, space):
    hr = np.radians(h)
    lo, hi = np.zeros_like(L), np.full_like(L, 0.5)
    for _ in range(50):
        mid = (lo + hi) / 2
        lab = np.column_stack([L, mid * np.cos(hr), mid * np.sin(hr)])
        ok = cs.in_gamut(cs._oklab_to_linear(lab, space), 0)
        lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
    return lo


def to_p3(table):
    """Display P3 table with the lightness, hue and fraction of the largest chroma of an sRGB table."""
    lab = cs.rgb_to_oklab(np.asarray(table), "srgb")
    L, a, b = lab.T
    C, h = np.hypot(a, b), np.arctan2(b, a)
    c_srgb, c_p3 = max_chroma(L, np.degrees(h), "srgb"), max_chroma(L, np.degrees(h), "display-p3")
    frac = np.where(c_srgb > 1e-6, C / np.maximum(c_srgb, 1e-6), 0.0)
    C2 = frac * c_p3
    rgb = cs.oklab_to_rgb(np.column_stack([L, C2 * np.cos(h), C2 * np.sin(h)]), "display-p3")
    return np.clip(rgb, 0, 1)


def main(src):
    mod = _load("okmaps_srgb", src)
    lines = [HEADER]
    for name in NAMES:
        t = to_p3(mod.COLORMAPS[name].colors)
        assert np.all(np.diff(cs.rgb_to_oklab(t, "display-p3")[:, 0]) > 0), name       # still dark -> light
        lines.append(f"_{name.upper()} = [")
        lines += [f"    ({r:.5f}, {g:.5f}, {b:.5f})," for r, g, b in t]
        lines.append("]\n")
    # the tables are named as in the sRGB module (_OK_DUSK, ...) and exposed as ok_dusk, ...
    footer = FOOTER % ", ".join(f'("{n}", _{n.upper()})' for n in NAMES)
    open(OUT, "w").write("\n".join(lines) + footer)
    print("wrote", OUT)


if __name__ == "__main__":
    main(sys.argv[1])
