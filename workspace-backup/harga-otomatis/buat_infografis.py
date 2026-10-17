#!/usr/bin/env python3
"""Generate infografis harga harian 1080x1080 (PIL, tanpa dependensi lain).
Input: data/harga-YYYY-MM-DD.json -> img/harga-YYYY-MM-DD.png
"""
import json, os, sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
IMG = os.path.join(BASE, "img")
os.makedirs(IMG, exist_ok=True)

W = H = 1080
BG = (18, 24, 38)          # navy gelap
CARD = (30, 40, 60)        # kartu
AKSEN = (255, 193, 7)      # kuning emas
PUTIH = (245, 245, 245)
ABU = (160, 170, 185)
HIJAU = (76, 175, 80)
MERAH = (244, 67, 54)

def font(size, bold=True):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
              "/usr/share/fonts/truetype/liberation/LiberationSans%s.ttf" % ("-Bold" if bold else "")]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def rp(n):
    return "Rp" + f"{n:,}".replace(",", ".")

def panah(harga, kemarin):
    if kemarin is None or kemarin == 0:
        return ("", ABU)
    if harga > kemarin:
        return ("\u25b2", MERAH)     # naik = merah (harga naik kurang baik)
    if harga < kemarin:
        return ("\u25bc", HIJAU)     # turun = hijau
    return ("\u25cf", ABU)

def main(tanggal=None):
    files = sorted(f for f in os.listdir(DATA) if f.startswith("harga-") and f.endswith(".json"))
    if not files:
        print("tidak ada data harga"); return 1
    if tanggal:
        target = f"harga-{tanggal}.json"
    else:
        target = files[-1]
    d = json.load(open(os.path.join(DATA, target)))
    items = d["items"]
    tgl = d["tanggal"]
    try:
        dt = datetime.strptime(tgl, "%Y-%m-%d")
        bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                 "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        tgl_indo = f"{dt.day:02d} {bulan[dt.month-1]} {dt.year}"
    except Exception:
        tgl_indo = tgl

    img = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(img)

    # header
    dr.rectangle([0, 0, W, 200], fill=(22, 30, 48))
    dr.rectangle([0, 200, W, 206], fill=AKSEN)
    dr.text((W // 2, 70), "HARGA HARI INI", font=font(64), fill=PUTIH, anchor="mm")
    dr.text((W // 2, 140), tgl_indo, font=font(36, False), fill=AKSEN, anchor="mm")

    # urutan: emas dulu, lalu sembako
    urutan = ["Emas Antam 1gr"] + [k for k in items if k != "Emas Antam 1gr"]
    y = 230
    row_h = 72
    for nama in urutan:
        v = items[nama]
        harga, kemarin, satuan = v["harga"], v.get("harga_kemarin"), v["satuan"]
        simbol, warna = panah(harga, kemarin)
        is_emas = nama.startswith("Emas")
        # kartu baris
        dr.rounded_rectangle([40, y, W - 40, y + row_h - 10], radius=14,
                             fill=(45, 55, 80) if is_emas else CARD)
        dr.text((70, y + (row_h - 10) // 2), nama, font=font(30), fill=AKSEN if is_emas else PUTIH, anchor="lm")
        kanan = f"{rp(harga)}/{satuan}"
        dr.text((W - 130, y + (row_h - 10) // 2), kanan, font=font(30), fill=PUTIH, anchor="rm")
        if simbol:
            dr.text((W - 85, y + (row_h - 10) // 2), simbol, font=font(30), fill=warna, anchor="lm")
        y += row_h

    # footer
    dr.rectangle([0, H - 90, W, H], fill=(22, 30, 48))
    dr.text((W // 2, H - 58), "Sumber: PIHPS Bank Indonesia & Logam Mulia",
            font=font(24, False), fill=ABU, anchor="mm")
    dr.text((W // 2, H - 28), "#hargahariini #sembako #hargapasar",
            font=font(22, False), fill=ABU, anchor="mm")

    out = os.path.join(IMG, target.replace("harga-", "harga-").replace(".json", ".png"))
    img.save(out)
    print(f"Infografis: {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
