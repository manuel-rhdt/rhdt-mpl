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

Fonts: Noto Sans, Noto Sans Mono and Noto Serif (OFL 1.1, see `fonts/LICENSE-Noto-OFL.txt`). Math is set in Noto Sans Math through `umbruch_matplotlib.config.math_font` (needs the backend change that adds it). Palettes: `rhdt_mpl.PALETTES`.

Colormaps (`rhdt_mpl.okmaps`, 256-entry sRGB tables, registered with Matplotlib on import, each also as `_r`):
multi-hue `ok_orchid` (default `image.cmap`) and `ok_dusk`; single-hue `ok_blue`, `ok_teal`, `ok_green`,
`ok_orange`, `ok_red`, `ok_purple`, `ok_pink`. All run dark to light; use `_r` for light to dark on a white background.

Palettes `ok6` and `ok8` are ordered so that the first k colors are the most separated; `"ok-print"` is the
ok6 colors paired one-to-one with the line styles `- -- : -. (0,(5,1,1,1)) (0,(1,1))`. `rhdt_mpl.cycle(name)` returns the
`cycler`, `set_cycle(name)` installs it.
