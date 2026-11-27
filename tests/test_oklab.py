import numpy as np
import pytest
from rhdt_mpl import colorspace as cs, oklab as ok, okmaps


@pytest.fixture(autouse=True)
def srgb():
    """The reference values below are sRGB ones."""
    with cs.using("srgb"):
        yield


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
    t = okmaps.COLORMAPS["ok_orchid"].colors          # Display P3 numbers
    with cs.using("display-p3"):
        assert abs(ok.lightness(t[0]) - 0.20) < 5e-3 and abs(ok.lightness(t[-1]) - 0.96) < 5e-3


def test_display_p3():
    with cs.using("display-p3"):
        assert close(ok.to_oklab("#ffffff"), (1, 0, 0)) and close(ok.to_oklab("#808080"), ok_gray)
        # P3 red is more saturated than sRGB red, and the maximum chroma of a hue is larger
        assert ok.to_oklch("#ff0000")[1] > 0.27
        L, C, h = ok.to_oklch(ok.oklch(0.7, 0.4, 30))
        assert abs(L - 0.7) < 2e-3 and abs(h - 30) < 1.5 and 0.23 < C < 0.4
        assert ok.oklab(*ok.to_oklab("#12ab34")) == "#12ab34"
    with cs.using("srgb"):
        assert ok.to_oklch(ok.oklch(0.7, 0.4, 30))[1] < 0.23         # the same request, less room in sRGB


ok_gray = (0.5999, 0, 0)         # gray 128/255: the transfer function is the same in both spaces


def test_conversion_between_spaces():
    import numpy as np
    g = np.array([[0.2, 0.2, 0.2], [0.5, 0.5, 0.5], [1, 1, 1]])
    assert np.allclose(cs.convert(g, "srgb", "display-p3"), g, atol=1e-6)      # same white point and transfer function
    rng = np.random.default_rng(1)
    s = rng.random((200, 3))
    p3 = cs.convert(s, "srgb", "display-p3")
    assert p3.min() >= 0 and p3.max() <= 1 and np.allclose(cs.convert(p3, "display-p3", "srgb"), s, atol=1e-6)
    assert np.allclose(cs.rgb_to_oklab(s, "srgb"), cs.rgb_to_oklab(p3, "display-p3"), atol=1e-6)   # the same colors
    out = cs.convert([[0.0, 1.0, 0.0]], "display-p3", "srgb")                   # P3 green is outside sRGB
    assert out.min() >= 0 and out.max() <= 1
    a, b = cs.rgb_to_oklab([0.0, 1.0, 0.0], "display-p3"), cs.rgb_to_oklab(out[0], "srgb")
    assert abs(a[0] - b[0]) < 2e-3 and abs(np.arctan2(a[2], a[1]) - np.arctan2(b[2], b[1])) < 0.02   # lightness and hue kept


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
    print("oklab tests ok")
