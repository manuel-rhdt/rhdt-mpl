"""Design the iridescent colormaps ok_colibri and ok_gorget: paths through hummingbird hues in OKLCH with
monotone lightness, gamut-mapped (chroma reduced at constant L and h) and re-spaced to equal OKLab arc length.

    python examples/design_colibri_cmaps.py        # prints the tables as Python source
"""
import numpy as np
from rhdt_mpl import oklab as ok

# (t, L, C, h) control points; h in degrees, unwrapped so the sweep is continuous
PATHS = {
    "ok_colibri": [(0.00, 0.17, 0.12, 292), (0.22, 0.34, 0.21, 285), (0.45, 0.50, 0.19, 255),
                   (0.62, 0.66, 0.11, 205), (0.72, 0.71, 0.12, 180), (0.80, 0.77, 0.15, 150), (0.90, 0.86, 0.17, 115),
                   (1.00, 0.93, 0.17, 98)],
    "ok_gorget": [(0.00, 0.17, 0.13, 300), (0.25, 0.38, 0.24, 335), (0.50, 0.53, 0.22, 385),
                  (0.74, 0.69, 0.16, 418), (1.00, 0.93, 0.17, 458)],
}


def rgb_float(L, C, h):
    """Gamut-mapped linear->sRGB floats for OKLCH (chroma reduced by bisection)."""
    hr = np.radians(h)
    lin = lambda c: ok._lab_to_linear_rgb([L, c * np.cos(hr), c * np.sin(hr)])
    if not ok._in_gamut(lin(C)):
        lo, hi = 0.0, C
        for _ in range(40):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ok._in_gamut(lin(mid)) else (lo, mid)
        C = lo
    return np.clip(ok._linear_to_srgb(np.clip(lin(C), 0, 1)), 0, 1)


def max_chroma(L, h):
    """Largest chroma inside sRGB at lightness *L* and hue *h*."""
    hr = np.radians(h)
    lo, hi = 0.0, 0.5
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if ok._in_gamut(ok._lab_to_linear_rgb([L, mid * np.cos(hr), mid * np.sin(hr)])) else (lo, mid)
    return lo


def table(points, n=256, fine=6000, margin=0.95, smooth=151):
    """The requested chroma is capped at *margin* of the gamut limit and smoothed, so that the path
    stays inside the gamut and has no creases where the gamut boundary changes direction."""
    pts = np.array(points)
    t = np.linspace(0, 1, fine)
    L, C, h = (np.interp(t, pts[:, 0], pts[:, k]) for k in (1, 2, 3))
    C = np.minimum(C, margin * np.array([max_chroma(a, b) for a, b in zip(L, h)]))
    k = np.ones(smooth) / smooth
    C = np.convolve(np.pad(C, smooth // 2, mode="edge"), k, mode="valid")
    rgb = np.array([rgb_float(*v) for v in zip(L, C, h)])
    lab = np.array([ok._rgb_to_lab(c) for c in rgb])
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(lab, axis=0), axis=1))])
    idx = np.interp(np.linspace(0, s[-1], n), s, np.arange(fine))
    out = np.array([[np.interp(i, np.arange(fine), rgb[:, k]) for k in range(3)] for i in idx])
    return out


def source(name, tab):
    rows = "\n".join("    (%.5f, %.5f, %.5f)," % tuple(r) for r in tab)
    return f"_{name.upper()} = [\n{rows}\n]\n"


if __name__ == "__main__":
    for name, pts in PATHS.items():
        print(source(name, table(pts)))
