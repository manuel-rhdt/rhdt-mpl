"""Color palettes: Okabe-Ito (from site.manuel-rhdt.de/post/colors), ok6 and ok8, the colibri palettes measured in
hummingbirds, and one palette per hummingbird species.

``PALETTES`` holds every palette as hex in the color space it is defined in (``NATIVE_SPACE``): the hummingbird palettes
(measured colors reach outside sRGB) in Display P3, Okabe-Ito, ok6 and ok8 in sRGB.  ``colors()`` and ``named_colors()``
return them in the current color space of the package (``rhdt_mpl.colorspace.current()``), converted, and gamut-mapped
by reducing chroma if the target is the smaller space."""
import numpy as np
from matplotlib.colors import to_hex, to_rgb

from . import colorspace
from .spectral_data import COLIBRI, COLIBRI_DARK, PARTNERS, SOURCES, WIDE      # noqa: E402,F401

PALETTES = {
    "okabe-ito": {"black": "#000000", "orange": "#E69F00", "sky blue": "#56B4E9",
                  "bluish green": "#009E73", "yellow": "#F0E442", "blue": "#0072B2",
                  "vermilion": "#D55E00", "reddish purple": "#CC79A7"},
    # Ordered so that the first k colors are the most separated.
    "ok6": {"navy": "#1d5e85", "gold": "#c8b222", "brown": "#8b3e09",
            "pink": "#f487c5", "green": "#469172", "violet": "#a351fb"},
    # Colors measured in the Colombian hummingbird reflectance database, species and patches mixed (spectral_data.py,
    # examples/build_spectral_data.py): eight bright colors, and for each a darker partner of similar hue.
    "colibri": COLIBRI,
    "colibri-dark": COLIBRI_DARK,
    # Hummingbird species, males: one palette per bird, the same four plumage parts each (gorget, crown, mantle, rump), the most
    # striking first. For the four Colombian species (tourmaline sunangel, ruby-topaz, golden-bellied starfrontlet,
    # golden-tailed sapphire) they are measured reflectance spectra (Beltran, Shultz & Parra, Dryad doi:10.5061/dryad.02v6wwq8w);
    # the violet-crowned and the broad-billed hummingbird are not in that database, so all of their colors are sampled from their
    # images (the violet-crowned has no gorget color: its white throat stands in).  See examples/build_species_palettes.py.
    "sunangel": {"gorget": "#d351b2", "crown": "#42712b", "mantle": "#435419", "rump": "#423d19"},
    "ruby-topaz": {"gorget": "#f28f2f", "crown": "#aa1742", "mantle": "#2b1e0c", "rump": "#433020"},
    "starfrontlet": {"gorget": "#6344de", "crown": "#3bd25a", "mantle": "#505439", "rump": "#ba682c"},
    "sapphire": {"gorget": "#0242b7", "crown": "#1842ce", "mantle": "#4c6725", "rump": "#8c4a28"},
    "violet-crowned": {"gorget": "#d0cec9", "crown": "#6643b2", "mantle": "#736e36", "rump": "#77713b"},
    "broad-billed": {"gorget": "#282b8a", "crown": "#609365", "mantle": "#427137", "rump": "#405d3d"},
    "ok8": {"navy": "#2a5b88", "gold": "#d6ab1b", "rust": "#8e3b1c",
            "violet": "#a936fb", "mint": "#4fbc90", "pink": "#f87fd8",
            "teal": "#228a8f", "coral": "#d0603d"},
}

#: The color space of the hex values of each palette; the default is sRGB.
NATIVE_SPACE = {name: "display-p3" for name in
                ("colibri", "colibri-dark", "sunangel", "ruby-topaz", "starfrontlet", "sapphire", "violet-crowned",
                 "broad-billed")}

#: Line styles paired one-to-one with the ok6 colors for the "ok-print" cycle.
OK_PRINT_LINESTYLES = ["-", "--", ":", "-.", (0, (5, 1, 1, 1)), (0, (1, 1))]

#: Palette used for the default property cycle, and the entries of it that are cycled
#: .
DEFAULT_PALETTE = "colibri"
DEFAULT_CYCLE = None            # all eight colors


def cycle(name):
    """A ``cycler`` for *name*: any palette in ``PALETTES`` (colors only), or ``"ok-print"``
    (the ok6 colors paired with ``OK_PRINT_LINESTYLES``)."""
    from cycler import cycler
    if name == "ok-print":
        return cycler(color=colors("ok6")) + cycler(linestyle=OK_PRINT_LINESTYLES)
    return cycler(color=colors(name))


def _in_current(name, hexval):
    src, dst = NATIVE_SPACE.get(name, "srgb"), colorspace.current()
    if src == dst:
        return hexval
    return to_hex(colorspace.convert(np.array(to_rgb(hexval)), src, dst))


def colors(name, names=None):
    """Hex colors of palette *name* in the current color space; *names* selects and orders entries."""
    pal = PALETTES[name]
    return [_in_current(name, pal[n]) for n in (names or pal)]


def named_colors():
    """``{"rhdt:palette:name": hex}`` (in the current color space) for every color of every palette, e.g.
    ``"rhdt:colibri:ruby"``, ``"rhdt:okabe-ito:sky blue"``, ``"rhdt:ok6:navy"``; plus the short
    form ``"rhdt:emerald"`` for the colors of the default palette (colibri).  Short forms exist only
    there because a bare name is ambiguous across palettes (``blue`` has three different values)."""
    out = {f"rhdt:{pal}:{name}": _in_current(pal, hexval) for pal, d in PALETTES.items() for name, hexval in d.items()}
    out.update({f"rhdt:{name}": _in_current(DEFAULT_PALETTE, hexval) for name, hexval in PALETTES[DEFAULT_PALETTE].items()})
    return out


def wide_css(palette, name):
    """The exact color of palette entry *name* as a CSS ``oklch()`` string when it lies outside the Display P3 gamut
    (the hex in the palette is then its nearest Display P3 color), else ``None``."""
    return WIDE.get(palette, {}).get(name)
