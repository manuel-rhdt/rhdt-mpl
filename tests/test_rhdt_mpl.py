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


def test_display_p3_is_the_default():
    import umbruch_matplotlib as um
    assert rhdt_mpl.colorspace.current() == "display-p3" and um.config.color_space == "display-p3"
    assert {k for k, v in rhdt_mpl.NATIVE_SPACE.items() if v == "display-p3"} >= {"colibri", "colibri-dark"}
    assert "ok6" not in rhdt_mpl.NATIVE_SPACE and "okabe-ito" not in rhdt_mpl.NATIVE_SPACE     # sRGB palettes


def test_cycles():
    import matplotlib as mpl
    assert list(rhdt_mpl.PALETTES["ok6"].values())[:2] == ["#1d5e85", "#c8b222"]    # sRGB numbers
    assert len(rhdt_mpl.PALETTES["ok8"]) == 8
    rhdt_mpl.set_cycle("ok-print")
    k = mpl.rcParams["axes.prop_cycle"].by_key()
    assert k["color"] == rhdt_mpl.palette("ok6")                                      # the same colors in P3 numbers
    assert k["color"][0] != "#1d5e85"
    assert k["linestyle"][4] == (0, (5, 1, 1, 1)) and len(k["linestyle"]) == 6
    rhdt_mpl.use(backend=False)     # restore the default cycle


def test_named_colors():
    import matplotlib as mpl, matplotlib.colors as mc
    assert mc.to_hex("rhdt:colibri:ruby") == "#aa1742"                           # P3 numbers: the native values
    assert mc.to_hex("rhdt:okabe-ito:sky blue") == rhdt_mpl.palette("okabe-ito")[2] != "#56b4e9"   # sRGB palette, converted
    assert mc.to_hex("rhdt:ok6:navy") == rhdt_mpl.palette("ok6")[0]
    assert mc.to_hex("rhdt:emerald") == "#00a543"                                # short form: default palette (colibri)
    assert not mc.is_color_like("rhdt:sky blue")                                  # other palettes need their full name
    assert not mc.is_color_like("rhdt:navy") and not mc.is_color_like("rhdt:okabe-ito:nope")
    assert mc.to_hex("orange") == "#ffa500" and not mc.is_color_like("okabe-ito:orange")     # no unprefixed names
    assert rhdt_mpl.PALETTES["ok6"]["navy"] == "#1d5e85"                         # PALETTES keeps the native numbers
    n = sum(len(p) for p in rhdt_mpl.PALETTES.values()) + len(rhdt_mpl.PALETTES[rhdt_mpl.palettes.DEFAULT_PALETTE])
    assert len(rhdt_mpl.named_colors()) == n
    assert list(mpl.color_sequences["rhdt:ok6"])[0] == rhdt_mpl.palette("ok6")[0]
    with mpl.rc_context({"text.color": "rhdt:colibri-dark:garnet", "axes.edgecolor": "rhdt:ok6:gold"}):
        assert mc.to_hex(mpl.rcParams["axes.edgecolor"]) == rhdt_mpl.palette("ok6")[1]
        fig = plt.figure(); t = fig.text(0.5, 0.5, "x")
        assert mc.to_hex(t.get_color()) == "#632520"


def test_colibri():
    import matplotlib.colors as mc
    for key in ("colibri", "colibri-dark"):
        assert len(rhdt_mpl.PALETTES[key]) == 8
        assert set(rhdt_mpl.SOURCES[key]) == set(rhdt_mpl.PALETTES[key])      # every color has its source
    assert not set(rhdt_mpl.PALETTES["colibri"]) & set(rhdt_mpl.PALETTES["colibri-dark"])  # the dark colors have names of their own
    assert list(rhdt_mpl.PARTNERS.values()) == list(rhdt_mpl.PALETTES["colibri"])          # partners in the order of colibri
    assert list(rhdt_mpl.PARTNERS) == list(rhdt_mpl.PALETTES["colibri-dark"])
    assert rhdt_mpl.PARTNERS["garnet"] == "ruby" and mc.to_hex("rhdt:colibri-dark:garnet") == "#632520"
    assert list(rhdt_mpl.PALETTES["colibri"])[:2] == ["emerald", "tourmaline"]
    assert mc.to_hex("rhdt:colibri:emerald") == "#00a543"                       # the nearest P3 color of one outside P3
    assert rhdt_mpl.wide_css("colibri", "emerald").startswith("oklch(0.61")
    assert rhdt_mpl.wide_css("colibri", "ruby") is None                         # outside sRGB, but inside Display P3: exact
    assert set(rhdt_mpl.WIDE["colibri"]) == {"emerald", "sapphire", "jade"}
    stand = [h for k in ("colibri", "colibri-dark") for h in rhdt_mpl.PALETTES[k].values()]
    assert len(set(stand)) == 16                                                # stand-ins are distinct
    # every bright color is visible on white (WCAG contrast of at least 3:1)
    cs = rhdt_mpl.colorspace
    for h in rhdt_mpl.PALETTES["colibri"].values():
        lin = cs.linear_to_srgb_linear(cs.decode(mc.to_rgb(h)), "display-p3")      # luminance from linear sRGB weights
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
        assert list(rhdt_mpl.PALETTES[key]) == ["gorget", "crown", "mantle", "rump"]
    assert mc.to_hex("rhdt:ruby-topaz:gorget") == "#f28f2f"          # a measured spectrum, in Display P3
    assert rhdt_mpl.palette("sapphire", ["gorget", "rump"]) == ["#0242b7", "#8c4a28"]
    for gone in ("anna", "ruby-throated", "rufous", "costa", "crimson-topaz", "sparkling-violetear"):
        assert gone not in rhdt_mpl.PALETTES


def test_default_cycle_is_colibri():
    import matplotlib as mpl
    rhdt_mpl.use(backend=False)
    assert mpl_cycle() == list(rhdt_mpl.PALETTES["colibri"].values())


def _pdf_streams(path):
    import re, zlib
    data = open(path, "rb").read()
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        try:
            yield zlib.decompress(m.group(1))
        except zlib.error:
            yield m.group(1)


def test_p3_colors_reach_the_pdf():
    import re
    import matplotlib.colors as mc
    fig, ax = plt.subplots(figsize=(2, 1.5))
    ax.plot([0, 1], [0, 1], color="rhdt:ruby", lw=4)
    path = os.path.join(tempfile.mkdtemp(), "p3.pdf")
    fig.savefig(path)
    plt.close(fig)
    streams = list(_pdf_streams(path))
    profiles = [s for s in streams if s[36:40] == b"acsp"]
    assert len(profiles) == 2                                 # umbruch's own sRGB profile and the Display P3 one
    ruby = mc.to_rgb("rhdt:ruby")
    found = [tuple(float(v) for v in m.groups()) for s in streams
             for m in re.finditer(rb"([\d.]+) ([\d.]+) ([\d.]+) SC", s)]
    assert any(max(abs(a - b) for a, b in zip(c, ruby)) < 2e-3 for c in found), (found, ruby)


def test_srgb_opt_out():
    import matplotlib as mpl, matplotlib.colors as mc
    import umbruch_matplotlib as um
    try:
        rhdt_mpl.use(backend=False, color_space="srgb")
        assert um.config.color_space == "srgb"
        assert rhdt_mpl.palette("ok6") == list(rhdt_mpl.PALETTES["ok6"].values())            # native: unchanged
        assert rhdt_mpl.palette("colibri")[5] != rhdt_mpl.PALETTES["colibri"]["ruby"]        # P3 colors converted
        assert mc.to_hex("rhdt:colibri:ruby") == rhdt_mpl.palette("colibri", ["ruby"])[0]
        for h in rhdt_mpl.palette("colibri"):
            assert all(0 <= v <= 1 for v in mc.to_rgb(h))                                    # inside sRGB
        assert mpl.colormaps["ok_blue"](0.5)[:3] != rhdt_mpl.okmaps.COLORMAPS["ok_blue"](0.5)[:3]
    finally:
        rhdt_mpl.use(backend=False)
    assert rhdt_mpl.colorspace.current() == "display-p3" and um.config.color_space == "display-p3"


def test_from_srgb_converts_names_and_hex():
    import numpy as np
    assert np.allclose(rhdt_mpl.from_srgb("white"), 1) and np.allclose(rhdt_mpl.from_srgb("#808080")[:3], 128 / 255)
    r = rhdt_mpl.from_srgb("red")                           # sRGB red is not saturated in Display P3
    assert 0.9 < r[0] < 1 and 0.1 < r[1] < 0.3
    assert np.allclose(rhdt_mpl.from_srgb("red", "srgb"), (1, 0, 0, 1))
    assert np.shape(rhdt_mpl.from_srgb(["red", "blue"])) == (2, 4)


def test_readme_lists_all_named_colors():
    import os
    readme = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")).read()
    rows = [l for l in readme.splitlines() if l.startswith("| <img")]
    expected = sum(len(p) for p in rhdt_mpl.PALETTES.values())
    assert len(rows) == expected, (len(rows), expected)          # regenerate with examples/make_color_table.py
    for palette, colors in rhdt_mpl.PALETTES.items():
        for name, hexv in colors.items():
            assert any(f"`rhdt:{palette}:{name}` | `{hexv.lower()}`" in r for r in rows), (palette, name)


DIVERGING = {"ok_green_magenta": (146, 324), "ok_ruby_sapphire": (12.4, 238.6)}      # name: hues of the two ends


def test_colormaps():
    import matplotlib as mpl
    import numpy as np
    assert mpl.rcParams["image.cmap"] == "ok_orchid"
    from rhdt_mpl import okmaps
    cs = rhdt_mpl.colorspace
    assert len(okmaps.COLORMAPS) == 13
    for n, cm in okmaps.COLORMAPS.items():
        for m in (n, n + "_r"):
            assert m in mpl.colormaps and mpl.colormaps[m].N == 256
        assert np.allclose(mpl.colormaps[n].colors, cm.colors)           # registered as they are in a P3 figure
        t = np.array(cm.colors)
        assert t.min() >= 0 and t.max() <= 1
        L = cs.rgb_to_oklab(t, "display-p3")[:, 0]
        if n in DIVERGING:                                                # diverging: dark -> light center -> dark
            assert np.all(np.diff(L[:128]) > 0) and np.all(np.diff(L[128:]) < 0)
        else:
            assert np.all(np.diff(L) > 0)                                 # dark -> light
    # native to P3: they use colors outside sRGB (some of their entries have a negative sRGB channel)
    outside = {}
    for n, cm in okmaps.COLORMAPS.items():
        lin = cs.linear_to_srgb_linear(cs.decode(np.array(cm.colors)), "display-p3")
        outside[n] = int(((lin < -1e-3) | (lin > 1 + 1e-3)).any(axis=1).sum())          # entries outside sRGB
    print(outside)
    assert sum(outside.values()) > 0
    assert outside["ok_orchid"] > 100                                         # the default map really uses the room of P3


def test_diverging_maps():
    for name, hues in DIVERGING.items():
        _check_diverging(name, hues)


def _check_diverging(name, hues):
    import numpy as np
    import matplotlib as mpl
    cs = rhdt_mpl.colorspace
    t = np.array(rhdt_mpl.okmaps.COLORMAPS[name].colors)
    lab = cs.rgb_to_oklab(t, "display-p3")
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    hue = np.degrees(np.arctan2(lab[:, 2], lab[:, 1])) % 360
    assert lab[127, 0] > 0.97 and chroma[127] < 0.02 and chroma[128] < 0.02      # a near-white center
    assert abs(lab[0, 0] - lab[-1, 0]) < 0.01 and 0.5 < lab[0, 0] < 0.6          # ends equally light
    assert abs(hue[0] - hues[0]) < 3 and abs(hue[-1] - hues[1]) < 3               # the two end hues
    assert chroma[0] > 0.15 and chroma[-1] > 0.15                                 # vivid (blue is limited by the gamut)
    for arm in (lab[:128], lab[128:]):                                            # nearly equal perceptual steps along an arm
        step = np.linalg.norm(np.diff(arm, axis=0), axis=1)[:-1]
        assert step.max() / step.min() < 1.15      # the gamut boundary of P3 bends the path a little
    r = mpl.colormaps[name + "_r"]
    assert np.allclose(r.colors, t[::-1])


def test_spiral_maps():
    import numpy as np
    cs = rhdt_mpl.colorspace
    for name in ("ok_ember", "ok_lagoon"):
        t = np.array(rhdt_mpl.okmaps.COLORMAPS[name].colors)
        lab = cs.rgb_to_oklab(t, "display-p3")
        L, chroma = lab[:, 0], np.hypot(lab[:, 1], lab[:, 2])
        x = np.linspace(0, 1, len(L))
        assert abs(L[0] - 0.25) < 0.02 and abs(L[-1] - 0.96) < 0.02
        assert np.abs(L - np.polyval(np.polyfit(x, L, 1), x)).max() < 0.05        # lightness close to a straight line
        step = np.linalg.norm(np.diff(lab, axis=0), axis=1)
        assert step.max() / step.min() < 1.05                                      # equal steps of OKLab distance
        assert chroma.mean() > 0.11 and chroma.max() > 0.17                        # high chroma (viridis peaks at 0.19)
        lin = cs.linear_to_srgb_linear(cs.decode(t), "display-p3")
        assert ((lin < -1e-3) | (lin > 1 + 1e-3)).any(axis=1).sum() > 100          # much of it outside sRGB


def test_orchid_pink_is_not_squeezed():
    """Hue 335 deg (magenta-pink) is reached at 40 % of ok_orchid, not at half."""
    import numpy as np
    cs = rhdt_mpl.colorspace
    lab = cs.rgb_to_oklab(np.array(rhdt_mpl.okmaps.COLORMAPS["ok_orchid"].colors), "display-p3")
    hue = np.degrees(np.arctan2(lab[:, 2], lab[:, 1])) % 360
    first = int(np.argmax((hue > 335) | (hue < 90)))
    assert 0.37 < first / 255 < 0.43, first / 255


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("rhdt_mpl tests ok")
