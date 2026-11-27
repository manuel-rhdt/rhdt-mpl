"""Color spaces of the package: sRGB and Display P3, OKLab, and gamut mapping.

Matplotlib has no color management: an RGB triple is three numbers in [0, 1].  The backend
(``umbruch_matplotlib.config.color_space``) says which space they are in, and ``rhdt_mpl.use`` sets it to
Display P3.  Everything in this package that produces numbers (palettes, colormaps, the OKLab helpers) produces
them in the *current* space, converting from the space it is defined in.

A color outside the gamut of the target space is brought back by reducing the OKLab chroma at constant
lightness and hue (not by clipping channels, which shifts the hue).  Display P3 and sRGB share the white point
(D65) and the transfer function, so grays are the same numbers in both and every sRGB color is inside P3.
"""
import contextlib

import numpy as np

SPACES = {
    #: primaries (xy of red, green, blue); white is D65 and the transfer function the sRGB one for all
    "srgb": ((0.640, 0.330), (0.300, 0.600), (0.150, 0.060)),
    "display-p3": ((0.680, 0.320), (0.265, 0.690), (0.150, 0.060)),
}
_D65_XY = (0.3127, 0.3290)

_EPS = 1e-6      # how far outside [0, 1] a linear channel may be and still count as inside the gamut

_M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                [0.2119034982, 0.6806995451, 0.1073969566],
                [0.0883024619, 0.2817188376, 0.6299787005]])
_M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                [1.9779984951, -2.4285922050, 0.4505937099],
                [0.0259040371, 0.7827717662, -0.8086757660]])
_M1_INV = np.linalg.inv(_M1)
_M2_INV = np.linalg.inv(_M2)


def _xy_to_xyz(xy):
    x, y = xy
    return np.array([x / y, 1.0, (1 - x - y) / y])


def _to_xyz(name):
    P = np.array([_xy_to_xyz(p) for p in SPACES[name]]).T
    return P * np.linalg.solve(P, _xy_to_xyz(_D65_XY))


#: linear RGB of each space -> linear sRGB (the space OKLab is defined from)
_TO_SRGB = {n: np.linalg.solve(_to_xyz("srgb"), _to_xyz(n)) for n in SPACES}
_FROM_SRGB = {n: np.linalg.inv(m) for n, m in _TO_SRGB.items()}

_current = "srgb"


def check(name):
    if name not in SPACES:
        raise ValueError(f"unsupported color space {name!r}; one of {sorted(SPACES)}")
    return name


def current():
    """The color space of the numbers Matplotlib is given (``"srgb"`` until ``rhdt_mpl.use`` says otherwise)."""
    return _current


def set_current(name):
    global _current
    _current = check(name)


@contextlib.contextmanager
def using(name):
    """``with using("display-p3"): ...`` makes *name* the current space for the block."""
    global _current
    old, _current = _current, check(name)
    try:
        yield
    finally:
        _current = old


def decode(v):
    """Encoded RGB -> linear light (the transfer function of sRGB and Display P3), sign-preserving."""
    v = np.asarray(v, float)
    a = np.abs(v)
    return np.sign(v) * np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def encode(v):
    """Linear light -> encoded RGB, sign-preserving."""
    v = np.asarray(v, float)
    a = np.abs(v)
    return np.sign(v) * np.where(a <= 0.0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - 0.055)


def linear_to_srgb_linear(lin, space):
    """Linear RGB in *space* -> linear sRGB (not clipped: a P3 color can have a channel above 1)."""
    return np.asarray(lin, float) @ _TO_SRGB[check(space)].T


def srgb_linear_to_linear(lin, space):
    """Linear sRGB -> linear RGB in *space* (not clipped)."""
    return np.asarray(lin, float) @ _FROM_SRGB[check(space)].T


def rgb_to_oklab(rgb, space=None):
    """OKLab (..., 3) of encoded RGB (..., 3) given in *space* (default: the current one)."""
    lms = linear_to_srgb_linear(decode(rgb), space or _current) @ _M1.T
    return np.cbrt(lms) @ _M2.T


def in_gamut(lin, eps=_EPS):
    """Whether linear RGB (..., 3) lies inside the gamut (each row, for an array of colors)."""
    lin = np.asarray(lin)
    return np.all((lin >= -eps) & (lin <= 1 + eps), axis=-1)


def _oklab_to_linear(lab, space):
    lms = (np.asarray(lab, float) @ _M2_INV.T) ** 3
    return srgb_linear_to_linear(lms @ _M1_INV.T, space)


def oklab_to_rgb(lab, space=None, clip_to_gamut=True):
    """Encoded RGB (..., 3) in *space* (default: the current one) of OKLab (..., 3).

    With *clip_to_gamut* a color outside the gamut of *space* keeps its lightness and hue and loses chroma, down to
    the boundary of the gamut.  Without it the result may lie outside [0, 1]."""
    space = space or _current
    lab = np.array(lab, float)
    single = lab.ndim == 1
    lab = np.atleast_2d(lab)
    lin = _oklab_to_linear(lab, space)
    if clip_to_gamut:
        bad = ~in_gamut(lin)
        if bad.any():
            L = lab[bad, 0]
            ab = lab[bad, 1:]
            lo, hi = np.zeros(len(L)), np.ones(len(L))
            for _ in range(40):          # largest chroma scale in [0, 1] that is inside
                mid = (lo + hi) / 2
                ok = in_gamut(_oklab_to_linear(np.column_stack([L, ab * mid[:, None]]), space))
                lo, hi = np.where(ok, mid, lo), np.where(ok, hi, mid)
            lin[bad] = _oklab_to_linear(np.column_stack([L, ab * lo[:, None]]), space)
        lin = np.clip(lin, 0, 1)
        # lightness outside (0, 1) has no chroma left to reduce
        lin[lab[:, 0] <= 0] = 0
        lin[lab[:, 0] >= 1] = 1
    rgb = encode(lin)
    return rgb[0] if single else rgb


def convert(rgb, src, dst):
    """Encoded RGB (..., 3) in *src* as encoded RGB in *dst*; a color outside the gamut of *dst* is gamut-mapped by
    reducing its chroma.  Identical spaces return the input unchanged."""
    rgb = np.asarray(rgb, float)
    if src == dst:
        return rgb
    lin = decode(rgb) @ (_FROM_SRGB[check(dst)] @ _TO_SRGB[check(src)]).T
    flat = np.atleast_2d(lin)
    if in_gamut(flat).all():
        return encode(np.clip(lin, 0, 1))
    return oklab_to_rgb(rgb_to_oklab(rgb, src), dst).reshape(rgb.shape)


def from_srgb(color, dst=None):
    """*color* (any Matplotlib color, or an array of RGB(A) rows) given as sRGB, as RGB(A) numbers in *dst* (default:
    the current space).  Use it for the colors Matplotlib supplies as sRGB (names, hex, built-in colormaps) when
    the figure is in Display P3: ``color=rhdt_mpl.from_srgb("tab:blue")``."""
    from matplotlib.colors import to_rgba_array
    dst = dst or _current
    single = isinstance(color, str) or (np.ndim(color) == 1 and len(color) in (3, 4)
                                        and not isinstance(color[0], str))
    rgba = to_rgba_array(color)
    out = np.concatenate([convert(rgba[:, :3], "srgb", dst), rgba[:, 3:]], axis=1)
    return tuple(out[0]) if single else out
