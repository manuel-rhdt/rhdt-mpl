"""Species palettes from measured spectra and from the reference images in docs/birds/.

Colombian species: crown, gorget, belly, mantle and rump are the measured reflectance spectra (the angle of maximum
reflectance, males) converted to sRGB by colombia_spectra.py; wing, tail and bill, which the database does not
measure, are sampled from the image.  The broad-billed hummingbird is not in the database, so all of its colors are
sampled from its image.  Prints the dicts used in rhdt_mpl/palettes.py, and the distance (OKLab x 100) between the
image and the measurement for every measured patch.

    python examples/build_species_palettes.py DATA_DIR       # DATA_DIR holds refcolC.txt
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import colombia_spectra as cs                  # noqa: E402
from rhdt_mpl import oklab as ok               # noqa: E402

IMAGES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds")
# sampling boxes (x0, y0, x1, y1) in the 1254 x 1254 images, which share one pose
BOX = {"crown": (690, 285, 780, 325), "gorget": (700, 490, 800, 610), "belly": (560, 730, 730, 800),
       "mantle": (390, 610, 500, 690), "rump": (300, 800, 380, 900), "wing": (110, 200, 300, 380),
       "tail": (140, 1020, 380, 1150), "bill": (1040, 368, 1140, 398), "body": (440, 700, 600, 800),
       "vent": (420, 870, 500, 950)}
BILL_BASE = (940, 368, 1040, 405)                # the broad-billed's bill is orange-red at the base
VIVID = ("crown", "gorget")                       # iridescent patches: the more saturated half of the pixels
# key -> (image file, species in the database or None, palette parts: name -> "spectrum" | "image:<box>")
SPECIES = {
    "sunangel": ("sunangel.webp", "Heliangelus_exortis"),
    "ruby-topaz": ("ruby-topaz.webp", "Chrysolampis_mosquitus"),
    "starfrontlet": ("starfrontlet.webp", "Coeligena_bonapartei"),
    "sapphire": ("sapphire.webp", "Chrysuronia_oenone"),
}
SPECIES["broad-billed"] = ("broad-billed.webp", None)         # last: it changes the bill box
MEASURED = ("gorget", "crown", "belly", "mantle", "rump")
UNMEASURED = ("wing", "tail", "bill")


def _hex(c):
    return "#%02x%02x%02x" % tuple(np.round(np.clip(c, 0, 1) * 255).astype(int))


def sample(img, name):
    x0, y0, x1, y1 = BOX[name]
    a = img[y0:y1, x0:x1].reshape(-1, 4)
    a = a[a[:, 3] > 0.95][:, :3]
    if name in VIVID:
        a = a[::2]
        chroma = np.array([ok.to_oklch(tuple(p))[1] for p in a])
        a = a[chroma >= np.quantile(chroma, 0.5)]
    return _hex(np.median(a, axis=0))


def dist(a, b):
    return 100 * float(np.linalg.norm(np.array(ok.to_oklab(a)) - np.array(ok.to_oklab(b))))


def build(data_dir):
    meta, spec = cs.load(os.path.join(data_dir, "refcolC.txt"))
    out = {}
    for key, (fn, sp) in SPECIES.items():
        img = np.asarray(Image.open(os.path.join(IMAGES, fn)).convert("RGBA")).astype(float) / 255
        if sp:
            measured = cs.patch_colors(meta, spec, sp, "Males")
            pal = {p: measured[p] for p in MEASURED}
            pal.update({p: sample(img, p) for p in UNMEASURED})
            diffs = {p: round(dist(sample(img, p), measured[p])) for p in MEASURED}
        else:
            BOX["bill"] = BILL_BASE
            pal = {"gorget": sample(img, "gorget"), "crown": sample(img, "crown"), "belly": sample(img, "body"),
                   "rump": sample(img, "rump"), "vent": sample(img, "vent"), "wing": sample(img, "wing"),
                   "tail": sample(img, "tail"), "bill": sample(img, "bill")}
            diffs = None
        out[key] = (pal, diffs)
    return out


if __name__ == "__main__":
    for key, (pal, diffs) in build(sys.argv[1]).items():
        print(f'    "{key}": {{' + ", ".join(f'"{k}": "{v}"' for k, v in pal.items()) + "},")
        if diffs:
            print(f"      # image vs spectrum (dE x100): {diffs}")
