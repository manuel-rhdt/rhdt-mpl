"""Species palettes from measured spectra and from the reference images in docs/birds/.

Colombian species: crown, gorget, belly, mantle and rump are the measured reflectance spectra (the angle of maximum
reflectance, males) converted to sRGB by colombia_spectra.py; wing, tail and bill, which the database does not
measure, are sampled from the image.  The broad-billed hummingbird is not in the database, so all of its colors are
sampled from its image.  Prints the dicts used in rhdt_mpl/palettes.py, and for every measured patch the distance
(OKLab x 100) between the image and the measurement, where the image has a box for that patch.

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
# sampling boxes (x0, y0, x1, y1), image coordinates; each image has its own because the birds are posed differently
_POSE_A = {"crown": (690, 285, 780, 325), "gorget": (700, 490, 800, 610), "belly": (560, 730, 730, 800),
           "mantle": (390, 610, 500, 690), "rump": (300, 800, 380, 900), "wing": (110, 200, 300, 380),
           "tail": (140, 1020, 380, 1150), "bill": (1040, 368, 1140, 398)}
# species -> (image, species in the database or None, boxes)
SPECIES = {
    "sunangel": ("sunangel.webp", "Heliangelus_exortis",
                 {"crown": (890, 160, 1000, 195), "gorget": (870, 290, 980, 380), "wing": (200, 250, 380, 350),
                  "tail": (505, 920, 555, 1060), "bill": (1050, 215, 1130, 226)}),
    "ruby-topaz": ("ruby-topaz.webp", "Chrysolampis_mosquitus", _POSE_A),
    "starfrontlet": ("starfrontlet.webp", "Coeligena_bonapartei", _POSE_A),
    "sapphire": ("sapphire.webp", "Chrysuronia_oenone", _POSE_A),
    "broad-billed": ("broad-billed.webp", None,
                     {"crown": (830, 232, 930, 256), "gorget": (870, 350, 950, 430), "belly": (700, 560, 820, 640),
                      "rump": (500, 690, 560, 740), "vent": (510, 800, 590, 870), "wing": (330, 340, 430, 400),
                      "tail": (400, 1000, 470, 1100), "bill": (1020, 278, 1110, 300)}),
}
VIVID = ("crown", "gorget")                       # iridescent patches: the more saturated half of the pixels
MEASURED = ("gorget", "crown", "belly", "mantle", "rump")
UNMEASURED = ("wing", "tail", "bill")
FROM_IMAGE = ("gorget", "crown", "belly", "rump", "vent", "wing", "tail", "bill")      # the broad-billed palette


def _hex(c):
    return "#%02x%02x%02x" % tuple(np.round(np.clip(c, 0, 1) * 255).astype(int))


def sample(img, box, vivid=False):
    x0, y0, x1, y1 = box
    a = img[y0:y1, x0:x1].reshape(-1, 4)
    a = a[a[:, 3] > 0.95][:, :3]
    if vivid:
        a = a[::2]
        chroma = np.array([ok.to_oklch(tuple(p))[1] for p in a])
        a = a[chroma >= np.quantile(chroma, 0.5)]
    return _hex(np.median(a, axis=0))


def dist(a, b):
    return 100 * float(np.linalg.norm(np.array(ok.to_oklab(a)) - np.array(ok.to_oklab(b))))


def build(data_dir):
    meta, spec = cs.load(os.path.join(data_dir, "refcolC.txt"))
    out = {}
    for key, (fn, sp, box) in SPECIES.items():
        img = np.asarray(Image.open(os.path.join(IMAGES, fn)).convert("RGBA")).astype(float) / 255
        s = {p: sample(img, b, p in VIVID) for p, b in box.items()}
        if sp:
            measured = cs.patch_colors(meta, spec, sp, "Males")
            pal = {p: measured[p] for p in MEASURED}
            pal.update({p: s[p] for p in UNMEASURED})
            diffs = {p: round(dist(s[p], measured[p])) for p in MEASURED if p in s}
        else:
            pal = {p: s[p] for p in FROM_IMAGE}
            diffs = None
        out[key] = (pal, diffs)
    return out


if __name__ == "__main__":
    for key, (pal, diffs) in build(sys.argv[1]).items():
        print(f'    "{key}": {{' + ", ".join(f'"{k}": "{v}"' for k, v in pal.items()) + "},")
        if diffs:
            print(f"      # image vs spectrum (dE x100): {diffs}")
