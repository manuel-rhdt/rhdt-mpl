"""Hummingbird species palettes, designed in OKLCH (L, C, h) per plumage part, from the general appearance
of the adult male (not sampled from photographs).  Prints the dict used in rhdt_mpl/palettes.py.

    python examples/design_species_palettes.py
"""
from rhdt_mpl import oklab

# name -> (latin name, {part: (L, C, h)}); the gorget (or the most striking patch) comes first
SPECIES = {
    "anna": ("Calypte anna", {
        "gorget": (0.56, 0.24, 357),    # iridescent rose-magenta throat and crown
        "back":   (0.60, 0.13, 150),    # metallic green
        "flank":  (0.74, 0.07, 150),    # pale green wash on the sides
        "belly":  (0.90, 0.01, 95),     # grey-white
        "wing":   (0.38, 0.04, 150),    # dusky green-grey
        "bill":   (0.24, 0.01, 260)}),
    "ruby-throated": ("Archilochus colubris", {
        "gorget": (0.50, 0.22, 27),     # ruby-red throat
        "back":   (0.58, 0.14, 155),    # emerald green
        "flank":  (0.72, 0.06, 140),
        "belly":  (0.94, 0.01, 90),     # white
        "wing":   (0.30, 0.03, 300),    # dusky violet-black
        "bill":   (0.22, 0.01, 260)}),
    "rufous": ("Selasphorus rufus", {
        "gorget": (0.66, 0.20, 42),     # flame-orange throat
        "back":   (0.57, 0.14, 55),     # copper
        "flank":  (0.77, 0.09, 70),     # buff
        "belly":  (0.95, 0.01, 80),     # white
        "wing":   (0.36, 0.04, 60),     # dusky brown
        "bill":   (0.22, 0.01, 60)}),
    "costa": ("Calypte costae", {
        "gorget": (0.44, 0.25, 302),    # violet-purple throat and crown
        "back":   (0.60, 0.12, 150),    # green
        "flank":  (0.75, 0.06, 150),
        "belly":  (0.94, 0.005, 90),    # whitish
        "wing":   (0.40, 0.03, 80),     # grey-brown
        "bill":   (0.22, 0.01, 260)}),
    "crimson-topaz": ("Topaza pella", {
        "body":   (0.50, 0.21, 24),     # crimson
        "throat": (0.85, 0.17, 100),    # golden-yellow
        "head":   (0.20, 0.02, 300),    # black
        "tail":   (0.38, 0.09, 165),    # dark green
        "wing":   (0.33, 0.06, 20),     # dark red-brown
        "sheen":  (0.62, 0.15, 150)}),  # green iridescence
    "sparkling-violetear": ("Colibri coruscans", {
        "ear":    (0.46, 0.22, 292),    # violet-blue ear patch
        "breast": (0.52, 0.17, 258),    # blue breast
        "back":   (0.62, 0.16, 150),    # green
        "belly":  (0.72, 0.12, 170),    # blue-green
        "tail":   (0.30, 0.07, 270),    # blue-black
        "bill":   (0.22, 0.01, 260)}),
}


def palettes():
    return {k: {part: oklab.oklch(*lch) for part, lch in parts.items()} for k, (_, parts) in SPECIES.items()}


if __name__ == "__main__":
    for k, pal in palettes().items():
        print(f'    "{k}": {pal},')
