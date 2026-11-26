"""Trace a photograph of a hummingbird (PNG with a transparent background) into an SVG illustration:
color regions found by k-means in OKLab, smoothed, outlined and filled with their median color.

    python examples/trace_hummingbird.py photo.png docs/birds/anna.svg [--k 14]

A reference tool: the trace shows the color regions and textures of a photograph, which are then drawn by hand
(see examples/draw_anna.py).  For a detailed trace: --k 40 --sigma 0.8 --min-area 8 --tol 0.35 --median 3.
"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure
from rhdt_mpl import oklab as ok


def to_lab(rgb):
    lin = ok._srgb_to_linear(rgb)
    lms = np.cbrt(lin @ ok._M1.T)
    return lms @ ok._M2.T


def kmeans(X, k, iters=40, seed=0):
    rng = np.random.default_rng(seed)
    C = [X[rng.integers(len(X))]]
    for _ in range(1, k):                                   # k-means++ initialisation
        d = np.min(((X[:, None, :] - np.array(C)[None]) ** 2).sum(-1), axis=1)
        C.append(X[rng.choice(len(X), p=d / d.sum())])
    C = np.array(C)
    for _ in range(iters):
        lab = np.argmin(((X[:, None, :] - C[None]) ** 2).sum(-1), axis=1)
        C = np.array([X[lab == j].mean(0) if np.any(lab == j) else C[j] for j in range(k)])
    return lab


def trace(png, k=14, spatial=0.15, sigma=1.6, min_area=40, tol=0.5, median=5):
    im = np.asarray(Image.open(png).convert("RGBA")).astype(float) / 255
    H, W = im.shape[:2]
    mask = ndimage.binary_erosion(im[..., 3] > 0.5, iterations=1)
    rgb = ndimage.median_filter(im[..., :3], size=(median, median, 1))  # calm the feather texture before clustering
    lab = to_lab(rgb)
    ys, xs = np.nonzero(mask)
    feats = np.column_stack([lab[ys, xs] * [1, 2, 2], spatial * xs / W, spatial * ys / H])
    labels = kmeans(feats, k)
    # smooth the label map: per-label blurred indicator, take the argmax inside the mask
    onehot = np.zeros((k, H, W))
    onehot[labels, ys, xs] = 1
    smooth = np.array([ndimage.gaussian_filter(o, sigma) for o in onehot])
    lmap = np.where(mask, smooth.argmax(0), -1)
    # small islands take the label of the nearest larger region
    for j in range(k):
        cc, n = ndimage.label(lmap == j)
        sizes = ndimage.sum(np.ones_like(cc), cc, range(1, n + 1))
        for i, sz in enumerate(sizes, 1):
            if sz < min_area:
                lmap[cc == i] = -2
    holes = lmap == -2
    if holes.any():
        _, (iy, ix) = ndimage.distance_transform_edt(holes | (lmap == -1) & False, return_indices=True)
        good = (lmap >= 0)
        _, (iy, ix) = ndimage.distance_transform_edt(~good, return_indices=True)
        lmap[holes] = lmap[iy[holes], ix[holes]]
    colors, regions = {}, []
    for j in range(k):
        sel = lmap == j
        if not sel.any():
            continue
        colors[j] = "#%02x%02x%02x" % tuple(np.round(np.median(im[..., :3][sel], axis=0) * 255).astype(int))
        field = ndimage.gaussian_filter(np.pad(sel.astype(float), 2), 0.8)
        subpaths = []
        for c in measure.find_contours(field, 0.5):
            c = measure.approximate_polygon(c, tol)
            if len(c) < 4:
                continue
            pts = " ".join(f"{x - 2:.1f},{y - 2:.1f}" for y, x in c)
            subpaths.append(f"M{pts}Z")
        regions.append((int(sel.sum()), colors[j], "".join(subpaths)))
    # silhouette
    sil = ndimage.gaussian_filter(np.pad(mask.astype(float), 2), 1.0)
    outline = "".join("M" + " ".join(f"{x - 2:.1f},{y - 2:.1f}" for y, x in measure.approximate_polygon(c, tol)) + "Z"
                      for c in measure.find_contours(sil, 0.5) if len(c) > 20)
    return W, H, mask, im, outline, sorted(regions, reverse=True)


def eye(im, mask, box):
    """Centre and radius of the darkest compact blob in *box* (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    L = to_lab(im[..., :3])[..., 0]
    dark = np.zeros_like(mask)
    dark[y0:y1, x0:x1] = (L[y0:y1, x0:x1] < 0.2) & mask[y0:y1, x0:x1]
    cc, n = ndimage.label(dark)
    if n == 0:
        return None
    sizes = ndimage.sum(dark, cc, range(1, n + 1))
    i = int(np.argmax(sizes)) + 1
    yy, xx = np.nonzero(cc == i)
    return xx.mean(), yy.mean(), max(2.5, np.sqrt(len(xx) / np.pi))


def svg(png, out, k=14, eye_box=None, **kw):
    W, H, mask, im, outline, regions = trace(png, k, **kw)
    base = max(regions)[1]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
         f'<path d="{outline}" fill="{base}"/>']
    for _, col, d in regions:
        s.append(f'<path d="{d}" fill="{col}" fill-rule="evenodd" stroke="{col}" stroke-width="0.7" stroke-linejoin="round"/>')
    if eye_box:
        e = eye(im, mask, eye_box)
        if e:
            ex, ey, r = e
            s += [f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r:.1f}" fill="#0b0a0a"/>',
                  f'<circle cx="{ex - r * 0.35:.1f}" cy="{ey - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#ffffff" opacity="0.9"/>']
    s.append("</svg>")
    with open(out, "w") as fh:
        fh.write("\n".join(s))
    return len(regions)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("png"); ap.add_argument("out"); ap.add_argument("--k", type=int, default=14)
    ap.add_argument("--eye", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--sigma", type=float, default=1.6); ap.add_argument("--min-area", type=int, default=40)
    ap.add_argument("--tol", type=float, default=0.5); ap.add_argument("--median", type=int, default=5)
    a = ap.parse_args()
    print(svg(a.png, a.out, a.k, a.eye, sigma=a.sigma, min_area=a.min_area, tol=a.tol, median=a.median), "regions")
