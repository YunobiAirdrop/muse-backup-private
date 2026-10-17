#!/usr/bin/env python3
"""Retry posting promo yang masih MENUNGGU PERSETUJUAN (2026-10-04).
Hanya posting ulang yang belum TERPOSTING, anti-duplikat."""
import json, os, sys, time, uuid, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import IG_ID, THREADS_1, THREADS_2, FB_PAGE

OUT = os.path.join(BASE, "promo_out")
MANIFEST = os.path.join(OUT, "manifest_2026-10-04.json")
REPORT = os.path.join(OUT, "posting_report_2026-10-04.json")
TIMEOUT = 200

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        return ("TERPOSTING" if r.returncode == 0 else "GAGAL", (r.stderr or r.stdout or "")[:150])
    except subprocess.TimeoutExpired:
        return ("MENUNGGU PERSETUJUAN", "timeout menunggu approval user")
    except Exception as e:
        return ("GAGAL", str(e)[:150])

def post_ig(img, vid, caption):
    cmd = ["instagram-cli", "post-feed", "--account-id", IG_ID, "--file", vid or img, "--caption", caption]
    if vid: cmd += ["--cover", img]
    return run(cmd)

def post_threads(account_id, img, vid, caption):
    media = {"file": vid or img}
    if vid: media["cover"] = img
    cmd = ["threads-cli", "publish-post", "--account-id", account_id,
           "--text", caption[:480], "--media-item", json.dumps(media)]
    return run(cmd)

def post_fb(img, vid, caption):
    cmd = ["facebook-cli", "pages", "posts", "create", "--page-id", FB_PAGE,
           "--text", caption[:900], "--request-id", str(uuid.uuid4()),
           "--privacy", "PUBLIC", "--file", vid or img]
    return run(cmd)

manifest = json.load(open(MANIFEST))
report = json.load(open(REPORT))
posted = {(h["produk"], h["akun"]) for h in report["hasil"] if h["status"] == "TERPOSTING"}

# video final per produk
import glob
def video_final(nama):
    slug = "".join(c if c.isalnum() else "-" for c in nama.lower())[:30]
    cands = glob.glob(os.path.join(OUT, "video_final_*.mp4"))
    # cocokkan berdasarkan urutan manifest
    return None

vids = sorted(glob.glob(os.path.join(OUT, "video_final_*.mp4")))
print(f"video ditemukan: {len(vids)}", flush=True)

AKUN = [("IG", lambda img, vid, cap: post_ig(img, vid, cap)),
        ("Threads-1", lambda img, vid, cap: post_threads(THREADS_1, img, vid, cap)),
        ("Threads-2", lambda img, vid, cap: post_threads(THREADS_2, img, vid, cap)),
        ("FB", lambda img, vid, cap: post_fb(img, vid, cap))]

for i, p in enumerate(manifest):
    nama = p["nama"]
    img = os.path.join(BASE, "promo_img", p.get("file_gambar", ""))
    if not os.path.exists(img):
        img = os.path.join(OUT, p.get("file_gambar", ""))
    vid = vids[i] if i < len(vids) else None
    caption = p["caption"]
    for akun, fn in AKUN:
        if (nama, akun) in posted:
            continue
        print(f">> {nama} [{akun}]", flush=True)
        status, info = fn(img, vid, caption)
        print(f"   {status} {info[:80]}", flush=True)
        report["hasil"].append({"produk": nama, "akun": akun, "status": status, "info": info})
        if status == "TERPOSTING":
            posted.add((nama, akun))
        json.dump(report, open(REPORT, "w"), ensure_ascii=False, indent=1)
        time.sleep(10)

print("SELESAI", flush=True)
