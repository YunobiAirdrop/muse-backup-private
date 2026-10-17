#!/usr/bin/env python3
"""Gambar ulang 3 countryball dari nol dengan PIL - bersih tanpa wajah."""
from PIL import Image, ImageDraw
import math

S = 640
CX, CY = 320, 310
R_OUT, R_IN = 232, 220  # radius outline & isi
WORK = "/home/hatch/workspace/fakta-bola-dunia/work"

def base_circle():
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([CX-R_OUT, CY-R_OUT, CX+R_OUT, CY+R_OUT], fill="black")
    return im, d

def star(d, cx, cy, r_out, color=(255, 215, 0)):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_out * 0.42
        a = -math.pi/2 + i * math.pi/5
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    d.polygon(pts, fill=color)

# ---------- ID: merah atas, putih bawah, diagonal (via mask) ----------
R = 220
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.ellipse([CX-R, CY-R, CX+R, CY+R], fill=(217, 30, 41))
d.polygon([(CX-R, CY+R), (CX+R, CY+R), (CX+R, 262), (CX-R, 372)], fill="white")
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).ellipse([CX-R, CY-R, CX+R, CY+R], fill=255)
im.putalpha(mask)
ImageDraw.Draw(im).ellipse([CX-R-7, CY-R-7, CX+R+7, CY+R+7], outline="black", width=14)
im.save(f"{WORK}/base-id.png")
print("id ok")

# ---------- CN: merah + 5 bintang kuning ----------
im, d = base_circle()
d.ellipse([CX-R_IN, CY-R_IN, CX+R_IN, CY+R_IN], fill=(224, 38, 17))
star(d, 170, 220, 72)          # bintang besar
star(d, 330, 145, 26)
star(d, 380, 205, 26)
star(d, 380, 285, 26)
star(d, 330, 345, 26)
im.save(f"{WORK}/base-cn.png")
print("cn ok")

# ---------- JP: putih + lingkaran merah ----------
im, d = base_circle()
d.ellipse([CX-R_IN, CY-R_IN, CX+R_IN, CY+R_IN], fill="white")
d.ellipse([CX-150, CY-120, CX+150, CY+180], fill=(227, 28, 37))
im.save(f"{WORK}/base-jp.png")
print("jp ok")
