#!/usr/bin/env python3
"""Rapikan nama file gambar hasil media.generate_image menjadi b001.webp dst.
Menangani nama seperti media-generation-b001-0-<uuid>.webp (ambil nomor beat dari nama).
Jika ada duplikat per beat, simpan yang terbesar. File bukan .webp diabaikan.
Penggunaan: python3 rapikan_gambar.py gambar/2026-10-06
"""
import os, re, sys, glob

gdir = sys.argv[1]
files = glob.glob(os.path.join(gdir, "*.webp"))
by_beat = {}
for f in files:
    base = os.path.basename(f)
    m = re.search(r'b0*(\d{1,3})', base)
    if not m:
        print("  lewati (tanpa nomor beat):", base); continue
    n = int(m.group(1))
    sz = os.path.getsize(f)
    if sz < 10240:
        print(f"  rusak/kecil ({sz}b):", base); continue
    if n not in by_beat or sz > by_beat[n][1]:
        by_beat[n] = (f, sz)

print(f"{len(by_beat)} beat unik dari {len(files)} file webp")
missing = [n for n in range(1, 77) if n not in by_beat]
for n in sorted(by_beat):
    src, sz = by_beat[n]
    dst = os.path.join(gdir, f"b{n:03d}.webp")
    if os.path.abspath(src) != os.path.abspath(dst):
        if os.path.exists(dst):
            os.remove(dst)
        os.rename(src, dst)
    print(f"  b{n:03d}.webp ({sz//1024}KB)")
if missing:
    print("HILANG:", [f"b{n:03d}" for n in missing])
else:
    print("LENGKAP: 76/76")
