"""Draw the hummingbird species of rhdt_mpl as SVG illustrations (perched, in profile, facing left), colored from
their palettes.  Writes docs/birds/<species>.svg.

    python examples/draw_hummingbirds.py
"""
import os
from rhdt_mpl import oklab
from rhdt_mpl.palettes import PALETTES

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "birds")

L, D, M = oklab.lighten, oklab.darken, oklab.mix


def grad(gid, stops, x1=0, y1=0, x2=1, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rgrad(gid, stops, cx=0.4, cy=0.35, r=0.7):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def sheen(c, k=0.13):
    """Stops for an iridescent patch: deep edge, saturated middle, bright glint."""
    return [(0, D(c, k)), (0.45, c), (0.7, L(c, k)), (1, D(c, k * 0.6))]


# ---------------------------------------------------------------- anatomy (viewBox 0 0 360 320)
BILL = "M142,94 C110,98 76,104 34,114 C76,110 110,109 144,108 Z"
HEAD = "M120,104 C118,80 136,64 158,65 C180,66 192,84 190,104 C188,122 172,134 154,134 C134,134 122,122 120,104 Z"
CROWN = "M121,95 C127,73 148,63 168,65 C183,67 192,80 191,99 C179,90 162,86 146,88 C136,89 127,92 121,95 Z"
BODY = ("M170,70 C204,78 230,106 242,140 C254,174 252,204 240,226 C230,240 212,244 198,236 "
        "C170,222 146,194 134,164 C124,138 128,108 142,88 C150,76 160,70 170,70 Z")
BELLY = ("M132,150 C142,184 164,214 192,232 C204,238 216,238 224,230 C206,216 188,194 176,170 "
         "C166,150 156,138 140,134 Z")
FLANK = "M174,168 C186,194 204,216 224,230 C236,220 242,200 238,182 C222,176 198,170 174,168 Z"
GORGET = "M124,106 C122,132 134,156 156,168 C168,160 176,146 177,128 C160,124 140,118 124,106 Z"
GORGET_FLARE = "M162,138 C180,156 190,182 190,210 C178,196 166,176 156,156 Z"
CHIN = "M125,106 C134,113 145,117 157,119 C146,122 134,118 126,112 Z"
EAR = "M160,96 C174,92 190,100 198,116 C188,122 172,121 162,111 Z"
BREAST = "M136,150 C146,178 166,202 190,214 C200,202 196,182 182,170 C168,160 152,154 136,150 Z"
WING = ("M196,94 C224,110 246,140 262,178 C276,210 290,240 304,268 C292,264 278,250 266,232 "
        "C246,206 224,172 208,140 C200,124 192,108 196,94 Z")
FEATHERS = ["M214,128 C238,170 262,214 298,262", "M206,116 C230,160 254,206 288,256",
            "M222,146 C244,186 266,226 290,252"]
COVERTS = "M196,94 C216,104 230,124 238,146 C222,140 208,126 200,110 Z"
TAIL = ("M220,212 C236,234 252,258 266,280 Q266,290 257,287 Q252,284 248,279 Q247,290 238,288 "
        "Q232,284 230,276 Q224,280 222,272 C218,254 214,236 210,220 Z")
TAIL_FORK = ("M220,212 C238,234 256,258 276,284 Q270,288 262,282 Q256,278 250,272 Q246,286 236,288 "
             "Q230,286 228,276 C222,254 216,236 210,220 Z")
STREAMER_1 = "M238,246 C258,280 292,300 344,306 C300,312 262,292 236,258 Z"
STREAMER_2 = "M242,244 C270,270 304,282 352,280 C310,292 270,284 240,256 Z"
BRANCH = "M30,258 C110,246 200,242 260,248 C292,251 322,258 352,268"
FEET = "M200,236 L197,247 M212,238 L210,249 M192,246 Q197,252 203,247 M205,248 Q211,253 216,249"
LEAVES = [(74, 247, -28), (98, 260, 24), (318, 262, -10)]
EYE = (156, 95)
SCALES = [(x, y) for y in range(110, 162, 7) for x in range(124 + (y // 7 % 2) * 4, 176, 9)]

def bird(key):
    p = PALETTES[key]
    g = {"anna": lambda: dict(gorget=p["gorget"], crown=p["gorget"], back=p["back"], belly=p["belly"], flank=p["flank"],
                      wing=p["wing"], tail=D(p["wing"], .05), bill=p["bill"], fork=False),
         "ruby-throated": lambda: dict(gorget=p["gorget"], crown=p["back"], back=p["back"], belly=p["belly"], flank=p["flank"],
                               wing=p["wing"], tail=p["wing"], bill=p["bill"], fork=True, chin=p["bill"]),
         "rufous": lambda: dict(gorget=p["gorget"], crown=M(p["back"], "#3b7a3b", 0.35), back=p["back"], belly=p["belly"],
                        flank=p["flank"], wing=p["wing"], tail=p["back"], bill=p["bill"], fork=False, head=p["back"]),
         "costa": lambda: dict(gorget=p["gorget"], crown=p["gorget"], back=p["back"], belly=p["belly"], flank=p["flank"],
                       wing=p["wing"], tail=D(p["back"], .12), bill=p["bill"], fork=False, flare=True),
         "crimson-topaz": lambda: dict(gorget=p["throat"], crown=p["head"], back=p["body"], belly=D(p["body"], .04),
                               flank=D(p["body"], .1), wing=p["wing"], tail=D(p["body"], .12), bill=p["head"],
                               fork=False, head=p["head"], streamers=p["head"], throat_rim=p["sheen"]),
         "sparkling-violetear": lambda: dict(gorget=p["back"], crown=p["back"], back=p["back"], belly=p["belly"],
                                     flank=p["belly"], wing=D(p["tail"], .02), tail=M(p["belly"], p["tail"], .55),
                                     bill=p["bill"], fork=False, ear=p["ear"], breast=p["breast"]),
         }[key]()
    head = g.get("head", g["back"])
    defs = [
        grad("back", [(0, L(g["back"], .08)), (0.5, g["back"]), (1, D(g["back"], .1))], 0, 0, 1, 1),
        grad("head", [(0, L(head, .1)), (0.6, head), (1, D(head, .08))], 0, 0, 0.6, 1),
        grad("belly", [(0, L(g["belly"], .03)), (1, D(g["belly"], .06))], 0, 0, 1, 1),
        grad("flank", [(0, g["flank"]), (1, D(g["flank"], .06))]),
        grad("wing", [(0, L(g["wing"], .06)), (0.5, g["wing"]), (1, D(g["wing"], .08))], 0, 0, 1, 0.6),
        grad("tail", [(0, g["tail"]), (1, D(g["tail"], .12))], 0, 0, 1, 1),
        grad("gorget", sheen(g["gorget"]), 0, 0, 0.9, 1),
        grad("crown", sheen(g["crown"], .1), 0, 0, 1, 0.6),
        grad("bill", [(0, D(g["bill"], .02)), (1, L(g["bill"], .12))], 1, 0, 0, 0),
        '<radialGradient id="vol" cx="0.3" cy="0.25" r="0.85">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.28"/><stop offset="0.45" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.8" stop-color="#000000" stop-opacity="0.10"/><stop offset="1" stop-color="#000000" stop-opacity="0.32"/>'
        '</radialGradient>',
        '<radialGradient id="hvol" cx="0.35" cy="0.25" r="0.8">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.30"/><stop offset="0.5" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.30"/></radialGradient>',
        f'<clipPath id="gclip"><path d="{GORGET}"/></clipPath>',
        f'<clipPath id="bclip"><path d="{BODY}"/></clipPath>',
        '<filter id="blur2" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="2.2"/></filter>',
        '<filter id="blur4" x="-15%" y="-15%" width="130%" height="130%"><feGaussianBlur stdDeviation="4"/></filter>',
    ]
    if "ear" in g:
        defs += [grad("ear", sheen(g["ear"]), 0, 0, 1, 1), grad("breast", sheen(g["breast"], .1), 0, 0, 1, 1)]
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 320" width="360" height="320">',
         "<defs>" + "".join(defs) +
         '<filter id="soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.6"/></filter>'
         "</defs>",
         f'<path d="{BRANCH}" fill="none" stroke="#6b5440" stroke-width="7" stroke-linecap="round"/>',
         f'<path d="{BRANCH}" fill="none" stroke="#8a7058" stroke-width="2.5" stroke-linecap="round" transform="translate(0,-2)"/>']
    for lx, ly, rot in LEAVES:
        s.append(f'<g transform="translate({lx},{ly}) rotate({rot})"><path d="M0,0 C8,-9 24,-9 34,0 C24,9 8,9 0,0 Z" '
                 f'fill="#4f7d3c"/><path d="M0,0 L32,0" stroke="#3d6430" stroke-width="0.8"/></g>')
    if "streamers" in g:
        s += [f'<path d="{STREAMER_2}" fill="{g["streamers"]}"/>', f'<path d="{STREAMER_1}" fill="{L(g["streamers"], .06)}"/>']
    s += [f'<path d="{TAIL_FORK if g["fork"] else TAIL}" fill="url(#tail)"/>',
          f'<path d="{FEET}" stroke="#2a2420" stroke-width="2.2" fill="none" stroke-linecap="round"/>',
          f'<path d="{BODY}" fill="url(#back)"/>',
          '<g clip-path="url(#bclip)">',
          f'<path d="{BELLY}" fill="url(#belly)" filter="url(#blur2)"/>',
          f'<path d="{FLANK}" fill="url(#flank)" opacity="0.85" filter="url(#blur4)"/>',
          '</g>',
          f'<path d="{BODY}" fill="url(#vol)"/>']
    if "breast" in g:
        s.append(f'<g clip-path="url(#bclip)"><path d="{BREAST}" fill="url(#breast)" filter="url(#blur2)"/></g>')
    s += [f'<path d="{WING}" fill="url(#wing)"/>',
          f'<path d="{COVERTS}" fill="{L(g["wing"], .05)}" opacity="0.8"/>']
    s += [f'<path d="{f}" fill="none" stroke="{L(g["wing"], .1)}" stroke-width="1" opacity="0.7"/>' for f in FEATHERS]
    s += [f'<path d="{BILL}" fill="url(#bill)"/>', f'<path d="{HEAD}" fill="url(#head)"/>']
    head_overlay = f'<path d="{HEAD}" fill="url(#hvol)"/>'
    if g["crown"] != head:
        s.append(f'<path d="{CROWN}" fill="url(#crown)" filter="url(#soft)"/>')
    if g.get("flare"):
        s.append(f'<path d="{GORGET_FLARE}" fill="url(#gorget)"/>')
    if "throat_rim" in g:
        s.append(f'<path d="{GORGET}" fill="{g["throat_rim"]}" transform="translate(1,3)"/>')
    s.append(f'<path d="{GORGET}" fill="url(#gorget)"/>')
    s.append('<g clip-path="url(#gclip)" fill="none" stroke="%s" stroke-width="0.9" opacity="0.55">' % L(g["gorget"], .2)
             + "".join(f'<path d="M{x - 4},{y} Q{x},{y + 4} {x + 4},{y}"/>' for x, y in SCALES) + "</g>")
    if "chin" in g:
        s.append(f'<path d="{CHIN}" fill="{g["chin"]}"/>')
    if "ear" in g:
        s.append(f'<path d="{EAR}" fill="url(#ear)"/>')
    s.append(head_overlay)
    ex, ey = EYE
    s += [f'<circle cx="{ex}" cy="{ey}" r="5.2" fill="#0c0b0b"/>',
          f'<circle cx="{ex - 1.6}" cy="{ey - 1.7}" r="1.5" fill="#ffffff" opacity="0.9"/>']
    if key in ("anna", "ruby-throated", "costa", "rufous"):
        s.append(f'<ellipse cx="{ex + 10}" cy="{ey + 1}" rx="3" ry="1.8" fill="#f4f1ea"/>')   # white spot behind the eye
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for key in ("anna", "ruby-throated", "rufous", "costa", "crimson-topaz", "sparkling-violetear"):
        with open(os.path.join(OUT, f"{key}.svg"), "w") as fh:
            fh.write(bird(key))
        print("wrote", key)
