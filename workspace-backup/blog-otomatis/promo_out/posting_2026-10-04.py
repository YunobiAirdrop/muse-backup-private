#!/usr/bin/env python3
"""Posting promo afiliasi harian 2026-10-04: 5 produk x 4 akun.
Setiap produk: 1 gambar promo + 1 video final presenter AI + caption + link.
Non-OK diklasifikasi: approval/pending/timeout -> 'menunggu persetujuan', lainnya 'gagal'.
"""
import json, os, subprocess, sys, time, uuid, threading

BASE = "/home/hatch/workspace/blog-otomatis"
OUT = os.path.join(BASE, "promo_out")
IG_ID = "17841462795414201"
THREADS_1 = "17841423460796922"
THREADS_2 = "17841442711837842"
FB_PAGE = "1347201611814398"
TIMEOUT = 200

ASSETS = {
    "Pouch Travel Organizer Serut": ("promo_90721168.jpg", "video_final_pouch-travel.mp4"),
    "Vitamin Minyak Ikan Kucing Omega 3&6": ("promo_90750872.jpg", "video_final_vitamin-ikan.mp4"),
    "Vitamin Pencernaan Kucing": ("promo_90768731.jpg", "video_final_vitamin-cerna.mp4"),
    "Sabun Cuci Piring 5 Liter Premium": ("promo_90784230.jpg", "video_final_sabun-piring.mp4"),
    "Impact Wrench Cordless Brushless 700NM": ("promo_90799485.jpg", "video_final_impact-wrench.mp4"),
}

def run(cmd, timeout=TIMEOUT):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout[-300:] + " | " + r.stderr[-300:]).strip()
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"")[-200:] if hasattr(e.stdout, "__len__") else ""
        return -1, f"TIMEOUT setelah {timeout}s (kemungkinan menunggu persetujuan) {out}"

def post_ig(img, vid, caption):
    cmd = ["instagram-cli", "post-feed", "--account-id", IG_ID,
           "--file", vid, "--caption", caption, "--cover", img]
    return run(cmd)

def post_threads(account_id, img, vid, caption):
    media = json.dumps({"file": vid, "cover": img})
    cmd = ["threads-cli", "publish-post", "--account-id", account_id,
           "--text", caption[:480], "--media-item", media]
    return run(cmd)

def post_fb(img, vid, caption):
    cmd = ["facebook-cli", "pages", "posts", "create",
           "--page-id", FB_PAGE, "--text", caption[:900],
           "--request-id", str(uuid.uuid4()), "--privacy", "PUBLIC",
           "--file", vid]
    return run(cmd)

def klasifikasikan(rc, msg):
    if rc == 0:
        return "TERPOSTING", msg
    m = msg.lower()
    if rc == -1 or any(k in m for k in ["approv", "pending", "confirm", "timeout", "user_confirmation", "waiting"]):
        return "MENUNGGU PERSETUJUAN", msg[:200]
    return "GAGAL", msg[:200]

def main():
    manifest = json.load(open(os.path.join(OUT, "manifest_2026-10-04.json")))
    hasil = []
    for p in manifest:
        nama = p["nama"]
        img_f, vid_f = ASSETS[nama]
        img, vid = os.path.join(OUT, img_f), os.path.join(OUT, vid_f)
        cap = p["caption"]
        print(f"\n>> {nama}", flush=True)
        tugas = [("IG", lambda: post_ig(img, vid, cap)),
                 ("Threads-1", lambda: post_threads(THREADS_1, img, vid, cap)),
                 ("Threads-2", lambda: post_threads(THREADS_2, img, vid, cap)),
                 ("FB", lambda: post_fb(img, vid, cap))]
        res = {}
        ths = []
        def kerja(k, fn):
            rc, msg = fn()
            res[k] = (rc, msg)
        for k, fn in tugas:
            t = threading.Thread(target=kerja, args=(k, fn))
            ths.append(t); t.start()
        for t in ths:
            t.join()
        for k, _ in tugas:
            rc, msg = res[k]
            status, info = klasifikasikan(rc, msg)
            print(f"  [{k}] {status}" + (f" :: {info[:80]}" if status != "TERPOSTING" else ""), flush=True)
            hasil.append({"produk": nama, "akun": k, "status": status, "info": info})
        time.sleep(60)  # jeda antar produk
    json.dump({"tanggal": "2026-10-04", "hasil": hasil},
              open(os.path.join(OUT, "posting_report_2026-10-04.json"), "w"),
              ensure_ascii=False, indent=1)
    ringkas = {}
    for h in hasil:
        ringkas[h["status"]] = ringkas.get(h["status"], 0) + 1
    print("\nRINGKASAN:", ringkas, flush=True)

if __name__ == "__main__":
    main()
