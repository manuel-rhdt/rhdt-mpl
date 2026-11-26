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
    test_backend_and_fonts("/tmp/claude-0/-home-user/b31222e4-7591-5457-af74-51ed8c3e5c07/scratchpad")
