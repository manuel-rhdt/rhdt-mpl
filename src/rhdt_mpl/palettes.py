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
    # Hummingbird jewel tones (gorgets, crowns and backs), designed in OKLCH; ordered so that the
    # first k are well separated.
    "colibri": {"violetear": "#710bc6", "topaz": "#e8ca17", "ruby": "#c6001f", "emerald": "#00ae64",
                "fuchsia": "#e825bc", "copper": "#db7d24", "sapphire": "#005dca", "turquoise": "#31c8c9"},
    # Hummingbird species: one palette per bird, colors named after plumage parts, designed in OKLCH from the general
    # appearance of the adult male (examples/design_species_palettes.py).  The gorget (or the most striking patch) is first.
    "anna": {"gorget": "#d10076", "back": "#3b9555", "flank": "#8cb894", "belly": "#e0ded7", "wing": "#334937", "bill": "#1c1f24"},
    "ruby-throated": {"gorget": "#bc0013", "back": "#0e9254", "flank": "#91ae8b", "belly": "#eeebe4", "wing": "#302a3b", "bill": "#181b1f"},
    "rufous": {"gorget": "#f15b00", "back": "#b45c03", "flank": "#d9aa74", "belly": "#f2eee7", "wing": "#4d3827", "bill": "#1e1a16"},
    "costa": {"gorget": "#6e00b9", "back": "#439458", "flank": "#93b99a", "belly": "#ecebe7", "wing": "#504635", "bill": "#181b1f"},
    "crimson-topaz": {"body": "#bb0021", "throat": "#e8cf23", "head": "#17141e", "tail": "#004f38", "wing": "#502828", "sheen": "#2e9e52"},
    "sparkling-violetear": {"ear": "#6228c5", "breast": "#1c65c8", "back": "#20a04e", "belly": "#43bd99", "tail": "#202b51", "bill": "#181b1f"},
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


def named_colors():
    """``{"rhdt:palette:name": hex}`` for every color of every palette, e.g.
    ``"rhdt:tol-vibrant:orange"``, ``"rhdt:okabe-ito:sky blue"``, ``"rhdt:ok6:navy"``; plus the short
    form ``"rhdt:orange"`` for the colors of the default palette (Tol Vibrant).  Short forms exist only
    there because a bare name is ambiguous across palettes (``blue`` has three different values)."""
    out = {f"rhdt:{pal}:{name}": hexval for pal, d in PALETTES.items() for name, hexval in d.items()}
    out.update({f"rhdt:{name}": hexval for name, hexval in PALETTES[DEFAULT_PALETTE].items()})
    return out
