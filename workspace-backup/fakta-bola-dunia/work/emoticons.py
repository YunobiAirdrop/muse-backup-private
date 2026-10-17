#!/usr/bin/env python3
"""Emoticon ekspresi kartun untuk part8: digambar PIL, gaya tebal konsisten.
Ukuran base 200px, di-resize saat dipakai."""
from PIL import Image, ImageDraw, ImageFont
import math

SIZE = 200
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def _blank():
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))

def sweat_drop(size=100):
    """Tetes keringat biru (gugup/khawatir/takut)."""
    im = _blank()
    d = ImageDraw.Draw(im)
    cx = SIZE // 2
    # tetes: segitiga atas + lingkaran bawah
    d.ellipse([cx-55, 75, cx+55, 185], fill=(80, 180, 255), outline=(20, 60, 140), width=8)
    d.polygon([(cx, 10), (cx-48, 110), (cx+48, 110)], fill=(80, 180, 255))
    d.line([(cx, 10), (cx-48, 110)], fill=(20, 60, 140), width=8)
    d.line([(cx, 10), (cx+48, 110)], fill=(20, 60, 140), width=8)
    # highlight putih
    d.ellipse([cx-35, 95, cx-10, 150], fill=(200, 235, 255))
    return im.resize((size, size), Image.LANCZOS)

def question(size=100):
    """Tanda tanya besar kuning/oranye (bingung)."""
    im = _blank()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 170)
    d.text((SIZE//2, SIZE//2-10), "?", font=f, fill=(255, 180, 0),
           stroke_width=10, stroke_fill=(30, 30, 30), anchor="mm")
    return im.resize((size, size), Image.LANCZOS)

def exclaim(size=100):
    """Tanda seru merah besar (kaget)."""
    im = _blank()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 170)
    d.text((SIZE//2, SIZE//2-10), "!", font=f, fill=(230, 30, 30),
           stroke_width=10, stroke_fill=(30, 30, 30), anchor="mm")
    return im.resize((size, size), Image.LANCZOS)

def interrobang(size=110):
    """!? kombinasi (kaget + bingung)."""
    im = _blank()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 120)
    d.text((SIZE//2-35, SIZE//2-5), "!", font=f, fill=(230, 30, 30),
           stroke_width=8, stroke_fill=(30, 30, 30), anchor="mm")
    d.text((SIZE//2+40, SIZE//2-5), "?", font=f, fill=(255, 180, 0),
           stroke_width=8, stroke_fill=(30, 30, 30), anchor="mm")
    return im.resize((size, size), Image.LANCZOS)

def anger(size=100):
    """Simbol marah merah 💢 (kesal)."""
    im = _blank()
    d = ImageDraw.Draw(im)
    cx, cy = SIZE // 2, SIZE // 2
    # 4 lengkungan membentuk simbol marah
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        x0, y0 = cx + 55*math.cos(a), cy + 55*math.sin(a)
        x1, y1 = cx + 20*math.cos(a), cy + 20*math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=(220, 30, 30), width=22)
    # outline: gambar ulang dengan width lebih besar di belakang
    im2 = _blank()
    d2 = ImageDraw.Draw(im2)
    for ang in (45, 135, 225, 315):
        a = math.radians(ang)
        x0, y0 = cx + 55*math.cos(a), cy + 55*math.sin(a)
        x1, y1 = cx + 20*math.cos(a), cy + 20*math.sin(a)
        d2.line([(x0, y0), (x1, y1)], fill=(30, 30, 30), width=30)
    im2.paste(im, (0, 0), im)
    return im2.resize((size, size), Image.LANCZOS)

def notes(size=100):
    """Not musik (senang)."""
    im = _blank()
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 150)
    d.text((SIZE//2, SIZE//2-10), "\u266a", font=f, fill=(255, 120, 200),
           stroke_width=8, stroke_fill=(30, 30, 30), anchor="mm")
    return im.resize((size, size), Image.LANCZOS)

EMOTICONS = {
    'sweat_drop': sweat_drop,
    'question': question,
    'exclaim': exclaim,
    'interrobang': interrobang,
    'anger': anger,
    'notes': notes,
}

if __name__ == "__main__":
    import os
    os.makedirs("/tmp/emoticon_preview", exist_ok=True)
    for name, fn in EMOTICONS.items():
        fn(160).save(f"/tmp/emoticon_preview/{name}.png")
    print("preview di /tmp/emoticon_preview/")
