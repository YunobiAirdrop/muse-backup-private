#!/usr/bin/env python3
"""Paket broadcast WhatsApp Channel: 3 artikel terbaik hari ini,
siap forward (gambar meme + teks + link). Full otomatis disiapkan,
user tinggal forward ke Channel (2x tap) — tidak ada API resmi
WhatsApp untuk auto-posting ke Channel.
Output: data/wa-broadcast-YYYY-MM-DD/ (3 jpg + broadcast.txt)
Pakai: ./venv/bin/python wa_broadcast.py [--dry-run]
"""
import json, os, sys, time
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_ig import artikel_hari_ini, unduh_gambar, IG_DIR
from meme_gen import bikin_meme

WIB = timezone(timedelta(hours=7))
JUMLAH = 3

BLOG_KEY = {"KabarViral": "kabarviral", "CuanPintar": "cuanpintar",
            "TeknoGebrakan": "teknogebrakan", "SehatBugar": "sehatbugar"}

def main():
    dry = "--dry-run" in sys.argv
    daftar = [a for a in artikel_hari_ini()
              if "picsum.photos" not in a.get("gambar", "")]
    pilihan = daftar[:JUMLAH]
    tgl = datetime.now(WIB).strftime("%Y-%m-%d")
    outdir = os.path.join(BASE, "data", f"wa-broadcast-{tgl}")
    os.makedirs(outdir, exist_ok=True)
    teks = []
    for i, a in enumerate(pilihan, 1):
        raw = os.path.join(IG_DIR, f"wa_raw_{i}.jpg")
        meme = os.path.join(outdir, f"wa_{i}.jpg")
        ok = unduh_gambar(a["gambar"], raw)
        if ok:
            try:
                bikin_meme(raw, a["judul"], BLOG_KEY.get(a["blog"], "kabarviral"), meme)
            except Exception:
                meme = raw if os.path.exists(raw) else None
        else:
            meme = None
        potongan = (
            f"*{a['judul']}*\n"
            f"_{a['blog']}_\n\n"
            f"Baca selengkapnya:\n{a['link']}"
        )
        teks.append({"file": os.path.basename(meme) if meme else None,
                     "teks": potongan})
    with open(os.path.join(outdir, "broadcast.txt"), "w") as f:
        for i, t in enumerate(teks, 1):
            f.write(f"=== {i} (gambar: {t['file']}) ===\n{t['teks']}\n\n")
    print(f"Paket WA: {len(teks)} item -> {outdir}")
    if dry:
        print("DRY RUN")
    return outdir, teks

if __name__ == "__main__":
    main()
