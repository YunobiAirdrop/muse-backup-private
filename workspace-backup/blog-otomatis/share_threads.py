#!/usr/bin/env python3
"""Auto-share 3 artikel terbaik hari ini ke Threads (@beritaviraldotcom).
Video berita 9:16 + 1 postingan ringkas (hook + link, maks 500 karakter).
CATATAN: tiap posting butuh explicit approval (aturan threads-cli) -> semi-otomatis.
Pakai: ./venv/bin/python share_threads.py [--dry-run]
"""
import json, os, sys, time, subprocess
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
from share_ig import artikel_hari_ini, unduh_gambar, hashtag_niche, IG_DIR
from meme_gen import bikin_meme
from video_gen import bikin_video

ACCOUNT_ID = "17841442711837842"  # beritaviraldotcom
JUMLAH_SHARE = 3
BLOG_KEY = {"KabarViral": "kabarviral", "CuanPintar": "cuanpintar",
            "TeknoGebrakan": "teknogebrakan", "SehatBugar": "sehatbugar"}

def hook_map():
    """judul -> post pertama dari thread_gen hari ini (kalau ada)."""
    m = {}
    f = os.path.join(DATA, f"thread-{date.today().isoformat()}.json")
    if os.path.exists(f):
        try:
            for item in json.load(open(f)):
                th = item.get("thread") or []
                if th:
                    m[item["judul"]] = th[0]
        except Exception:
            pass
    return m

def bikin_teks(artikel, hooks):
    hook = hooks.get(artikel["judul"], artikel["judul"])
    tags = hashtag_niche(artikel["blog"], pakai_fyp=True)
    teks = f"{hook}\n\nBaca selengkapnya: {artikel['link']}\n\n{tags}"
    return teks[:480]

def posting_threads(artikel, hooks):
    judul = artikel["judul"]
    ts = int(time.time())
    img_raw = os.path.join(IG_DIR, f"raw_{ts}.jpg")
    if not unduh_gambar(artikel["gambar"], img_raw):
        print(f"  gambar gagal: {judul[:40]}")
        return False
    img_path = os.path.join(IG_DIR, f"meme_{ts}.jpg")
    try:
        bikin_meme(img_raw, judul, BLOG_KEY.get(artikel["blog"], "kabarviral"), img_path)
    except Exception:
        img_path = img_raw
    vid_path = os.path.join(IG_DIR, f"vid_{ts}.mp4")
    try:
        bikin_video(img_path, vid_path)
    except Exception as e:
        print(f"  video gagal ({str(e)[:60]})")
        vid_path = None
    teks = bikin_teks(artikel, hooks)
    cmd = ["threads-cli", "publish-post", "--account-id", ACCOUNT_ID, "--text", teks]
    if vid_path:
        cmd += ["--media-item", json.dumps({"file": vid_path, "cover": img_path})]
    else:
        cmd += ["--media-item", json.dumps({"file": img_path})]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    ok = r.returncode == 0
    print(f"  {'OK' if ok else 'GAGAL'}: {judul[:50]}")
    if not ok:
        print(f"    err: {r.stderr[:300]}")
    return ok

def main():
    dry = "--dry-run" in sys.argv
    daftar = artikel_hari_ini()[:JUMLAH_SHARE]
    hooks = hook_map()
    print(f"Artikel siap share Threads: {len(daftar)}")
    for a in daftar:
        print(f" - {a['judul'][:60]} ({a['blog']})")
    if dry:
        print("DRY RUN - tidak posting")
        return
    for i, a in enumerate(daftar):
        posting_threads(a, hooks)
        if i < len(daftar) - 1:
            time.sleep(120)

if __name__ == "__main__":
    main()
