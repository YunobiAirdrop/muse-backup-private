#!/usr/bin/env python3
"""Posting promo afiliasi 2026-10-05 ke 4 akun: IG, Threads x2, FB Page.
Video final presenter AI (720p WA-friendly) + gambar promo sebagai cover + caption + link.
Posting butuh approval user (runtime): timeout -> catat MENUNGGU PERSETUJUAN, bukan gagal.
Anti-duplikat: skip (produk, akun) yang sudah TERPOSTING di report.
"""
import json, os, sys, time, uuid, subprocess, glob

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import IG_ID, THREADS_1, THREADS_2, FB_PAGE

OUT = os.path.join(BASE, "promo_out")
MANIFEST = os.path.join(OUT, "manifest-2026-10-05.json")
REPORT = os.path.join(OUT, "posting_report_2026-10-05.json")
TIMEOUT = 150

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        return ("TERPOSTING" if r.returncode == 0 else "GAGAL", (r.stderr or r.stdout or "")[:150])
    except subprocess.TimeoutExpired:
        return ("MENUNGGU PERSETUJUAN", "timeout menunggu approval user")
    except Exception as e:
        return ("GAGAL", str(e)[:150])

def post_ig(img, vid, caption):
    cmd = ["instagram-cli", "post-feed", "--account-id", IG_ID,
           "--file", vid or img, "--caption", caption]
    if vid:
        cmd += ["--cover", img]
    return run(cmd)

def post_threads(account_id, img, vid, caption):
    media = {"file": vid or img}
    if vid:
        media["cover"] = img
    cmd = ["threads-cli", "publish-post", "--account-id", account_id,
           "--text", caption[:480], "--media-item", json.dumps(media)]
    return run(cmd)

def post_fb(img, vid, caption):
    cmd = ["facebook-cli", "pages", "posts", "create",
           "--page-id", FB_PAGE, "--text", caption[:900],
           "--request-id", str(uuid.uuid4()),
           "--privacy", "PUBLIC", "--file", vid or img]
    return run(cmd)

manifest = json.load(open(MANIFEST))
report = {"tanggal": manifest["tanggal"], "hasil": []}
if os.path.exists(REPORT):
    try:
        report = json.load(open(REPORT))
    except Exception:
        pass
posted = {(h["produk"], h["akun"]) for h in report["hasil"] if h["status"] == "TERPOSTING"}

AKUN = [("IG", "ig"), ("Threads-@beritaviraldotcom", "t1"),
        ("Threads-@ngewebyuk", "t2"), ("FB-BeritaViraldotcom", "fb")]

for p in manifest["produk"]:
    nama, slug = p["nama"], p["slug"]
    img = p["gambar_promo"]
    vid = p.get("video_final_720p") or p.get("video_final") or p.get("video_fallback")
    caption = p["caption"]
    for nama_akun, kode in AKUN:
        key = (slug, kode)
        if key in posted:
            print(f"  [{nama_akun}] {slug}: sudah TERPOSTING (skip)", flush=True)
            continue
        if kode == "ig":
            status, info = post_ig(img, vid, caption)
        elif kode == "t1":
            status, info = post_threads(THREADS_1, img, vid, caption)
        elif kode == "t2":
            status, info = post_threads(THREADS_2, img, vid, caption)
        else:
            status, info = post_fb(img, vid, caption)
        print(f"  [{nama_akun}] {nama}: {status} {info[:60]}", flush=True)
        report["hasil"].append({"produk": slug, "nama": nama, "akun": kode,
                                "akun_nama": nama_akun, "status": status,
                                "info": info, "video": os.path.basename(vid) if vid else None})
        json.dump(report, open(REPORT, "w"), ensure_ascii=False, indent=1)
        if status == "TERPOSTING":
            posted.add(key)
        time.sleep(10)

n_ok = sum(1 for h in report["hasil"] if h["status"] == "TERPOSTING")
n_wait = sum(1 for h in report["hasil"] if h["status"] == "MENUNGGU PERSETUJUAN")
print(f"SELESAI: TERPOSTING={n_ok} MENUNGGU_PERSETUJUAN={n_wait} TOTAL={len(report['hasil'])}")
json.dump(report, open(REPORT, "w"), ensure_ascii=False, indent=1)
