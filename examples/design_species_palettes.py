"""Hummingbird species palettes, designed in OKLCH (L, C, h) per plumage part, from the general appearance
of the adult male; Anna's, the ruby-throated, the rufous and Costa's hummingbird are sampled from reference photographs.  Prints the dict used in rhdt_mpl/palettes.py.

    python examples/design_species_palettes.py
"""
from rhdt_mpl import oklab

# name -> (latin name, {part: (L, C, h)}); the gorget (or the most striking patch) comes first
SPECIES = {
    "anna": ("Calypte anna", {          # from a reference photograph, matching examples/draw_anna.py
        "gorget": "#f64e88",            # rose-pink, the most saturated quarter of the gorget
        "crown":  "#e88a6e",            # peach-rose crown
        "gold":   "#c09a3e",            # gold fringe at the front of the gorget
        "back":   "#5a6338",            # olive-green scales
        "flank":  "#765842",            # brownish buff of the lower flank
        "belly":  "#8b847d",            # warm grey chest
        "wing":   "#b3aca1",            # grey-brown wing
        "bill":   "#302e29"}),
    "ruby-throated": ("Archilochus colubris", {   # from a reference photograph, matching draw_ruby_throated.py
        "gorget": "#f1562f",            # orange-red throat (ruby in other light)
        "crown":  "#a1958a",            # grey-olive head
        "back":   "#9c8465",            # olive back with a golden sheen
        "collar": "#fcf3ea",            # white collar
        "belly":  "#e9cfb6",            # buff belly
        "wing":   "#bc8b70",            # mauve-brown wing
        "tail":   "#9b5972",            # iridescent purple tail feathers
        "bill":   "#50565c"}),
    "rufous": ("Selasphorus rufus", {     # from a reference photograph, matching draw_rufous.py
        "gorget": "#f0363e",            # scarlet gorget
        "bronze": "#b54d2d",            # bronze-olive gorget near the chin
        "crown":  "#ec804d",            # bright rufous head
        "back":   "#d27143",            # rufous body
        "bib":    "#eee7e8",            # white bib
        "wing":   "#baa9b8",            # pale lilac-grey wing
        "tip":    "#37241f",            # dark tail tips
        "bill":   "#3b3946"}),
    "costa": ("Calypte costae", {       # from two reference photographs, matching draw_costa.py
        "gorget": "#bf0edc",            # brilliant violet-magenta gorget
        "crown":  "#d056d6",            # magenta crown
        "flare":  "#770ba8",            # deep violet gorget flares
        "back":   "#76825a",            # sage-green back and flanks (second photograph)
        "chest":  "#beb6db",            # pale lavender-grey chest
        "wing":   "#6e5d68",            # dusky grey-mauve wing
        "tail":   "#231c1c",            # near-black tail
        "bill":   "#13121e"}),
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
    return {k: {part: (v if isinstance(v, str) else oklab.oklch(*v)) for part, v in parts.items()}
            for k, (_, parts) in SPECIES.items()}


if __name__ == "__main__":
    for k, pal in palettes().items():
        print(f'    "{k}": {pal},')
