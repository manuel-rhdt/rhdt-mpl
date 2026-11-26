"""Color adjustments in OKLab / OKLCH (Ottosson, 2020).

All functions take any Matplotlib color spec ("#EE7733", "C1", "tab:red", an RGB tuple, ...)
and return a ``#rrggbb`` string; alpha is ignored.  OKLCH is lightness L in [0, 1], chroma C
(about 0 to 0.4 inside sRGB) and hue h in degrees.

A result that falls outside the sRGB gamut is brought back by reducing chroma at constant
lightness and hue, not by clipping channels (which shifts the hue).

    from rhdt_mpl import oklab
    oklab.muted("#EE7733")                  # same hue, less chroma, a bit lighter
    oklab.lighten("#0077BB", 0.1)           # +0.1 in L
    oklab.adjust("#009988", dh=-20)         # rotate the hue
    oklab.mix("#EE7733", "#0077BB", 0.3)    # interpolate in OKLab
    oklab.family("#33BBEE", 3)              # three lightness steps of one hue
"""
import numpy as np
from matplotlib.colors import to_rgb

__all__ = ["to_oklab", "to_oklch", "oklab", "oklch", "adjust", "lighten", "darken",
           "saturate", "desaturate", "rotate_hue", "mix", "muted", "family", "lightness"]

_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1_INV = np.linalg.inv(_M1)
_M2_INV = np.linalg.inv(_M2)


def _srgb_to_linear(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.abs(c) ** (1 / 2.4) - 0.055)


def _rgb_to_lab(rgb):
    lms = _M1 @ _srgb_to_linear(rgb)
    return _M2 @ np.cbrt(lms)


def _lab_to_linear_rgb(lab):
    lms = (_M2_INV @ np.asarray(lab, float)) ** 3
    return _M1_INV @ lms


def to_oklab(color):
    """(L, a, b) of *color*."""
    return tuple(float(v) for v in _rgb_to_lab(to_rgb(color)))


def to_oklch(color):
    """(L, C, h) of *color*, h in degrees [0, 360)."""
    L, a, b = _rgb_to_lab(to_rgb(color))
    return float(L), float(np.hypot(a, b)), float(np.degrees(np.arctan2(b, a)) % 360)


def lightness(color):
    """OKLab lightness L of *color*."""
    return to_oklab(color)[0]


def _hex(rgb):
    rgb = np.clip(np.round(np.asarray(rgb, float) * 255), 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(rgb)


def _in_gamut(lin, eps=1e-6):
    return bool(np.all(lin >= -eps) and np.all(lin <= 1 + eps))


def oklch(L, C, h):
    """Hex color for OKLCH (*L*, *C*, *h* degrees), gamut-mapped by reducing *C*."""
    if L <= 0:
        return "#000000"
    if L >= 1:
        return "#ffffff"
    C = max(float(C), 0.0)
    hr = np.radians(h)

    def lin(c):
        return _lab_to_linear_rgb([L, c * np.cos(hr), c * np.sin(hr)])

    if not _in_gamut(lin(C)):
        lo, hi = 0.0, C
        for _ in range(40):
            mid = (lo + hi) / 2
            if _in_gamut(lin(mid)):
                lo = mid
            else:
                hi = mid
        C = lo
    return _hex(_linear_to_srgb(np.clip(lin(C), 0, 1)))


def oklab(L, a, b):
    """Hex color for OKLab (*L*, *a*, *b*), gamut-mapped by reducing chroma."""
    return oklch(L, float(np.hypot(a, b)), float(np.degrees(np.arctan2(b, a))))


def adjust(color, *, L=None, C=None, h=None, dL=0.0, dC=0.0, dh=0.0, scale_C=1.0):
    """Change OKLCH coordinates of *color*.

    ``L``, ``C``, ``h`` set a coordinate; ``dL``, ``dC``, ``dh`` add to it; ``scale_C``
    multiplies the chroma (applied before ``dC``).  Gray stays gray under hue changes.
    """
    L0, C0, h0 = to_oklch(color)
    L1 = (L0 if L is None else L) + dL
    C1 = (C0 if C is None else C) * scale_C + dC
    h1 = (h0 if h is None else h) + dh
    return oklch(float(np.clip(L1, 0, 1)), C1, h1)


def lighten(color, amount=0.1):
    """Raise OKLab lightness by *amount* (L runs from 0 to 1)."""
    return adjust(color, dL=amount)


def darken(color, amount=0.1):
    """Lower OKLab lightness by *amount*."""
    return adjust(color, dL=-amount)


def saturate(color, factor=1.3):
    """Multiply chroma by *factor* (> 1), up to the sRGB gamut."""
    return adjust(color, scale_C=factor)


def desaturate(color, factor=0.7):
    """Multiply chroma by *factor* (< 1)."""
    return adjust(color, scale_C=factor)


def rotate_hue(color, degrees):
    """Rotate the OKLCH hue by *degrees*."""
    return adjust(color, dh=degrees)


def mix(color1, color2, t=0.5):
    """Interpolate between two colors in OKLab; t=0 gives *color1*, t=1 gives *color2*."""
    a, b = _rgb_to_lab(to_rgb(color1)), _rgb_to_lab(to_rgb(color2))
    return oklab(*((1 - t) * a + t * b))


def muted(color, chroma=0.5, lighten=0.15):
    """A quieter version of *color*: chroma multiplied by *chroma*, and lightness moved
    the fraction *lighten* of the way to white.  The hue is kept, so a muted line still
    reads as belonging to its bright counterpart."""
    L, C, h = to_oklch(color)
    return oklch(L + lighten * (1 - L), C * chroma, h)


def family(color, n, spread=0.3, lo=0.3, hi=0.85):
    """*n* colors of the hue and chroma of *color*, differing in lightness.

    Lightness is spaced evenly over a window of width *spread* centred on that of *color*,
    kept inside [*lo*, *hi*], and ordered dark to light.  Hue alone is not enough to tell
    members apart (and not at all for some readers), so the steps are in lightness; pair
    them with different markers or dashes as well.
    """
    L, C, h = to_oklch(color)
    if n == 1:
        return [_hex(to_rgb(color))]
    span = min(spread, hi - lo)
    start = min(max(L - span / 2, lo), hi - span)
    return [oklch(start + span * i / (n - 1), C, h) for i in range(n)]
