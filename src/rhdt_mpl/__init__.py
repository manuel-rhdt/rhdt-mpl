"""Matplotlib defaults: umbruch backend, Noto fonts, personal color palettes.

    import rhdt_mpl          # before importing matplotlib.pyplot, ideally
    import matplotlib.pyplot as plt

Importing the package selects the umbruch backend, registers the bundled Noto fonts,
hands them to umbruch, and applies the ``rhdt`` style.  ``rhdt_mpl.use(...)`` redoes
this explicitly; ``rhdt_mpl.set_palette(name)`` changes the color cycle.
"""
import os
from importlib import resources

import matplotlib as mpl
import matplotlib.style
from matplotlib import font_manager as fm

from .palettes import PALETTES, DEFAULT_PALETTE, DEFAULT_CYCLE, colors

__all__ = ["use", "set_palette", "palette", "PALETTES", "font_dir"]

BACKEND = "module://umbruch_matplotlib"
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


def _register_fonts():
    for fn in sorted(os.listdir(font_dir)):
        if fn.endswith(".ttf"):
            fm.fontManager.addfont(os.path.join(font_dir, fn))


def _install_bridge():
    """Start umbruch with the bundled fonts (the backend's default bridge uses
    ``--no-system-fonts`` and would only see umbruch's built-in families)."""
    import umbruch_matplotlib as um
    um.config.math_font = MATH_FONT
    if um.config.bridge is not None:
        return
    exe = um.find_umbruch()
    if exe is None:
        return          # the backend reports this itself when it is used
    args = ("--no-system-fonts", "--font-dir", font_dir)
    try:
        server = um.UmbruchServer(exe, args=args)
        server._start()
        um.config.bridge = server
    except Exception:
        um.config.bridge = um.UmbruchCli(exe, args=args)


def use(backend=True, style=True):
    """Apply the defaults.  ``backend=False`` keeps the current backend."""
    _register_fonts()
    if style:
        mpl.style.use(_style)
        mpl.rcParams["axes.prop_cycle"] = mpl.cycler(
            color=colors(DEFAULT_PALETTE, DEFAULT_CYCLE))
    if backend:
        _install_bridge()
        mpl.use(BACKEND)


use()
