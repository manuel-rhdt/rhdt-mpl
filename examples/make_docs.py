"""Regenerate the SVG figures of the README into docs/.  Needs an umbruch binary ($UMBRUCH or PATH)
and pdftocairo (poppler).  The figures are drawn by the umbruch backend to PDF and converted to SVG
with the text as embedded glyph outlines, so they look the same in every browser.

    python examples/make_docs.py
"""
import os
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
docs = os.path.join(os.path.dirname(here), "docs")
os.makedirs(docs, exist_ok=True)

# (script, [pdfs it writes])
jobs = [("showcase_colors.py", ["colors", "colormaps"]),
        ("features.py", ["features"]),
        ("colibri.py", ["colibri"]),
        ("oklab_helpers.py", ["oklab_helpers"])]

# the hummingbird illustrations are written as SVG directly
subprocess.run([sys.executable, os.path.join(here, "draw_hummingbirds.py")], check=True)

with tempfile.TemporaryDirectory() as tmp:
    for script, names in jobs:
        subprocess.run([sys.executable, os.path.join(here, script), tmp], check=True)
        for n in names:
            subprocess.run(["pdftocairo", "-svg", os.path.join(tmp, n + ".pdf"), os.path.join(docs, n + ".svg")],
                           check=True)
            print("wrote", os.path.join(docs, n + ".svg"))
