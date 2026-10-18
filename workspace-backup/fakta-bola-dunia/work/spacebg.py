#!/usr/bin/env python3
"""Background luar angkasa 100% digambar PIL untuk countryball Fakta Bola Dunia.

Scene 1080x1920: gradasi gelap statis, 2 layer bintang berkelip (parallax
scrolling ke bawah), 1 planet + cincin (bergerak pelan), sesekali bintang
jatuh. Signature sama dengan gamebg.py: draw_background(fi), paste_ball_shadow.
"""
import math
import random
from PIL import Image, ImageDraw

W, H = 1080, 1920

random.seed(7)

# ---------------- gradasi langit statis ----------------
def _make_space():
    sky = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(sky)
    top = (8, 10, 40)
    bot = (30, 16, 70)
    for y in range(H):
        t = y / H
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # nebula halus: 2 blob ungu/biru transparan
    neb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(neb)
    for cx, cy, r, col in [(250, 500, 320, (120, 60, 200, 26)),
                           (820, 1300, 380, (60, 120, 220, 22)),
                           (700, 300, 260, (180, 80, 200, 20))]:
        for rr in range(r, 0, -12):
            a = int(col[3] * (1 - rr / r))
            nd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(col[0], col[1], col[2], a))
    sky = Image.alpha_composite(sky.convert("RGBA"), neb).convert("RGB")
    return sky

def _twinkle(ph, fi):
    """Faktor kecerahan bintang dari fase + frame."""
    return 0.35 + 0.65 * (0.5 + 0.5 * math.sin(fi * 0.12 + ph))

# ---------------- planet + cincin ----------------
def _make_planet():
    s = 460
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s // 2
    # cincin (belakang)
    d.ellipse([c-210, c-60, c+210, c+60], fill=(150, 170, 200, 90))
    d.ellipse([c-170, c-42, c+170, c+42], fill=(0, 0, 0, 0))
    # badan planet
    d.ellipse([c-130, c-130, c+130, c+130], fill=(90, 140, 210))
    # bayangan sisi
    for i in range(40):
        a = int(90 * (i / 40))
        d.ellipse([c-130+i*2, c-130, c+130, c+130], outline=(20, 30, 70, a), width=2)
    # garis daratan
    for gy, gw in [(-50, 90), (10, 110), (70, 70)]:
        d.ellipse([c-gw, c+gy-18, c+gw, c+gy+18], fill=(120, 180, 120))
    # cincin (depan)
    d.ellipse([c-210, c-40, c+210, c+40], outline=(200, 210, 230, 160), width=14)
    d.ellipse([c-190, c-30, c+190, c+30], outline=(170, 185, 210, 120), width=8)
    return im

def _make_blob():
    s = 560
    blob = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    for r in range(s // 2, 0, -6):
        a = int(70 * (1 - r / (s / 2)))
        if a > 0:
            d.ellipse([s/2-r, s/2-r, s/2+r, s/2+r], fill=(5, 5, 20, a))
    return blob

_SKY = _make_space()
_PLANET = _make_planet()
_BLOB = _make_blob()

# daftar bintang: (x, y_base, phase, size, layer_speed)
def _make_stars(seed, n, sizes, speed):
    rng = random.Random(seed)
    return [(rng.uniform(0, W), rng.uniform(0, H),
             rng.uniform(0, 2*math.pi), rng.choice(sizes), speed)
            for _ in range(n)]

_STARS_FAR = _make_stars(11, 130, (1, 2), 0.6)    # kecil, lambat
_STARS_NEAR = _make_stars(22, 60, (2, 3, 4), 1.6)  # besar, cepat

def draw_background(fi):
    """Kembalikan PIL Image RGB 1080x1920 untuk frame ke-fi."""
    fr = _SKY.copy()
    d = ImageDraw.Draw(fr, "RGBA")
    # 2 layer bintang: scroll ke bawah, berkelip
    for (x, y0, ph, s, speed) in (_STARS_FAR + _STARS_NEAR):
        y = (y0 + fi * speed) % H
        tw = _twinkle(ph, fi)
        br = int(255 * tw)
        d.ellipse([x-s, y-s, x+s, y+s], fill=(br, br, int(255*tw+10*(1-tw)), 255))
        if s >= 3 and tw > 0.85:
            # cross flare untuk bintang terang
            l = s + 5
            d.line([(x-l, y), (x+l, y)], fill=(255, 255, 255, 200), width=2)
            d.line([(x, y-l), (x, y+l)], fill=(255, 255, 255, 200), width=2)
    # planet: melayang pelan, bobbing
    px, py = 780, 260 + int(40 * math.sin(fi * 0.02))
    ps = _PLANET.size[0]
    fr.paste(_PLANET, (px - ps//2, py - ps//2), _PLANET)
    # bintang jatuh: tiap ~7 detik, durasi 0.8s, lintasan diagonal
    cyc = 210  # 7 detik @30fps
    ph = fi % cyc
    if 150 <= ph < 174:
        t = (ph - 150) / 24.0
        sx = 900 - t * 700
        sy = 120 + t * 420
        tail = 130
        for k in range(tail, 0, -6):
            kk = k / tail
            xx = sx + kk * 90
            yy = sy - kk * 55
            a = int(230 * kk * (1 - t * 0.4))
            if a > 0:
                d.ellipse([xx-3, yy-3, xx+3, yy+3], fill=(255, 255, 255, a))
        d.ellipse([sx-6, sy-6, sx+6, sy+6], fill=(255, 255, 255, 255))
    return fr

def paste_ball_shadow(fr, bx, by, ball_size):
    """Bayangan lembut di belakang bola agar terbaca jelas.
    bx,by = kiri-atas bola; ball_size = diameter."""
    s = _BLOB.size[0]
    cx = bx + ball_size // 2 - s // 2
    cy = by + ball_size // 2 - s // 2
    fr.paste(_BLOB, (cx, cy), _BLOB)
