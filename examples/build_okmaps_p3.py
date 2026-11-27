"""Build src/rhdt_mpl/okmaps.py: the nine colormaps as 256-entry tables in Display P3.

The maps were designed in OKLab as sRGB tables, each at a fixed fraction of the largest chroma the sRGB gamut allows at
its lightness and hue (0.9 for the single-hue maps, less for the quieter ones).  The Display P3 tables keep the lightness
and hue of every entry and the same *fraction* of the largest chroma of the Display P3 gamut, so they are as saturated
relative to their gamut as the originals and use the room P3 has: the chroma grows by 1.0 to 1.4 times.

``ok_orchid`` is the exception (TWEAKS).  At the same fraction it stayed almost inside sRGB (35 of 256 entries outside), and
its pink end took up less of the map than the purple (about 37 % against 50 % of the range at a chroma of at least 0.10).
So its chroma fraction is multiplied by 1.3 (at most 0.95), and the hue along the map is re-timed with
``w(t) = t + 0.4 t (1 - t)``, which reaches magenta-pink at 40 % of the map instead of 50 %.  The lightness of every entry,
and so its dark -> light order, is unchanged.

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
#: the diverging maps, designed directly in Display P3 (see diverging_p3)
DIVERGING = {"ok_green_magenta": dict(hues=(146.0, 324.0), end_L=0.56, end_fraction=0.95, center_L=0.985,
                                      chroma_exp=0.6, lightness_exp=1.3),
             "ok_ruby_sapphire": dict(hues=(12.4, 238.6), end_L=0.56, end_fraction=0.95, center_L=0.985,
                                      chroma_exp=0.6, lightness_exp=1.3)}
ALL = NAMES + list(DIVERGING)

HEADER = '''"""Personal colormaps (256-entry tables in Display P3, designed in OKLab).

Multi-hue:   ok_dusk, ok_orchid
Single-hue:  ok_blue, ok_teal, ok_green, ok_orange, ok_red, ok_purple, ok_pink
Diverging:   ok_green_magenta (green - light center - magenta), ok_ruby_sapphire (ruby - light center - sapphire)
All but the diverging map run dark -> light; append _r for light -> dark (usual for single-hue maps
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


#: per map: *gain* multiplies the fraction of the largest chroma (at most *cap*), *warp* re-times the hue and the fraction
#: along the map by w(t) = t + warp * t * (1 - t); the lightness is not touched
TWEAKS = {"ok_orchid": dict(gain=1.3, cap=0.95, warp=0.4)}


def to_p3(table, gain=1.0, cap=1.0, warp=0.0):
    """Display P3 table with the lightness, hue and fraction of the largest chroma of an sRGB table (see TWEAKS)."""
    lab = cs.rgb_to_oklab(np.asarray(table), "srgb")
    L, a, b = lab.T
    C, h = np.hypot(a, b), np.unwrap(np.arctan2(b, a))
    c_srgb = max_chroma(L, np.degrees(h), "srgb")
    frac = np.where(c_srgb > 1e-6, C / np.maximum(c_srgb, 1e-6), 0.0)
    t = np.linspace(0, 1, len(L))
    w = t + warp * t * (1 - t)
    h, frac = np.interp(w, t, h), np.minimum(np.interp(w, t, frac) * gain, cap)
    c_p3 = max_chroma(L, np.degrees(h), "display-p3")
    C2 = frac * c_p3
    rgb = cs.oklab_to_rgb(np.column_stack([L, C2 * np.cos(h), C2 * np.sin(h)]), "display-p3")
    return np.clip(rgb, 0, 1)


def diverging_p3(hues, end_L=0.56, end_fraction=0.95, center_L=0.985, chroma_exp=0.6, lightness_exp=1.3, N=256):
    """A diverging Display P3 table of *N* entries: two arms of constant OKLCH hue (*hues*, degrees, first arm at index 0)
    that meet in a near-white center.  Along an arm at distance s from the center (0 to 1) the lightness is
    ``center_L - (center_L - end_L) * s ** lightness_exp`` and the chroma ``end_fraction * s ** chroma_exp`` times the largest
    chroma Display P3 allows there.  Each arm is then re-sampled at equal steps of OKLab distance, so that the colors
    change equally fast everywhere along it (the two arms are about 10 % different in length)."""
    n = 4001
    s = np.linspace(0, 1, n)
    arms = []
    for hue in hues:
        L = center_L - (center_L - end_L) * s ** lightness_exp
        C = end_fraction * max_chroma(L, np.full(n, hue), "display-p3") * s ** chroma_exp
        h = np.radians(hue)
        lab = np.column_stack([L, C * np.cos(h), C * np.sin(h)])
        arms.append((lab, np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(lab, axis=0), axis=1))])))
    t = np.arange(N) / (N - 1)
    sd = np.abs(2 * t - 1)
    out = np.zeros((N, 3))
    for (lab, arc), mask in zip(arms, (t < 0.5, t >= 0.5)):
        pos = np.interp(sd[mask] * arc[-1], arc, np.arange(n))
        i = np.floor(pos).astype(int).clip(0, n - 2)
        f = (pos - i)[:, None]
        out[mask] = lab[i] * (1 - f) + lab[i + 1] * f
    return np.clip(cs.oklab_to_rgb(out, "display-p3"), 0, 1)


def main(src):
    mod = _load("okmaps_srgb", src)
    lines = [HEADER]
    for name in ALL:
        if name in DIVERGING:
            t = diverging_p3(**DIVERGING[name])
            L = cs.rgb_to_oklab(t, "display-p3")[:, 0]
            assert np.all(np.diff(L[:128]) > 0) and np.all(np.diff(L[128:]) < 0), name  # dark -> light -> dark
        else:
            t = to_p3(mod.COLORMAPS[name].colors, **TWEAKS.get(name, {}))
            assert np.all(np.diff(cs.rgb_to_oklab(t, "display-p3")[:, 0]) > 0), name   # still dark -> light
        lines.append(f"_{name.upper()} = [")
        lines += [f"    ({r:.5f}, {g:.5f}, {b:.5f})," for r, g, b in t]
        lines.append("]\n")
    # the tables are named as in the sRGB module (_OK_DUSK, ...) and exposed as ok_dusk, ...
    footer = FOOTER % ", ".join(f'("{n}", _{n.upper()})' for n in ALL)
    open(OUT, "w").write("\n".join(lines) + footer)
    print("wrote", OUT)


if __name__ == "__main__":
    main(sys.argv[1])
