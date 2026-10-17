#!/usr/bin/env python3
"""Background animasi gaya gameplay (Minecraft/Roblox-like) 100% digambar via PIL.

Scene 1080x1920, 3 layer parallax scrolling seamless:
  langit (statis + awan lambat) -> bukit/pohon (sedang) -> tanah (cepat)
Plus: air berkilau, karakter kotak jalan, partikel orb melayang.
"""
import math
import random
from PIL import Image, ImageDraw

W, H = 1080, 1920
HORIZON = 1250          # garis atas tanah
CLOUD_Y = 60
HILL_H = 340
GROUND_H = H - HORIZON  # 670

random.seed(42)

# ---------------- langit (statis) ----------------
def _make_sky():
    sky = Image.new("RGB", (W, HORIZON))
    d = ImageDraw.Draw(sky)
    top = (86, 165, 248)
    bot = (172, 226, 255)
    for y in range(HORIZON):
        t = y / HORIZON
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # matahari kotak + glow
    sx, sy, ss = 830, 170, 110
    glow = Image.new("RGBA", (ss * 3, ss * 3), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(ss * 3 // 2, 0, -10):
        a = int(55 * (1 - r / (ss * 1.5)))
        if a > 0:
            gd.ellipse([ss * 1.5 - r, ss * 1.5 - r, ss * 1.5 + r, ss * 1.5 + r],
                       fill=(255, 242, 150, a))
    sky.paste(glow, (int(sx - ss * 0.5), int(sy - ss * 0.5)), glow)
    d2 = ImageDraw.Draw(sky)
    d2.rectangle([sx, sy, sx + ss, sy + ss], fill=(255, 214, 64))
    d2.rectangle([sx, sy, sx + ss, sy + ss], outline=(228, 178, 32), width=6)
    return sky


# ---------------- tile seamless ----------------
def _seamless_tile(width, height, draw_fn):
    """draw_fn(d, xoff, width, height): gambar elemen di xoff+local_x.
    Dipanggil 3x lalu crop sepertiga tengah -> tile seamless."""
    wide = Image.new("RGBA", (width * 3, height), (0, 0, 0, 0))
    for k in range(3):
        draw_fn(ImageDraw.Draw(wide), k * width, width, height)
    return wide.crop((width, 0, width * 2, height))


def _draw_clouds(d, xoff, width, height):
    for i in range(8):
        lx = random.Random(100 + i).uniform(-160, width + 160)
        ly = random.Random(200 + i).uniform(10, height - 140)
        n = random.Random(300 + i).randint(3, 6)
        for j in range(n):
            ox = random.Random(400 + i * 10 + j).uniform(-70, 70)
            oy = random.Random(500 + i * 10 + j).uniform(-25, 25)
            s = random.Random(600 + i * 10 + j).uniform(45, 95)
            x, y = xoff + lx + ox, ly + oy
            d.rectangle([x, y, x + s, y + s * 0.62], fill=(255, 255, 255, 235))
        # bayangan bawah awan
        d.rectangle([xoff + lx - 70, ly + 42, xoff + lx + 70, ly + 58],
                    fill=(215, 232, 248, 235))


def _draw_hills(d, xoff, width, height):
    # bukit: ellipse hijau tua berderet
    rng = random.Random(77)
    x = -120
    while x < width + 120:
        bw = rng.uniform(260, 460)
        bh = rng.uniform(150, 260)
        y0 = height - bh
        d.ellipse([xoff + x, y0, xoff + x + bw, y0 + bh * 2],
                  fill=(74, 148, 74, 255))
        x += bw * rng.uniform(0.55, 0.8)
    # bukit muda di depan
    rng = random.Random(78)
    x = -100
    while x < width + 100:
        bw = rng.uniform(180, 320)
        bh = rng.uniform(90, 160)
        y0 = height - bh
        d.ellipse([xoff + x, y0, xoff + x + bw, y0 + bh * 2],
                  fill=(102, 178, 92, 255))
        x += bw * rng.uniform(0.6, 0.9)
    # pohon kotak
    rng = random.Random(79)
    for i in range(5):
        lx = rng.uniform(-60, width + 60)
        base = height - rng.uniform(40, 120)
        tw, th = 34, 110
        d.rectangle([xoff + lx - tw / 2, base - th, xoff + lx + tw / 2, base],
                    fill=(122, 84, 48, 255))
        d.rectangle([xoff + lx - tw / 2, base - th, xoff + lx + tw / 2, base],
                    outline=(90, 60, 32, 255), width=3)
        ls = 120  # ukuran daun
        ly = base - th - ls + 20
        d.rectangle([xoff + lx - ls / 2, ly, xoff + lx + ls / 2, ly + ls],
                    fill=(52, 140, 52, 255))
        d.rectangle([xoff + lx - ls / 2, ly, xoff + lx + ls / 2, ly + ls],
                    outline=(34, 110, 34, 255), width=4)
        # highlight daun
        d.rectangle([xoff + lx - ls / 2 + 12, ly + 12,
                     xoff + lx - ls / 2 + 44, ly + 44], fill=(86, 170, 86, 255))


def _draw_ground(d, xoff, width, height):
    # tanah coklat
    d.rectangle([xoff - 4, 0, xoff + width + 4, height], fill=(148, 101, 62, 255))
    rng = random.Random(55)
    # speckle tanah
    for i in range(260):
        lx = rng.uniform(-20, width + 20)
        ly = rng.uniform(50, height)
        s = rng.uniform(14, 26)
        col = (118, 78, 44, 255) if rng.random() < 0.6 else (170, 122, 78, 255)
        d.rectangle([xoff + lx, ly, xoff + lx + s, ly + s], fill=col)
    # kerikil abu
    for i in range(24):
        lx = rng.uniform(-20, width + 20)
        ly = rng.uniform(80, height - 20)
        s = rng.uniform(12, 22)
        d.rectangle([xoff + lx, ly, xoff + lx + s, ly + s], fill=(140, 140, 140, 255))
    # kolam air: x lokal 700..950
    px0, px1 = 700, 950
    d.rectangle([xoff + px0, 0, xoff + px1, 130], fill=(56, 132, 228, 255))
    d.rectangle([xoff + px0, 0, xoff + px1, 26], fill=(120, 180, 245, 255))
    # rumput di atas tanah (digambar setelah air agar menutup tepi)
    d.rectangle([xoff - 4, 0, xoff + width + 4, 44], fill=(96, 186, 72, 255))
    for i in range(120):
        lx = rng.uniform(-20, width + 20)
        s = rng.uniform(12, 24)
        gy = rng.uniform(0, 36)
        col = (74, 158, 56, 255) if rng.random() < 0.5 else (120, 205, 92, 255)
        d.rectangle([xoff + lx, gy, xoff + lx + s, gy + 10], fill=col)
    # rumput menjuntai
    for i in range(60):
        lx = rng.uniform(-20, width + 20)
        d.rectangle([xoff + lx, 44, xoff + lx + 12, 44 + rng.uniform(10, 26)],
                    fill=(74, 158, 56, 255))


# ---------------- karakter kotak jalan ----------------
def _make_walker():
    frames = []
    for leg in (0, 1):
        im = Image.new("RGBA", (110, 170), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        # kaki (bergantian)
        leg_col = (60, 60, 70)
        if leg == 0:
            d.rectangle([28, 120, 50, 168], fill=leg_col)
            d.rectangle([60, 112, 82, 160], fill=leg_col)
        else:
            d.rectangle([28, 112, 50, 160], fill=leg_col)
            d.rectangle([60, 120, 82, 168], fill=leg_col)
        # badan biru
        d.rectangle([20, 62, 90, 122], fill=(52, 120, 220, 255))
        d.rectangle([20, 62, 90, 122], outline=(30, 80, 170, 255), width=4)
        # lengan (ayun berlawanan dengan kaki)
        arm = -8 if leg == 0 else 8
        d.rectangle([8, 66 + arm, 24, 110 + arm], fill=(240, 200, 150, 255))
        d.rectangle([86, 66 - arm, 102, 110 - arm], fill=(240, 200, 150, 255))
        # kepala kotak
        d.rectangle([25, 6, 85, 62], fill=(240, 200, 150, 255))
        d.rectangle([25, 6, 85, 62], outline=(200, 160, 115, 255), width=4)
        # mata pixel
        d.rectangle([38, 28, 48, 40], fill=(20, 20, 20, 255))
        d.rectangle([62, 28, 72, 40], fill=(20, 20, 20, 255))
        # rambut
        d.rectangle([25, 6, 85, 22], fill=(90, 60, 30, 255))
        frames.append(im)
    return frames


# ---------------- bayangan lembut di belakang bola ----------------
def _make_blob():
    s = 560
    blob = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(blob)
    for r in range(s // 2, 0, -6):
        a = int(95 * (1 - r / (s / 2)))
        if a > 0:
            d.ellipse([s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r],
                      fill=(20, 40, 70, a))
    return blob


# ---------------- pre-render ----------------
_SKY = _make_sky()
_CLOUDS = _seamless_tile(W, 480, _draw_clouds)
_HILLS = _seamless_tile(W, HILL_H, _draw_hills)
_GROUND = _seamless_tile(W, GROUND_H, _draw_ground).convert("RGB")
_WALKER = _make_walker()
_BLOB = _make_blob()

# kolam air: x lokal di tile tanah
POOL_X0, POOL_X1 = 700, 950


def _paste_scroll(fr, tile, y, speed, fi, is_rgb=False):
    off = int(fi * speed) % W
    if is_rgb:
        fr.paste(tile, (-off, y))
        fr.paste(tile, (-off + W, y))
    else:
        fr.paste(tile, (-off, y), tile)
        fr.paste(tile, (-off + W, y), tile)


def draw_background(fi):
    """Kembalikan PIL Image RGB 1080x1920 untuk frame ke-fi."""
    fr = Image.new("RGB", (W, H))
    fr.paste(_SKY, (0, 0))
    _paste_scroll(fr, _CLOUDS, CLOUD_Y, 0.5, fi)
    _paste_scroll(fr, _HILLS, HORIZON - HILL_H + 20, 1.5, fi)
    _paste_scroll(fr, _GROUND, HORIZON, 3.5, fi, is_rgb=True)

    d = ImageDraw.Draw(fr, "RGBA")
    # kilau air: pixel putih berkedip di atas kolam (ikut scroll tanah)
    goff = int(fi * 3.5) % W
    shimmer_on = (fi // 8) % 2 == 0
    for k, px in enumerate([730, 800, 870, 925]):
        sx = (px - goff) % W
        sy = HORIZON + (14 if (k % 2 == 0) == shimmer_on else 44)
        d.rectangle([sx, sy, sx + 22, sy + 12], fill=(255, 255, 255, 200))

    # karakter jalan: melintasi layar kiri->kanan, loop
    wx = int((fi * 1.6) % (W + 320)) - 160
    wy = HORIZON - 168 + 6
    fr.paste(_WALKER[(fi // 7) % 2], (wx, wy), _WALKER[(fi // 7) % 2])

    # partikel orb melayang ke atas
    for i in range(10):
        cyc = 260
        ph = (fi + i * 61) % cyc
        t = ph / cyc
        px = (i * 197 + 260) % W + int(18 * math.sin(fi * 0.05 + i))
        py = int(H - 60 - t * (H - 200))
        s = 12 if t < 0.8 else 8
        a = int(230 * math.sin(t * math.pi))
        if a > 0:
            d.rectangle([px, py, px + s, py + s], fill=(255, 235, 130, a))
    return fr


def paste_ball_shadow(fr, bx, by, ball_size):
    """Bayangan lembut di belakang bola agar terbaca jelas.
    bx,by = kiri-atas bola; ball_size = diameter."""
    s = _BLOB.size[0]
    cx = bx + ball_size // 2 - s // 2
    cy = by + ball_size // 2 - s // 2
    fr.paste(_BLOB, (cx, cy), _BLOB)
