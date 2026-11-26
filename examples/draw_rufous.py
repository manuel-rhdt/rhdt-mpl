"""Rufous hummingbird (Selasphorus rufus), male in flight, drawn by hand in SVG in the same pose as draw_anna.py.

The anatomy is Anna's; the markings and colors follow a reference photograph of a rufous hummingbird (not needed to
run this, and mirrored to face left): rufous head, back and flanks, a gorget from bronze at the chin to scarlet with a
flared rear edge, white bib and vent, pale lilac wing with rufous coverts, rufous tail with dark tips.
Coordinates are those of a 491 x 400 frame.

    python examples/draw_rufous.py          # writes docs/birds/rufous.svg
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw_anna as A                          # noqa: E402
import draw_ruby_throated as R                 # noqa: E402
from draw_anna import smooth, lin, scales      # noqa: E402
from rhdt_mpl import oklab                     # noqa: E402
from rhdt_mpl.palettes import PALETTES         # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds", "rufous.svg")
P = PALETTES["rufous"]
L, D, M = oklab.lighten, oklab.darken, oklab.mix

BODY, WING, COVERTS, BILL, EYE, FEET, PRIMARIES = A.BODY, A.WING, A.COVERTS, A.BILL, A.EYE, A.FEET, A.PRIMARIES
GORGET, COLLAR, CHIN = R.GORGET, R.COLLAR, R.CHIN
LORES = [(60, 44), (76, 42), (92, 46), (104, 54), (100, 64), (84, 66), (68, 62), (61, 54)]   # bronze lores and chin
FLARE = [(150, 70), (166, 76), (178, 92), (176, 112), (166, 118), (160, 100), (156, 84)]      # gorget feathers flared back
BELLY = R.BELLY
TAIL = [((214, 300), (266, 392), 26), ((236, 300), (288, 384), 26), ((224, 302), (280, 394), 26)]


def draw():
    g, br = P["gorget"], P["bronze"]
    rufous = P["back"]
    defs = [
        lin("gorget", [(0, br), (0.3, M(br, g, .45)), (0.6, g), (1, D(g, .14))], 66, 62, 166, 118),
        lin("flare", [(0, g), (1, D(g, .12))], 150, 70, 178, 118),
        lin("lores", [(0, D(br, .1)), (1, D(br, .2))], 60, 42, 104, 66),
        lin("head", [(0, L(P["crown"], .03)), (1, D(P["crown"], .06))], 62, 20, 156, 60),
        lin("bib", [(0, P["bib"]), (0.8, D(P["bib"], .04)), (1, M(P["bib"], rufous, .3))], 66, 100, 172, 156),
        lin("body", [(0, L(rufous, .04)), (0.5, rufous), (1, D(rufous, .1))], 70, 60, 240, 300),
        lin("belly", [(0, M(rufous, P["bib"], .35)), (1, M(rufous, P["bib"], .2))], 70, 140, 160, 260),
        lin("wing", [(0, M(P["wing"], rufous, .45)), (0.25, M(P["wing"], rufous, .15)), (0.6, P["wing"]),
                     (1, L(P["wing"], .05))], 200, 140, 489, 130),
        lin("coverts", [(0, D(rufous, .06)), (1, M(rufous, P["wing"], .4))], 196, 120, 272, 168),
        lin("tail", [(0, rufous), (0.6, D(rufous, .08)), (0.82, M(rufous, P["tip"], .6)), (1, P["tip"])],
            220, 300, 285, 392),
        lin("bill", [(0, D(P["bill"], .1)), (0.7, P["bill"]), (1, L(P["bill"], .08))], 70, 30, 2, 1),
        '<radialGradient id="vol" gradientUnits="userSpaceOnUse" cx="110" cy="130" r="190">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.14"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.24"/></radialGradient>',
        f'<clipPath id="c-body"><path d="{smooth(BODY)}"/></clipPath>',
        f'<clipPath id="c-gorget"><path d="{smooth(GORGET)}"/></clipPath>',
    ]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 491 400" width="491" height="400">',
         "<defs>" + "".join(defs) + "</defs>"]
    for base, tip, w in TAIL:
        s.append(f'<path d="{smooth(R.feather(base, tip, w))}" fill="url(#tail)" stroke="{D(rufous, .14)}" stroke-width="1"/>')
        s.append(f'<path d="M{base[0]},{base[1]} L{tip[0]},{tip[1]}" stroke="{D(rufous, .2)}" stroke-width="0.9" opacity="0.6"/>')
    s.append(f'<path d="{BILL}" fill="url(#bill)"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#body)"/>')
    s.append('<g clip-path="url(#c-body)">')
    s.append(f'<path d="{smooth(BELLY)}" fill="url(#belly)"/>')
    s.append(scales((64, 120, 240, 300), D(rufous, .14), step=7, size=(1.6, 3), opacity=(0.25, 0.6), seed=31))
    s.append(scales((64, 20, 160, 70), D(P["crown"], .12), step=5, size=(1.2, 2.2), opacity=(0.2, 0.5), seed=32, width=0.9))
    s.append(f'<path d="{smooth(A.TUFT)}" fill="{P["bib"]}" opacity="0.95"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#vol)"/>')
    s.append(f'<path d="{smooth(COLLAR)}" fill="url(#bib)"/>')
    s.append(f'<path d="{smooth(LORES)}" fill="url(#lores)"/>')
    s.append(f'<path d="{smooth(FLARE)}" fill="url(#flare)"/>')
    s.append(f'<path d="{smooth(GORGET)}" fill="url(#gorget)"/>')
    s.append('<g clip-path="url(#c-gorget)">' +
             scales((64, 60, 168, 124), L(g, .14), step=6, size=(1.8, 3.0), opacity=(0.3, 0.8), seed=33) +
             scales((64, 63, 168, 124), D(g, .18), step=6, size=(1.6, 2.6), opacity=(0.25, 0.55), seed=34, width=0.8)
             + "</g>")
    s.append(scales((150, 70, 180, 120), L(g, .12), step=6, size=(1.6, 2.6), opacity=(0.3, 0.7), seed=35))
    s.append("</g>")
    ex, ey, er = EYE
    s += [f'<circle cx="{ex}" cy="{ey}" r="{er + 1.2}" fill="{D(P["crown"], .35)}"/>',
          f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="#0a0909"/>',
          f'<circle cx="{ex - 2.2}" cy="{ey - 2.3}" r="1.9" fill="#ffffff" opacity="0.9"/>',
          f'<ellipse cx="{ex + 12}" cy="{ey + 2}" rx="4" ry="2.6" fill="{P["bib"]}" opacity="0.9"/>']
    s.append(f'<path d="{smooth(WING)}" fill="url(#wing)" opacity="0.96"/>')
    s.append(f'<path d="{smooth(COVERTS)}" fill="url(#coverts)"/>')
    s += [f'<path d="M{a[0]},{a[1]} Q{(a[0] + b[0]) / 2:.0f},{(a[1] + b[1]) / 2 - 6:.0f} {b[0]},{b[1]}" '
          f'stroke="{D(P["wing"], .16)}" stroke-width="1.1" fill="none" opacity="0.6"/>' for a, b in PRIMARIES]
    s.append(f'<path d="M200,128 C260,114 360,104 470,106" stroke="{D(P["wing"], .24)}" stroke-width="2" fill="none" opacity="0.45"/>')
    s += [f'<path d="{f}" stroke="{P["tip"]}" stroke-width="2.4" fill="none" stroke-linecap="round"/>' for f in FEET]
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        fh.write(draw())
    print("wrote", OUT)
