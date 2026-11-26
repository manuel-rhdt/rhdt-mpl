"""Build src/rhdt_mpl/spectral_data.py: the colibri palettes and the exact colors of the spectrum-based palettes.

The colibri palettes use only colors measured in the Colombian hummingbird reflectance database (Beltran, Shultz & Parra,
Dryad doi:10.5061/dryad.02v6wwq8w), mixing species and patches freely:
  colibri       eight bright, vivid colors, one per hue (PICKS below), each at least 3:1 against white (WCAG, for
                lines and markers on a white background), ordered so that the first k are best separated
  colibri-dark  for each of them a darker partner of similar hue (lightness lower by 0.08 to 0.26), also from the data,
                chosen jointly so that the eight darker colors are as distinct from each other as possible; the
                entries are named after gems of those colors, in the same order as their bright partners (PARTNERS maps the names)
Colors are the median spectrum of the specimens of one species, sex and patch (at least two specimens), converted with
the CIE 1931 observer under D65.  A color outside the sRGB gamut keeps its exact value as an OKLCH string in WIDE; the
hex in the palette is then its nearest sRGB color (chroma reduced at constant lightness and hue), made unique.

    python examples/build_spectral_data.py DATA_DIR       # DATA_DIR holds refcolC.txt; rewrites spectral_data.py
"""
import collections
import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import colombia_spectra as cs                  # noqa: E402
from rhdt_mpl import oklab as ok               # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "rhdt_mpl", "spectral_data.py")
# name -> (species, sex, patch): the bright palette.  The hues are crimson, amber, olive-yellow, green, teal, blue, violet and
# magenta; chosen from the measured colors that are at least 3:1 against white and have a chroma of 0.13 or more, so that
# the eight are as distinct as possible (the dataset has no bright yellow that is visible on white).
PICKS = {
    "ruby": ("Chrysolampis_mosquitus", "Males", "crown"),
    "amber": ("Coeligena_bonapartei", "Males", "rump"),
    "peridot": ("Eriocnemis_vestita", "Males", "rump"),
    "emerald": ("Urosticte_benjamini", "Males", "gorget"),
    "jade": ("Aglaiocercus_coelestis", "Females", "crown"),
    "sapphire": ("Lepidopyga_coeruleogularis", "Males", "gorget"),
    "amethyst": ("Eriocnemis_vestita", "Males", "gorget"),
    "tourmaline": ("Heliangelus_strophianus", "Males", "gorget"),
}
# the dark partner of each bright color gets a name of its own (a gem or mineral of that color)
DARK_NAMES = {"emerald": "malachite", "tourmaline": "rhodolite", "amethyst": "iolite", "amber": "bronzite",
              "sapphire": "lapis", "ruby": "garnet", "jade": "apatite", "peridot": "serpentine"}
MIN_CONTRAST = 3.0


def contrast_with_white(hexv):
    c = np.array([int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 1.05 / (0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2] + 0.05)


def hue_dist(a, b):
    return abs(((a - b + 180) % 360) - 180)


def candidates(data_dir):
    meta, spec = cs.load(os.path.join(data_dir, "refcolC.txt"))
    groups = collections.defaultdict(list)
    for i, m in enumerate(meta):
        groups[(m["Species"], m["Sex"], m["Feather_type"])].append(i)
    out = []
    for (sp, sex, code), idx in sorted(groups.items()):
        if len(idx) < 2:
            continue
        lin = cs.spectrum_to_linear_rgb(np.median(spec[idx], axis=0))
        L, C, h, wide = cs.exact_oklch(lin)
        stand = ok.oklch(L, C, h)
        # distances are measured between the colors as they are DISPLAYED (the sRGB stand-ins), not the exact ones: for a
        # color outside the gamut the stand-in has less chroma, so displayed colors are closer together than exact ones
        out.append(dict(species=sp, sex=sex, patch=cs.PATCHES[code], n=len(idx), L=L, C=C, h=h, wide=wide,
                        lab=np.array(ok.to_oklab(stand)), stand=stand))
    return out


def dist(a, b):
    return 100 * float(np.linalg.norm(a["lab"] - b["lab"]))


def in_sector(c, lo, hi):
    return lo <= c["h"] < hi if lo < hi else (c["h"] >= lo or c["h"] < hi)


def pick_bright(cand):
    out = {}
    for name, (sp, sex, patch) in PICKS.items():
        c = next(c for c in cand if (c["species"], c["sex"], c["patch"]) == (sp, sex, patch))
        assert contrast_with_white(c["stand"]) >= MIN_CONTRAST, (name, c["stand"])
        c["name"] = name
        out[name] = c
    return order_by_separation(list(out.values()))


def pick_dark(cand, bright):
    options = []
    for b in bright:
        o = [c for c in cand if c["C"] >= 0.08 and hue_dist(c["h"], b["h"]) <= 28 and 0.08 <= b["L"] - c["L"] <= 0.26]
        seen = []
        for c in sorted(o, key=lambda c: (-c["n"], -c["C"])):
            if all(dist(c, s) > 3 for s in seen):
                seen.append(c)
        options.append(seen)
    score = lambda S: min(dist(a, c) for a, c in itertools.combinations(S, 2))
    rng, best = np.random.default_rng(7), None
    for _ in range(300):
        S = [o[rng.integers(len(o))] for o in options]
        s, improved = score(S), True
        while improved:
            improved = False
            for i, opts in enumerate(options):
                for u in opts:
                    T = S[:i] + [u] + S[i + 1:]
                    t = score(T)
                    if t > s + 1e-9:
                        S, s, improved = T, t, True
        key = (s, sum(c["C"] for c in S))
        if best is None or key > best[0]:
            best = (key, S)
    return best[1]


def order_by_separation(S):
    """Farthest-point order, from the start that makes the first k colors best separated for every k."""
    best = None
    for start in S:
        order = [start]
        while len(order) < len(S):
            order.append(max((c for c in S if c not in order), key=lambda c: min(dist(c, o) for o in order)))
        score = [min(dist(order[a], order[b]) for a in range(k) for b in range(a)) for k in range(2, len(S) + 1)]
        if best is None or score > best[0]:
            best = (score, order)
    return best[1]


def unique_hex(h, used):
    """The hex itself, or the nearest one that no other color uses (so a stand-in can be told from other colors)."""
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    for d in range(0, 4):
        for dr, dg, db in itertools.product(range(-d, d + 1), repeat=3):
            if max(abs(dr), abs(dg), abs(db)) != d:
                continue
            t = "#%02x%02x%02x" % tuple(min(255, max(0, v)) for v in (r + dr, g + dg, b + db))
            if t not in used:
                return t
    return h


def oklch_css(L, C, h):
    return f"oklch({L:.4f} {C:.4f} {h:.2f})"


def species_wide(data_dir):
    """Exact colors of the measured patches of the four Colombian species palettes that lie outside sRGB."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_species_palettes as bsp
    meta, spec = cs.load(os.path.join(data_dir, "refcolC.txt"))
    wide = {}
    for key, (fn, sp, box) in bsp.SPECIES.items():
        if not sp:
            continue
        for part in (p for p in bsp.MEASURED if p in bsp.KEEP[key]):
            idx = [i for i, m in enumerate(meta) if m["Species"] == sp and m["Sex"] == "Males" and
                   m["Feather_type"] == {v: k for k, v in cs.PATCHES.items()}[part if part != "mantle" else "mantle"]]
            L, C, h, is_wide = cs.exact_oklch(cs.spectrum_to_linear_rgb(np.median(spec[idx], axis=0)))
            if is_wide:
                wide.setdefault(key, {})[part] = oklch_css(L, C, h)
    return wide


def main(data_dir):
    cand = candidates(data_dir)
    bright = pick_bright(cand)
    dark = pick_dark(cand, bright)
    for b, d in zip(bright, dark):
        d["name"] = DARK_NAMES[b["name"]]
    partners = {d["name"]: b["name"] for b, d in zip(bright, dark)}              # dark color -> its bright partner
    pal, wide, src, used = {}, {}, {}, set()
    for label, S in (("colibri", bright), ("colibri-dark", dark)):
        pal[label], wide[label], src[label] = {}, {}, {}
        for c in S:
            nm = c["name"]
            hx = unique_hex(c["stand"], used)
            used.add(hx)
            pal[label][nm] = hx
            src[label][nm] = (c["species"], c["sex"], c["patch"], c["n"])
            if c["wide"]:
                wide[label][nm] = oklch_css(c["L"], c["C"], c["h"])
    wide.update(species_wide(data_dir))
    lines = ['"""Generated by examples/build_spectral_data.py; do not edit by hand.',
             "",
             "COLIBRI, COLIBRI_DARK: palettes of colors measured in the Colombian hummingbird reflectance database",
             "(Beltran, Shultz & Parra, Dryad doi:10.5061/dryad.02v6wwq8w); the hex is the color in sRGB, or its nearest",
             "sRGB color when it lies outside the gamut.  WIDE gives the exact color of those entries as an OKLCH string.",
             "SOURCES gives (species, sex, patch, number of specimens) of every color.",
             '"""', ""]
    for var, label in (("COLIBRI", "colibri"), ("COLIBRI_DARK", "colibri-dark")):
        lines.append(f"{var} = {{")
        lines += [f'    "{k}": "{v}",' for k, v in pal[label].items()]
        lines += ["}", ""]
    lines.append("WIDE = {")
    for label, d in wide.items():
        if d:
            lines.append(f'    "{label}": {{')
            lines += [f'        "{k}": "{v}",' for k, v in d.items()]
            lines.append("    },")
    lines += ["}", "", "# dark color -> the bright color of colibri it is the darker partner of (the same index in both palettes)",
              "PARTNERS = {"]
    lines += [f'    "{k}": "{v}",' for k, v in partners.items()]
    lines += ["}", "", "SOURCES = {"]
    for label in ("colibri", "colibri-dark"):
        lines.append(f'    "{label}": {{')
        lines += [f'        "{k}": {tuple(v)!r},' for k, v in src[label].items()]
        lines.append("    },")
    lines += ["}", ""]
    open(OUT, "w").write("\n".join(lines))
    print("wrote", OUT)
    for label in ("colibri", "colibri-dark"):
        print(label)
        for k, v in pal[label].items():
            print(f"   {v}{'*' if k in wide[label] else ' '} {k:11s} contrast {contrast_with_white(v):.1f}  {src[label][k]}")
    order = [c for c in bright]
    print("colibri first-k min distance:", [round(min(dist(order[a], order[b]) for a in range(k) for b in range(a)), 1)
                                          for k in range(2, len(order) + 1)])
    print("colibri-dark min distance:", round(min(dist(a, b) for a, b in itertools.combinations(dark, 2)), 1))


if __name__ == "__main__":
    main(sys.argv[1])
