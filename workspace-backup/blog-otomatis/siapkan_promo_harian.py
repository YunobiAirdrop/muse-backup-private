#!/usr/bin/env python3
"""Persiapan konten promo harian: gambar promo + video Ken Burns (fallback)
untuk 5 produk yang SUDAH dipilih dry-run (indeks 5-9, sudah tercatat di
promo_history.json). Jangan panggil pilih_produk() lagi (akan memilih
produk lain karena dry-run menandai riwayat).
Output: manifest JSON di promo_out/manifest-2026-10-03.json
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import PRODUK, siapkan_konten, bikin_caption

WIB = timezone(timedelta(hours=7))
OUT = os.path.join(BASE, "promo_out")
os.makedirs(OUT, exist_ok=True)

INDEKS = [5, 6, 7, 8, 9]  # dari dry-run 2026-10-03 12:11 WIB
SLUGS = ["rebus-telur", "nb-freshfoam", "nb-rebel", "spion-koso", "knalpot"]

manifest = {"tanggal": datetime.now(WIB).date().isoformat(), "produk": []}
for idx, slug in zip(INDEKS, SLUGS):
    p = PRODUK[idx]
    fimg, nama, harga, warna, link, tags = p
    print(f">> {nama}", flush=True)
    img, vid = siapkan_konten(p)
    caption = bikin_caption(p)
    manifest["produk"].append({
        "indeks": idx, "slug": slug, "nama": nama, "harga": harga,
        "warna": warna, "link": link, "tags": tags,
        "gambar_src": os.path.join(BASE, "promo_img", fimg),
        "gambar_promo": img, "video_fallback": vid, "caption": caption,
        "video_final": None,
    })
    print(f"   img={img} fallback_vid={vid}", flush=True)

mpath = os.path.join(OUT, "manifest-2026-10-03.json")
json.dump(manifest, open(mpath, "w"), ensure_ascii=False, indent=1)
print("manifest:", mpath)
