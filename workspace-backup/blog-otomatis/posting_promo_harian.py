#!/usr/bin/env python3
"""Posting promo harian ke 4 akun sosmed.
Baca manifest, pakai video final presenter (final-wa.mp4) bila ada,
fallback ke video Ken Burns, terakhir gambar saja.
Tiap panggilan CLI dibatasi timeout 150 dtk: stall = 'menunggu persetujuan'.
"""
import json, os, sys, time, uuid, subprocess
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_promo import IG_ID, THREADS_1, THREADS_2, FB_PAGE

WIB = timezone(timedelta(hours=7))
OUT = os.path.join(BASE, "promo_out")
MANIFEST = os.path.join(OUT, "manifest-2026-10-03.json")
HASIL = os.path.join(OUT, "hasil-posting-2026-10-03.json")
TIMEOUT = 150

def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        return ("ok" if r.returncode == 0 else "gagal", (r.stderr or r.stdout or "")[:200])
    except subprocess.TimeoutExpired:
        return ("menunggu persetujuan", "timeout 150 dtk menunggu approval user")
    except Exception as e:
        return ("gagal", str(e)[:200])

def post_ig(img, vid, caption):
    cmd = ["instagram-cli", "post-feed", "--account-id", IG_ID,
           "--file", vid or img, "--caption", caption]
    if vid:
        cmd += ["--cover", img]
    return run(cmd)

def post_threads(account_id, img, vid, caption):
    teks = caption[:480]
    media = {"file": vid or img}
    if vid:
        media["cover"] = img
    cmd = ["threads-cli", "publish-post", "--account-id", account_id,
           "--text", teks, "--media-item", json.dumps(media)]
    return run(cmd)

def post_fb(img, vid, caption):
    cmd = ["facebook-cli", "pages", "posts", "create",
           "--page-id", FB_PAGE, "--text", caption[:900],
           "--request-id", str(uuid.uuid4()),
           "--privacy", "PUBLIC", "--file", vid or img]
    return run(cmd)

def main():
    manifest = json.load(open(MANIFEST))
    hasil = {"tanggal": datetime.now(WIB).date().isoformat(), "posting": []}
    for p in manifest["produk"]:
        slug = p["slug"]
        d = os.path.join(OUT, "2026-10-03", slug)
        final_wa = os.path.join(d, "final-wa.mp4")
        vid = final_wa if os.path.exists(final_wa) else p.get("video_fallback")
        if vid and not os.path.exists(vid):
            vid = None
        img, caption = p["gambar_promo"], p["caption"]
        sumber = "presenter-20s" if (vid and "final-wa" in vid) else ("kenburns" if vid else "gambar")
        print(f"\n>> {p['nama']} [{sumber}]", flush=True)
        rec = {"produk": p["nama"], "video": sumber, "akun": {}}
        tugas = [("IG", lambda: post_ig(img, vid, caption)),
                 ("Threads-beritaviraldotcom", lambda: post_threads(THREADS_1, img, vid, caption)),
                 ("Threads-ngewebyuk", lambda: post_threads(THREADS_2, img, vid, caption)),
                 ("FB-BeritaViraldotcom", lambda: post_fb(img, vid, caption))]
        for nama_akun, fn in tugas:
            status, info = fn()
            rec["akun"][nama_akun] = {"status": status, "info": info}
            print(f"   [{nama_akun}] {status} {info[:80]}", flush=True)
            time.sleep(15)
        hasil["posting"].append(rec)
    json.dump(hasil, open(HASIL, "w"), ensure_ascii=False, indent=1)
    print("\nhasil:", HASIL)

if __name__ == "__main__":
    main()
