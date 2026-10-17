#!/usr/bin/env python3
"""Aset wajah PIL konsisten untuk countryball. Posisi proporsional dari center (320,320)."""
from PIL import Image, ImageDraw

EYE_L = (250, 260); EYE_R = (390, 260)
MOUTH_C = (320, 400)

def draw_eyes(d, style):
    if style == "normal":
        for (x, y) in (EYE_L, EYE_R):
            d.ellipse([x-14, y-14, x+14, y+14], fill="black")
            d.ellipse([x-9, y-9, x-1, y-1], fill="white")
    elif style == "kaget":
        for (x, y) in (EYE_L, EYE_R):
            d.ellipse([x-24, y-24, x+24, y+24], outline="black", width=7)
            d.ellipse([x-8, y-8, x+8, y+8], fill="black")
    elif style == "senang":
        for (x, y) in (EYE_L, EYE_R):
            d.arc([x-20, y-14, x+20, y+26], start=200, end=340, fill="black", width=8)

def draw_mouth(d, style):
    x, y = MOUTH_C
    if style == "tutup":
        d.arc([x-22, y-16, x+22, y+16], start=20, end=160, fill="black", width=7)
    elif style == "buka_kecil":
        d.ellipse([x-20, y-14, x+20, y+18], fill="black")
        d.ellipse([x-12, y-6, x+12, y+12], fill=(150, 60, 60))
    elif style == "buka_lebar":
        d.ellipse([x-34, y-26, x+34, y+34], fill="black")
        d.ellipse([x-20, y-4, x+20, y+26], fill=(150, 60, 60))
    elif style == "senyum":
        d.arc([x-30, y-24, x+30, y+24], start=15, end=165, fill="black", width=8)
    elif style == "o":
        d.ellipse([x-24, y-28, x+24, y+28], outline="black", width=9)

def face_image(char, eye_style, mouth_style, size=300):
    """Kembalikan PIL Image (RGBA, size x size) bola + wajah."""
    base = Image.open(f"/home/hatch/workspace/fakta-bola-dunia/work/base-{char}.png").convert("RGBA")
    d = ImageDraw.Draw(base)
    draw_eyes(d, eye_style)
    draw_mouth(d, mouth_style)
    if size != 640:
        base = base.resize((size, size), Image.LANCZOS)
    return base
