#!/usr/bin/env python3
"""Generator gambar meme berita viral (gaya Suara.com di FB):
foto artikel + headline tebal putih/merah di atas gradient gelap + watermark blog.
Pakai: ./venv/bin/python meme_gen.py --gambar foto.jpg --judul "Headline" --blog "KabarViral" --out meme.jpg
"""
import argparse, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1080
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

WARNA = {
    "kabarviral": ("#E63946", "KABARVIRAL"),
    "cuanpintar": ("#2A9D48", "CUANPINTAR"),
    "teknogebrakan": ("#2979FF", "TEKNOGEBRAKAN"),
    "sehatbugar": ("#FF6B35", "SEHATBUGAR"),
}

def font(size):
    return ImageFont.truetype(FONT_BOLD, size)

def bikin_meme(path_gambar, judul, blog, path_out):
    warna, label = WARNA.get(blog, ("#E63946", blog.upper()))
    # 1. background foto (cover crop square)
    try:
        bg = Image.open(path_gambar).convert("RGB")
    except Exception:
        bg = Image.new("RGB", (W, H), (20, 20, 25))
    # cover crop
    r = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * r) + 1, int(bg.height * r) + 1), Image.LANCZOS)
    x = (bg.width - W) // 2
    y = (bg.height - H) // 2
    bg = bg.crop((x, y, x + W, y + H))
    # sedikit gelapkan foto biar teks terbaca
    bg = bg.point(lambda p: int(p * 0.92))

    # 2. gradient gelap di bawah (55% bawah)
    grad = Image.new("L", (1, H))
    for i in range(H):
        # transparan di atas, pekat di bawah
        v = 0 if i < H * 0.40 else int(210 * (i - H * 0.40) / (H * 0.60))
        grad.putpixel((0, i), v)
    hitam = Image.new("RGB", (W, H), (0, 0, 0))
    bg.paste(hitam, (0, 0), grad.resize((W, H)))

    d = ImageDraw.Draw(bg)

    # 3. watermark blog kiri atas (pill)
    fl = font(44)
    tw = d.textlength(label, font=fl)
    pad = 28
    d.rounded_rectangle([36, 36, 36 + tw + pad * 2, 36 + 76], radius=38, fill=warna)
    d.text((36 + pad, 48), label, font=fl, fill="white")

    # 4. headline: potong jadi 2 bagian, bagian akhir warna aksen
    # heuristik: kata kunci emosional diwarnai
    kata_aksen = ["viral", "jangan", "bawa", "gratis", "cair", "naik", "turun",
                  "bahaya", "waspada", "heboh", "gempar", "bocor", "rahasia"]
    kata = judul.strip().split()
    # wrap manual per baris
    f = font(64)
    baris = []
    cur = ""
    for k in kata:
        t = (cur + " " + k).strip()
        if d.textlength(t, font=f) > W - 120:
            baris.append(cur)
            cur = k
        else:
            cur = t
    if cur:
        baris.append(cur)
    baris = baris[:4]  # maks 4 baris

    # gambar dari bawah ke atas
    yb = H - 60
    for b in baris[::-1]:
        # warnai kata aksen
        xk = 60
        for k in b.split():
            fk = f
            fill = "white"
            if k.lower().strip(",.!?") in kata_aksen:
                fill = "#FFD23F"  # kuning emas utk penekanan
            # stroke hitam biar terbaca
            d.text((xk, yb - 70), k, font=fk, fill=fill,
                   stroke_width=3, stroke_fill="black")
            xk += d.textlength(k + " ", font=fk)
        yb -= 84

    # 5. garis aksen di atas teks
    d.rectangle([60, yb - 10, 220, yb - 2], fill=warna)

    bg.save(path_out, "JPEG", quality=90)
    return path_out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gambar", required=True)
    ap.add_argument("--judul", required=True)
    ap.add_argument("--blog", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = bikin_meme(a.gambar, a.judul, a.blog, a.out)
    print("meme jadi:", out)

if __name__ == "__main__":
    main()
