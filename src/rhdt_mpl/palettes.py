"""Color palettes, copied from site.manuel-rhdt.de/post/colors (data/colors.yaml)."""

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
    "ok8": {"navy": "#2a5b88", "gold": "#d6ab1b", "rust": "#8e3b1c",
            "violet": "#a936fb", "mint": "#4fbc90", "pink": "#f87fd8",
            "teal": "#228a8f", "coral": "#d0603d"},
}

#: Line styles paired one-to-one with the ok6 colors for the "ok-print" cycle.
OK_PRINT_LINESTYLES = ["-", "--", ":", "-.", (0, (5, 1, 1, 1)), (0, (1, 1))]

#: Palette used for the default property cycle, and the entries of it that are cycled
#: (the grey is left out; the paper figures use it for baselines).
DEFAULT_PALETTE = "tol-vibrant"
DEFAULT_CYCLE = ["orange", "blue", "cyan", "magenta", "red", "teal"]


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
