#!/usr/bin/env python3
"""Lanjutan posting promo 2026-10-08: hanya 3 slot yang belum pernah dicoba
(mainan-sains -> Threads-1, Threads-2, FB). Run utama terhenti SIGTERM di tengah
slot mainan-sains/Threads-1. Import-safe: pakai fungsi dari posting_promo_20261008."""
import json, os, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from posting_promo_20261008 import (
    post_threads, post_fb, REPORT, MANIFEST, OUT, THREADS_1, THREADS_2,
)
from share_promo import PRODUK

def main():
    manifest = {p["nama"]: p for p in json.load(open(MANIFEST))["produk"]}
    rakit = {}
    rp = os.path.join(OUT, "rakit_2026-10-08.json")
    if os.path.exists(rp):
        rakit = json.load(open(rp))
    report = json.load(open(REPORT))

    p = manifest["Mainan Edukasi Sains Kayu Anak"]
    nama = p["nama"]
    img = p["gambar_promo"]
    slug = p["file_gambar"].replace(".jpg", "")
    vid = rakit.get(slug, {}).get("wa") or p.get("video_fallback")
    caption = p["caption"]

    sudah = {(h["produk"], h["akun"]) for h in report["hasil"]}
    tugas = [
        ("Threads-1", lambda: post_threads(THREADS_1, img, vid, caption)),
        ("Threads-2", lambda: post_threads(THREADS_2, img, vid, caption)),
        ("FB", lambda: post_fb(img, vid, caption)),
    ]
    for akun, fn in tugas:
        if (nama, akun) in sudah:
            print(f">> {nama} [{akun}] SUDAH ADA DI REPORT, lewati", flush=True)
            continue
        print(f">> {nama} [{akun}]", flush=True)
        status, info = fn()
        print(f"   {status} {info[:80]}", flush=True)
        report["hasil"].append({"produk": nama, "akun": akun,
                                "status": status, "info": info})
        json.dump(report, open(REPORT, "w"), ensure_ascii=False, indent=1)
        time.sleep(30)
    print("LANJUTAN SELESAI", flush=True)
    ringkas = {}
    for h in report["hasil"]:
        ringkas[h["status"]] = ringkas.get(h["status"], 0) + 1
    print("RINGKASAN:", ringkas, flush=True)

if __name__ == "__main__":
    main()
