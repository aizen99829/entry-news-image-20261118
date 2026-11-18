#!/usr/bin/env python3
"""Render the news poster for Wednesday 18 November 2026.

One 1024x1024 PNG, drawn with PIL + DejaVu fonts. No network, no
randomness (star positions are a fixed list), so re-runs are byte-identical.

Layout (1024x1024):
  masthead 0-116 | hero 124-476 | grid 2x2 488-864 | strip 876-1012
Word budget: 62 words total (R3, counted in BUILD-R3.md).
R3 changes (from JUDGE-R2.md, all cheap, no redesign): masthead
title "THE WORLD IN ONE DAY" restored (+5 words, paid by dropping
"Meets" from the Trump sub and "Huang not back" -> "Huang out");
hero drone blunt nose + front canards; radar panel near-vertical
with a rotating-base disc; minimal face on the Trump bust;
interceptor given a big orange flame + yellow core and shifted
~15px clear of the ship's mast; "hits Fri." -> "lands Fri."
(trailing period dropped: 491px at 28px vs 486px panel, 480px
without it — font floor is 28px, so the period is the price);
Kerch smoke as a rising column of elongated puffs; PERSIAN GULF
label 28px + dark outline, waves shifted right so they never
cross it.
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
    """Night sky over the Gulf: radar array + headland left, big
    delta-wing drone centre, orange explosion right, warship on the
    sea below, PERSIAN GULF sea label."""
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
    # --- coastline headland + airbase strip, bottom left (Bahrain) ---
    d.polygon([(x0, y1), (x0, sea_y + 8), (x0 + 120, sea_y + 18),
               (x0 + 210, sea_y + 4), (x0 + 250, y1)], fill=(96, 88, 66))
    d.line([(x0 + 36, sea_y + 24), (x0 + 150, sea_y + 16)],
           fill=(210, 205, 190), width=4)
    d.line([(x0 + 180, sea_y + 10), (x0 + 180, sea_y - 14)],
           fill=(200, 200, 200), width=3)
    d.ellipse([x0 + 175, sea_y - 20, x0 + 185, sea_y - 10],
              fill=(255, 60, 60))
    # waves (start right of the Gulf label so they never cross it;
    # R3: label grew to 28px, so waves start further right)
    for wx in range(x0 + 540, x1 - 20, 90):
        d.arc([wx, sea_y + 12, wx + 70, sea_y + 34], 180, 360,
              fill=(120, 170, 220), width=4)
    # sea label, map-style, in the water right of the headland
    # (R3: 24 -> 28px + dark outline so it survives the 300px
    # downscale, where it was only faint in R2)
    d.text((x0 + 265, sea_y + 14), "PERSIAN GULF", font=font(SANS_B, 28),
           fill=(150, 190, 230), stroke_width=2, stroke_fill=(8, 28, 58))
    # --- radar array, left: mast + turntable disc + near-vertical
    # phased-array panel (R3: panel upright so it reads as radar,
    # not a solar panel/billboard; the rotating base makes the
    # radar reading explicit) ---
    bx, by = x0 + 110, sea_y + 16         # mast base, on the headland
    d.line([(bx, by), (bx, by - 58)], fill=(200, 200, 200), width=7)
    d.line([(bx - 26, by), (bx + 26, by)], fill=(200, 200, 200), width=6)
    # rotating base: flat turntable disc the panel sits on
    d.ellipse([bx - 20, by - 66, bx + 20, by - 54], fill=(160, 160, 160),
              outline=(90, 90, 90))
    d.line([(bx, by - 54), (bx, by - 64)], fill=(200, 200, 200), width=5)
    # near-vertical rectangular panel (slight tilt only), with grid lines
    d.polygon([(bx - 30, by - 104), (bx + 22, by - 110), (bx + 28, by - 68),
               (bx - 24, by - 62)], fill=(225, 225, 225),
              outline=(90, 90, 90))
    d.line([(bx - 28, by - 86), (bx + 25, by - 90)], fill=(150, 150, 150),
           width=2)
    d.line([(bx - 4, by - 103), (bx + 2, by - 65)], fill=(150, 150, 150),
           width=2)
    # thin sweep line up-right (no big wedge: R1 beam dominated)
    d.line([(bx + 22, by - 110), (bx + 150, by - 182)],
           fill=(240, 220, 120), width=3)
    d.ellipse([bx + 146, by - 186, bx + 154, by - 178],
              fill=(240, 220, 120))
    # --- military delta-wing drone (Shahed-style flying wing), centre ---
    # No rotors, no nav lights: a flat dark flying wing with a BLUNT
    # nose (R3: the sharp point read as a stealth jet / paper plane)
    # and small front canards, plus a rear pusher prop and tail fin.
    cx, cy = 500, 222
    d.polygon([(cx + 106, cy - 9), (cx + 106, cy + 9), (cx - 80, cy + 44),
               (cx - 62, cy), (cx - 80, cy - 44)], fill=(45, 45, 45),
              outline=(220, 220, 220))
    d.line([(cx + 106, cy), (cx - 62, cy)], fill=(140, 140, 140), width=3)
    # small canards fore of the wing, above and below the fuselage line
    d.polygon([(cx + 56, cy - 4), (cx + 80, cy - 24), (cx + 88, cy - 4)],
              fill=(60, 60, 60), outline=(200, 200, 200))
    d.polygon([(cx + 56, cy + 4), (cx + 80, cy + 24), (cx + 88, cy + 4)],
              fill=(60, 60, 60), outline=(200, 200, 200))
    d.polygon([(cx - 62, cy - 6), (cx - 40, cy - 30), (cx - 30, cy - 6)],
              fill=(60, 60, 60), outline=(200, 200, 200))
    d.ellipse([cx - 30, cy - 10, cx + 10, cy + 10], fill=(90, 90, 90),
              outline=(220, 220, 220))
    # interceptor missile climbing at the drone from the warship
    # below: white body streak, BIG orange flame + yellow core at
    # the rear (R3: the old small flame read as an antenna; the
    # whole missile is shifted ~15px left of the ship's mast so it
    # no longer merges with it)
    d.line([(cx + 76, cy + 26), (cx + 140, cy + 70)], fill=WHITE, width=6)
    d.ellipse([cx + 68, cy + 18, cx + 84, cy + 34], fill=WHITE)
    d.ellipse([cx + 134, cy + 64, cx + 158, cy + 88], fill=(255, 110, 0))
    d.ellipse([cx + 140, cy + 70, cx + 152, cy + 82], fill=(255, 190, 40))
    d.ellipse([cx + 152, cy + 80, cx + 164, cy + 92], fill=(120, 120, 120))
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
    # small second drone, top right: same delta-wing shape (blunt
    # nose, R3), smaller, with a short white contrail behind it
    sx, sy = 760, 165
    d.line([(sx - 78, sy + 12), (sx - 42, sy + 4)], fill=WHITE, width=3)
    d.polygon([(sx + 34, sy - 5), (sx + 34, sy + 5), (sx - 28, sy + 16),
               (sx - 22, sy), (sx - 28, sy - 16)], fill=(45, 45, 45),
              outline=(220, 220, 220))
    d.ellipse([sx - 34, sy - 4, sx - 24, sy + 4], fill=(170, 170, 170))
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
    # (bigger than R1: the collapse must read at 300px)
    d.polygon([(mid - 40, deck_y + 8), (mid + 36, deck_y + 20),
               (mid + 26, deck_y + 36), (mid - 48, deck_y + 24)],
              fill=(40, 40, 40))
    for sx in (mid - 52, mid - 12, mid + 28):
        d.arc([sx, sea_y - 14, sx + 36, sea_y + 10], 180, 360,
              fill=WHITE, width=5)
    # smoke plume over the gap: a rising, slightly leaning column
    # of elongated puffs (taller than wide, R3: R2's four round
    # balls still read as balloons), dark at the base where it
    # leaves the fallen deck, paler as it rises. Clearly anchored
    # to the wreck, not a disc.
    for sx, sy, rx, ry, col in [
            (mid - 14, deck_y - 2, 13, 17, (70, 70, 70)),
            (mid + 8, deck_y - 10, 14, 19, (90, 90, 90)),
            (mid - 4, deck_y - 24, 11, 17, (110, 110, 110)),
            (mid + 12, deck_y - 33, 9, 14, (130, 130, 130)),
            (mid - 1, deck_y - 38, 7, 10, (150, 150, 150))]:
        d.ellipse([sx - rx, sy - ry, sx + rx, sy + ry], fill=col)


def draw_trump(d, x0, y0, x1, y1):
    """Trump bust (blond hair, navy suit, red tie) at left, Air Force
    One small and high, and the four Quad flags redrawn correctly
    along the bottom: US (stripes + blue canton with star dots),
    Japan (red disc), Australia (blue ensign: Union Jack canton +
    Southern Cross dots), India (saffron/white/green)."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 238, 245))
    # --- figure, left: navy suit, white shirt, red tie, blond hair ---
    fx = x0 + 52
    d.polygon([(fx - 38, y1 - 2), (fx + 38, y1 - 2), (fx + 26, y0 + 44),
               (fx - 26, y0 + 44)], fill=(25, 45, 90))
    d.polygon([(fx - 10, y0 + 44), (fx + 10, y0 + 44), (fx, y0 + 62)],
              fill=(255, 255, 255))
    d.polygon([(fx - 4, y0 + 48), (fx + 4, y0 + 48), (fx + 6, y0 + 72),
               (fx - 6, y0 + 72)], fill=(178, 34, 34))
    d.rectangle([fx - 8, y0 + 34, fx + 8, y0 + 46], fill=(232, 190, 150))
    d.ellipse([fx - 15, y0 + 8, fx + 15, y0 + 38], fill=(232, 190, 150))
    d.pieslice([fx - 15, y0 + 8, fx + 15, y0 + 38], 180, 360,
               fill=(240, 210, 90))
    d.polygon([(fx - 15, y0 + 22), (fx + 15, y0 + 22), (fx + 13, y0 + 12),
               (fx - 13, y0 + 12)], fill=(240, 210, 90))
    # minimal face (R3: R2's blank skin block read as a mannequin):
    # two eyes, a short nose line, a mouth line — no detailed
    # portrait, just enough to read as a human face at 1024px
    d.ellipse([fx - 8, y0 + 25, fx - 4, y0 + 29], fill=(60, 40, 30))
    d.ellipse([fx + 4, y0 + 25, fx + 8, y0 + 29], fill=(60, 40, 30))
    d.line([(fx, y0 + 27), (fx - 1, y0 + 31)], fill=(160, 120, 90), width=2)
    d.line([(fx - 4, y0 + 33), (fx + 4, y0 + 33)], fill=(120, 60, 50),
           width=2)
    # --- plane: smaller, top-right ---
    cx = x0 + 300
    py = y0 + 22
    d.ellipse([cx - 85, py - 9, cx + 85, py + 9], fill=(30, 90, 160))
    d.polygon([(cx + 66, py - 7), (cx + 96, py - 32), (cx + 96, py - 5)],
              fill=(30, 90, 160))
    d.polygon([(cx - 6, py + 5), (cx + 28, py + 5), (cx + 48, py + 17),
               (cx + 14, py + 17)], fill=(20, 60, 120))
    d.polygon([(cx - 32, py - 5), (cx - 6, py - 5), (cx - 18, py - 15),
               (cx - 38, py - 15)], fill=(20, 60, 120))
    for wx in range(cx - 68, cx + 56, 18):
        d.ellipse([wx, py - 3, wx + 6, py + 3], fill=WHITE)
    # --- four Quad flags on poles along the bottom ---
    fy = y1 - 4
    # US: red field, white stripes, blue canton with star dots
    fx = x0 + 128
    d.line([(fx, fy), (fx, fy - 22)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 22, fx + 56, fy], fill=(178, 34, 34))
    for wy in (fy - 19, fy - 13, fy - 6):
        d.rectangle([fx, wy, fx + 56, wy + 3], fill=WHITE)
    d.rectangle([fx, fy - 22, fx + 22, fy - 11], fill=(0, 40, 110))
    for sx in (fx + 4, fx + 11, fx + 18):
        for sy in (fy - 19, fy - 14):
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
    # Japan: white with red dot
    fx += 88
    d.line([(fx, fy), (fx, fy - 22)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 22, fx + 56, fy], fill=WHITE,
                outline=(60, 60, 60))
    d.ellipse([fx + 21, fy - 17, fx + 35, fy - 5], fill=(200, 40, 40))
    # Australia: blue ensign — Union Jack canton + Southern Cross
    fx += 88
    d.line([(fx, fy), (fx, fy - 22)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 22, fx + 56, fy], fill=(0, 40, 110))
    d.line([(fx, fy - 22), (fx + 26, fy - 11)], fill=WHITE, width=2)
    d.line([(fx + 26, fy - 22), (fx, fy - 11)], fill=WHITE, width=2)
    d.line([(fx + 13, fy - 22), (fx + 13, fy - 11)], fill=WHITE, width=3)
    d.line([(fx, fy - 16), (fx + 26, fy - 16)], fill=WHITE, width=3)
    d.line([(fx + 13, fy - 22), (fx + 13, fy - 11)], fill=(200, 40, 40),
           width=2)
    d.line([(fx, fy - 16), (fx + 26, fy - 16)], fill=(200, 40, 40), width=2)
    d.ellipse([fx + 30, fy - 8, fx + 36, fy - 2], fill=WHITE)
    for sx, sy in [(fx + 45, fy - 16), (fx + 49, fy - 10), (fx + 41, fy - 6),
                    (fx + 50, fy - 19)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=WHITE)
    # India: saffron / white / green
    fx += 88
    d.line([(fx, fy), (fx, fy - 22)], fill=(60, 60, 60), width=4)
    d.rectangle([fx, fy - 22, fx + 56, fy - 15], fill=(255, 153, 51))
    d.rectangle([fx, fy - 15, fx + 56, fy - 8], fill=WHITE)
    d.rectangle([fx, fy - 8, fx + 56, fy - 1], fill=(0, 130, 60))


def draw_nvidia(d, x0, y0, x1, y1):
    """Green GPU chip + steep rising arrow. R2: chip shrunk to fit
    its 80px icon zone (R1 pins crossed the panel top and cut the
    headline); pins now stop 2px inside the zone, 10px clear of
    the headline below."""
    d.rectangle([x0, y0, x1, y1], fill=(222, 243, 214))
    cx = (x0 + x1) // 2 - 90
    cy = (y0 + y1) // 2
    # chip pins (stop at cy +/- 38: zone half-height is 40)
    for px in range(cx - 44, cx + 45, 16):
        d.line([(px, cy - 30), (px, cy - 38)], fill=(40, 90, 20), width=4)
        d.line([(px, cy + 30), (px, cy + 38)], fill=(40, 90, 20), width=4)
    for py in range(cy - 30, cy + 31, 16):
        d.line([(cx - 30, py), (cx - 38, py)], fill=(40, 90, 20), width=4)
        d.line([(cx + 30, py), (cx + 38, py)], fill=(40, 90, 20), width=4)
    d.rounded_rectangle([cx - 30, cy - 30, cx + 30, cy + 30], radius=8,
                        fill=(118, 185, 0))
    d.rounded_rectangle([cx - 16, cy - 16, cx + 16, cy + 16], radius=5,
                        fill=(30, 90, 20))
    # rising arrow, right side
    ax0, ay1 = cx + 92, y1 - 8
    d.line([(ax0, ay1), (ax0 + 52, ay1 - 30), (ax0 + 104, ay1 - 46),
            (ax0 + 150, ay1 - 64)], fill=(20, 120, 20), width=9)
    d.polygon([(ax0 + 150, ay1 - 64), (ax0 + 118, ay1 - 64),
               (ax0 + 150, ay1 - 32)], fill=(20, 120, 20))


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

    # ---- masthead: nameplate title restored (R3: R2 dropped it to
    # pay the word budget and left empty cream above the date) + date
    # Title is flanked by thin rules, newspaper-nameplate style.
    # Word budget: +5 words for the title, paid by dropping "Meets"
    # from the Trump sub and shortening "Huang not back" to "Huang
    # out" (see panels below) — total stays at 62 words. ----
    title = "THE WORLD IN ONE DAY"
    tf = font(SANS_B, 24)
    tw = text_w(tf, title)
    centre(d, W // 2, 6, title, tf, INK)
    d.line([(16, 18), (W // 2 - tw // 2 - 20, 18)], fill=INK, width=2)
    d.line([(W // 2 + tw // 2 + 20, 18), (W - 16, 18)], fill=INK, width=2)
    centre(d, W // 2, 36, "WEDNESDAY 18 NOVEMBER 2026",
           font(SERIF_B, 50), INK)
    d.rectangle([16, 106, W - 16, 112], fill=RED)

    # ---- hero ----
    hx0, hy0, hx1, hy1 = 16, 124, W - 16, 476
    d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=10, outline=INK, width=2)
    draw_hero(d, hx0 + 2, hy0 + 2, hx1 - 2, hy0 + 236)
    d.rectangle([hx0 + 2, hy0 + 236, hx1 - 2, hy0 + 302], fill=NAVY)
    centre(d, W // 2, hy0 + 246, "DRONES OVER BAHRAIN",
           font(SANS_B, 54), WHITE)
    centre(d, W // 2, hy0 + 312, "Iran drones stopped; US hits Qeshm.",
           font(SANS_B, 30), INK)

    # ---- grid 2x2 ----
    panel(d, 16, 488, 502, 672, (214, 228, 240), draw_kerch,
          "KERCH DOWN (17 NOV)", "Ukraine strike; 270m falls.")
    panel(d, 522, 488, 1008, 672, (232, 238, 245), draw_trump,
          "TRUMP IN MANILA", "Marcos; Xi\u2013Putin Thu.")
    panel(d, 16, 680, 502, 864, (222, 243, 214), draw_nvidia,
          "NVIDIA: REVENUE $115.8BN", "Up 103%; Huang out.")
    panel(d, 522, 680, 1008, 864, (198, 224, 245), draw_akvan,
          "AKVAN NEARS INDIA", "204,070 to evacuate; lands Fri")

    # ---- strip ALSO TODAY: two full-size lines (28px) instead of
    # one cramped line — fills the dead black space R1 left below
    # the single line, and carries the (17 NOV) label for Dhoni ----
    sx0, sy0, sx1, sy1 = 16, 876, W - 16, 1012
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=10, fill=(20, 20, 20))
    d.text((32, sy0 + 8), "ALSO TODAY", font=font(SANS_B, 24), fill=(255, 90, 70))
    # thin red rule under the strip label, echoing the masthead
    d.rectangle([32, sy0 + 40, 32 + text_w(font(SANS_B, 24), "ALSO TODAY"),
                 sy0 + 43], fill=(255, 90, 70))
    centre(d, W // 2, sy0 + 50, "DHONI QUITS IPL (17 NOV)",
           font(SANS_B, 28), WHITE)
    centre(d, W // 2, sy0 + 92, "GAZA: 70,000 TENTS FLOODED "
           "(15\u201316 NOV)", font(SANS_B, 28), WHITE)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
