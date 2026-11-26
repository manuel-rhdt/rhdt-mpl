"""Build src/rhdt_mpl/spectral_data.py: the colibri palettes and the exact colors of the spectrum-based palettes.

The colibri palettes use only colors measured in the Colombian hummingbird reflectance database (Beltran, Shultz & Parra,
Dryad doi:10.5061/dryad.02v6wwq8w), mixing species and patches freely:
  colibri       eight bright colors, the most vivid one per hue sector (with a preference for well measured ones),
                with the blue chosen to be as far as possible from the others; ordered so the first k are best separated
  colibri-dark  for each of them a darker partner of similar hue (lightness lower by 0.08 to 0.26), also from the data,
                chosen jointly so that the eight darker colors are as distinct from each other as possible
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
SECTORS = [("red", 345, 30), ("orange", 30, 80), ("yellow-green", 95, 130), ("green", 132, 156), ("teal", 156, 215),
           ("blue", 222, 272), ("violet", 272, 312), ("magenta", 318, 350)]


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
        lab = np.array([L, C * np.cos(np.radians(h)), C * np.sin(np.radians(h))])
        out.append(dict(species=sp, sex=sex, patch=cs.PATCHES[code], n=len(idx), L=L, C=C, h=h, wide=wide, lab=lab,
                        stand=ok.oklch(L, C, h)))
    return out


def dist(a, b):
    return 100 * float(np.linalg.norm(a["lab"] - b["lab"]))


def in_sector(c, lo, hi):
    return lo <= c["h"] < hi if lo < hi else (c["h"] >= lo or c["h"] < hi)


def pick_bright(cand):
    chosen = {}
    for name, lo, hi in SECTORS:
        pool = [c for c in cand if in_sector(c, lo, hi) and c["L"] >= 0.48 and c["C"] >= 0.12]
        if name != "blue":
            chosen[name] = max(pool, key=lambda c: c["C"] + 0.004 * min(c["n"], 10))
    others = list(chosen.values())
    pool = [c for c in cand if in_sector(c, 222, 272) and c["L"] >= 0.5 and c["C"] >= 0.12]
    chosen["blue"] = max(pool, key=lambda c: min(dist(c, o) for o in others))
    S = list(chosen.values())
    order = [max(S, key=lambda c: c["C"])]
    while len(order) < len(S):
        order.append(max((c for c in S if c not in order), key=lambda c: min(dist(c, o) for o in order)))
    return order


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


def name_of(c):
    return f"{c['species'].split('_')[1]} {c['patch']}"


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
        for part in bsp.MEASURED:
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
    pal, wide, src, used = {}, {}, {}, set()
    for label, S in (("colibri", bright), ("colibri-dark", dark)):
        pal[label], wide[label], src[label] = {}, {}, {}
        for c in S:
            nm = name_of(c)
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
            print(f"   {v}{'*' if k in wide[label] else ' '} {k:24s} {src[label][k]}")


if __name__ == "__main__":
    main(sys.argv[1])
