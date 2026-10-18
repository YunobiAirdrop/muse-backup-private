#!/usr/bin/env python3
"""Aset wajah v2: mata kartun BESAR (oval putih + pupil), tangan sarung tangan putih.
Base bola digambar PIL dari nol. Ukuran 800px, di-resize saat pakai."""
from PIL import Image, ImageDraw
import math

SIZE = 800
C = SIZE // 2  # center
R = SIZE // 2 - 8  # radius

# Posisi wajah (proporsional dari center)
EYE_Y = C - 90
EYE_DX = 110
MOUTH_Y = C + 130

def base_ball(char):
    """Bola bendera polos tanpa wajah. char: id/cn/jp"""
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if char == 'id':
        # merah atas, putih bawah
        d.ellipse([8, 8, SIZE-8, SIZE-8], fill=(230, 230, 230))
        d.pieslice([8, 8, SIZE-8, SIZE-8], start=180, end=360, fill=(220, 30, 40))
        # rapikan: gambar ulang lingkaran penuh lalu tutup bawah dengan clip
        im2 = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(im2)
        d2.ellipse([8, 8, SIZE-8, SIZE-8], fill=(220, 30, 40))
        # putih untuk setengah bawah (dengan sedikit lengkung)
        d2.pieslice([8, 8, SIZE-8, SIZE-8], start=0, end=180, fill=(240, 240, 240))
        im = im2
    elif char == 'cn':
        d.ellipse([8, 8, SIZE-8, SIZE-8], fill=(222, 40, 30))
        # bintang besar + 4 kecil
        def star(cx, cy, r):
            pts = []
            for i in range(10):
                a = -math.pi/2 + i * math.pi / 5
                rr = r if i % 2 == 0 else r * 0.42
                pts.append((cx + rr*math.cos(a), cy + rr*math.sin(a)))
            d.polygon(pts, fill=(255, 215, 0))
        star(200, 250, 70)
        star(330, 170, 28); star(380, 230, 28); star(380, 310, 28); star(330, 370, 28)
    elif char == 'jp':
        d.ellipse([8, 8, SIZE-8, SIZE-8], fill=(245, 245, 245))
        d.ellipse([C-130, C-130, C+130, C+130], fill=(200, 30, 40))
    elif char == 'np':
        # NEPAL: merah tua (crimson) + outline biru + matahari/bulan putih
        d.ellipse([8, 8, SIZE-8, SIZE-8], fill=(190, 20, 40))
        # dua segitiga bertumpuk (pennon), outline biru
        pts = [(C, 90), (C+170, 360), (C, 360), (C+190, 650), (C, 650)]
        d.polygon(pts, fill=(160, 10, 32))
        d.line(pts[:2], fill=(10, 40, 130), width=18, joint='curve')
        d.line(pts[2:], fill=(10, 40, 130), width=18, joint='curve')
        d.line([(C, 90), (C, 650)], fill=(10, 40, 130), width=16)
        # matahari (atas): lingkaran putih + 8 sinar
        sx, sy, sr = C, 220, 40
        d.ellipse([sx-sr, sy-sr, sx+sr, sy+sr], fill="white")
        for i in range(8):
            a = i * math.pi / 4
            x1, y1 = sx + (sr+6)*math.cos(a), sy + (sr+6)*math.sin(a)
            x2, y2 = sx + (sr+30)*math.cos(a), sy + (sr+30)*math.sin(a)
            d.line([(x1, y1), (x2, y2)], fill="white", width=10)
        # bulan sabit (bawah)
        bx, by, br = C, 520, 46
        d.ellipse([bx-br, by-br, bx+br, by+br], fill="white")
        d.ellipse([bx-br+22, by-br-8, bx+br+22, by+br-8], fill=(160, 10, 32))
    elif char == 'bt':
        # BUTAN: diagonal kuning atas-kiri / oranye bawah-kanan + naga putih
        d.ellipse([8, 8, SIZE-8, SIZE-8], fill=(255, 128, 0))
        d.pieslice([8, 8, SIZE-8, SIZE-8], start=180, end=360, fill=(255, 205, 0))
        # perhalus: gambar ulang diagonal tegas dari kiri-atas ke kanan-bawah
        im2 = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        d2b = ImageDraw.Draw(im2)
        d2b.ellipse([8, 8, SIZE-8, SIZE-8], fill=(255, 205, 0))
        d2b.polygon([(8, 792), (792, 792), (792, 8)], fill=(255, 128, 0))
        # mask lingkaran
        mask = Image.new("L", (SIZE, SIZE), 0)
        ImageDraw.Draw(mask).ellipse([8, 8, SIZE-8, SIZE-8], fill=255)
        im.paste(im2, (0, 0), mask)
        d = ImageDraw.Draw(im)
        # naga putih sederhana (Druk): tubuh lengkung S + kepala + kaki
        body = [(C-170, C+150), (C-90, C+60), (C-10, C+80), (C+70, C-10),
                (C+150, C-60), (C+190, C-150)]
        d.line(body, fill="white", width=52, joint='curve')
        for i in range(0, len(body)-1, 2):
            d.line([body[i], body[i+1]], fill="white", width=52, joint='curve')
        # kaki: 4 kaki pendek
        for (fx, fy) in [(C-120, C+110), (C-40, C+120), (C+40, C+30), (C+120, C-20)]:
            d.rounded_rectangle([fx-14, fy-14, fx+14, fy+40], radius=14,
                                fill="white", outline=(20, 20, 20), width=4)
        # kepala naga di ujung atas
        hx, hy = C+190, C-150
        d.ellipse([hx-58, hy-48, hx+58, hy+48], fill="white",
                  outline=(20, 20, 20), width=6)
        # moncong + tanduk
        d.polygon([(hx+30, hy-10), (hx+110, hy+5), (hx+30, hy+30)], fill="white",
                  outline=(20, 20, 20))
        d.polygon([(hx-20, hy-42), (hx-40, hy-110), (hx+8, hy-52)], fill="white",
                  outline=(20, 20, 20))
        d.polygon([(hx+30, hy-48), (hx+45, hy-115), (hx+62, hy-48)], fill="white",
                  outline=(20, 20, 20))
        # mata naga
        d.ellipse([hx+5, hy-18, hx+25, hy+2], fill=(20, 20, 20))
        # permata merah di cakar
        d.polygon([(C-40, C+118), (C-22, C+136), (C-40, C+154), (C-58, C+136)],
                  fill=(200, 30, 40), outline=(20, 20, 20))
    # outline hitam
    d2 = ImageDraw.Draw(im)
    d2.ellipse([8, 8, SIZE-8, SIZE-8], outline=(20, 20, 20), width=10)
    return im


def draw_eyes(d, style):
    """Mata kartun BESAR: oval putih + pupil hitam."""
    w_norm, h_norm = 150, 190   # lebar x tinggi oval mata normal
    for sx in (-1, 1):
        x = C + sx * EYE_DX
        y = EYE_Y
        if style == "normal":
            d.ellipse([x-w_norm//2, y-h_norm//2, x+w_norm//2, y+h_norm//2],
                      fill="white", outline=(20, 20, 20), width=6)
            d.ellipse([x-28, y-28, x+28, y+28], fill=(20, 20, 20))
            d.ellipse([x-12, y-40, x+8, y-20], fill="white")  # highlight
        elif style == "kaget":
            w, h = 170, 230
            d.ellipse([x-w//2, y-h//2, x+w//2, y+h//2],
                      fill="white", outline=(20, 20, 20), width=7)
            d.ellipse([x-20, y-20, x+20, y+20], fill=(20, 20, 20))
        elif style == "senang":
            # mata melengkung ^ ^
            d.arc([x-70, y-60, x+70, y+80], start=200, end=340, fill=(20, 20, 20), width=14)
        elif style == "bingung":
            d.ellipse([x-w_norm//2, y-h_norm//2, x+w_norm//2, y+h_norm//2],
                      fill="white", outline=(20, 20, 20), width=6)
            # pupil ke samping (bingung)
            px = x + sx * 35
            d.ellipse([px-28, y-28, px+28, y+28], fill=(20, 20, 20))
        elif style == "takut":
            w, h = 165, 220
            d.ellipse([x-w//2, y-h//2, x+w//2, y+h//2],
                      fill="white", outline=(20, 20, 20), width=7)
            d.ellipse([x-14, y-14, x+14, y+14], fill=(20, 20, 20))


def draw_mouth(d, style):
    x, y = C, MOUTH_Y
    if style == "tutup":
        d.arc([x-45, y-30, x+45, y+30], start=20, end=160, fill=(20, 20, 20), width=10)
    elif style == "buka_kecil":
        d.ellipse([x-40, y-28, x+40, y+36], fill=(20, 20, 20))
        d.ellipse([x-24, y-8, x+24, y+24], fill=(170, 70, 70))
    elif style == "buka_lebar":
        d.ellipse([x-65, y-50, x+65, y+65], fill=(20, 20, 20))
        d.ellipse([x-38, y-5, x+38, y+50], fill=(170, 70, 70))
    elif style == "senyum":
        d.arc([x-60, y-45, x+60, y+45], start=15, end=165, fill=(20, 20, 20), width=12)
    elif style == "o":
        d.ellipse([x-45, y-55, x+45, y+55], outline=(20, 20, 20), width=12)


def draw_hand(side="right", pose="point"):
    """Tangan sarung tangan kartun putih. Kembalikan Image RGBA ~200x200."""
    S = 220
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = S//2, S//2
    if pose == "point":
        # telapak + jari telunjuk menunjuk ke kanan
        d.ellipse([cx-60, cy-50, cx+40, cy+60], fill="white", outline=(20,20,20), width=6)
        # jari telunjuk horizontal
        d.rounded_rectangle([cx+20, cy-22, cx+110, cy+18], radius=18,
                            fill="white", outline=(20,20,20), width=6)
        # 3 jari terlipat
        for i, fy in enumerate([cy+25, cy+45, cy+62]):
            d.rounded_rectangle([cx-30, fy-12, cx+30, fy+12], radius=10,
                                fill="white", outline=(20,20,20), width=5)
        # jempol
        d.ellipse([cx-75, cy-10, cx-35, cy+35], fill="white", outline=(20,20,20), width=5)
    elif pose == "wave":
        # telapak terbuka
        d.ellipse([cx-55, cy-40, cx+55, cy+70], fill="white", outline=(20,20,20), width=6)
        for i in range(4):
            fx = cx - 42 + i*28
            d.rounded_rectangle([fx-13, cy-95, fx+13, cy-30], radius=12,
                                fill="white", outline=(20,20,20), width=5)
        d.ellipse([cx-80, cy+10, cx-45, cy+50], fill="white", outline=(20,20,20), width=5)
    elif pose == "cheek":
        # tangan di pipi (kaget): telapak dengan jari rapat
        d.ellipse([cx-50, cy-60, cx+50, cy+60], fill="white", outline=(20,20,20), width=6)
        for i in range(4):
            fx = cx - 36 + i*24
            d.rounded_rectangle([fx-11, cy-110, fx+11, cy-55], radius=10,
                                fill="white", outline=(20,20,20), width=5)
    elif pose == "thumbs_up":
        # jempol ke atas (setuju/semangat): kepalan + jempol vertikal
        d.ellipse([cx-55, cy-20, cx+55, cy+70], fill="white", outline=(20,20,20), width=6)
        d.rounded_rectangle([cx-20, cy-95, cx+20, cy+15], radius=18,
                            fill="white", outline=(20,20,20), width=6)
        for i in range(3):  # garis buku jari
            fy = cy + 5 + i*20
            d.line([cx-40, fy, cx+40, fy], fill=(20,20,20), width=4)
    elif pose == "open_palm":
        # telapak terbuka ke atas (mempresentasikan): jari rapat ke atas
        d.ellipse([cx-60, cy-10, cx+60, cy+80], fill="white", outline=(20,20,20), width=6)
        d.rounded_rectangle([cx-45, cy-95, cx+45, cy+25], radius=20,
                            fill="white", outline=(20,20,20), width=6)
        d.ellipse([cx-88, cy+15, cx-52, cy+58], fill="white", outline=(20,20,20), width=5)
    elif pose == "fist":
        # kepalan tangan (penekanan/serius)
        d.rounded_rectangle([cx-60, cy-40, cx+60, cy+70], radius=30,
                            fill="white", outline=(20,20,20), width=6)
        for i in range(3):  # garis buku jari
            fx = cx - 30 + i*30
            d.line([fx, cy-38, fx, cy-8], fill=(20,20,20), width=4)
        d.rounded_rectangle([cx-55, cy+8, cx+55, cy+34], radius=12,
                            fill="white", outline=(20,20,20), width=5)
    elif pose == "peace":
        # jari V / peace sign (fun)
        d.ellipse([cx-55, cy-5, cx+55, cy+72], fill="white", outline=(20,20,20), width=6)
        # telunjuk miring kiri, jari tengah miring kanan (bentuk V)
        d.polygon([(cx-42, cy+12), (cx-58, cy-88), (cx-28, cy-92), (cx-12, cy+8)],
                  fill="white", outline=(20,20,20))
        d.polygon([(cx+12, cy+8), (cx+28, cy-92), (cx+58, cy-88), (cx+42, cy+12)],
                  fill="white", outline=(20,20,20))
        # 2 jari terlipat + jempol
        d.ellipse([cx-38, cy+22, cx+38, cy+58], fill="white", outline=(20,20,20), width=5)
        d.ellipse([cx-78, cy+12, cx-42, cy+52], fill="white", outline=(20,20,20), width=5)
    elif pose == "clap":
        # telapak datar tampak samping (untuk tepuk tangan)
        d.ellipse([cx-45, cy-60, cx+55, cy+60], fill="white", outline=(20,20,20), width=6)
        for i in range(4):
            fy = cy - 36 + i*24
            d.rounded_rectangle([cx-95, fy-10, cx-40, fy+10], radius=9,
                                fill="white", outline=(20,20,20), width=5)
    if side == "left":
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im


# Cache tangan
_HANDS = {}
def get_hand(side, pose):
    k = (side, pose)
    if k not in _HANDS:
        _HANDS[k] = draw_hand(side, pose)
    return _HANDS[k]


# Cache bola+wajah
_BALLS = {}
def face_image_v2(char, eye_style, mouth_style, size=400):
    k = (char, eye_style, mouth_style, size)
    if k not in _BALLS:
        im = base_ball(char)
        d = ImageDraw.Draw(im)
        draw_eyes(d, eye_style)
        draw_mouth(d, mouth_style)
        if size != SIZE:
            im = im.resize((size, size), Image.LANCZOS)
        _BALLS[k] = im
    return _BALLS[k]
