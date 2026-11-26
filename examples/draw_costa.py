"""Costa's hummingbird (Calypte costae), male, drawn by hand in SVG in the same pose as draw_anna.py.

The anatomy is Anna's; the markings and colors follow two reference photographs of perched Costa's hummingbirds (not
needed to run this): violet crown and gorget, the gorget's long flares down the sides of the neck, a dark face, pale
lavender-grey chest, sage-green back and flanks, a mottled belly, dusky wing and near-black tail with pale bars.
Coordinates are those of a 491 x 400 frame.

    python examples/draw_costa.py          # writes docs/birds/costa.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_anna as A                          # noqa: E402
import draw_ruby_throated as R                 # noqa: E402
from draw_anna import smooth, lin, scales      # noqa: E402
from rhdt_mpl import oklab                     # noqa: E402
from rhdt_mpl.palettes import PALETTES         # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds", "costa.svg")
P = PALETTES["costa"]
L, D, M = oklab.lighten, oklab.darken, oklab.mix

BODY, WING, COVERTS, BILL, EYE, FEET, PRIMARIES = A.BODY, A.WING, A.COVERTS, A.BILL, A.EYE, A.FEET, A.PRIMARIES
CROWN, GORGET, CHEST = R.CROWN, R.GORGET, A.CHEST
FACE = [(60, 44), (80, 40), (100, 44), (116, 50), (124, 60), (114, 66), (96, 66), (76, 64), (62, 58)]
FLARE = [(144, 78), (162, 82), (176, 108), (186, 146), (192, 196), (182, 180), (168, 150), (154, 120), (146, 98)]
BELLY = [(84, 180), (110, 172), (140, 168), (172, 172), (210, 190), (230, 226), (234, 262), (226, 284), (200, 290),
         (170, 292), (140, 290), (114, 276), (96, 250), (86, 216)]
TAIL = [((214, 300), (264, 392), 26), ((236, 300), (288, 384), 26), ((224, 302), (279, 394), 26)]


def draw():
    g, fl = P["gorget"], P["flare"]
    belly = M(P["chest"], P["back"], .4)
    dark = M(P["tail"], fl, .25)
    defs = [
        lin("gorget", [(0, M(dark, g, .35)), (0.3, g), (0.65, L(g, .06)), (1, M(g, fl, .6))], 66, 62, 166, 118),
        lin("flare", [(0, M(g, fl, .4)), (1, D(fl, .06))], 146, 78, 192, 196),
        lin("crown", [(0, P["crown"]), (0.5, M(P["crown"], g, .35)), (1, M(P["crown"], g, .7))], 62, 20, 156, 60),
        lin("face", [(0, dark), (1, M(dark, P["wing"], .3))], 60, 40, 124, 66),
        lin("body", [(0, P["chest"]), (0.5, M(P["chest"], belly, .5)), (1, D(belly, .08))], 70, 60, 240, 300),
        lin("chest", [(0, L(P["chest"], .05)), (1, P["chest"])], 70, 118, 150, 236),
        lin("belly", [(0, belly), (1, D(belly, .1))], 90, 170, 230, 290),
        lin("green", [(0, L(P["back"], .08)), (0.45, P["back"]), (1, D(P["back"], .12))], 120, 135, 225, 280),
        f'<clipPath id="c-green"><path d="{smooth(A.GREEN)}"/></clipPath>',
        lin("wing", [(0, D(P["wing"], .1)), (0.4, P["wing"]), (0.8, L(P["wing"], .06)), (1, L(P["wing"], .1))],
            200, 140, 489, 130),
        lin("coverts", [(0, D(P["wing"], .14)), (1, D(P["wing"], .06))], 196, 120, 272, 168),
        lin("tail", [(0, M(P["tail"], P["wing"], .35)), (0.5, P["tail"]), (1, D(P["tail"], .02))], 214, 300, 288, 392),
        lin("bill", [(0, P["bill"]), (0.7, L(P["bill"], .06)), (1, L(P["bill"], .14))], 70, 30, 2, 1),
        '<radialGradient id="vol" gradientUnits="userSpaceOnUse" cx="110" cy="130" r="190">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.14"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.24"/></radialGradient>',
        f'<clipPath id="c-body"><path d="{smooth(BODY)}"/></clipPath>',
        f'<clipPath id="c-gorget"><path d="{smooth(GORGET)}"/></clipPath>',
        f'<clipPath id="c-crown"><path d="{smooth(CROWN)}"/></clipPath>',
        f'<clipPath id="c-flare"><path d="{smooth(FLARE)}"/></clipPath>',
    ]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 491 400" width="491" height="400">',
         "<defs>" + "".join(defs) + "</defs>"]
    for base, tip, w in TAIL:
        s.append(f'<path d="{smooth(R.feather(base, tip, w))}" fill="url(#tail)" stroke="{L(P["tail"], .14)}" stroke-width="1"/>')
    for k in range(4):                                                     # pale bars on the tail
        t = 0.35 + 0.15 * k
        x0, y0 = 214 + (288 - 214) * t - 14, 300 + (392 - 300) * t
        s.append(f'<path d="M{x0:.0f},{y0 + 4:.0f} q14,-6 30,-4" stroke="{belly}" stroke-width="2.2" fill="none" '
                 f'opacity="0.35" stroke-linecap="round"/>')
    s.append(f'<path d="{BILL}" fill="url(#bill)"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#body)"/>')
    s.append('<g clip-path="url(#c-body)">')
    s.append(f'<path d="{smooth(CHEST)}" fill="url(#chest)"/>')
    s.append(f'<path d="{smooth(BELLY)}" fill="url(#belly)"/>')
    s.append(scales((80, 160, 240, 296), D(belly, .18), step=7, size=(1.6, 3), opacity=(0.25, 0.6), seed=41))
    s.append(f'<path d="{smooth(A.GREEN)}" fill="url(#green)"/>')
    s.append('<g clip-path="url(#c-green)">' + scales((108, 128, 234, 286), D(P["back"], .16), seed=47) +
             scales((112, 134, 230, 280), L(P["back"], .12), step=9, size=(1.4, 2.4), opacity=(0.2, 0.5), seed=48,
                    width=0.9) + "</g>")
    s.append(scales((64, 120, 180, 220), D(P["chest"], .14), step=6, size=(1.2, 2.2), opacity=(0.15, 0.4), seed=42, width=0.9))
    s.append(f'<path d="{smooth(A.TUFT)}" fill="{L(P["chest"], .1)}" opacity="0.95"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#vol)"/>')
    s.append(f'<path d="{smooth(CROWN)}" fill="url(#crown)"/>')
    s.append('<g clip-path="url(#c-crown)">' +
             scales((60, 18, 160, 62), L(P["crown"], .14), step=5, size=(1.2, 2.2), opacity=(0.3, 0.7), seed=43, width=0.9)
             + "</g>")
    s.append(f'<path d="{smooth(FACE)}" fill="url(#face)"/>')
    s.append(f'<path d="{smooth(FLARE)}" fill="url(#flare)"/>')
    s.append('<g clip-path="url(#c-flare)">' +
             scales((140, 76, 196, 200), L(fl, .16), step=6, size=(1.8, 3), opacity=(0.3, 0.75), seed=44) + "</g>")
    s.append(f'<path d="{smooth(GORGET)}" fill="url(#gorget)"/>')
    s.append('<g clip-path="url(#c-gorget)">' +
             scales((64, 60, 168, 124), L(g, .16), step=6, size=(1.8, 3.0), opacity=(0.3, 0.85), seed=45) +
             scales((64, 63, 168, 124), D(g, .2), step=6, size=(1.6, 2.6), opacity=(0.25, 0.55), seed=46, width=0.8)
             + "</g>")
    s.append("</g>")
    ex, ey, er = EYE
    s += [f'<circle cx="{ex}" cy="{ey}" r="{er + 1.2}" fill="{dark}"/>',
          f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="#0a0909"/>',
          f'<circle cx="{ex - 2.2}" cy="{ey - 2.3}" r="1.9" fill="#ffffff" opacity="0.9"/>',
          f'<path d="M{ex + 7},{ey - 4} q8,-1 14,4 q-7,0 -13,1 z" fill="{L(P["chest"], .08)}" opacity="0.9"/>']
    s.append(f'<path d="{smooth(WING)}" fill="url(#wing)" opacity="0.97"/>')
    s.append(f'<path d="{smooth(COVERTS)}" fill="url(#coverts)"/>')
    s += [f'<path d="M{a[0]},{a[1]} Q{(a[0] + b[0]) / 2:.0f},{(a[1] + b[1]) / 2 - 6:.0f} {b[0]},{b[1]}" '
          f'stroke="{D(P["wing"], .14)}" stroke-width="1.1" fill="none" opacity="0.6"/>' for a, b in PRIMARIES]
    s.append(f'<path d="M200,128 C260,114 360,104 470,106" stroke="{D(P["wing"], .2)}" stroke-width="2" fill="none" opacity="0.45"/>')
    s += [f'<path d="{f}" stroke="{P["tail"]}" stroke-width="2.4" fill="none" stroke-linecap="round"/>' for f in FEET]
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        fh.write(draw())
    print("wrote", OUT)
