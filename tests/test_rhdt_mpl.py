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
    assert mc.to_hex("rhdt:orange") == mc.to_hex("rhdt:tol-vibrant:orange")      # short form: default palette
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
    assert list(rhdt_mpl.PALETTES["colibri"])[0] == "leadbeateri gorget"
    assert mc.to_hex("rhdt:colibri:mosquitus crown") == "#b60042"              # the stand-in of an out-of-gamut color
    assert rhdt_mpl.wide_css("colibri", "mosquitus crown").startswith("oklch(0.49")
    assert rhdt_mpl.wide_css("colibri", "pyra gorget") is None                 # inside sRGB: exact
    stand = [h for k in ("colibri", "colibri-dark") for h in rhdt_mpl.PALETTES[k].values()]
    assert len(set(stand)) == 16                                               # stand-ins are distinct
    rhdt_mpl.set_cycle("colibri")
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
    test_backend_and_fonts("/tmp/claude-0/-home-user/b31222e4-7591-5457-af74-51ed8c3e5c07/scratchpad")
