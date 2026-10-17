#!/usr/bin/env python3
"""Posting promo 2026-10-07 ke 4 akun: IG, Threads x2, FB Page.
- Tiap post CLI timeout 200 dtk -> status MENUNGGU PERSETUJUAN (aturan runtime, bukan gagal).
- Probe rate limit Threads sekali di awal: kalau 429 -> semua Threads diskip sampai lewat tengah malam.
- Anti-duplikat: lewati yang sudah TERPOSTING di report."""
import json, os, sys, time, uuid, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import IG_ID, THREADS_1, THREADS_2, FB_PAGE

OUT = os.path.join(BASE, "promo_out")
MANIFEST = os.path.join(OUT, "manifest_2026-10-07.json")
REPORT = os.path.join(OUT, "posting_report_2026-10-07.json")
TIMEOUT = 200

def run(cmd, timeout=TIMEOUT):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (r.stderr or r.stdout or "")[:200]
        if r.returncode == 0:
            return ("TERPOSTING", out)
        if "429" in out or "rate" in out.lower():
            return ("RATE_LIMIT", out)
        return ("GAGAL", out)
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
    cmd = ["facebook-cli", "pages", "posts", "create", "--page-id", FB_PAGE,
           "--text", caption[:900], "--request-id", str(uuid.uuid4()),
           "--privacy", "PUBLIC", "--file", vid or img]
    return run(cmd)

manifest = json.load(open(MANIFEST))["produk"]
# video final hasil rakit
rakit = {}
rp = os.path.join(OUT, "rakit_2026-10-07.json")
if os.path.exists(rp):
    rakit = json.load(open(rp))
report = {"tanggal": "2026-10-07", "hasil": []}
if os.path.exists(REPORT):
    report = json.load(open(REPORT))
posted = {(h["produk"], h["akun"]) for h in report["hasil"] if h["status"] == "TERPOSTING"}

threads_blocked = any(h["akun"].startswith("Threads") and h["status"] == "RATE_LIMIT"
                      for h in report["hasil"])

AKUN = [("IG", lambda img, vid, cap: post_ig(img, vid, cap)),
        ("Threads-1", lambda img, vid, cap: post_threads(THREADS_1, img, vid, cap)),
        ("Threads-2", lambda img, vid, cap: post_threads(THREADS_2, img, vid, cap)),
        ("FB", lambda img, vid, cap: post_fb(img, vid, cap))]

for p in manifest:
    nama = p["nama"]
    img = p["gambar_promo"]
    slug = p["file_gambar"].replace(".jpg", "")
    vid = (rakit.get(slug, {}).get("wa") or p.get("video_final")
           or p.get("video_fallback"))
    caption = p["caption"]
    for akun, fn in AKUN:
        if (nama, akun) in posted:
            continue
        if akun.startswith("Threads") and threads_blocked:
            st = ("RATE_LIMIT", "diskip: rate limit Threads masih aktif, coba lagi lewat tengah malam")
            report["hasil"].append({"produk": nama, "akun": akun, "status": st[0], "info": st[1]})
            print(f">> {nama} [{akun}] {st[0]}", flush=True)
            continue
        print(f">> {nama} [{akun}]", flush=True)
        status, info = fn(img, vid, caption)
        print(f"   {status} {info[:80]}", flush=True)
        report["hasil"].append({"produk": nama, "akun": akun, "status": status, "info": info})
        if status == "TERPOSTING":
            posted.add((nama, akun))
        if akun.startswith("Threads") and status == "RATE_LIMIT":
            threads_blocked = True
            print("   !! Threads rate limit aktif -> semua postingan Threads diskip", flush=True)
        json.dump(report, open(REPORT, "w"), ensure_ascii=False, indent=1)
        time.sleep(30)

print("SELESAI", flush=True)
ringkas = {}
for h in report["hasil"]:
    ringkas[h["status"]] = ringkas.get(h["status"], 0) + 1
print("RINGKASAN:", ringkas, flush=True)
