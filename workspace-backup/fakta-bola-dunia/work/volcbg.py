#!/usr/bin/env python3
"""Background gunung berapi 100% digambar PIL untuk countryball Fakta Bola Dunia.

Scene 1080x1920: langit senja gelap gradasi + bintang berkelip, 3 siluet gunung
berapi (kiri: Merapi, tengah: Etna, kanan: Islandia) dengan kawah lava berdenyut,
asap mengepul animasi, partikel bara api beterbangan, tanah vulkanik gelap,
grain film halus. Signature sama dengan riverbg.py: draw_background(fi),
paste_ball_shadow(fr, bx, by, ball_size).
"""
import math
import random
from PIL import Image, ImageDraw
import numpy as np

W, H = 1080, 1920
rng = random.Random(20261020)

# ---------------- langit (statis, dibuat sekali) ----------------
def _make_sky():
    sky = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(sky)
    stops = [  # (pos, rgb) langit senja gelap
        (0.00, (6, 10, 30)),
        (0.35, (24, 18, 62)),
        (0.52, (80, 34, 66)),
        (0.60, (205, 95, 52)),
        (0.64, (150, 62, 44)),
        (0.70, (30, 18, 24)),
        (1.00, (14, 10, 14)),
    ]
    for y in range(H):
        t = y / H
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                u = (t - t0) / (t1 - t0) if t1 > t0 else 0
                c = tuple(int(c0[k] + (c1[k] - c0[k]) * u) for k in range(3))
                d.line([(0, y), (W, y)], fill=c)
                break
    return sky

# bintang: (x, y, radius, fase kedip)
_STARS = [(rng.uniform(0, W), rng.uniform(0, 950), rng.uniform(1.2, 3.0),
           rng.uniform(0, 2 * math.pi)) for _ in range(140)]

# ---------------- gunung berapi (siluet statis) ----------------
# (cx, base_y, tinggi, lebar_setengah)
_VOLC = [
    (-60, 1230, 430, 560),     # kiri: Merapi
    (600, 1330, 560, 720),     # tengah: Etna (paling besar)
    (1160, 1260, 470, 600),    # kanan: Eyjafjallajokull
]

def _make_volcanoes():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for cx, base, hgt, hw in _VOLC:
        top = base - hgt
        rim_w = hw * 0.30
        # tubuh gunung: segitiga berlekuk
        pts = [(cx - hw, base), (cx - rim_w, top + 20), (cx + rim_w, top + 20),
               (cx + hw, base)]
        d.polygon(pts, fill=(22, 15, 20, 255))
        # sisi gelap: arsir kanan lebih gelap
        d.polygon([(cx, base), (cx + rim_w, top + 20),
                   (cx + hw, base)], fill=(15, 10, 14, 255))
        # kawah: lekukan di puncak
        d.polygon([(cx - rim_w, top + 20), (cx - rim_w * 0.55, top + 46),
                   (cx + rim_w * 0.55, top + 46), (cx + rim_w, top + 20)],
                  fill=(10, 6, 8, 255))
    return im

_SIL = _make_volcanoes()

# lava mengalir di lereng (statis, diglow saat draw)
_LAVA = []
for cx, base, hgt, hw in _VOLC:
    top = base - hgt
    for k in range(3):
        sx = cx + (-hw * 0.12) + k * hw * 0.10
        _LAVA.append((sx, top + 46, sx + rng.uniform(-30, 30), top + 46 + rng.uniform(120, 260)))

# ---------------- tanah vulkanik (statis) ----------------
def _make_ground():
    g = Image.new("RGBA", (W, H - 1180), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    top_col = (34, 22, 26)
    bot_col = (12, 8, 10)
    gh = H - 1180
    for y in range(gh):
        u = y / gh
        c = tuple(int(top_col[k] + (bot_col[k] - top_col[k]) * u) for k in range(3))
        d.line([(0, y), (W, y)], fill=c + (255,))
    # retakan lava menyala tipis
    for _ in range(9):
        x0 = rng.uniform(40, W - 40)
        y0 = rng.uniform(0, gh)
        pts = [(x0, y0)]
        for s in range(5):
            pts.append((x0 + rng.uniform(-40, 40), y0 + rng.uniform(10, 45)))
        d.line(pts, fill=(255, 120, 30, 170), width=4)
    return g

_GROUND = _make_ground()

# ---------------- asap: per gunung (dx, fase, speed, skala) ----------------
_SMOKE = []
for cx, base, hgt, hw in _VOLC:
    for _ in range(12):
        _SMOKE.append((cx, base - hgt, rng.uniform(-hw * 0.15, hw * 0.15),
                       rng.uniform(0, 1), rng.uniform(70, 120),
                       rng.uniform(0.7, 1.4)))

# ---------------- bara api: (volcano_idx, dx, fase, speed) ----------------
_EMBERS = []
for vi, (cx, base, hgt, hw) in enumerate(_VOLC):
    for _ in range(26):
        _EMBERS.append((vi, rng.uniform(-hw * 0.25, hw * 0.25),
                        rng.uniform(0, 1), rng.uniform(90, 220),
                        rng.uniform(2, 5)))

_SKY = _make_sky()

# noise grain sekali (di-tile acak tiap frame via offset sederhana)
_GRAIN = (np.random.default_rng(7).normal(0, 3.0, (120, 68)).astype(np.float32))


def _draw_stars(fr, tsec):
    d = ImageDraw.Draw(fr, "RGBA")
    for x, y, r, ph in _STARS:
        tw = 0.45 + 0.55 * abs(math.sin(tsec * 1.6 + ph))
        a = int(150 * tw + 60)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 240, a))


def _draw_lava(fr, tsec):
    d = ImageDraw.Draw(fr, "RGBA")
    pulse = 0.65 + 0.35 * math.sin(tsec * 2.2)
    for cx, base, hgt, hw in _VOLC:
        top = base - hgt
        rim_w = hw * 0.30
        gw = rim_w * 1.05
        # kawah berdenyut
        glow = int(255 * pulse)
        d.ellipse([cx - gw, top + 6, cx + gw, top + 66],
                  fill=(255, int(90 + 90 * pulse), 20, 255))
        d.ellipse([cx - gw * 0.55, top + 18, cx + gw * 0.55, top + 54],
                  fill=(255, int(200 + 40 * pulse), 120, 255))
        # halo cahaya di sekitar kawah
        halo_r = gw * (1.6 + 0.3 * pulse)
        d.ellipse([cx - halo_r, top - halo_r * 0.5, cx + halo_r, top + halo_r * 0.9],
                  fill=(255, 110, 30, int(40 * pulse)))
    # aliran lava di lereng
    for sx, sy, ex, ey in _LAVA:
        w = 6 + int(3 * math.sin(tsec * 3 + sx))
        d.line([(sx, sy), (ex, ey)], fill=(255, int(120 * pulse + 60), 25, 235), width=w)


def _draw_smoke(fr, tsec):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for cx, top_y, dx, ph, sp, sc in _SMOKE:
        life = (tsec * sp / 420 + ph) % 1.0
        y = top_y - 40 - life * 520
        x = cx + dx + 60 * math.sin(life * 4.5 + ph * 9)
        r = int((26 + life * 120) * sc)
        a = int(150 * (1 - life) * (0.55 + 0.45 * (1 - life)))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(90, 80, 95, a))
    fr.alpha_composite(layer)


def _draw_embers(fr, tsec):
    d = ImageDraw.Draw(fr, "RGBA")
    for vi, dx, ph, sp, sz in _EMBERS:
        cx, base, hgt, hw = _VOLC[vi]
        top_y = base - hgt
        life = (tsec * sp / 520 + ph) % 1.0
        y = top_y + 30 - life * 480
        x = cx + dx + 45 * math.sin(life * 6 + ph * 12)
        flick = 0.4 + 0.6 * abs(math.sin(tsec * 9 + ph * 20))
        a = int(255 * flick * (1 - life * 0.7))
        col = (255, int(140 * flick + 60), 30, a)
        r = sz * (1 - life * 0.4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)


def draw_background(fi):
    """Kembalikan PIL Image RGB 1080x1920 untuk frame ke-fi."""
    tsec = fi / 30.0
    fr = _SKY.copy()
    _draw_stars(fr, tsec)
    fr = fr.convert("RGBA")
    fr.alpha_composite(_SIL)
    _draw_lava(fr, tsec)
    fr.alpha_composite(_GROUND, (0, 1180))
    _draw_smoke(fr, tsec)
    _draw_embers(fr, tsec)
    fr = fr.convert("RGB")
    # grain film halus (tile noise kecil)
    tile = np.tile(_GRAIN, (H // 120 + 1, W // 68 + 1))[:H, :W]
    shift = (fi * 37) % 120
    tile = np.roll(tile, shift, axis=0)
    arr = np.asarray(fr).astype(np.float32) + tile[..., None]
    np.clip(arr, 0, 255, out=arr)
    return Image.fromarray(arr.astype(np.uint8))


def paste_ball_shadow(fr, bx, by, ball_size):
    """Bayangan oval di bawah bola (bola melayang di atas tanah vulkanik)."""
    d = ImageDraw.Draw(fr, "RGBA")
    cx = bx + ball_size // 2
    cy = by + ball_size + 26
    d.ellipse([cx - 150, cy - 26, cx + 150, cy + 26], fill=(0, 0, 0, 110))
