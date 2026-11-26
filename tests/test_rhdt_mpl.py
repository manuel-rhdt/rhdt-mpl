import os, subprocess, tempfile
import numpy as np
import rhdt_mpl
import matplotlib
import matplotlib.pyplot as plt
from umbruch_matplotlib import rich


def test_backend_and_fonts(tmp_path=None):
    assert matplotlib.get_backend().lower() == "module://umbruch_matplotlib"
    assert matplotlib.rcParams["font.sans-serif"][0] == "Noto Sans"
    out = os.path.join(tmp_path or tempfile.mkdtemp(), "fig.pdf")
    x = np.linspace(0, 2 * np.pi, 100)
    fig, ax = plt.subplots()
    for k in range(4):
        ax.plot(x, np.sin(x + k / 2), label=f"k={k}")
    ax.set_xlabel(rich("time <i>t</i> (ms)"))
    ax.set_ylabel(r"$\sin(x)$")
    ax.set_title("Noto Sans check")
    ax.legend()
    fig.savefig(out)
    names = subprocess.run(["pdffonts", out], capture_output=True, text=True).stdout
    print(names)
    assert "NotoSansMath" in names and "STIX" not in names and "DejaVu" not in names


def test_cycles():
    import matplotlib as mpl
    assert list(rhdt_mpl.PALETTES["ok6"].values())[:2] == ["#1d5e85", "#c8b222"]
    assert len(rhdt_mpl.PALETTES["ok8"]) == 8
    rhdt_mpl.set_cycle("ok-print")
    k = mpl.rcParams["axes.prop_cycle"].by_key()
    assert k["color"] == list(rhdt_mpl.PALETTES["ok6"].values())
    assert k["linestyle"][4] == (0, (5, 1, 1, 1)) and len(k["linestyle"]) == 6
    rhdt_mpl.use(backend=False)     # restore the default cycle


def test_named_colors():
    import matplotlib as mpl, matplotlib.colors as mc
    assert mc.to_hex("rhdt:tol-vibrant:orange") == "#ee7733" and mc.to_hex("rhdt:okabe-ito:sky blue") == "#56b4e9"
    assert mc.to_hex("rhdt:ok6:navy") == "#1d5e85" and mc.to_hex("rhdt:ok8:navy") == "#2a5b88"
    assert mc.to_hex("rhdt:emerald") == "#00a051"                                # short form: default palette (colibri)
    assert not mc.is_color_like("rhdt:orange")                                    # Tol Vibrant needs its full name
    assert not mc.is_color_like("rhdt:navy") and not mc.is_color_like("rhdt:tol-vibrant:nope")
    assert mc.to_hex("orange") == "#ffa500" and not mc.is_color_like("tol-vibrant:orange")   # no unprefixed names
    n = sum(len(p) for p in rhdt_mpl.PALETTES.values()) + len(rhdt_mpl.PALETTES[rhdt_mpl.palettes.DEFAULT_PALETTE])
    assert len(rhdt_mpl.named_colors()) == n
    assert list(mpl.color_sequences["rhdt:ok6"])[0] == "#1d5e85"
    with mpl.rc_context({"text.color": "rhdt:tol-dark:dark red", "axes.edgecolor": "rhdt:ok6:gold"}):
        assert mc.to_hex(mpl.rcParams["axes.edgecolor"]) == "#c8b222"
        fig = plt.figure(); t = fig.text(0.5, 0.5, "x")
        assert mc.to_hex(t.get_color()) == "#663333"


def test_colibri():
    import matplotlib.colors as mc
    for key in ("colibri", "colibri-dark"):
        assert len(rhdt_mpl.PALETTES[key]) == 8
        assert set(rhdt_mpl.SOURCES[key]) == set(rhdt_mpl.PALETTES[key])      # every color has its source
    assert not set(rhdt_mpl.PALETTES["colibri"]) & set(rhdt_mpl.PALETTES["colibri-dark"])  # the dark colors have names of their own
    assert list(rhdt_mpl.PARTNERS.values()) == list(rhdt_mpl.PALETTES["colibri"])          # partners in the order of colibri
    assert list(rhdt_mpl.PARTNERS) == list(rhdt_mpl.PALETTES["colibri-dark"])
    assert rhdt_mpl.PARTNERS["garnet"] == "ruby" and mc.to_hex("rhdt:colibri-dark:garnet") == "#6c1f1d"
    assert list(rhdt_mpl.PALETTES["colibri"])[:2] == ["emerald", "tourmaline"]
    assert mc.to_hex("rhdt:colibri:ruby") == "#b60042"                          # the stand-in of an out-of-gamut color
    assert rhdt_mpl.wide_css("colibri", "ruby").startswith("oklch(0.49")
    assert rhdt_mpl.wide_css("colibri", "amber") is None                        # inside sRGB: exact
    stand = [h for k in ("colibri", "colibri-dark") for h in rhdt_mpl.PALETTES[k].values()]
    assert len(set(stand)) == 16                                                # stand-ins are distinct
    # every bright color is visible on white (WCAG contrast of at least 3:1)
    for h in rhdt_mpl.PALETTES["colibri"].values():
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        assert 1.05 / (0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2] + 0.05) >= 3.0, h
    rhdt_mpl.set_cycle("colibri-dark")
    assert len(mpl_cycle()) == 8
    rhdt_mpl.use(backend=False)


def mpl_cycle():
    import matplotlib as mpl
    return mpl.rcParams["axes.prop_cycle"].by_key()["color"]


def test_species_palettes():
    import matplotlib.colors as mc
    for key in ("sunangel", "ruby-topaz", "starfrontlet", "sapphire", "violet-crowned", "broad-billed"):
        assert len(rhdt_mpl.PALETTES[key]) == 8
    for key in ("sunangel", "ruby-topaz", "starfrontlet", "sapphire", "broad-billed"):
        assert list(rhdt_mpl.PALETTES[key])[0] == "gorget"
    assert list(rhdt_mpl.PALETTES["sunangel"]) == ["gorget", "crown", "belly", "mantle", "rump", "wing", "tail", "bill"]
    assert list(rhdt_mpl.PALETTES["violet-crowned"])[:2] == ["crown", "throat"]
    assert "vent" in rhdt_mpl.PALETTES["broad-billed"]
    assert mc.to_hex("rhdt:ruby-topaz:gorget") == "#ff8a1b"          # a measured spectrum
    assert rhdt_mpl.palette("sapphire", ["gorget", "crown"]) == ["#0043be", "#0043d6"]
    for gone in ("anna", "ruby-throated", "rufous", "costa", "crimson-topaz", "sparkling-violetear"):
        assert gone not in rhdt_mpl.PALETTES


def test_default_cycle_is_colibri():
    import matplotlib as mpl
    rhdt_mpl.use(backend=False)
    assert mpl_cycle() == list(rhdt_mpl.PALETTES["colibri"].values())


def test_readme_lists_all_named_colors():
    import os
    readme = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")).read()
    rows = [l for l in readme.splitlines() if l.startswith("| <img")]
    expected = sum(len(p) for p in rhdt_mpl.PALETTES.values())
    assert len(rows) == expected, (len(rows), expected)          # regenerate with examples/make_color_table.py
    for palette, colors in rhdt_mpl.PALETTES.items():
        for name, hexv in colors.items():
            assert any(f"`rhdt:{palette}:{name}` | `{hexv.lower()}`" in r for r in rows), (palette, name)


def test_colormaps():
    import matplotlib as mpl
    assert mpl.rcParams["image.cmap"] == "ok_orchid"
    from rhdt_mpl import okmaps
    assert len(okmaps.COLORMAPS) == 9
    for n in okmaps.COLORMAPS:
        for m in (n, n + "_r"):
            assert m in mpl.colormaps and mpl.colormaps[m].N == 256


if __name__ == "__main__":
    test_colormaps()
    test_cycles()
    test_named_colors()
    test_colibri()
    test_species_palettes()
    test_readme_lists_all_named_colors()
    test_default_cycle_is_colibri()
    test_backend_and_fonts("/tmp/claude-0/-home-user/b31222e4-7591-5457-af74-51ed8c3e5c07/scratchpad")
