"""Anna's hummingbird (Calypte anna), male in flight, drawn by hand in SVG.

Every part is a closed smooth curve (Catmull-Rom through the points below, converted to cubic Beziers),
filled with gradients and given feather texture.  The control points were placed by hand on a reference
photograph; the photograph is not needed to run this.  Coordinates are those of a 491 x 400 frame.

    python examples/draw_anna.py            # writes docs/birds/anna.svg
"""
import os
import random

from rhdt_mpl import oklab
from rhdt_mpl.palettes import PALETTES

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds", "anna.svg")
P = PALETTES["anna"]
L, D, M = oklab.lighten, oklab.darken, oklab.mix

# ------------------------------------------------------------------ shapes (hand-placed control points)
BODY = [(64, 26), (88, 20), (111, 22), (132, 29), (147, 42), (154, 60), (157, 90), (170, 112), (186, 128),
        (210, 150), (226, 190), (232, 230), (238, 272), (244, 300), (220, 310), (196, 310), (170, 300),
        (150, 296), (128, 290), (104, 262), (84, 228), (72, 190), (66, 150), (63, 110), (61, 75), (60, 48)]
CROWN = [(64, 31), (85, 21), (111, 21), (132, 27), (147, 41), (130, 38), (110, 36), (88, 36), (70, 40)]
FACE = [(61, 40), (84, 35), (106, 36), (122, 40), (128, 50), (124, 60), (110, 63), (92, 61), (74, 60), (63, 57)]
BEHIND_EYE = [(124, 38), (138, 36), (149, 44), (154, 58), (148, 64), (134, 63), (126, 56), (127, 46)]
GORGET = [(82, 58), (104, 62), (124, 66), (142, 64), (153, 61), (160, 80), (165, 100), (167, 120), (150, 125),
          (128, 122), (106, 120), (88, 116), (76, 104), (71, 86), (70, 68)]
FRINGE = [(63, 57), (82, 59), (79, 80), (78, 100), (86, 117), (74, 113), (66, 97), (63, 77)]
CHEST = [(66, 112), (100, 118), (130, 124), (162, 124), (172, 140), (162, 180), (150, 215), (130, 236), (108, 240),
         (88, 232), (76, 205), (68, 170), (64, 140)]
GREEN = [(118, 142), (150, 128), (178, 130), (202, 148), (220, 182), (229, 222), (233, 262), (226, 282), (206, 284),
         (184, 272), (160, 262), (140, 250), (118, 236), (108, 214), (110, 182), (114, 160)]
BUFF = [(94, 220), (116, 230), (140, 248), (166, 262), (178, 278), (172, 293), (148, 295), (126, 287), (107, 266),
        (97, 244)]
TUFT = [(186, 284), (198, 278), (212, 280), (224, 288), (216, 293), (204, 296), (192, 295)]
TAIL = [(204, 300), (226, 297), (246, 304), (262, 334), (276, 366), (284, 390), (277, 397), (262, 385), (240, 358),
        (218, 330), (204, 316)]
WING = [(196, 128), (232, 118), (300, 112), (402, 105), (470, 106), (486, 113), (489, 130), (484, 147), (470, 166),
        (420, 171), (360, 179), (300, 191), (256, 206), (230, 219), (214, 196), (206, 168), (198, 146)]
COVERTS = [(196, 128), (232, 118), (264, 121), (272, 138), (252, 153), (226, 161), (210, 168), (200, 150)]
BILL = "M70,28 C48,19 24,9 2,1 C22,11 44,25 68,43 Z"
EYE = (117.5, 49.0, 6.6)
FEET = ["M122,288 C118,296 124,302 131,299", "M126,290 C124,298 131,302 136,297",
        "M152,292 C149,300 156,305 162,301", "M157,293 C155,301 162,304 167,299"]
PRIMARIES = [((240, 150), (486, 140)), ((240, 152), (470, 163)), ((238, 156), (420, 170)), ((236, 160), (360, 178)),
             ((232, 166), (300, 190)), ((236, 146), (480, 118))]
TAIL_LINES = [((222, 302), (276, 380)), ((232, 302), (281, 388)), ((214, 306), (262, 376))]


def smooth(points, tension=0.5):
    """Closed Catmull-Rom curve through *points* as an SVG path."""
    n = len(points)
    d = [f"M{points[0][0]},{points[0][1]}"]
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]},{p2[1]}")
    return "".join(d) + "Z"


def lin(gid, stops, x1, y1, x2, y2):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f"{s}</linearGradient>")


def scales(region_bbox, color, step=6, size=(2.0, 3.4), opacity=(0.35, 0.85), seed=1, width=1.1):
    """Crescent feather marks in a jittered grid over *region_bbox* (x0, y0, x1, y1)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = region_bbox
    out = []
    for y in range(y0, y1, step):
        off = (y // step) % 2 * step / 2
        for x in range(int(x0 + off), x1, step):
            jx, jy, w, o = rnd.uniform(-1.6, 1.6), rnd.uniform(-1.4, 1.4), rnd.uniform(*size), rnd.uniform(*opacity)
            cx, cy = x + jx, y + jy
            out.append(f'<path d="M{cx - w:.1f},{cy:.1f} Q{cx:.1f},{cy + w * 1.1:.1f} {cx + w:.1f},{cy:.1f}" '
                       f'opacity="{o:.2f}"/>')
    return (f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round">' + "".join(out) + "</g>")


def draw():
    g = P["gorget"]
    defs = [
        lin("gorget", [(0, L(g, .1)), (0.35, g), (0.75, D(g, .1)), (1, D(g, .2))], 80, 60, 165, 125),
        lin("fringe", [(0, L(P["gold"], .08)), (0.5, P["gold"]), (1, M(D(P["gold"], .12), P["back"], .5))], 64, 58, 86, 118),
        lin("crown", [(0, M(P["crown"], P["gold"], .3)), (0.45, P["crown"]), (1, M(P["crown"], g, .45))], 64, 22, 147, 40),
        lin("behind", [(0, M(P["crown"], g, .5)), (0.6, D(g, .04)), (1, D(g, .16))], 124, 36, 154, 64),
        lin("face", [(0, M(P["bill"], P["gold"], .35)), (0.5, M(P["bill"], P["flank"], .45)), (1, M(P["bill"], P["flank"], .3))], 60, 36, 150, 66),
        lin("chest", [(0, L(P["belly"], .07)), (0.5, P["belly"]), (1, D(P["belly"], .08))], 70, 118, 150, 236),
        lin("green", [(0, L(P["back"], .1)), (0.45, P["back"]), (1, D(P["back"], .1))], 120, 135, 225, 280),
        lin("buff", [(0, L(P["flank"], .06)), (1, D(P["flank"], .06))], 96, 222, 176, 292),
        lin("body", [(0, P["belly"]), (1, M(P["belly"], P["back"], .6))], 70, 60, 240, 300),
        lin("wing", [(0, D(P["wing"], .14)), (0.25, D(P["wing"], .04)), (0.6, P["wing"]), (1, L(P["wing"], .08))], 200, 140, 489, 130),
        lin("coverts", [(0, D(P["wing"], .2)), (1, D(P["wing"], .1))], 196, 120, 272, 168),
        lin("tail", [(0, M(P["bill"], P["flank"], .55)), (0.5, M(P["bill"], P["flank"], .4)), (1, P["bill"])], 205, 300, 284, 395),
        lin("bill", [(0, "#2a2824"), (0.7, P["bill"]), (1, "#4a4640")], 70, 30, 2, 1),
        '<radialGradient id="vol" gradientUnits="userSpaceOnUse" cx="110" cy="130" r="190">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.16"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.28"/></radialGradient>',
        f'<clipPath id="c-body"><path d="{smooth(BODY)}"/></clipPath>',
        f'<clipPath id="c-green"><path d="{smooth(GREEN)}"/></clipPath>',
        f'<clipPath id="c-gorget"><path d="{smooth(GORGET)}"/></clipPath>',
        f'<clipPath id="c-chest"><path d="{smooth(CHEST)}"/></clipPath>',
    ]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 491 400" width="491" height="400">',
         "<defs>" + "".join(defs) + "</defs>"]
    # tail
    s.append(f'<path d="{smooth(TAIL)}" fill="url(#tail)"/>')
    s += [f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="#7a6a55" stroke-width="1" opacity="0.6"/>'
          for a, b in TAIL_LINES]
    # body and its plumage, softly blended inside the body outline
    s.append(f'<path d="{BILL}" fill="url(#bill)"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#body)"/>')
    s.append('<g clip-path="url(#c-body)">')
    s.append(f'<path d="{smooth(CHEST)}" fill="url(#chest)"/>')
    s.append(f'<path d="{smooth(BUFF)}" fill="url(#buff)"/>')
    s.append(f'<path d="{smooth(GREEN)}" fill="url(#green)"/>')
    s.append(f'<g clip-path="url(#c-green)">' + scales((108, 128, 234, 286), D(P["back"], .16), seed=3) +
             scales((112, 134, 230, 280), L(P["back"], .12), step=9, size=(1.4, 2.4), opacity=(0.2, 0.5), seed=4, width=0.9)
             + "</g>")
    s.append('<g clip-path="url(#c-chest)">' + scales((64, 124, 170, 240), "#5e5a48", step=6, size=(1.2, 2.4),
                                                         opacity=(0.25, 0.6), seed=5, width=1.1) + "</g>")
    s.append(f'<path d="{smooth(TUFT)}" fill="{L(P['belly'], .32)}" opacity="0.95"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#vol)"/>')
    s.append("</g>")
    # head
    s.append('<g clip-path="url(#c-body)">')
    s.append(f'<path d="{smooth(FACE)}" fill="url(#face)"/>')
    s.append(f'<path d="{smooth(BEHIND_EYE)}" fill="url(#behind)"/>')
    s.append(f'<path d="{smooth(CROWN)}" fill="url(#crown)"/>')
    s.append(f'<path d="{smooth(FRINGE)}" fill="url(#fringe)"/>')
    s.append(f'<path d="{smooth(GORGET)}" fill="url(#gorget)"/>')
    s.append('<g clip-path="url(#c-gorget)">' + scales((68, 60, 168, 126), L(g, .16), step=6, size=(1.8, 3.0),
                                                          opacity=(0.3, 0.8), seed=6) +
             scales((68, 63, 168, 126), D(g, .14), step=6, size=(1.6, 2.6), opacity=(0.2, 0.5), seed=7, width=0.8)
             + "</g>")
    s.append("</g>")
    ex, ey, er = EYE
    s += [f'<circle cx="{ex}" cy="{ey}" r="{er + 1.2}" fill="#1c1814"/>',
          f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="#0a0909"/>',
          f'<circle cx="{ex - 2.2}" cy="{ey - 2.3}" r="1.9" fill="#ffffff" opacity="0.9"/>',
          f'<ellipse cx="{ex + 13}" cy="{ey + 2}" rx="2.6" ry="1.7" fill="#e8e4da" opacity="0.85"/>']
    # wing in front of the body
    s.append(f'<path d="{smooth(WING)}" fill="url(#wing)" opacity="0.95"/>')
    s.append(f'<path d="{smooth(COVERTS)}" fill="url(#coverts)"/>')
    s += [f'<path d="M{a[0]},{a[1]} Q{(a[0] + b[0]) / 2:.0f},{(a[1] + b[1]) / 2 - 6:.0f} {b[0]},{b[1]}" '
          f'stroke="#8f887c" stroke-width="1.1" fill="none" opacity="0.55"/>' for a, b in PRIMARIES]
    s.append('<path d="M200,128 C260,114 360,104 470,106" stroke="#6f685d" stroke-width="2" fill="none" opacity="0.45"/>')
    # feet
    s += [f'<path d="{f}" stroke="#2a2420" stroke-width="2.4" fill="none" stroke-linecap="round"/>' for f in FEET]
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        fh.write(draw())
    print("wrote", OUT)
