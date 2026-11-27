"""Matplotlib defaults: umbruch backend, Noto fonts, personal color palettes.

    import rhdt_mpl          # before importing matplotlib.pyplot, ideally
    import matplotlib.pyplot as plt

Importing the package selects the umbruch backend in the Display P3 color space, registers the bundled
Noto fonts (the backend hands them to umbruch), and applies the ``rhdt`` style.  ``rhdt_mpl.use(...)`` redoes
this explicitly; ``rhdt_mpl.set_palette(name)`` changes the color cycle.
"""
import os
import sys
from importlib import resources

import matplotlib as mpl
import matplotlib.style
from matplotlib import font_manager as fm

from . import colorspace  # sRGB / Display P3, OKLab, gamut mapping
from . import okmaps  # ok_orchid, ok_blue, ... (+ _r), registered in the color space by use()
from . import oklab  # OKLab color helpers
from .colorspace import from_srgb
from .palettes import (PALETTES, NATIVE_SPACE, DEFAULT_PALETTE, DEFAULT_CYCLE, OK_PRINT_LINESTYLES, colors, cycle,
                       named_colors, wide_css, WIDE, SOURCES, PARTNERS)

__all__ = ["use", "set_palette", "set_cycle", "cycle", "register_colors", "named_colors", "wide_css", "from_srgb", "colorspace", "NATIVE_SPACE", "SOURCES", "PARTNERS", "palette", "panel_labels", "PALETTES", "font_dir",
           "TWO_COLUMN", "oklab"]

BACKEND = "module://umbruch_matplotlib"
TWO_COLUMN = 510 / 72   # figure width in inches used for the ML-PWS paper figures
DEFAULT_CMAP = "ok_orchid"
DEFAULT_COLOR_SPACE = "display-p3"
MATH_FONT = "Noto Sans Math"   # needs a backend with config.math_font

_here = resources.files(__package__)
font_dir = os.fspath(_here / "fonts")
_style = os.fspath(_here / "rhdt.mplstyle")


def palette(name, names=None):
    """List of hex colors of palette *name* (see ``PALETTES``)."""
    return colors(name, names)


def set_palette(name, names=None):
    """Use palette *name* (optionally only/ordered *names*) as the property cycle."""
    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(color=colors(name, names))


def panel_labels(axes, labels="abcdefghijklmnopqrstuvwxyz", x=0.0, y=1.01, size=10):
    """Bold lowercase panel letters at the top left of each axes, as in the ML-PWS figures."""
    import numpy as np
    for ax, label in zip(np.ravel(axes), labels):
        ax.text(x, y, label, transform=ax.transAxes, fontsize=size, fontweight="bold",
                va="bottom", ha="left")


def set_cycle(name):
    """Set the property cycle to palette *name*, or to ``"ok-print"`` (ok6 colors with line
    styles, for figures that must survive greyscale printing)."""
    mpl.rcParams["axes.prop_cycle"] = cycle(name)


def register_colors():
    """Make the palette colors usable by name anywhere Matplotlib takes a color
    (``color="rhdt:colibri:ruby"``, or ``"rhdt:ruby"`` for the default palette), and the palettes usable as ``matplotlib.color_sequences``."""
    import matplotlib.colors as mcolors
    mapping = mcolors.get_named_colors_mapping()
    for key, value in named_colors().items():
        mapping[key] = value
    for name in PALETTES:
        mpl.color_sequences.register(f"rhdt:{name}", colors(name))


def _register_fonts():
    for fn in sorted(os.listdir(font_dir)):
        if fn.endswith(".ttf"):
            fm.fontManager.addfont(os.path.join(font_dir, fn))


def use(backend=True, style=True, color_space=DEFAULT_COLOR_SPACE):
    """Apply the defaults.  ``backend=False`` keeps the current backend.

    *color_space* is the space of every number Matplotlib is given from here on: ``"display-p3"`` (the default) or
    ``"srgb"``.  It is passed to the backend, and the palettes, named colors, color cycle and colormaps are
    registered in it.  Colors you write yourself (hex, names, ``"C0"``, built-in colormaps) are still read as numbers
    of that space; ``from_srgb`` converts those."""
    colorspace.set_current(color_space)
    _register_fonts()
    okmaps.register(color_space)
    register_colors()
    if style:
        mpl.style.use(_style)
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(
            color=colors(DEFAULT_PALETTE, DEFAULT_CYCLE))
        mpl.rcParams["image.cmap"] = DEFAULT_CMAP
    if backend:
        import umbruch_matplotlib as um
        um.config.math_font = MATH_FONT
        um.config.color_space = color_space
        mpl.use(BACKEND)
    elif "umbruch_matplotlib" in sys.modules:
        sys.modules["umbruch_matplotlib"].config.color_space = color_space


use()
