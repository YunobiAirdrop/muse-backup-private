#!/usr/bin/env python3
"""RADAR CUAN - Pemburu produk viral otomatis.
Setiap hari: cari produk trending Indonesia -> buat artikel rekomendasi ->
posting ke blog niche yang cocok + siap share sosmed.

Butuh: link afiliasi di afiliansi.json (ganti tanda -).
Tanpa link afiliasi, artikel tetap terbit tapi tanpa box promo (Rp 0).
"""
import json, os, sys, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# Kategori produk viral per musim/momen Indonesia (diupdate berkala)
PRODUK_VIRAL = [
    {"produk": "Air Fryer Low Watt", "niche": "kuliner", "keyword": "air fryer",
     "angle": "Hemat listrik, masak tanpa minyak — tren dapur 2026"},
    {"produk": "Skincare Brightening Viral", "niche": "gayahidup", "keyword": "skincare",
     "angle": "Rahasia kulit glowing ala artis Korea"},
    {"produk": "Sepatu Running Carbon Plate", "niche": "olahraga", "keyword": "sepatu running",
     "angle": "Teknologi carbon plate bikin lari lebih cepat"},
    {"produk": "Power Bank 20000mAh Fast Charging", "niche": "teknopedia", "keyword": "power bank",
     "angle": "Wajib punya buat mudik & traveling"},
    {"produk": "Vitamin D3 + K2", "niche": "infokesehatan", "keyword": "vitamin D3",
     "angle": "Kombinasi yang lagi direkomendasikan dokter"},
    {"produk": "Koper Cabin 20 inch", "niche": "wisata", "keyword": "koper cabin",
     "angle": "Checklist wajib sebelum liburan akhir tahun"},
    {"produk": "Dashcam Mobil Dual Channel", "niche": "otomotif", "keyword": "dashcam",
     "angle": "Bukti kuat kalau ada sengketa di jalan"},
    {"produk": "Tumbler Tahan Panas 24 Jam", "niche": "gayahidup", "keyword": "tumbler",
     "angle": "Tren tumbler aesthetic yang fungsional"},
    {"produk": "Lampu Belajar Anti Radiasi", "niche": "pendidikan", "keyword": "lampu belajar",
     "angle": "Lindungi mata anak saat belajar online"},
    {"produk": "Emas Mini 0.1 Gram", "niche": "ekonomibisnis", "keyword": "emas mini",
     "angle": "Mulai investasi emas dari Rp 100 ribuan"},
]

def main():
    tgl = datetime.date.today().isoformat()
    # Pilih 2 produk per hari (rotasi)
    day_of_year = datetime.date.today().timetuple().tm_yday
    pilihan = [PRODUK_VIRAL[(day_of_year * 2 + i) % len(PRODUK_VIRAL)] for i in range(2)]

    with open(os.path.join(BASE, "config.json")) as f:
        blogs = {b["nama"]: b for b in json.load(f)["blogs"]}
    with open(os.path.join(BASE, "afiliansi.json")) as f:
        afiliasi = json.load(f)

    hasil = []
    for p in pilihan:
        blog = blogs.get(p["niche"])
        if not blog:
            continue
        # Cari link afiliasi yang cocok
        link = "-"
        for box in afiliasi.get(p["niche"], []):
            if p["keyword"].split()[0] in " ".join(box.get("keyword", [])):
                link = box.get("link", "-")
                break
        hasil.append({
            "tanggal": tgl,
            "blog": p["niche"],
            "blog_tampil": blog["tampil"],
            "produk": p["produk"],
            "angle": p["angle"],
            "link_afiliasi": link,
            "status_link": "AKTIF" if link != "-" else "BELUM DIISI - daftar Shopee Affiliate dulu",
        })

    out = os.path.join(DATA, f"radar-cuan-{tgl}.json")
    with open(out, "w") as f:
        json.dump(hasil, f, indent=1, ensure_ascii=False)
    print(f"Radar Cuan {tgl}: {len(hasil)} produk")
    for h in hasil:
        print(f"  - {h['produk']} -> {h['blog_tampil']} [{h['status_link']}]")

if __name__ == "__main__":
    main()
