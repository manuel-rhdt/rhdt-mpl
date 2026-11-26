"""Ruby-throated hummingbird (Archilochus colubris), male in flight, drawn by hand in SVG in the same pose as
draw_anna.py, so that the two read as a pair.

The anatomy (body, head, wing, feet) is Anna's; the markings and colors follow a reference photograph of a
ruby-throated hummingbird (not needed to run this): orange-red gorget over a dark chin, white collar, grey-olive
crown, olive back and flanks, buff belly, mauve-brown wing and a dark forked tail with a purple sheen.
Coordinates are those of a 491 x 400 frame.

    python examples/draw_ruby_throated.py          # writes docs/birds/ruby-throated.svg
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_anna as A                          # noqa: E402
from draw_anna import smooth, lin, scales      # noqa: E402
from rhdt_mpl import oklab                     # noqa: E402
from rhdt_mpl.palettes import PALETTES         # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds", "ruby-throated.svg")
P = PALETTES["ruby-throated"]
L, D, M = oklab.lighten, oklab.darken, oklab.mix

# ------------------------------------------------------------------ shapes: Anna's anatomy, ruby-throated markings
BODY, WING, COVERTS, BILL, EYE, FEET, PRIMARIES = A.BODY, A.WING, A.COVERTS, A.BILL, A.EYE, A.FEET, A.PRIMARIES
CROWN = [(62, 34), (84, 21), (111, 21), (134, 27), (150, 42), (156, 60), (140, 52), (118, 40), (92, 38), (70, 42)]
FACE = [(60, 44), (84, 38), (106, 40), (122, 44), (130, 54), (124, 62), (108, 64), (90, 62), (72, 60), (61, 56)]
CHIN = [(62, 56), (80, 60), (98, 63), (90, 70), (74, 70), (64, 66)]               # dark chin line under the bill
GORGET = [(66, 64), (92, 64), (118, 66), (140, 64), (154, 60), (162, 78), (166, 98), (162, 114), (146, 120),
          (124, 116), (102, 112), (84, 106), (72, 94), (66, 80)]
COLLAR = [(66, 96), (80, 108), (104, 116), (128, 121), (150, 124), (166, 118), (172, 134), (160, 150),
          (128, 156), (98, 154), (76, 146), (66, 128)]
BELLY = [(64, 140), (96, 150), (128, 154), (160, 148), (166, 176), (156, 214), (140, 244), (124, 262), (104, 254),
         (86, 230), (74, 200), (66, 170)]
FLANK = [(118, 150), (150, 130), (178, 130), (202, 148), (220, 182), (229, 222), (233, 262), (226, 282), (206, 284),
         (184, 272), (164, 256), (146, 236), (136, 210), (130, 182), (124, 162)]
LOWER = [(94, 236), (116, 244), (140, 256), (166, 266), (180, 282), (172, 294), (148, 296), (126, 288), (106, 270)]
# forked tail: outer feathers longer than the central ones
TAIL = [((214, 300), (262, 394), 24), ((238, 300), (292, 382), 24), ((222, 302), (264, 360), 22),
        ((230, 302), (276, 360), 22)]


def feather(base, tip, width, tip_round=0.35):
    """Control points of a feather from *base* to *tip* with a rounded tip."""
    (bx, by), (tx, ty) = base, tip
    ux, uy = tx - bx, ty - by
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    px, py, w = -uy, ux, width / 2
    pts = [(bx + px * w * 0.8, by + py * w * 0.8), (bx + ux * n * 0.5 + px * w, by + uy * n * 0.5 + py * w),
           (tx - ux * w * tip_round + px * w * 0.8, ty - uy * w * tip_round + py * w * 0.8), (tx, ty),
           (tx - ux * w * tip_round - px * w * 0.8, ty - uy * w * tip_round - py * w * 0.8),
           (bx + ux * n * 0.5 - px * w, by + uy * n * 0.5 - py * w), (bx - px * w * 0.8, by - py * w * 0.8)]
    return [(round(x, 1), round(y, 1)) for x, y in pts]


def draw():
    g = P["gorget"]
    olive = P["back"]
    sparkle = M(olive, "#c8c050", .55)
    defs = [
        lin("gorget", [(0, L(g, .08)), (0.4, g), (0.8, D(g, .1)), (1, D(g, .2))], 70, 62, 166, 122),
        lin("crown", [(0, M(P["crown"], olive, .4)), (1, D(M(P["crown"], olive, .5), .06))], 62, 20, 156, 60),
        lin("face", [(0, D(P["crown"], .3)), (1, D(P["crown"], .22))], 60, 40, 130, 64),
        lin("collar", [(0, P["collar"]), (1, D(P["collar"], .05))], 66, 100, 172, 156),
        lin("belly", [(0, L(P["belly"], .03)), (1, D(P["belly"], .06))], 70, 140, 160, 260),
        lin("flank", [(0, L(olive, .04)), (0.5, olive), (1, D(olive, .12))], 120, 135, 225, 280),
        lin("lower", [(0, P["belly"]), (1, D(P["belly"], .08))], 96, 236, 178, 296),
        lin("body", [(0, P["belly"]), (1, D(M(P["belly"], olive, .6), .06))], 70, 60, 240, 300),
        lin("wing", [(0, D(P["wing"], .2)), (0.3, D(P["wing"], .08)), (0.65, P["wing"]), (1, L(P["wing"], .06))],
            200, 140, 489, 130),
        lin("coverts", [(0, D(P["wing"], .26)), (1, D(P["wing"], .14))], 196, 120, 272, 168),
        lin("tail", [(0, D(M(P["tail"], P["bill"], .3), .1)), (0.6, D(P["tail"], .14)), (1, D(P["tail"], .24))],
            214, 300, 290, 392),
        lin("bill", [(0, D(P["bill"], .14)), (0.7, P["bill"]), (1, L(P["bill"], .06))], 70, 30, 2, 1),
        '<radialGradient id="vol" gradientUnits="userSpaceOnUse" cx="110" cy="130" r="190">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.14"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.26"/></radialGradient>',
        f'<clipPath id="c-body"><path d="{smooth(BODY)}"/></clipPath>',
        f'<clipPath id="c-flank"><path d="{smooth(FLANK)}"/></clipPath>',
        f'<clipPath id="c-gorget"><path d="{smooth(GORGET)}"/></clipPath>',
        f'<clipPath id="c-crown"><path d="{smooth(CROWN)}"/></clipPath>',
        '<filter id="soft" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2"/></filter>',
        '<filter id="blur1" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1"/></filter>',
        '<filter id="blur2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3"/></filter>',
    ]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 491 400" width="491" height="400">',
         "<defs>" + "".join(defs) + "</defs>"]
    # forked tail
    for base, tip, w in TAIL:
        s.append(f'<path d="{smooth(feather(base, tip, w))}" fill="url(#tail)" '
                 f'stroke="{M(L(P["tail"], .1), P["wing"], .4)}" stroke-width="1.2"/>')
        s.append(f'<path d="M{base[0]},{base[1]} L{tip[0]},{tip[1]}" stroke="{L(P["tail"], .1)}" '
                 f'stroke-width="0.9" opacity="0.6"/>')
    # body and plumage
    s.append(f'<path d="{BILL}" fill="url(#bill)"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#body)"/>')
    s.append('<g clip-path="url(#c-body)">')
    s.append(f'<path d="{smooth(BELLY)}" fill="url(#belly)" filter="url(#soft)"/>')
    s.append(f'<path d="{smooth(LOWER)}" fill="url(#lower)" filter="url(#soft)"/>')
    s.append(f'<path d="{smooth(FLANK)}" fill="url(#flank)" filter="url(#soft)"/>')
    s.append('<g clip-path="url(#c-flank)">' +
             scales((118, 128, 234, 286), D(olive, .16), seed=21) +
             scales((122, 134, 230, 280), sparkle, step=9, size=(1.4, 2.4), opacity=(0.25, 0.6), seed=22, width=0.9)
             + "</g>")
    s.append(f'<path d="{smooth(A.TUFT)}" fill="{P["collar"]}" filter="url(#blur2)" opacity="0.9"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#vol)"/>')
    # head
    s.append(f'<path d="{smooth(COLLAR)}" fill="url(#collar)" filter="url(#blur1)"/>')
    s.append(f'<path d="{smooth(CROWN)}" fill="url(#crown)" filter="url(#blur1)"/>')
    s.append('<g clip-path="url(#c-crown)">' +
             scales((60, 18, 160, 62), D(P["crown"], .18), step=5, size=(1.2, 2.2), opacity=(0.25, 0.6), seed=23,
                    width=0.9) +
             scales((60, 18, 160, 62), sparkle, step=8, size=(1, 1.8), opacity=(0.3, 0.7), seed=24, width=0.9) + "</g>")
    s.append(f'<path d="{smooth(FACE)}" fill="url(#face)" filter="url(#blur2)"/>')
    s.append(f'<path d="{smooth(GORGET)}" fill="url(#gorget)"/>')
    s.append('<g clip-path="url(#c-gorget)">' +
             scales((64, 60, 168, 124), L(g, .14), step=6, size=(1.8, 3.0), opacity=(0.3, 0.8), seed=25) +
             scales((64, 63, 168, 124), D(g, .16), step=6, size=(1.6, 2.6), opacity=(0.2, 0.5), seed=26, width=0.8)
             + "</g>")
    s.append(f'<path d="{smooth(CHIN)}" fill="{D(P["crown"], .36)}" filter="url(#blur1)"/>')
    s.append("</g>")
    ex, ey, er = EYE
    s += [f'<circle cx="{ex}" cy="{ey}" r="{er + 1.2}" fill="{D(P["crown"], .4)}"/>',
          f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="#0a0909"/>',
          f'<circle cx="{ex - 2.2}" cy="{ey - 2.3}" r="1.9" fill="#ffffff" opacity="0.9"/>',
          f'<ellipse cx="{ex + 13}" cy="{ey + 3}" rx="2.6" ry="1.7" fill="{P["collar"]}" opacity="0.85"/>']
    # wing
    s.append(f'<path d="{smooth(WING)}" fill="url(#wing)" opacity="0.96" filter="url(#blur1)"/>')
    s.append(f'<path d="{smooth(COVERTS)}" fill="url(#coverts)" filter="url(#blur1)"/>')
    s += [f'<path d="M{a[0]},{a[1]} Q{(a[0] + b[0]) / 2:.0f},{(a[1] + b[1]) / 2 - 6:.0f} {b[0]},{b[1]}" '
          f'stroke="{D(P["wing"], .2)}" stroke-width="1.1" fill="none" opacity="0.55"/>' for a, b in PRIMARIES]
    s.append(f'<path d="M200,128 C260,114 360,104 470,106" stroke="{D(P["wing"], .3)}" stroke-width="2" '
             f'fill="none" opacity="0.45"/>')
    # feet
    s += [f'<path d="{f}" stroke="{D(P["crown"], .4)}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
          for f in FEET]
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        fh.write(draw())
    print("wrote", OUT)
