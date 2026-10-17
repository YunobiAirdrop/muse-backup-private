#!/usr/bin/env python3
"""Posting infografis harga harian ke IG @falcon_esport537 & Threads @beritaviraldotcom.
CATATAN: tiap posting butuh explicit approval (aturan runtime) -> semi-otomatis.
Saat approval card muncul, worker melaporkan "menunggu persetujuan", JANGAN bypass.
Pakai: python3 posting_harga.py [--dry-run] [YYYY-MM-DD]
"""
import json, os, sys, subprocess
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
IMG = os.path.join(BASE, "img")

IG_ACCOUNT = "17841462795414201"       # falcon_esport537
THREADS_ACCOUNT = "17841423460796922"  # beritaviraldotcom (verified 2026-10-06 via threads-cli accounts)

def rp(n):
    return "Rp" + f"{n:,}".replace(",", ".")

def panah(harga, kemarin):
    if kemarin is None or kemarin == 0 or harga == kemarin:
        return ""
    return " naik" if harga > kemarin else " turun"

def bikin_caption(d):
    try:
        dt = datetime.strptime(d["tanggal"], "%Y-%m-%d")
        bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                 "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
        tgl = f"{dt.day} {bulan[dt.month-1]} {dt.year}"
    except Exception:
        tgl = d["tanggal"]
    baris = [f"HARGA HARI INI - {tgl}", ""]
    for nama, v in d["items"].items():
        arah = panah(v["harga"], v.get("harga_kemarin"))
        baris.append(f"{nama}: {rp(v['harga'])}/{v['satuan']}{arah}")
    baris += ["",
              "Sumber: PIHPS Bank Indonesia & Logam Mulia",
              "#hargahariini #sembako #hargapasar #hargapangan #infoharga"]
    return "\n".join(baris)

def post_ig(img_path, caption):
    cmd = ["instagram-cli", "post-feed", "--account-id", IG_ACCOUNT,
           "--file", img_path, "--caption", caption]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    ok = r.returncode == 0
    print(f"  IG: {'OK' if ok else 'GAGAL/menunggu persetujuan'}")
    if not ok:
        print(f"    {r.stderr[:200]}")
    return ok

def post_threads(img_path, caption):
    cmd = ["threads-cli", "publish-post", "--account-id", THREADS_ACCOUNT,
           "--text", caption[:480],
           "--media-item", json.dumps({"file": img_path})]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    ok = r.returncode == 0
    print(f"  Threads: {'OK' if ok else 'GAGAL/menunggu persetujuan'}")
    if not ok:
        print(f"    {r.stderr[:200]}")
    return ok

def main():
    dry = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        target = f"harga-{args[0]}"
    else:
        files = sorted(f for f in os.listdir(DATA) if f.startswith("harga-"))
        if not files:
            print("tidak ada data harga"); return 1
        target = files[-1][:-5]
    d = json.load(open(os.path.join(DATA, target + ".json")))
    img_path = os.path.join(IMG, target + ".png")
    if not os.path.exists(img_path):
        print(f"gambar tidak ada: {img_path}"); return 1
    caption = bikin_caption(d)
    print(f"Target: {target}")
    print("--- caption ---")
    print(caption)
    print("---------------")
    if dry:
        print("DRY RUN - tidak posting")
        return 0
    ok1 = post_ig(img_path, caption)
    ok2 = post_threads(img_path, caption)
    json.dump({"tanggal": d["tanggal"], "ig": ok1, "threads": ok2},
              open(os.path.join(DATA, f"posting-{d['tanggal']}.json"), "w"))
    return 0 if (ok1 and ok2) else 2

if __name__ == "__main__":
    sys.exit(main())
