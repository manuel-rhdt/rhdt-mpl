# rhdt-mpl

Personal Matplotlib defaults: the [umbruch](https://github.com/manuel-rhdt/umbruch) backend, bundled Noto fonts,
named palettes and cycles, nine colormaps, and helpers for adjusting colors in OKLab.

```python
import rhdt_mpl                      # import before pyplot
import matplotlib.pyplot as plt
```

Importing the package does five things:

1. selects the backend `module://umbruch_matplotlib` (PDF output with text and math laid out by umbruch),
2. registers the bundled Noto Sans, Noto Sans Mono, Noto Serif and Noto Sans Math with Matplotlib and starts umbruch with
   `--font-dir` pointing at them (the backend's default bridge uses `--no-system-fonts` and would not see them),
3. applies the style `rhdt.mplstyle` and the default color cycle,
4. registers the colormaps (`ok_orchid`, ... and their `_r` versions),
5. registers every palette color under the name `rhdt:<palette>:<name>` and every palette as a color sequence.

`rhdt_mpl.use(backend=False)` re-applies the style without changing the backend.

All figures below are produced by this package. They are drawn by the umbruch backend to PDF and converted to SVG with the
text as outlines (`python examples/make_docs.py`).

## Everything in one figure

<img src="docs/features.svg" alt="Overview of the features: default cycle with math and rich text, print cycle, default colormap, single-hue colormap, named colors and roles, 8-color cycle" width="100%">

Panels from the top left: **a** default style and cycle with a rich-text label and a math label; **b** the greyscale-safe
`ok-print` cycle; **c** the default colormap `ok_orchid`; **d** a reversed single-hue colormap; **e** named colors with a
black theory line, a bright highlight and a muted family; **f** the 8-color cycle. The script is `examples/features.py`.

## Style

The style follows the ML-PWS paper figures: full axes box in black, outward ticks, 8 pt text (axis labels 8.8 pt, titles
9.6 pt), 1.5 pt lines, markers of 4 pt without edge, legends without frame, constrained layout, `savefig.bbox = tight`.
The grid is off but styled (`#B0B0B0`, 0.8 pt); `ax.grid()` turns it on.

```python
import rhdt_mpl
fig, ax = plt.subplots(figsize=(rhdt_mpl.TWO_COLUMN, 2.8))   # 510 pt, the width of the paper figures
...
rhdt_mpl.panel_labels(axs)                                    # bold a, b, c, ... at the top left of each axes
fig.savefig("fig.pdf")
```

Labels may contain rich text and math, set by umbruch ([umbruch-matplotlib](https://github.com/manuel-rhdt/umbruch-matplotlib)):

```python
from umbruch_matplotlib import rich
ax.set_xlabel(rich("time <i>t</i> (ms)"))
ax.set_ylabel(r"$\hat\rho_{ij}(t)$")
```

## Palettes and cycles

<img src="docs/colors.svg" alt="All palettes, cycles, named colors and OKLab helpers with their syntax" width="100%">

The default cycle is Tol Vibrant without the grey (orange, blue, cyan, magenta, red, teal). Palettes:
`tol-bright`, `tol-vibrant`, `tol-muted`, `tol-pale`, `tol-dark`, `okabe-ito`, `colibri` (eight saturated hummingbird
jewel tones), the species palettes `sunangel`, `ruby-topaz`, `starfrontlet`, `sapphire` and `broad-billed`, and
the two cycles `ok6` and `ok8`.
In the cycles `ok6`, `ok8` and `colibri` the first k colors are the best separated. The hummingbird palettes have their own section below.

```python
rhdt_mpl.palette("okabe-ito")                    # list of hex colors
rhdt_mpl.palette("tol-vibrant", ["orange", "teal"])   # select and order by name
rhdt_mpl.set_palette("okabe-ito")                # use as the color cycle
rhdt_mpl.set_cycle("ok8")                        # any palette, or "ok-print"
ax.set_prop_cycle(rhdt_mpl.cycle("ok6"))         # per axes
rhdt_mpl.use(backend=False)                      # back to the default cycle
```

`ok-print` pairs the `ok6` colors one-to-one with the line styles `-`, `--`, `:`, `-.`, `(0,(5,1,1,1))`, `(0,(1,1))`, so
that lines stay distinguishable in greyscale. `rhdt_mpl.PALETTES` holds the palettes as `{name: hex}` dicts; the colors are
those of <https://site.manuel-rhdt.de/post/colors/>.

## Individual colors by name

Every palette color is registered with Matplotlib as `"rhdt:<palette>:<name>"`, accepted wherever a color is, including
`rcParams` and the `oklab` helpers:

```python
ax.plot(x, y, color="rhdt:tol-vibrant:orange")
ax.bar(x, h, color="rhdt:tol-pale:pale blue", edgecolor="rhdt:tol-dark:dark blue")
ax.plot(x, y, color="rhdt:okabe-ito:sky blue")
```

The colors of the default palette (Tol Vibrant) also have the short form `"rhdt:orange"`. Other palettes have none,
because bare names are ambiguous: `blue` is three different colors across the palettes, and `ok6:navy` differs from
`ok8:navy`. Matplotlib's own CSS4 names (`"orange"`, `"navy"`) are untouched. `rhdt_mpl.named_colors()` lists all names.
The palettes are also available as `matplotlib.color_sequences["rhdt:ok6"]` and so on.

## Colormaps

<img src="docs/colormaps.svg" alt="The nine colormaps with their OKLab lightness" width="100%">

256-entry sRGB tables designed in OKLab, with the OKLab lightness of each shown underneath. All run dark to light; append
`_r` for light to dark, which is the usual direction for single-hue maps on a white background. `ok_orchid` is the default
`image.cmap`.

```python
plt.imshow(z)                        # ok_orchid
plt.imshow(z, cmap="ok_dusk")        # multi-hue: ok_dusk, ok_orchid
plt.imshow(z, cmap="ok_blue_r")      # single-hue: ok_blue, ok_teal, ok_green, ok_orange, ok_red, ok_purple, ok_pink
```

## Hummingbird palettes

<img src="docs/colibri.svg" alt="The colibri palette and one palette per hummingbird species, with plumage-part names and hex codes, and the palettes used with a dark line, a bright accent and quieter secondary lines" width="100%">

<table>
<tr><td align="center"><img src="docs/birds/sunangel.webp" width="260" alt="Tourmaline sunangel"><br><code>sunangel</code><br>Tourmaline sunangel<br><i>Heliangelus exortis</i></td><td align="center"><img src="docs/birds/ruby-topaz.webp" width="260" alt="Ruby-topaz"><br><code>ruby-topaz</code><br>Ruby-topaz<br><i>Chrysolampis mosquitus</i></td><td align="center"><img src="docs/birds/starfrontlet.webp" width="260" alt="Golden-bellied starfrontlet"><br><code>starfrontlet</code><br>Golden-bellied starfrontlet<br><i>Coeligena bonapartei</i></td></tr>
<tr><td align="center"><img src="docs/birds/sapphire.webp" width="260" alt="Golden-tailed sapphire"><br><code>sapphire</code><br>Golden-tailed sapphire<br><i>Chrysuronia oenone</i></td><td align="center"><img src="docs/birds/broad-billed.webp" width="260" alt="Broad-billed hummingbird"><br><code>broad-billed</code><br>Broad-billed hummingbird<br><i>Cynanthus latirostris</i></td><td></td></tr>
</table>

The birds are generated reference images (males, hovering), not photographs. Two kinds of palette are named after
hummingbirds:

- **`colibri`**: eight saturated jewel tones, ordered so that the first k colors are the best separated: violetear
  `#710bc6`, topaz `#e8ca17`, ruby `#c6001f`, emerald `#00ae64`, fuchsia `#e825bc`, copper `#db7d24`, sapphire `#005dca`,
  turquoise `#31c8c9`. Use it as a cycle: `rhdt_mpl.set_cycle("colibri")`.
- **One palette per species**, eight colors named after plumage parts, the gorget first: `sunangel`, `ruby-topaz`,
  `starfrontlet`, `sapphire` and `broad-billed`. For the first four, the **gorget, crown, belly, mantle and rump are
  measured reflectance spectra** of males from the Colombian hummingbird database of Beltran, Shultz & Parra (*Evolution*,
  [Dryad](https://doi.org/10.5061/dryad.02v6wwq8w)), taken at the angle of maximum reflectance and converted to sRGB (CIE 1931
  observer, D65; colors outside the sRGB gamut are brought back by reducing chroma at constant OKLab lightness and hue,
  which affects the ruby-topaz crown and gorget, the starfrontlet crown and the sapphire crown and gorget).
  The **wing, tail and bill** are not in the database and are sampled from the images, as are all colors of the
  broad-billed hummingbird, which the database does not contain (it has a `vent` color, the white undertail).
  `examples/build_species_palettes.py` builds the palettes and prints how far each measured patch is from the image.

```python
rhdt_mpl.palette("ruby-topaz")                       # gorget, crown, belly, mantle, rump, wing, tail, bill
rhdt_mpl.palette("ruby-topaz", ["gorget", "tail"])   # select and order by name
ax.plot(x, y, color="rhdt:ruby-topaz:gorget")        # the accent
ax.plot(x, theory, color="rhdt:ruby-topaz:mantle", lw=2)   # a dark line
ax.plot(x, other, color="rhdt:ruby-topaz:rump")      # a quiet one
```

A bird is one bright accent on a quiet body, which is the pattern for data too: a bright gorget for the result that
matters, a dark part for a theory line, quieter parts for secondary lines. Iridescent colors depend on the viewing angle, and
the spectra were measured on museum study skins and live birds, so the measured colors are one view of each patch; the
image colors, when they differ, are the image generator's choice (the largest differences are the starfrontlet crown, which
the image shows duller, and the ruby-topaz belly and mantle, which the image shows nearly black). The `colibri` palette
is the one meant for cycles; the species palettes are for choosing colors by name.

## Color helpers in OKLab

<img src="docs/oklab_helpers.svg" alt="Each OKLab helper applied to the Tol Vibrant colors, and the black, bright, muted pattern in a plot" width="100%">

```python
from rhdt_mpl import oklab

oklab.muted("rhdt:orange")                  # same hue, less chroma, a bit lighter: for secondary lines
oklab.family("rhdt:tol-vibrant:cyan", 3)    # three lightness steps of one hue, dark to light
oklab.lighten("#0077BB", 0.1)               # +0.1 OKLab lightness
oklab.darken("#0077BB", 0.1)
oklab.rotate_hue("#009988", -20)            # degrees in OKLCH
oklab.mix("#EE7733", "#0077BB", 0.3)        # interpolate in OKLab
oklab.adjust("#EE7733", dL=0.05, scale_C=0.8)   # set or shift L, C, h, or scale C
oklab.to_oklab(c), oklab.to_oklch(c), oklab.oklab(L, a, b), oklab.oklch(L, C, h), oklab.lightness(c)
```

All functions take any Matplotlib color and return `#rrggbb`. A result outside the sRGB gamut is brought back by reducing
chroma at constant lightness and hue, not by clipping channels. `family` varies lightness only, so members of a family
should also differ in marker or dash (hue alone is not enough for everyone).

## Installation

```
pip install --no-deps git+https://github.com/manuel-rhdt/rhdt-mpl
pip install matplotlib
```

The package needs two things that are not on PyPI:

- the **umbruch** executable (`$UMBRUCH`, `PATH`, or the `umbruch` Python package), from
  <https://github.com/manuel-rhdt/umbruch>, and
- **umbruch-matplotlib**, from <https://github.com/manuel-rhdt/umbruch-matplotlib>. Its `pip` dependency on
  `umbruch>=0.5.0` cannot be resolved from PyPI; install it with `--no-deps` when the executable is installed separately.

The math font (Noto Sans Math, set through `umbruch_matplotlib.config.math_font`) needs a version of umbruch-matplotlib that
has this option. Without it the attribute is set but ignored, and formulas are set in umbruch's built-in math fonts.

Fonts: Noto Sans, Noto Sans Mono, Noto Serif and Noto Sans Math (SIL Open Font License 1.1, see
`src/rhdt_mpl/fonts/LICENSE-Noto-OFL.txt`), about 5 MB.

## Development

```
python examples/make_docs.py                          # regenerate docs/*.svg (needs umbruch and pdftocairo)
UMBRUCH=/path/to/umbruch python tests/test_rhdt_mpl.py
python tests/test_oklab.py
```

`examples/` also holds `gallery.py` (a four-panel figure), `compare_cycles.py` (the same data under several cycles),
`colombia_spectra.py` (reflectance spectra to sRGB), `colombia_overview.py` and `colombia_picks.py` (figures of the Colombian
species) and `build_species_palettes.py`; the spectra are not in the repository.
