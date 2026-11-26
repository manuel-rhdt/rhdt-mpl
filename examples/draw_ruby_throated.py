"""Ruby-throated hummingbird (Archilochus colubris), male in flight, drawn by hand in SVG.

Same technique as draw_anna.py: smooth closed curves through hand-placed control points (placed on a reference
photograph, which is not needed to run this), gradients and feather texture, all colors from the palette.
Coordinates are those of a 941 x 1082 frame.

    python examples/draw_ruby_throated.py          # writes docs/birds/ruby-throated.svg
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw_anna import smooth, lin, scales      # noqa: E402
from rhdt_mpl import oklab                     # noqa: E402
from rhdt_mpl.palettes import PALETTES         # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds", "ruby-throated.svg")
P = PALETTES["ruby-throated"]
L, D, M = oklab.lighten, oklab.darken, oklab.mix

# ------------------------------------------------------------------ shapes (hand-placed control points)
BILL = "M556,70 C500,61 420,64 338,72 C420,75 500,81 556,94 Z"
HEAD = [(540, 92), (548, 52), (570, 22), (610, 4), (660, 0), (712, 6), (752, 30), (776, 72), (790, 112),
        (782, 136), (700, 130), (640, 118), (580, 112), (548, 108)]
CROWN = [(548, 52), (570, 22), (610, 4), (660, 0), (712, 6), (752, 30), (770, 62), (730, 48), (680, 40),
         (630, 38), (590, 44), (560, 58)]
GORGET = [(546, 112), (600, 118), (660, 126), (720, 132), (774, 118), (782, 150), (764, 196), (724, 228),
          (684, 248), (662, 268), (640, 256), (612, 248), (590, 232), (570, 200), (554, 160)]
COLLAR = [(570, 200), (600, 240), (640, 260), (662, 272), (690, 250), (730, 226), (770, 190), (790, 168),
          (802, 230), (780, 272), (700, 292), (620, 302), (590, 292), (575, 250)]
BODY = [(548, 108), (560, 150), (580, 230), (590, 300), (596, 380), (604, 460), (612, 520), (640, 560),
        (690, 600), (720, 650), (730, 720), (740, 800), (760, 850), (800, 860), (850, 820), (880, 740),
        (905, 660), (930, 600), (940, 520), (935, 440), (915, 360), (890, 300), (860, 240), (830, 190),
        (800, 140), (778, 110), (774, 70)]
BACK = [(778, 110), (800, 140), (830, 190), (860, 240), (890, 300), (915, 360), (935, 440), (940, 520),
        (930, 600), (905, 660), (884, 640), (892, 560), (882, 460), (862, 380), (832, 320), (804, 260),
        (792, 200), (784, 150)]
BELLY = [(640, 540), (700, 560), (760, 598), (830, 618), (882, 640), (902, 682), (882, 760), (852, 820),
         (802, 860), (762, 850), (742, 800), (732, 722), (714, 652), (682, 602), (642, 572)]
FLANK = [(600, 420), (640, 430), (662, 480), (656, 540), (630, 562), (608, 522)]
WING_L = [(572, 175), (530, 165), (450, 150), (380, 138), (300, 125), (200, 120), (120, 128), (60, 156),
          (24, 182), (4, 196), (24, 206), (60, 226), (100, 258), (200, 300), (300, 340), (400, 390), (480, 432), (540, 456),
          (576, 448), (598, 425), (600, 330), (590, 240)]
WING_L_FEATHERS = [((560, 300), (14, 202)), ((560, 310), (100, 256)), ((562, 318), (200, 298)),
                   ((566, 326), (300, 338)), ((570, 336), (400, 388)), ((574, 346), (480, 430)),
                   ((560, 230), (60, 170))]
WING_R = [(598, 300), (650, 272), (740, 262), (820, 268), (870, 286), (900, 330), (905, 400), (895, 470),
          (880, 520), (840, 538), (760, 530), (690, 512), (640, 488), (610, 450), (600, 380)]
WING_R_FEATHERS = [((620, 300), (880, 520)), ((640, 292), (900, 450)), ((660, 284), (902, 380)),
                   ((620, 320), (840, 536))]
TAIL_FAN = [((650, 575), (312, 698), 66), ((660, 618), (352, 782), 72), ((676, 660), (440, 856), 74),
            ((694, 696), (556, 885), 70), ((708, 726), (650, 886), 56)]
TAIL_FORK = [((862, 690), (852, 962), 58), ((828, 730), (838, 1004), 62), ((770, 750), (760, 1060), 62),
             ((800, 750), (800, 1080), 62)]
UNDERTAIL = [(655, 835), (690, 825), (712, 850), (705, 885), (675, 890), (655, 870)]
FEET = [  # (leg, toes) per foot
    ("M612,548 C606,570 606,596 612,620", ["M612,620 C614,632 622,640 632,636", "M612,622 C606,634 610,644 620,644"]),
    ("M752,598 C740,610 732,628 730,646", ["M730,646 C728,660 736,670 748,668", "M732,648 C720,656 716,670 726,676",
                                           "M736,644 C748,640 758,648 760,660"]),
]
EYE = (675.0, 80.0, 19.0)


def feather(base, tip, width, tip_round=0.55):
    """Control points of a long feather from *base* to *tip* with a rounded tip."""
    (bx, by), (tx, ty) = base, tip
    ux, uy = tx - bx, ty - by
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    px, py = -uy, ux                                      # normal
    w = width / 2
    pts = [(bx + px * w * 0.8, by + py * w * 0.8),
           (bx + ux * n * 0.5 + px * w, by + uy * n * 0.5 + py * w),
           (tx - ux * w * tip_round + px * w * 0.85, ty - uy * w * tip_round + py * w * 0.85),
           (tx, ty),
           (tx - ux * w * tip_round - px * w * 0.85, ty - uy * w * tip_round - py * w * 0.85),
           (bx + ux * n * 0.5 - px * w, by + uy * n * 0.5 - py * w),
           (bx - px * w * 0.8, by - py * w * 0.8)]
    return [(round(x, 1), round(y, 1)) for x, y in pts], (ux, uy, px, py, n, w)


def barbs(base, frame, color, step=9, opacity=0.45):
    """Barb lines from the rachis toward both vanes of a feather."""
    bx, by = base
    ux, uy, px, py, n, w = frame
    out = []
    for t in range(int(step * 1.5), int(n - step), step):
        cx, cy = bx + ux * t, by + uy * t
        for side in (1, -1):
            ex = cx + px * side * w * 0.85 + ux * w * 0.6
            ey = cy + py * side * w * 0.85 + uy * w * 0.6
            out.append(f"M{cx:.1f},{cy:.1f} L{ex:.1f},{ey:.1f}")
    return (f'<path d="{" ".join(out)}" stroke="{color}" stroke-width="0.9" fill="none" opacity="{opacity}"/>')


def draw():
    g = P["gorget"]
    tail_dark = M(P["tail"], P["bill"], 0.65)
    defs = [
        lin("gorget", [(0, L(g, .08)), (0.4, g), (0.8, D(g, .1)), (1, D(g, .18))], 560, 110, 770, 260),
        lin("head", [(0, L(P["crown"], .04)), (1, D(P["crown"], .14))], 550, 0, 780, 130),
        lin("crown", [(0, M(P["crown"], P["back"], .5)), (1, D(M(P["crown"], P["back"], .4), .08))], 550, 0, 770, 60),
        lin("collar", [(0, D(P["collar"], .06)), (0.5, P["collar"]), (1, D(P["collar"], .04))], 570, 200, 800, 300),
        lin("body", [(0, D(P["belly"], .12)), (1, D(P["back"], .06))], 600, 300, 900, 600),
        lin("back", [(0, D(P["back"], .06)), (0.5, P["back"]), (1, L(M(P["back"], "#b8b04a", .3), .04))], 790, 120, 930, 560),
        lin("belly", [(0, D(P["belly"], .06)), (0.5, P["belly"]), (1, L(P["belly"], .05))], 650, 560, 880, 820),
        lin("flank", [(0, D(P["wing"], .14)), (1, D(P["wing"], .2))], 600, 420, 660, 560),
        lin("wingL", [(0, D(P["wing"], .14)), (0.35, D(P["wing"], .04)), (0.75, P["wing"]), (1, D(P["wing"], .06))],
            590, 300, 0, 200),
        lin("wingR", [(0, D(P["wing"], .34)), (0.25, D(P["wing"], .2)), (0.7, D(P["wing"], .14)), (1, D(P["wing"], .08))],
            600, 270, 880, 540),
        lin("tail", [(0, D(P["tail"], .16)), (0.55, D(P["tail"], .06)), (1, P["tail"])], 680, 650, 320, 820),
        lin("fork", [(0, D(M(P["tail"], P["wing"], .5), .18)), (0.5, D(M(P["tail"], P["wing"], .4), .3)), (1, D(tail_dark, .08))],
            780, 700, 800, 1080),
        lin("undertail", [(0, M(P["belly"], "#e8d070", .6)), (1, M(P["belly"], "#c8a84a", .5))], 655, 825, 712, 890),
        lin("bill", [(0, D(P["bill"], .12)), (0.7, P["bill"]), (1, L(P["bill"], .06))], 556, 80, 338, 72),
        '<radialGradient id="vol" gradientUnits="userSpaceOnUse" cx="680" cy="420" r="420">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.12"/><stop offset="0.55" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.25"/></radialGradient>',
        f'<clipPath id="c-body"><path d="{smooth(BODY)}"/></clipPath>',
        f'<clipPath id="c-gorget"><path d="{smooth(GORGET)}"/></clipPath>',
        f'<clipPath id="c-head"><path d="{smooth(HEAD)}"/></clipPath>',
        f'<clipPath id="c-back"><path d="{smooth(BACK)}"/></clipPath>',
        '<filter id="blur1" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.2"/></filter>',
        '<filter id="blur3" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter>',
        '<filter id="motion" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3 1.5"/></filter>',
    ]
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 941 1082" width="941" height="1082">',
         "<defs>" + "".join(defs) + "</defs>"]
    # spread tail feathers (behind), each with rachis and barbs
    for base, tip, w in TAIL_FAN:
        pts, frame = feather(base, tip, w, tip_round=0.3)
        s.append(f'<path d="{smooth(pts)}" fill="url(#tail)" stroke="{M(L(P["tail"], .16), P["wing"], .35)}" stroke-width="3"/>')
        s.append(barbs(base, frame, D(P["tail"], .16)))
        s.append(f'<path d="M{base[0]},{base[1]} L{tip[0]},{tip[1]}" stroke="{L(P["tail"], .2)}" stroke-width="1.6" opacity="0.7"/>')
    # far wing, behind the body
    s.append(f'<path d="{smooth(WING_L)}" fill="url(#wingL)"/>')
    s += [f'<path d="M{a[0]},{a[1]} Q{(a[0] + b[0]) / 2:.0f},{(a[1] + b[1]) / 2 - 8:.0f} {b[0]},{b[1]}" '
          f'stroke="{D(P["wing"], .18)}" stroke-width="1.4" fill="none" opacity="0.55"/>' for a, b in WING_L_FEATHERS]
    s.append(f'<path d="M570,172 C450,150 300,126 120,126" stroke="{D(P["wing"], .22)}" stroke-width="3" fill="none" opacity="0.5"/>')
    # forked tail
    for base, tip, w in TAIL_FORK:
        pts, frame = feather(base, tip, w, tip_round=0.3)
        s.append(f'<path d="{smooth(pts)}" fill="url(#fork)" stroke="{M(P["tail"], P["bill"], .4)}" stroke-width="1"/>')
        s.append(f'<path d="M{base[0]},{base[1]} L{tip[0]},{tip[1]}" stroke="{L(P["tail"], .05)}" stroke-width="1.2" opacity="0.5"/>')
    # body
    s.append(f'<path d="{BILL}" fill="url(#bill)"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#body)"/>')
    s.append('<g clip-path="url(#c-body)">')
    s.append(f'<path d="{smooth(BELLY)}" fill="url(#belly)" filter="url(#blur3)"/>')
    s.append(f'<path d="{smooth(FLANK)}" fill="url(#flank)" filter="url(#blur3)" opacity="0.8"/>')
    s.append(f'<path d="{smooth(BACK)}" fill="url(#back)" filter="url(#blur1)"/>')
    s.append('<g clip-path="url(#c-back)">' + scales((780, 110, 940, 660), D(P["back"], .14), step=11, size=(3, 5),
                                                         opacity=(0.3, 0.7), seed=11, width=1.4) + "</g>")
    s.append(f'<path d="{smooth(COLLAR)}" fill="url(#collar)" filter="url(#blur1)"/>')
    s.append(f'<path d="{smooth(BODY)}" fill="url(#vol)"/>')
    s.append("</g>")
    s.append(f'<path d="{smooth(UNDERTAIL)}" fill="url(#undertail)" filter="url(#blur3)" opacity="0.75"/>')
    # head
    s.append(f'<path d="{smooth(HEAD)}" fill="url(#head)"/>')
    s.append('<g clip-path="url(#c-head)">')
    s.append(f'<path d="{smooth(CROWN)}" fill="url(#crown)" filter="url(#blur3)"/>')
    s.append(scales((545, 0, 780, 120), D(P["crown"], .16), step=9, size=(2, 3.4), opacity=(0.2, 0.55), seed=12, width=1.1))
    s.append(scales((545, 0, 780, 60), M(P["back"], "#c8c050", .5), step=13, size=(1.6, 2.6), opacity=(0.2, 0.5), seed=13))
    s.append("</g>")
    s.append(f'<path d="{smooth(GORGET)}" fill="url(#gorget)"/>')
    s.append('<g clip-path="url(#c-gorget)">' +
             scales((540, 110, 790, 275), L(g, .14), step=11, size=(3.4, 5.6), opacity=(0.35, 0.85), seed=14, width=1.6) +
             scales((546, 116, 790, 275), D(g, .16), step=11, size=(3, 5), opacity=(0.3, 0.6), seed=15, width=1.3) + "</g>")
    ex, ey, er = EYE
    s += [f'<circle cx="{ex}" cy="{ey}" r="{er + 3}" fill="{D(P["crown"], .3)}"/>',
          f'<circle cx="{ex}" cy="{ey}" r="{er}" fill="#0a0909"/>',
          f'<circle cx="{ex - 6}" cy="{ey - 7}" r="5" fill="#ffffff" opacity="0.9"/>',
          f'<ellipse cx="{ex + 30}" cy="{ey + 8}" rx="6" ry="4" fill="{P["collar"]}" opacity="0.8"/>']
    # feet
    for leg, toes in FEET:
        s.append(f'<path d="{leg}" stroke="{D(P["crown"], .14)}" stroke-width="18" fill="none" stroke-linecap="round"/>')
        s.append(f'<path d="{leg}" stroke="{D(P["crown"], .28)}" stroke-width="18" fill="none" stroke-dasharray="3 5" opacity="0.6"/>')
        s += [f'<path d="{t}" stroke="{D(P["crown"], .3)}" stroke-width="7" fill="none" stroke-linecap="round"/>' for t in toes]
        s += [f'<circle cx="{t.split()[-1].split(",")[0]}" cy="{t.split()[-1].split(",")[1]}" r="3.4" fill="#141210"/>' for t in toes]
    # near wing, in front, blurred by motion
    s.append(f'<path d="{smooth(WING_R)}" fill="url(#wingR)" opacity="0.92" filter="url(#motion)"/>')
    s += [f'<path d="M{a[0]},{a[1]} Q{(a[0] + b[0]) / 2:.0f},{(a[1] + b[1]) / 2 - 10:.0f} {b[0]},{b[1]}" '
          f'stroke="{D(P["wing"], .26)}" stroke-width="2" fill="none" opacity="0.35" filter="url(#motion)"/>'
          for a, b in WING_R_FEATHERS]
    s.append(f'<path d="M604,300 C660,272 760,262 868,284" stroke="{D(P["wing"], .42)}" stroke-width="10" fill="none" '
             f'stroke-linecap="round" opacity="0.6" filter="url(#motion)"/>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    with open(OUT, "w") as fh:
        fh.write(draw())
    print("wrote", OUT)
