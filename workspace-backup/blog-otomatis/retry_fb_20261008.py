#!/usr/bin/env python3
"""Retry 1x dua slot FB yang GAGAL karena 'Sentinel rejected media artifact
registration' (error infra transient, kemarin juga terjadi). Update entri di
report in-place (tidak menambah duplikat)."""
import json, os, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from posting_promo_20261008 import post_fb, REPORT, MANIFEST, OUT

TARGET = [
    ("Gamis Kondangan Kayla Dress Viral", "FB"),
    ("Aura Midi Dress Jumbo Busui Friendly", "FB"),
]

def main():
    manifest = {p["nama"]: p for p in json.load(open(MANIFEST))["produk"]}
    rakit = {}
    rp = os.path.join(OUT, "rakit_2026-10-08.json")
    if os.path.exists(rp):
        rakit = json.load(open(rp))
    report = json.load(open(REPORT))
    for nama, akun in TARGET:
        p = manifest[nama]
        img = p["gambar_promo"]
        slug = p["file_gambar"].replace(".jpg", "")
        vid = rakit.get(slug, {}).get("wa") or p.get("video_fallback")
        print(f">> retry {nama} [{akun}]", flush=True)
        status, info = post_fb(img, vid, p["caption"])
        print(f"   {status} {info[:80]}", flush=True)
        for h in report["hasil"]:
            if h["produk"] == nama and h["akun"] == akun:
                h["status"] = status
                h["info"] = info
                break
        json.dump(report, open(REPORT, "w"), ensure_ascii=False, indent=1)
        time.sleep(30)
    print("RETRY SELESAI", flush=True)

if __name__ == "__main__":
    main()
