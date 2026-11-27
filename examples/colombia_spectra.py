"""Colors of Colombian hummingbird plumage from measured reflectance spectra.

Data: Beltran, Shultz & Parra, "Sexual and ecological drivers of plumage conspicuousness in hummingbirds",
Evolution; Dryad doi:10.5061/dryad.02v6wwq8w (refcolC.txt: 131 species, five patches, reflectance 300-700 nm at the
angle of maximum reflectance; refmin.txt / refthird.txt: the angle of minimum and an intermediate reflectance).
The data are not part of this repository; pass the path of the extracted files.

A spectrum is turned into a screen color by integrating it against the CIE 1931 2 degree observer under illuminant
D65 (colour-science), converting to linear sRGB, then to the current color space of rhdt_mpl (Display P3 for the
palettes: ``with rhdt_mpl.colorspace.using("display-p3")``) and, when the color lies outside its gamut, reducing chroma
at constant OKLab lightness and hue (rhdt_mpl.oklab).  Reflectance beyond 700 nm is held at its value at 700 nm.

    from colombia_spectra import load, patch_colors
    meta, spec = load("data/refcolC.txt")
    patch_colors(meta, spec, "Colibri_coruscans", "Males")      # {"crown": "#...", "gorget": "#...", ...}
"""
import csv

import numpy as np

PATCHES = {"1": "crown", "2": "gorget", "3": "belly", "4": "mantle", "5": "rump"}
WAVELENGTHS = np.arange(300, 701)


def load(path):
    """(metadata list of dicts, reflectance array [n, 401] in percent) from a reflectance table."""
    with open(path) as fh:
        rd = csv.reader(fh, delimiter="\t")
        hdr = [h.strip('"') for h in next(rd)]
        rows = list(rd)
    assert all(len(r) == len(hdr) + 1 for r in rows)          # rows carry a leading row number the header lacks
    meta = [dict(zip(hdr[:12], r[1:13])) for r in rows]
    spec = np.array([[float(v) for v in r[13:]] for r in rows])
    return meta, spec


_colour = None


def _tools():
    global _colour
    if _colour is None:
        import colour
        _colour = (colour, colour.MSDS_CMFS["CIE 1931 2 Degree Standard Observer"], colour.SDS_ILLUMINANTS["D65"])
    return _colour


def spectrum_to_linear_rgb(reflectance_percent):
    """Linear sRGB (may lie outside [0, 1]) of a reflectance spectrum sampled 300-700 nm every nm."""
    colour, cmfs, illuminant = _tools()
    wl = np.arange(300, 781)
    r = np.concatenate([np.clip(reflectance_percent, 0, None) / 100.0,
                        np.full(80, np.clip(reflectance_percent[-1], 0, None) / 100.0)])
    sd = colour.SpectralDistribution(dict(zip(wl, r)))
    XYZ = colour.sd_to_XYZ(sd, cmfs, illuminant) / 100.0
    return colour.XYZ_to_RGB(XYZ, "sRGB", apply_cctf_encoding=False)


def linear_rgb_to_hex(lin):
    """Hex color in the current color space (``rhdt_mpl.colorspace``; use ``with colorspace.using("display-p3")``) from
    linear sRGB; out-of-gamut colors keep OKLab lightness and hue and lose chroma.  Returns (hex, was_in_gamut)."""
    from rhdt_mpl import colorspace as cs, oklab as ok
    lin = np.asarray(lin, float)
    here = cs.srgb_linear_to_linear(lin, cs.current())
    if cs.in_gamut(here, 1e-4):
        return ok._hex(cs.encode(np.clip(here, 0, 1))), True
    return ok.oklab(*(ok._M2 @ np.cbrt(ok._M1 @ lin))), False


def exact_oklch(lin):
    """(L, C, h) of a linear sRGB color that may lie outside the gamut (no clipping), and whether it is outside the gamut
    of the current color space."""
    from rhdt_mpl import colorspace as cs, oklab as ok
    lin = np.asarray(lin, float)
    L, a, b = ok._M2 @ np.cbrt(ok._M1 @ lin)
    wide = not bool(cs.in_gamut(cs.srgb_linear_to_linear(lin, cs.current()), 1e-4))
    return float(L), float(np.hypot(a, b)), float(np.degrees(np.arctan2(b, a)) % 360), wide


def patch_colors(meta, spec, species, sex="Males", average="median"):
    """{patch name: hex} for *species*: the median spectrum over its specimens of that sex, per patch."""
    out = {}
    for code, name in PATCHES.items():
        idx = [i for i, m in enumerate(meta) if m["Species"] == species and m["Sex"] == sex and m["Feather_type"] == code]
        if not idx:
            continue
        s = np.median(spec[idx], axis=0) if average == "median" else spec[idx].mean(axis=0)
        out[name] = linear_rgb_to_hex(spectrum_to_linear_rgb(s))[0]
    return out


def species_list(meta):
    return sorted({m["Species"] for m in meta})
