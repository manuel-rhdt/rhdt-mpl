"""Species palettes from measured spectra and from the reference images in docs/birds/.

Colombian species: crown, gorget, belly, mantle and rump are the measured reflectance spectra (the angle of maximum
reflectance, males) converted to sRGB by colombia_spectra.py; wing, tail and bill, which the database does not
measure, are sampled from the image.  The violet-crowned and broad-billed hummingbirds are not in the database, so all
of their colors are sampled from their images.  Prints the dicts used in rhdt_mpl/palettes.py, and for every measured
patch that has a box in the image the distance (OKLab x 100) between the image and the measurement.

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
# species -> (image, species in the database or None, sampling boxes (x0, y0, x1, y1) in image coordinates)
SPECIES = {
    "sunangel": ("sunangel.webp", "Heliangelus_exortis",
                 {"crown": (295, 55, 365, 78), "gorget": (300, 110, 350, 170), "wing": (60, 70, 150, 140),
                  "tail": (188, 380, 212, 460), "bill": (375, 77, 415, 87)}),
    "ruby-topaz": ("ruby-topaz.webp", "Chrysolampis_mosquitus",
                   {"crown": (325, 50, 395, 72), "gorget": (340, 115, 400, 170), "belly": (290, 230, 360, 290),
                    "wing": (60, 100, 160, 150), "tail": (200, 330, 300, 390), "bill": (430, 75, 470, 85)}),
    "starfrontlet": ("starfrontlet.webp", "Coeligena_bonapartei",
                     {"crown": (360, 58, 420, 76), "gorget": (385, 100, 425, 145), "belly": (310, 215, 370, 280),
                      "mantle": (250, 150, 320, 190), "rump": (210, 320, 245, 350), "wing": (40, 110, 150, 160),
                      "tail": (160, 410, 190, 450), "bill": (470, 63, 530, 75)}),
    "sapphire": ("sapphire.webp", "Chrysuronia_oenone",
                 {"crown": (320, 60, 380, 80), "gorget": (320, 110, 360, 160), "belly": (250, 235, 320, 285),
                  "mantle": (230, 150, 290, 190), "rump": (150, 315, 200, 335), "wing": (60, 110, 150, 160),
                  "tail": (120, 420, 175, 480), "bill": (420, 70, 460, 82)}),
    "violet-crowned": ("violet-crowned.webp", None,
                       {"crown": (365, 48, 430, 68), "throat": (370, 90, 420, 160), "belly": (330, 230, 380, 280),
                        "back": (250, 240, 300, 290), "rump": (225, 310, 260, 345), "wing": (60, 60, 150, 110),
                        "tail": (235, 420, 270, 470), "bill": (450, 62, 510, 78)}),
    "broad-billed": ("broad-billed.webp", None,
                     {"crown": (330, 60, 400, 85), "gorget": (365, 125, 400, 165), "belly": (275, 245, 330, 290),
                      "rump": (190, 295, 235, 318), "vent": (205, 335, 245, 380), "wing": (50, 130, 150, 180),
                      "tail": (160, 440, 210, 490), "bill": (410, 80, 465, 98)}),
}
VIVID = ("crown", "gorget")                       # iridescent patches: the more saturated half of the pixels
DARK_BILL = ("sunangel", "ruby-topaz", "starfrontlet", "sapphire")   # black bills with silvery highlights: darker half of the pixels
MEASURED = ("gorget", "crown", "belly", "mantle", "rump")
UNMEASURED = ("wing", "tail", "bill")
IMAGE_ONLY = {"violet-crowned": ("crown", "throat", "belly", "back", "rump", "wing", "tail", "bill"),
              "broad-billed": ("gorget", "crown", "belly", "rump", "vent", "wing", "tail", "bill")}


def _hex(c):
    return "#%02x%02x%02x" % tuple(np.round(np.clip(c, 0, 1) * 255).astype(int))


def sample(img, box, vivid=False, dark=False):
    x0, y0, x1, y1 = box
    a = img[y0:y1, x0:x1].reshape(-1, 4)
    a = a[a[:, 3] > 0.95][:, :3]
    if vivid:
        a = a[::2]
        chroma = np.array([ok.to_oklch(tuple(p))[1] for p in a])
        a = a[chroma >= np.quantile(chroma, 0.5)]
    if dark:
        light = np.array([ok.to_oklab(tuple(p))[0] for p in a])
        a = a[light <= np.quantile(light, 0.5)]
    return _hex(np.median(a, axis=0))


def dist(a, b):
    return 100 * float(np.linalg.norm(np.array(ok.to_oklab(a)) - np.array(ok.to_oklab(b))))


def build(data_dir):
    meta, spec = cs.load(os.path.join(data_dir, "refcolC.txt"))
    out = {}
    for key, (fn, sp, box) in SPECIES.items():
        img = np.asarray(Image.open(os.path.join(IMAGES, fn)).convert("RGBA")).astype(float) / 255
        s = {p: sample(img, b, p in VIVID, p == "bill" and key in DARK_BILL) for p, b in box.items()}
        if sp:
            measured = cs.patch_colors(meta, spec, sp, "Males")
            pal = {p: measured[p] for p in MEASURED}
            pal.update({p: s[p] for p in UNMEASURED})
            diffs = {p: round(dist(s[p], measured[p])) for p in MEASURED if p in s}
        else:
            pal = {p: s[p] for p in IMAGE_ONLY[key]}
            diffs = None
        out[key] = (pal, diffs)
    return out


if __name__ == "__main__":
    for key, (pal, diffs) in build(sys.argv[1]).items():
        print(f'    "{key}": {{' + ", ".join(f'"{k}": "{v}"' for k, v in pal.items()) + "},")
        if diffs:
            print(f"      # image vs spectrum (dE x100): {diffs}")
