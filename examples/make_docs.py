"""Regenerate the SVG figures of the README into docs/.  Needs an umbruch binary ($UMBRUCH or PATH)
and pdftocairo (poppler).  The figures are drawn by the umbruch backend to PDF (Display P3) and converted to SVG
with the text as embedded glyph outlines, so they look the same in every browser, and the colors as Display P3
(wide_svg.py).

    python examples/make_docs.py
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wide_svg import pdf_to_wide_svg   # noqa: E402

here = os.path.dirname(os.path.abspath(__file__))
docs = os.path.join(os.path.dirname(here), "docs")
os.makedirs(docs, exist_ok=True)

# (script, [pdfs it writes])
jobs = [("showcase_colors.py", ["colors", "colormaps"]),
        ("features.py", ["features"]),
        ("colibri.py", ["colibri"]),
        ("oklab_helpers.py", ["oklab_helpers"]),
        ("colormap_examples.py", ["cmap_wigner", "cmap_fields", "cmap_curves"]),
        ("math_examples.py", ["math"])]

with tempfile.TemporaryDirectory() as tmp:
    for script, names in jobs:
        subprocess.run([sys.executable, os.path.join(here, script), tmp], check=True)
        for n in names:
            pdf_to_wide_svg(os.path.join(tmp, n + ".pdf"), os.path.join(docs, n + ".svg"))
            print("wrote", os.path.join(docs, n + ".svg"))

# the table of all named colors in the README, with its swatch images
subprocess.run([sys.executable, os.path.join(here, "make_color_table.py")], check=True)
