import numpy as np
from rhdt_mpl import oklab as ok, okmaps


def close(a, b, tol=2e-4):
    return np.allclose(a, b, atol=tol)


def test_reference_values():
    # Ottosson's published values for sRGB red, white and black
    assert close(ok.to_oklab("#ff0000"), (0.62796, 0.22486, 0.12585), 1e-4)
    assert close(ok.to_oklab("#ffffff"), (1, 0, 0)) and close(ok.to_oklab("#000"), (0, 0, 0))


def test_round_trip_and_gamut():
    rng = np.random.default_rng(0)
    for _ in range(300):
        c = "#%02x%02x%02x" % tuple(rng.integers(0, 256, 3))
        assert ok.oklab(*ok.to_oklab(c)) == c
    L, C, h = ok.to_oklch(ok.oklch(0.7, 0.4, 30))      # far outside sRGB
    assert abs(L - 0.7) < 2e-3 and abs(h - 30) < 1.5 and C < 0.4


def test_adjustments():
    c = "#EE7733"
    L, C, h = ok.to_oklch(c)
    assert ok.lightness(ok.lighten(c, 0.1)) > L > ok.lightness(ok.darken(c, 0.1))
    m = ok.to_oklch(ok.muted(c))
    assert m[1] < 0.6 * C and m[0] > L and abs(m[2] - h) < 2
    assert abs((ok.to_oklch(ok.rotate_hue(c, 40))[2] - h - 40) % 360) < 2
    assert ok.mix("#EE7733", "#0077BB", 0) == "#ee7733" and ok.mix("#EE7733", "#0077BB", 1) == "#0077bb"
    assert ok.rotate_hue("#808080", 90) == "#808080"


def test_family_is_ordered_in_lightness_with_constant_hue():
    f = ok.family("#33BBEE", 4)
    Ls = [ok.lightness(c) for c in f]
    assert Ls == sorted(Ls) and Ls[-1] - Ls[0] > 0.2
    hs = [ok.to_oklch(c)[2] for c in f]
    assert max(hs) - min(hs) < 3


def test_agrees_with_colormap_design_lightness():
    t = okmaps.COLORMAPS["ok_orchid"].colors
    assert abs(ok.lightness(t[0]) - 0.20) < 5e-3 and abs(ok.lightness(t[-1]) - 0.96) < 5e-3


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("oklab tests ok")
