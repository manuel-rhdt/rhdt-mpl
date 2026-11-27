"""PDF (Display P3, as the umbruch backend writes it) to an SVG whose colors are Display P3 too.

pdftocairo color-manages the PDF and writes sRGB, which clips everything outside that gamut.  So the ICC profiles are
first replaced by DeviceRGB, which pdftocairo passes through unchanged: the SVG then holds the Display P3 numbers.
They are rewritten as CSS ``color(display-p3 r g b)`` in a ``style`` attribute, next to the sRGB version in the plain
``fill``/``stroke`` attribute that a browser without ``color()`` falls back to; embedded PNGs get a Display P3 ICC
profile.  Grays are left alone (they are the same in both spaces).

    from wide_svg import pdf_to_wide_svg
    pdf_to_wide_svg("fig.pdf", "fig.svg")
"""
import os
import re
import subprocess
import tempfile

import numpy as np
import pikepdf

import umbruch_matplotlib as um
from rhdt_mpl import colorspace as cs


def _device_rgb(obj, seen):
    """Replace every ICCBased color space below *obj* by DeviceRGB, and drop DefaultRGB (which would remap it)."""
    if isinstance(obj, pikepdf.Array):
        for i, x in enumerate(obj):
            if isinstance(x, pikepdf.Array) and len(x) == 2 and x[0] == "/ICCBased":
                obj[i] = pikepdf.Name.DeviceRGB
            else:
                _device_rgb(x, seen)
    elif isinstance(obj, (pikepdf.Dictionary, pikepdf.Stream)):
        if obj.is_indirect:
            if obj.objgen in seen:
                return
            seen.add(obj.objgen)
        if "/DefaultRGB" in obj.keys():
            del obj["/DefaultRGB"]
        for k in list(obj.keys()):
            if k == "/Parent":
                continue
            v = obj[k]
            if isinstance(v, pikepdf.Array) and len(v) == 2 and v[0] == "/ICCBased":
                obj[k] = pikepdf.Name.DeviceRGB
            else:
                _device_rgb(v, seen)


def strip_icc(src, dst):
    with pikepdf.open(src) as pdf:
        seen = set()
        for page in pdf.pages:
            _device_rgb(page.obj, seen)
        pdf.save(dst)


_RGB = re.compile(r'\b(fill|stroke)="rgb\(([\d.]+)%, ([\d.]+)%, ([\d.]+)%\)"')
_TAG = re.compile(r"<[a-zA-Z][^>]*>")
_IMG = re.compile(r'(xlink:href|href)="(data:image/png;base64,[^"]+)"')


def _tag(m):
    tag, styles = m.group(0), []

    def one(c):
        prop = c.group(1)
        p3 = np.array([float(c.group(i)) / 100 for i in (2, 3, 4)])
        if np.ptp(p3) < 1e-4:                                    # gray: the same in sRGB
            return c.group(0)
        s = cs.convert(p3, "display-p3", "srgb")
        styles.append(f"{prop}:color(display-p3 {p3[0]:.4f} {p3[1]:.4f} {p3[2]:.4f})")
        return f'{prop}="rgb({s[0] * 100:.4f}%, {s[1] * 100:.4f}%, {s[2] * 100:.4f}%)"'

    tag = _RGB.sub(one, tag)
    if styles:
        css = ";".join(styles)
        if ' style="' in tag:
            tag = tag.replace(' style="', f' style="{css};', 1)
        else:
            tag = re.sub(r"(/?>)$", lambda e: f' style="{css}"{e.group(1)}', tag)
    return tag


def p3_svg(svg):
    """The text of an SVG whose ``rgb()`` colors and PNG images are Display P3 numbers, with Display P3 colors."""
    svg = _TAG.sub(_tag, svg)
    return _IMG.sub(lambda m: f'{m.group(1)}="{um._tag_png_uri(m.group(2), "display-p3")}"', svg)


def pdf_to_wide_svg(pdf, svg):
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.pdf")
        strip_icc(pdf, raw)
        subprocess.run(["pdftocairo", "-svg", raw, os.path.join(tmp, "out.svg")], check=True)
        text = open(os.path.join(tmp, "out.svg"), encoding="utf-8").read()
    with open(svg, "w", encoding="utf-8") as fh:
        fh.write(p3_svg(text))
