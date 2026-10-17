#!/usr/bin/env python3
"""Generate thumbnail horor 1280x720: gambar gelap + teks merah darah + efek seram.
Penggunaan: python3 bikin_thumbnail.py <gambar_bg> <judul> <output>
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

def bikin_thumbnail(bg_path, judul, out):
    bg = Image.open(bg_path).convert("RGB")
    # crop/resize ke 1280x720
    w, h = bg.size
    target_ratio = 1280 / 720
    if w / h > target_ratio:
        nw = int(h * target_ratio); x0 = (w - nw) // 2
        bg = bg.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / target_ratio); y0 = (h - nh) // 2
        bg = bg.crop((0, y0, w, y0 + nh))
    bg = bg.resize((1280, 720), Image.LANCZOS)
    # gelapkan + tambah merah gelap untuk nuansa horor
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    bg = ImageEnhance.Color(bg).enhance(0.7)
    merah = Image.new("RGB", (1280, 720), (60, 0, 0))
    bg = Image.blend(bg, merah, 0.25)
    # vignette kuat
    vig = Image.new("L", (1280, 720), 0)
    dv = ImageDraw.Draw(vig)
    dv.ellipse([-300, -200, 1580, 920], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    hitam = Image.new("RGB", (1280, 720), (0, 0, 0))
    bg = Image.composite(bg, hitam, vig)
    # gradient bawah untuk teks
    overlay = Image.new("L", (1, 720))
    for y in range(720):
        v = int(220 * max(0, (y - 300) / 420))
        overlay.putpixel((0, y), v)
    overlay = overlay.resize((1280, 720))
    bg = Image.composite(hitam, bg, overlay)

    d = ImageDraw.Draw(bg)
    for fp in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
               "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]:
        if os.path.exists(fp):
            font_path = fp; break
    else:
        font_path = None
    # pecah judul jadi 2-3 baris, MAKS 4 kata total
    kata = judul.split()[:4]
    baris, cur = [], ""
    for k in kata:
        if len(cur + " " + k) > 16:
            baris.append(cur.strip()); cur = k
        else:
            cur = (cur + " " + k).strip()
    if cur: baris.append(cur)
    baris = baris[:3]
    size = 100 if len(baris) <= 2 else 80
    font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()
    y = 720 - len(baris) * (size + 14) - 50
    for b in baris:
        bb = d.textbbox((0, 0), b.upper(), font=font)
        tw = bb[2] - bb[0]
        x = (1280 - tw) // 2
        # outline hitam tebal + teks MERAH DARAH (gaya thumbnail horor)
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                d.text((x + dx, y + dy), b.upper(), font=font, fill=(0, 0, 0))
        d.text((x, y), b.upper(), font=font, fill=(180, 10, 10))
        y += size + 14
    bg.save(out, format="JPEG", quality=92)
    print(f"OK: {out}")

if __name__ == "__main__":
    bikin_thumbnail(sys.argv[1], sys.argv[2], sys.argv[3])
