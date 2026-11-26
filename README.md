# rhdt-mpl

Matplotlib defaults: umbruch backend, bundled Noto fonts, palettes from site.manuel-rhdt.de/post/colors.

```python
import rhdt_mpl                 # import before pyplot
import matplotlib.pyplot as plt
rhdt_mpl.set_palette("okabe-ito")   # optional; default cycle is Tol Bright without grey
```

Importing selects `module://umbruch_matplotlib`, registers the Noto fonts with Matplotlib, starts umbruch with
`--font-dir` pointing at the bundled fonts (the backend's own default bridge uses `--no-system-fonts` and would not
see them), and applies `rhdt.mplstyle`. `rhdt_mpl.use(backend=False)` keeps the current backend.

Fonts: Noto Sans, Noto Sans Mono and Noto Serif (OFL 1.1, see `fonts/LICENSE-Noto-OFL.txt`). Math is set by the backend
in STIX Two Math; this package does not change that. Palettes: `rhdt_mpl.PALETTES`.
