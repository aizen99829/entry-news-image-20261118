#!/usr/bin/env python3
"""Render the news poster for Wednesday 18 November 2026.

One 1024x1024 PNG, drawn with PIL + DejaVu fonts. No network, no
randomness (star positions are a fixed list), so re-runs are byte-identical.

Layout (1024x1024):
  masthead 0-116 | hero 124-476 | grid 2x2 488-864 | strip 876-1012
Word budget: 59 words total (counted in BUILD-R1.md).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "poster.png")

CREAM = (247, 242, 231)
INK = (20, 20, 20)
RED = (178, 34, 34)
NAVY = (11, 27, 51)
NAVY2 = (22, 50, 79)
SEA = (14, 42, 74)
WHITE = (255, 255, 255)
GREY = (90, 90, 90)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(fnt, s):
    return fnt.getbbox(s)[2]


def fit_font(path, s, size, max_w, minimum=24):
    """Largest size <= `size` that fits `max_w`."""
    while size > minimum and text_w(font(path, size), s) > max_w:
        size -= 1
    return font(path, size)


def centre(d, cx, y, s, fnt, fill):
    d.text((cx - text_w(fnt, s) // 2, y), s, font=fnt, fill=fill)


def starburst(d, cx, cy, r_out, r_in, points, fill):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * i / points - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def spiral_points(cx, cy, turns, r_max, steps=220):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = t * turns * 2 * math.pi
        r = t * r_max
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_hero(d, x0, y0, x1, y1):
    """Night sky over the Gulf: radar left, big delta drone centre,
    orange explosion right, warship on the sea below."""
    # sky gradient (fixed bands, deterministic)
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        r = int(NAVY[0] + (NAVY2[0] - NAVY[0]) * t)
        g = int(NAVY[1] + (NAVY2[1] - NAVY[1]) * t)
        b = int(NAVY[2] + (NAVY2[2] - NAVY[2]) * t)
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))
    # fixed stars
    for sx, sy, sr in [(80, 150, 2), (240, 140, 2), (420, 138, 3),
                       (640, 145, 2), (820, 135, 2), (950, 160, 3),
                       (330, 175, 2), (560, 165, 2), (180, 200, 2)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=WHITE)
    sea_y = y1 - 52
    d.rectangle([x0, sea_y, x1, y1], fill=SEA)
    # waves
    for wx in range(x0 + 20, x1 - 20, 90):
        d.arc([wx, sea_y + 12, wx + 70, sea_y + 34], 180, 360,
              fill=(120, 170, 220), width=4)
    # --- radar dish, left: A-frame mast + tilted parabolic bowl ---
    bx, by = x0 + 110, sea_y - 6          # mast base
    d.line([(bx - 26, by), (bx, by - 84)], fill=(200, 200, 200), width=7)
    d.line([(bx + 26, by), (bx, by - 84)], fill=(200, 200, 200), width=7)
    d.line([(bx - 34, by), (bx + 34, by)], fill=(200, 200, 200), width=6)
    # bowl: arc points of a tilted ellipse, drawn as a thick curve
    pts = []
    for i in range(41):
        u = -1.0 + 2.0 * i / 40            # along the dish face
        v = 0.55 * (1 - u * u)            # bowl depth
        a = math.radians(32)
        px = bx - 8 + (u * 62) * math.cos(a) - (v * 62) * math.sin(a)
        py = by - 108 + (u * 62) * math.sin(a) + (v * 62) * math.cos(a)
        pts.append((px, py))
    d.line(pts, fill=(235, 235, 235), width=10, joint="curve")
    d.line([pts[0], pts[-1]], fill=(235, 235, 235), width=6)
    d.line([(bx - 8, by - 108), (bx + 22, by - 132)], fill=(235, 235, 235),
           width=5)
    d.ellipse([bx + 16, by - 138, bx + 28, by - 126], fill=(240, 220, 120))
    # sweeping beam (pale yellow wedge up-right)
    d.polygon([(bx + 22, by - 132), (bx + 170, by - 200), (bx + 150, by - 140)],
              fill=(240, 220, 120))
    # --- quadcopter drone, centre: body + 4 arms + spinning rotors ---
    cx, cy = 500, 222
    # arms to the four rotor hubs
    for hx, hy in [(cx - 118, cy - 46), (cx + 118, cy - 46),
                   (cx - 118, cy + 46), (cx + 118, cy + 46)]:
        d.line([(cx, cy), (hx, hy)], fill=(200, 200, 200), width=9)
        d.ellipse([hx - 52, hy - 9, hx + 52, hy + 9], fill=(170, 170, 170),
                  outline=(230, 230, 230))
        d.ellipse([hx - 10, hy - 10, hx + 10, hy + 10], fill=(60, 60, 60))
    d.rounded_rectangle([cx - 62, cy - 24, cx + 62, cy + 24], radius=16,
                        fill=(38, 38, 38), outline=(220, 220, 220), width=3)
    d.ellipse([cx - 18, cy - 12, cx + 18, cy + 12], fill=(90, 90, 90),
              outline=(220, 220, 220))
    # red navigation lights front/back, green light on the nose
    d.ellipse([cx - 70, cy - 7, cx - 56, cy + 7], fill=(255, 60, 60))
    d.ellipse([cx + 56, cy - 7, cx + 70, cy + 7], fill=(60, 255, 120))
    # interceptor streak crossing toward the drone from the right
    d.line([(cx + 300, cy - 95), (cx + 200, cy - 40)], fill=WHITE, width=5)
    d.ellipse([cx + 292, cy - 103, cx + 308, cy - 87], fill=(255, 80, 40))
    # --- explosion burst, right: irregular fireball, no sun-like rays ---
    ex, ey = 880, 240
    d.ellipse([ex - 58, ey - 30, ex + 30, ey + 58], fill=(220, 40, 0))
    d.ellipse([ex - 30, ey - 52, ex + 58, ey + 30], fill=(255, 110, 0))
    d.ellipse([ex - 12, ey - 28, ex + 44, ey + 22], fill=(255, 170, 40))
    d.polygon([(ex - 40, ey - 40), (ex - 18, ey - 92), (ex + 2, ey - 44)],
              fill=(255, 140, 20))
    d.polygon([(ex + 6, ey - 48), (ex + 30, ey - 96), (ex + 44, ey - 42)],
              fill=(255, 110, 0))
    # smoke puffs above the burst
    for sx, sy, sr in [(ex - 46, ey - 82, 22), (ex - 8, ey - 100, 26),
                       (ex + 34, ey - 84, 20)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(110, 110, 110))
    # small second drone, top right
    sx, sy = 760, 165
    d.line([(sx - 34, sy - 14), (sx + 34, sy + 14)], fill=(200, 200, 200),
           width=5)
    d.line([(sx - 34, sy + 14), (sx + 34, sy - 14)], fill=(200, 200, 200),
           width=5)
    for hx, hy in [(sx - 34, sy - 14), (sx + 34, sy - 14), (sx - 34, sy + 14),
                   (sx + 34, sy + 14)]:
        d.ellipse([hx - 18, hy - 4, hx + 18, hy + 4], fill=(170, 170, 170))
    d.ellipse([sx - 12, sy - 8, sx + 12, sy + 8], fill=(38, 38, 38),
              outline=(220, 220, 220))
    d.ellipse([sx - 16, sy - 3, sx - 8, sy + 5], fill=(255, 60, 60))
    # --- warship silhouette on the sea ---
    hx, hy = 660, sea_y + 8
    d.polygon([(hx - 95, hy + 26), (hx + 105, hy + 26), (hx + 88, hy + 2),
               (hx - 78, hy + 2)], fill=(70, 70, 70))
    d.rectangle([hx - 30, hy - 26, hx + 10, hy + 2], fill=(70, 70, 70))
    for wx in range(hx - 24, hx + 6, 10):
        d.rectangle([wx, hy - 20, wx + 5, hy - 12], fill=(220, 220, 220))
    d.line([(hx + 30, hy + 2), (hx + 30, hy - 38)], fill=(70, 70, 70), width=6)
    d.line([(hx + 18, hy - 30), (hx + 42, hy - 30)], fill=(70, 70, 70),
           width=5)
    d.ellipse([hx + 24, hy - 44, hx + 36, hy - 32], fill=(255, 60, 60))


def draw_kerch(d, x0, y0, x1, y1):
    """Tall curved-arch bridge, middle span fallen into the sea."""
    d.rectangle([x0, y0, x1, y1], fill=(214, 228, 240))
    sea_y = y1 - 18
    d.rectangle([x0, sea_y, x1, y1], fill=(70, 130, 190))
    deck_y = y0 + 50
    mid = (x0 + x1) // 2
    # two tall parabolic arches (curved, not triangular) with hangers
    for ax0, ax1 in [(x0 + 18, mid - 48), (mid + 48, x1 - 18)]:
        amx = (ax0 + ax1) // 2
        half = (ax1 - ax0) / 2
        apex = y0 + 4
        pts = []
        for i in range(33):
            t = -1.0 + 2.0 * i / 32
            px = amx + t * half
            py = deck_y - (deck_y - apex) * (1 - t * t)
            pts.append((px, py))
        d.line(pts, fill=(50, 50, 50), width=8, joint="curve")
        for i in range(1, 8):
            t = -1.0 + 2.0 * i / 8
            hx = amx + t * half
            hy = deck_y - (deck_y - apex) * (1 - t * t)
            d.line([(hx, deck_y), (hx, hy)], fill=(50, 50, 50), width=3)
    # deck: standing sections only, thick, with a wide gap in the middle
    d.rectangle([x0 + 8, deck_y - 7, mid - 48, deck_y + 7], fill=(40, 40, 40))
    d.rectangle([mid + 48, deck_y - 7, x1 - 8, deck_y + 7], fill=(40, 40, 40))
    # fallen deck fragment, tilted, just above the water + splash
    d.polygon([(mid - 32, deck_y + 12), (mid + 28, deck_y + 22),
               (mid + 20, deck_y + 32), (mid - 40, deck_y + 22)],
              fill=(40, 40, 40))
    for sx in (mid - 44, mid - 8, mid + 28):
        d.arc([sx, sea_y - 12, sx + 30, sea_y + 8], 180, 360,
              fill=WHITE, width=5)
    # smoke over the gap
    d.ellipse([mid - 30, y0 + 22, mid + 2, y0 + 54], fill=(110, 110, 110))


def draw_trump(d, x0, y0, x1, y1):
    """Air Force One (small, high) over the four Quad flags."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 238, 245))
    cx = (x0 + x1) // 2
    py = y0 + 24
    # plane: short fuselage, tail fin, one thin swept wing below
    d.ellipse([cx - 105, py - 10, cx + 105, py + 10], fill=(30, 90, 160))
    d.polygon([(cx + 82, py - 8), (cx + 118, py - 38), (cx + 118, py - 6)],
              fill=(30, 90, 160))
    d.polygon([(cx - 8, py + 6), (cx + 34, py + 6), (cx + 58, py + 20),
               (cx + 16, py + 20)], fill=(20, 60, 120))
    d.polygon([(cx - 40, py - 6), (cx - 8, py - 6), (cx - 22, py - 18),
               (cx - 48, py - 18)], fill=(20, 60, 120))
    for wx in range(cx - 84, cx + 70, 20):
        d.ellipse([wx, py - 4, wx + 7, py + 3], fill=WHITE)
    # four Quad flags on poles along the bottom: US, Japan, Australia, India
    fy = y1 - 6
    fx = x0 + 34
    # US: red with white stripes
    d.line([(fx, fy), (fx, fy - 34)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 34, fx + 52, fy - 14], fill=(178, 34, 34))
    d.rectangle([fx, fy - 29, fx + 52, fy - 25], fill=WHITE)
    d.rectangle([fx, fy - 21, fx + 52, fy - 17], fill=WHITE)
    # Japan: white with red dot
    fx += 100
    d.line([(fx, fy), (fx, fy - 34)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 34, fx + 52, fy - 14], fill=WHITE,
                outline=(60, 60, 60))
    d.ellipse([fx + 19, fy - 29, fx + 33, fy - 15], fill=(200, 40, 40))
    # Australia: blue with white cross bars
    fx += 100
    d.line([(fx, fy), (fx, fy - 34)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 34, fx + 52, fy - 14], fill=(0, 60, 140))
    d.rectangle([fx, fy - 26, fx + 52, fy - 22], fill=WHITE)
    d.rectangle([fx + 24, fy - 34, fx + 28, fy - 14], fill=WHITE)
    # India: saffron / white / green
    fx += 100
    d.line([(fx, fy), (fx, fy - 34)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 34, fx + 52, fy - 27], fill=(255, 153, 51))
    d.rectangle([fx, fy - 27, fx + 52, fy - 20], fill=WHITE)
    d.rectangle([fx, fy - 20, fx + 52, fy - 14], fill=(0, 130, 60))


def draw_nvidia(d, x0, y0, x1, y1):
    """Green GPU chip + steep rising arrow."""
    d.rectangle([x0, y0, x1, y1], fill=(222, 243, 214))
    cx = (x0 + x1) // 2 - 90
    cy = (y0 + y1) // 2
    # chip pins
    for px in range(cx - 52, cx + 53, 18):
        d.line([(px, cy - 52), (px, cy - 66)], fill=(40, 90, 20), width=4)
        d.line([(px, cy + 52), (px, cy + 66)], fill=(40, 90, 20), width=4)
    for py in range(cy - 40, cy + 41, 18):
        d.line([(cx - 52, py), (cx - 66, py)], fill=(40, 90, 20), width=4)
        d.line([(cx + 52, py), (cx + 66, py)], fill=(40, 90, 20), width=4)
    d.rounded_rectangle([cx - 52, cy - 52, cx + 52, cy + 52], radius=10,
                        fill=(118, 185, 0))
    d.rounded_rectangle([cx - 28, cy - 28, cx + 28, cy + 28], radius=6,
                        fill=(30, 90, 20))
    # rising arrow, right side
    ax0, ay1 = cx + 92, y1 - 14
    d.line([(ax0, ay1), (ax0 + 52, ay1 - 34), (ax0 + 104, ay1 - 52),
            (ax0 + 150, ay1 - 74)], fill=(20, 120, 20), width=9)
    d.polygon([(ax0 + 150, ay1 - 74), (ax0 + 118, ay1 - 74),
               (ax0 + 150, ay1 - 42)], fill=(20, 120, 20))


def draw_akvan(d, x0, y0, x1, y1):
    """Satellite spiral of the cyclone over a blue sea."""
    d.rectangle([x0, y0, x1, y1], fill=(198, 224, 245))
    cx = (x0 + x1) // 2 - 110
    cy = (y0 + y1) // 2
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=(40, 90, 160))
    pts = spiral_points(cx, cy, 2.6, 56)
    d.line(pts, fill=WHITE, width=9, joint="curve")
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(20, 50, 100))
    # rain + wave, right side
    for rx in range(cx + 96, x1 - 12, 26):
        d.line([(rx, y0 + 16), (rx - 10, y0 + 52)], fill=(60, 110, 180),
               width=4)
    wy = y1 - 16
    d.arc([cx + 84, wy - 12, cx + 150, wy + 12], 180, 360,
          fill=(20, 80, 160), width=5)
    d.arc([cx + 150, wy - 12, cx + 216, wy + 12], 180, 360,
          fill=(20, 80, 160), width=5)


def panel(d, x0, y0, x1, y1, bg, draw_icon, headline, sub):
    d.rounded_rectangle([x0, y0, x1, y1], radius=10, fill=bg,
                        outline=INK, width=2)
    draw_icon(d, x0 + 10, y0 + 8, x1 - 10, y0 + 88)
    hf = fit_font(SANS_B, headline, 36, (x1 - x0) - 24, minimum=28)
    centre(d, (x0 + x1) // 2, y0 + 96, headline, hf, INK)
    sf = font(SANS_B, 28)
    centre(d, (x0 + x1) // 2, y0 + 140, sub, sf, (40, 40, 40))


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    centre(d, W // 2, 12, "THE WORLD IN ONE DAY", font(SANS_B, 32), RED)
    centre(d, W // 2, 48, "WEDNESDAY 18 NOVEMBER 2026",
           font(SERIF_B, 50), INK)
    d.rectangle([16, 106, W - 16, 112], fill=RED)

    # ---- hero ----
    hx0, hy0, hx1, hy1 = 16, 124, W - 16, 476
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=10, outline=INK, width=2)
    draw_hero(d, hx0 + 2, hy0 + 2, hx1 - 2, hy0 + 236)
    d.rectangle([hx0 + 2, hy0 + 236, hx1 - 2, hy0 + 302], fill=NAVY)
    centre(d, W // 2, hy0 + 246, "DRONES OVER BAHRAIN",
           font(SANS_B, 54), WHITE)
    centre(d, W // 2, hy0 + 312, "Iran drones intercepted; US hits Qeshm.",
           font(SANS_B, 30), INK)

    # ---- grid 2x2 ----
    panel(d, 16, 488, 502, 672, (214, 228, 240), draw_kerch,
          "KERCH BRIDGE DOWN", "Ukraine strike; 270m falls.")
    panel(d, 522, 488, 1008, 672, (232, 238, 245), draw_trump,
          "TRUMP IN MANILA", "Meets Marcos; Xi\u2013Putin Thu.")
    panel(d, 16, 680, 502, 864, (222, 243, 214), draw_nvidia,
          "NVIDIA: REVENUE $115.8BN", "Up 103%; Huang stays out.")
    panel(d, 522, 680, 1008, 864, (198, 224, 245), draw_akvan,
          "AKVAN NEARS INDIA", "204,070 evacuate; lands Fri.")

    # ---- strip ALSO TODAY ----
    sx0, sy0, sx1, sy1 = 16, 876, W - 16, 1012
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=10, fill=(20, 20, 20))
    d.text((32, sy0 + 8), "ALSO TODAY", font=font(SANS_B, 24), fill=(255, 90, 70))
    items = ("DHONI QUITS IPL  \u2022  GAZA: 70,000 TENTS FLOODED "
             "(15\u201316 NOV)")
    fnt = fit_font(SANS_B, items, 28, (sx1 - sx0) - 32, minimum=24)
    centre(d, W // 2, sy0 + 52, items, fnt, WHITE)
    # thin red rule under the strip label, echoing the masthead
    d.rectangle([32, sy0 + 40, 32 + text_w(font(SANS_B, 24), "ALSO TODAY"),
                 sy0 + 43], fill=(255, 90, 70))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
