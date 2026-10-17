#!/usr/bin/env python3
"""Driver produksi konten promo 2026-10-06: gunakan 5 produk yang SUDAH terpilih
(indeks 1-5, tercatat di promo_history.json dari dry-run). TIDAK memanggil
pilih_produk lagi agar rotasi tidak berubah."""
import json, os, sys
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import PRODUK, siapkan_konten, bikin_caption

OUT = os.path.join(BASE, "promo_out")
manifest = []
for i in [1, 2, 3, 4, 5]:
    p = PRODUK[i]
    fimg, nama, harga, warna, link, tags = p
    print(f">> [{i}] {nama}", flush=True)
    img, vid = siapkan_konten(p)
    caption = bikin_caption(p)
    print(f"   img={os.path.basename(img)} vid={os.path.basename(vid) if vid else None}", flush=True)
    manifest.append({
        "indeks": i, "file_gambar": fimg, "nama": nama, "harga": harga,
        "warna": warna, "link": link, "tags": tags,
        "gambar_promo": img, "video_fallback": vid, "caption": caption,
        "video_final": None,
    })
json.dump({"tanggal": "2026-10-06", "produk": manifest},
          open(os.path.join(OUT, "manifest_2026-10-06.json"), "w"),
          ensure_ascii=False, indent=1)
print("MANIFEST OK", flush=True)
