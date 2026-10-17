#!/usr/bin/env python3
"""Posting resep harian ke IG @falcon_esport537.
- Bikin caption: hook + bahan singkat + CTA + hashtag + 1 link afiliasi dapur (rotasi 7 hari, riwayat sendiri)
- Default: --dry-run (tulis antrean ke data/antrean-ig-YYYY-MM-DD.json, TIDAK posting)
- --post: posting beneran via instagram-cli (butuh approval user di runtime!)
"""
import json, os, sys, subprocess
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
BLOG_OTOMATIS = os.path.expanduser("~/workspace/blog-otomatis")
sys.path.insert(0, BLOG_OTOMATIS)
import share_promo

ACCOUNT_ID = "17841462795414201"  # @falcon_esport537 (lihat share_ig.py)
HASHTAG = "#resep #masakanindonesia #reseprumahan #resepmudah #dapur #fyp #viral #resepviral #masak #kulinerindonesia"

def pilih_afiliasi_dapur():
    """1 produk peralatan dapur, rotasi 7 hari (riwayat sendiri, tidak ganggu promo utama)."""
    hist_path = os.path.join(BASE, "riwayat-afiliasi.json")
    hist = json.load(open(hist_path)) if os.path.exists(hist_path) else {}
    batas = (date.today() - timedelta(days=7)).isoformat()
    dapur_tag = ("dapur", "alatdapur", "masak", "alatmasak", "perabotdapur", "masakpraktis")
    semua_dapur = [(i, p) for i, p in enumerate(share_promo.PRODUK)
                   if any(h in dapur_tag for h in p[5])]
    kandidat = [(i, p) for i, p in semua_dapur
                if hist.get(str(i), "2000-01-01") < batas]
    if not kandidat:  # pool dapur habis < 7 hari: pakai ulang produk dapur yang paling lama dipakai (tetap peralatan dapur)
        kandidat = semua_dapur
    if not kandidat:  # jaga-jaga: pool dapur kosong total
        kandidat = list(enumerate(share_promo.PRODUK))
    idx, prod = sorted(kandidat, key=lambda x: hist.get(str(x[0]), "2000-01-01"))[0]
    hist[str(idx)] = date.today().isoformat()
    json.dump(hist, open(hist_path, "w"))
    return prod  # (file_gambar, nama, harga, warna, link, hashtag)

def bikin_caption(resep, produk):
    bahan_txt = "\n".join(f"• {b}" for b in resep["bahan"][:6])
    if len(resep["bahan"]) > 6:
        bahan_txt += f"\n• ...dan {len(resep['bahan']) - 6} bahan lainnya"
    nama_p, harga_p, link_p = produk[1], produk[2], produk[4]
    return (
f"🍳 {resep['judul']}\n\n"
f"{resep['deskripsi']}\n\n"
f"🧂 Bahan-bahan:\n{bahan_txt}\n\n"
f"⏱ {resep['waktu']} | 🍽 {resep['porsi']} | Level: {resep['kesulitan']}\n\n"
f"💡 Tips: {resep['tips'][0] if resep['tips'] else '-'}\n\n"
f"Save dulu biar nggak lupa! Follow untuk resep tiap hari 👩‍🍳\n\n"
f"🛒 {nama_p} - {harga_p}: {link_p}\n\n"
f"{HASHTAG}"
    )

def main():
    post = "--post" in sys.argv
    hari = date.today().isoformat()
    resep_path = os.path.join(DATA, f"resep-{hari}.json")
    if not os.path.exists(resep_path):
        print(f"Resep hari ini belum ada: {resep_path} (jalankan bikin_resep.py dulu)")
        sys.exit(1)
    daftar = json.load(open(resep_path))
    antrean = []
    for r in daftar:
        img = os.path.join(BASE, "gambar", f"{hari}-{r['nama_pool'].lower().replace(' ', '-')}.jpg")
        if not os.path.exists(img):
            # cari file gambar yang cocok (nama boleh beda)
            cands = [f for f in os.listdir(os.path.join(BASE, "gambar")) if f.startswith(hari)]
            img = os.path.join(BASE, "gambar", cands[0]) if cands else None
        produk = pilih_afiliasi_dapur()
        caption = bikin_caption(r, produk)
        if len(caption) > 2100:
            caption = caption[:2100]
        item = {"judul": r["judul"], "gambar": img, "caption": caption,
                "produk": produk[1], "status": "menunggu persetujuan"}
        if post and img:
            cmd = ["instagram-cli", "post-feed", "--account-id", ACCOUNT_ID,
                   "--file", img, "--caption", caption]
            rr = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            item["status"] = "terposting" if rr.returncode == 0 else f"gagal: {rr.stderr[:150]}"
            print(f"  {item['status']}: {r['judul'][:50]}")
        else:
            print(f"  antre (menunggu persetujuan): {r['judul'][:50]}")
        antrean.append(item)
    out = os.path.join(DATA, f"antrean-ig-{hari}.json")
    json.dump(antrean, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"Antrean: {out}")

if __name__ == "__main__":
    main()
