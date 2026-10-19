#!/usr/bin/env python3
"""Background sungai 100% digambar PIL untuk countryball Fakta Bola Dunia.

Scene 1080x1920: langit gradasi + matahari + awan melayang, bukit jauh,
sungai berliku mengalir (garis arus animasi), tepi rumput + gelagah bergoyang,
pohon di bantaran. Signature sama dengan spacebg.py: draw_background(fi),
paste_ball_shadow(fr, bx, by, ball_size).
"""
import math
import random
from PIL import Image, ImageDraw

W, H = 1080, 1920

random.seed(191019)

# ---------------- langit + matahari (statis) ----------------
def _make_sky():
    sky = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(sky)
    top = (110, 180, 235)
    mid = (170, 215, 245)
    bot = (235, 245, 250)
    for y in range(H):
        t = y / H
        if t < 0.45:
            u = t / 0.45
            c = tuple(int(top[i] + (mid[i] - top[i]) * u) for i in range(3))
        else:
            u = (t - 0.45) / 0.55
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * u) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    return sky

def _make_sun():
    s = 340
    sun = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(sun)
    for r, a in [(160, 40), (130, 70), (105, 110)]:
        d.ellipse([s//2-r, s//2-r, s//2+r, s//2+r], fill=(255, 235, 150, a))
    d.ellipse([s//2-85, s//2-85, s//2+85, s//2+85], fill=(255, 245, 180, 255))
    return sun

def _make_cloud(w=300, h=110):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx, cy, r in [(w*0.25, h*0.6, h*0.38), (w*0.5, h*0.45, h*0.45),
                      (w*0.75, h*0.6, h*0.38), (w*0.5, h*0.65, h*0.35)]:
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255, 235))
    return im

def _make_hills():
    im = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx, r, col in [(120, 420, (120, 180, 130)), (520, 520, (100, 165, 120)),
                       (950, 460, (125, 185, 135))]:
        d.ellipse([cx-r, 420-r*0.55, cx+r, 420+r*0.55], fill=col + (255,))
    return im

def _make_tree():
    im = Image.new("RGBA", (220, 300), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([100, 170, 120, 300], fill=(120, 80, 50, 255))
    for cx, cy, r in [(110, 120, 80), (60, 160, 55), (160, 160, 55), (110, 70, 60)]:
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(60, 150, 80, 255))
    for cx, cy, r in [(90, 100, 40), (130, 140, 35)]:
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(80, 175, 95, 255))
    return im

def _make_grass_tuft():
    im = Image.new("RGBA", (90, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (x0, x1, h) in enumerate([(10, 30, 100), (30, 45, 120),
                                     (50, 60, 105), (65, 80, 115)]):
        d.polygon([(x0, 120), ((x0+x1)//2, 120-h), (x1, 120)],
                  fill=(70, 160, 80, 255))
    return im

_SKY = _make_sky()
_SUN = _make_sun()
_CLOUDS = [_make_cloud(300, 110), _make_cloud(220, 90), _make_cloud(360, 130)]
_HILLS = _make_hills()
_TREE = _make_tree()
_TUFT = _make_grass_tuft()
_CLOUD_POS = [(120, 180, 22), (650, 420, 14), (380, 90, 30)]  # x, y, speed px/dtk

# sungai: tepi kiri/kanan berliku (fungsi y)
def _edge_l(y):
    return 300 + 90 * math.sin(y * 0.004 + 1.2) - y * 0.06

def _edge_r(y):
    return 780 + 90 * math.sin(y * 0.004 + 3.6) + y * 0.04

# garis arus: daftar (x_frac, y0, panjang, speed)
_ARUS = [(random.random(), random.uniform(600, 1900),
          random.uniform(60, 140), random.uniform(90, 160))
         for _ in range(26)]

_TREES = [(90, 950), (930, 700), (60, 1500), (950, 1550), (830, 1150)]
_TUFTS = [(random.uniform(0, 240), random.uniform(750, 1900)) for _ in range(14)] + \
         [(random.uniform(840, 1040), random.uniform(750, 1900)) for _ in range(14)]


def _draw_river(fr, fi):
    d = ImageDraw.Draw(fr, "RGBA")
    # badan air
    pts_l = [(_edge_l(y), y) for y in range(640, H + 40, 20)]
    pts_r = [(_edge_r(y), y) for y in range(640, H + 40, 20)]
    for y in range(640, H):
        t = (y - 640) / (H - 640)
        c = (int(60 + 40 * t), int(150 + 30 * t), int(215 + 25 * t))
        xl, xr = _edge_l(y), _edge_r(y)
        d.line([(xl, y), (xr, y)], fill=c + (255,), width=3)
    # tepian rumput: isi area luar sungai di bawah bukit
    for y in range(640, H):
        t = (y - 640) / (H - 640)
        g = (int(90 + 40 * t), int(175 + 30 * t), int(95 + 25 * t))
        xl, xr = _edge_l(y), _edge_r(y)
        d.line([(0, y), (xl, y)], fill=g + (255,), width=3)
        d.line([(xr, y), (W, y)], fill=g + (255,), width=3)
    # highlight permukaan: garis arus putih bergerak ke bawah
    tsec = fi / 30.0
    for xf, y0, ln, sp in _ARUS:
        y = 640 + ((y0 - 640 + tsec * sp) % (H - 640))
        xl, xr = _edge_l(y), _edge_r(y)
        x = xl + xf * (xr - xl)
        a = 110
        d.line([(x, y), (x, y + ln)], fill=(255, 255, 255, a), width=5)
    # riak horizontal sesekali
    for k in range(8):
        yb = 700 + k * 150
        y = yb + int(18 * math.sin(tsec * 1.5 + k * 1.7))
        xl, xr = _edge_l(y), _edge_r(y)
        for s in range(3):
            xs = xl + (xr - xl) * (0.2 + 0.3 * s) + 20 * math.sin(tsec + k + s)
            d.arc([xs - 40, y - 12, xs + 40, y + 12], start=200, end=340,
                  fill=(255, 255, 255, 90), width=4)


def draw_background(fi):
    """Kembalikan PIL Image RGB 1080x1920 untuk frame ke-fi."""
    fr = _SKY.copy()
    # matahari
    fr.paste(_SUN, (830 - 170, 130), _SUN)
    # awan melayang
    tsec = fi / 30.0
    for (x0, y, sp), cl in zip(_CLOUD_POS, _CLOUDS):
        x = int((x0 + tsec * sp) % (W + 400)) - 200
        fr.paste(cl, (x, y), cl)
    # bukit jauh
    fr.paste(_HILLS, (0, 480), _HILLS)
    _draw_river(fr, fi)
    # pohon di bantaran
    for tx, ty in _TREES:
        fr.paste(_TREE, (tx, ty), _TREE)
    # gelagah bergoyang di tepi sungai
    for gx, gy in _TUFTS:
        sway = int(10 * math.sin(tsec * 2.0 + gx * 0.05))
        fr.paste(_TUFT, (int(gx) + sway, int(gy)), _TUFT)
    return fr.convert("RGB")


def paste_ball_shadow(fr, bx, by, ball_size):
    """Bayangan oval di bawah bola (bola melayang di atas sungai)."""
    d = ImageDraw.Draw(fr, "RGBA")
    cx = bx + ball_size // 2
    cy = by + ball_size + 26
    d.ellipse([cx - 150, cy - 26, cx + 150, cy + 26], fill=(20, 40, 60, 90))
