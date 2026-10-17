#!/usr/bin/env python3
"""Kirim ulang 15 slot promo yang approval-nya timeout (2026-10-08).
Hanya slot MENUNGGU PERSETUJUAN; GAGAL/TERPOSTING tidak disentuh (anti-duplikat)."""
import json, subprocess, sys, time, uuid, os

BASE = "/home/hatch/workspace/blog-otomatis"
IG_ID = "17841462795414201"
THREADS_1 = "17841423460796922"
THREADS_2 = "17841442711837842"
FB_PAGE = "1347201611814398"

manifest = json.load(open(f"{BASE}/promo_out/manifest_2026-10-08.json"))
rakit = json.load(open(f"{BASE}/promo_out/rakit_2026-10-08.json"))
report_path = f"{BASE}/promo_out/posting_report_2026-10-08.json"
report = json.load(open(report_path))

# nama -> (slug, caption, gambar, video_wa)
pmap = {}
for p in manifest["produk"]:
    slug = p["file_gambar"].replace(".jpg", "")
    pmap[p["nama"]] = (slug, p["caption"], p["gambar_promo"],
                       rakit[slug]["wa"] if slug in rakit else None)

def post_ig(img, vid, caption):
    cmd = ["instagram-cli", "post-feed", "--account-id", IG_ID,
           "--file", vid or img, "--caption", caption]
    if vid: cmd += ["--cover", img]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode == 0, (r.stderr or r.stdout)[:200]

def post_threads(account_id, img, vid, caption):
    cmd = ["threads-cli", "publish-post", "--account-id", account_id,
           "--text", caption[:480],
           "--media-item", json.dumps({"file": vid or img,
                                       **({"cover": img} if vid else {})})]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode == 0, (r.stderr or r.stdout)[:200]

def post_fb(img, vid, caption):
    cmd = ["facebook-cli", "pages", "posts", "create", "--page-id", FB_PAGE,
           "--text", caption[:900], "--request-id", str(uuid.uuid4()),
           "--privacy", "PUBLIC", "--file", vid or img]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return r.returncode == 0, (r.stderr or r.stdout)[:200]

n_retry = 0
for slot in report["hasil"]:
    if slot["status"] != "MENUNGGU PERSETUJUAN":
        continue
    nama, akun = slot["produk"], slot["akun"]
    if nama not in pmap:
        slot["info"] = "retry: produk tidak ada di manifest"; continue
    slug, caption, img, vid = pmap[nama]
    if not os.path.exists(vid or ""):
        slot["info"] = "retry: video tidak ada"; continue
    print(f">> {nama} -> {akun}", flush=True)
    try:
        if akun == "IG": ok, err = post_ig(img, vid, caption)
        elif akun == "Threads-1": ok, err = post_threads(THREADS_1, img, vid, caption)
        elif akun == "Threads-2": ok, err = post_threads(THREADS_2, img, vid, caption)
        else: ok, err = post_fb(img, vid, caption)
    except subprocess.TimeoutExpired:
        ok, err = False, "timeout menunggu approval user (retry)"
    slot["status"] = "TERPOSTING" if ok else "MENUNGGU PERSETUJUAN"
    slot["info"] = ("retry ok" if ok else f"retry: {err[:120]}")
    print(f"   {'TERPOSTING' if ok else 'TETAP MENUNGGU: ' + err[:80]}", flush=True)
    n_retry += 1
    json.dump(report, open(report_path, "w"), indent=1, ensure_ascii=False)
    time.sleep(30)

print(f"SELESAI: {n_retry} slot dicoba ulang", flush=True)
