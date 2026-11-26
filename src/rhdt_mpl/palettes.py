"""Color palettes, copied from site.manuel-rhdt.de/post/colors (data/colors.yaml)."""

from .spectral_data import COLIBRI, COLIBRI_DARK, PARTNERS, SOURCES, WIDE      # noqa: E402,F401

PALETTES = {
    "tol-bright": {"blue": "#4477AA", "cyan": "#66CCEE", "green": "#228833",
                   "yellow": "#CCBB44", "red": "#EE6677", "purple": "#AA3377",
                   "grey": "#BBBBBB"},
    "tol-vibrant": {"orange": "#EE7733", "blue": "#0077BB", "cyan": "#33BBEE",
                    "magenta": "#EE3377", "red": "#CC3311", "teal": "#009988",
                    "grey": "#BBBBBB"},
    "tol-muted": {"indigo": "#332288", "cyan": "#88CCEE", "teal": "#44AA99",
                  "green": "#117733", "olive": "#999933", "sand": "#DDCC77",
                  "rose": "#CC6677", "wine": "#882255", "purple": "#AA4499",
                  "pale grey": "#DDDDDD"},
    "tol-pale": {"pale blue": "#BBCCEE", "pale cyan": "#CCEEFF",
                 "pale green": "#CCDDAA", "pale yellow": "#EEEEBB",
                 "pale red": "#FFCCCC", "pale grey": "#DDDDDD"},
    "tol-dark": {"dark blue": "#222255", "dark cyan": "#225555",
                 "dark green": "#225522", "dark yellow": "#666633",
                 "dark red": "#663333", "dark grey": "#555555"},
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
    # Hummingbird species, males: one palette per bird, colors named after plumage parts, the most striking patch first.
    # For the four Colombian species (tourmaline sunangel, ruby-topaz, golden-bellied starfrontlet, golden-tailed sapphire) the
    # gorget, crown, belly, mantle and rump are measured reflectance spectra (Beltran, Shultz & Parra, Dryad
    # doi:10.5061/dryad.02v6wwq8w) and wing, tail and bill are sampled from the reference images; the violet-crowned and the
    # broad-billed hummingbird are not in that database, so all of their colors are sampled from their images.
    # See examples/build_species_palettes.py.
    "sunangel": {"gorget": "#e444b6", "crown": "#30721e", "belly": "#413f23", "mantle": "#3e5509", "rump": "#433d12", "wing": "#8f7a73", "tail": "#443730", "bill": "#464746"},
    "ruby-topaz": {"gorget": "#ff8a1b", "crown": "#ba0040", "belly": "#554236", "mantle": "#2e1d09", "rump": "#462f1d", "wing": "#897672", "tail": "#4f2612", "bill": "#222124"},
    "starfrontlet": {"gorget": "#6842e7", "crown": "#00d645", "belly": "#b36916", "mantle": "#4f5436", "rump": "#c76313", "wing": "#816a5d", "tail": "#231d11", "bill": "#1a1b1b"},
    "sapphire": {"gorget": "#0043be", "crown": "#0043d6", "belly": "#4d661f", "mantle": "#446817", "rump": "#96451e", "wing": "#8a7465", "tail": "#b66f2b", "bill": "#433234"},
    "violet-crowned": {"crown": "#6c41b8", "throat": "#d9d7d5", "belly": "#cdcbc6", "back": "#746e2c", "rump": "#787132", "wing": "#a18e86", "tail": "#756247", "bill": "#e27e78"},
    "broad-billed": {"gorget": "#272b90", "crown": "#4e9560", "belly": "#21501b", "rump": "#375e39", "vent": "#b8b7b3", "wing": "#7b6a61", "tail": "#181c25", "bill": "#ed6f41"},
    "ok8": {"navy": "#2a5b88", "gold": "#d6ab1b", "rust": "#8e3b1c",
            "violet": "#a936fb", "mint": "#4fbc90", "pink": "#f87fd8",
            "teal": "#228a8f", "coral": "#d0603d"},
}

#: Line styles paired one-to-one with the ok6 colors for the "ok-print" cycle.
OK_PRINT_LINESTYLES = ["-", "--", ":", "-.", (0, (5, 1, 1, 1)), (0, (1, 1))]

#: Palette used for the default property cycle, and the entries of it that are cycled
#: .
DEFAULT_PALETTE = "colibri-dark"
DEFAULT_CYCLE = None            # all eight colors


def cycle(name):
    """A ``cycler`` for *name*: any palette in ``PALETTES`` (colors only), or ``"ok-print"``
    (the ok6 colors paired with ``OK_PRINT_LINESTYLES``)."""
    from cycler import cycler
    if name == "ok-print":
        return cycler(color=colors("ok6")) + cycler(linestyle=OK_PRINT_LINESTYLES)
    return cycler(color=colors(name))


def colors(name, names=None):
    """Hex colors of palette *name*; *names* selects and orders entries."""
    pal = PALETTES[name]
    return [pal[n] for n in (names or pal)]


def named_colors():
    """``{"rhdt:palette:name": hex}`` for every color of every palette, e.g.
    ``"rhdt:tol-vibrant:orange"``, ``"rhdt:okabe-ito:sky blue"``, ``"rhdt:ok6:navy"``; plus the short
    form ``"rhdt:benjamini gorget"`` for the colors of the default palette (colibri-dark).  Short forms exist only
    there because a bare name is ambiguous across palettes (``blue`` has three different values)."""
    out = {f"rhdt:{pal}:{name}": hexval for pal, d in PALETTES.items() for name, hexval in d.items()}
    out.update({f"rhdt:{name}": hexval for name, hexval in PALETTES[DEFAULT_PALETTE].items()})
    return out


def wide_css(palette, name):
    """The exact color of palette entry *name* as a CSS ``oklch()`` string when it lies outside the sRGB gamut (the hex
    in the palette is then its nearest sRGB color), else ``None``."""
    return WIDE.get(palette, {}).get(name)
