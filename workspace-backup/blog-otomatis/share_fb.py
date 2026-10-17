#!/usr/bin/env python3
"""Auto-share 3 artikel terbaik hari ini ke Facebook Page BeritaViraldotcom.
Gambar meme + video berita 9:16 + caption viral + link (bisa diklik di FB).
CATATAN: tiap posting butuh approval (aturan facebook-cli) -> mode semi-otomatis.
Pakai: ./venv/bin/python share_fb.py [--dry-run]
"""
import json, os, sys, time, subprocess, uuid

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from share_ig import artikel_hari_ini, unduh_gambar, hashtag_niche, IG_DIR
from meme_gen import bikin_meme
from video_gen import bikin_video

PAGE_ID = "1347201611814398"  # BeritaViraldotcom
JUMLAH_SHARE = 3
BLOG_KEY = {"KabarViral": "kabarviral", "CuanPintar": "cuanpintar",
            "TeknoGebrakan": "teknogebrakan", "SehatBugar": "sehatbugar"}

def bikin_caption_fb(artikel):
    try:
        from caption_viral import bikin_caption
        cap = bikin_caption(artikel["judul"], artikel["blog"])
    except Exception:
        cap = f"{artikel['judul']}\n\n{hashtag_niche(artikel['blog'], n=5)}"
    cap = cap[:900]
    # link blog di FB bisa diklik -> taruh jelas
    return f"{cap}\n\nBaca selengkapnya: {artikel['link']}"

def posting_fb(artikel):
    judul = artikel["judul"]
    ts = int(time.time())
    img_raw = os.path.join(IG_DIR, f"raw_{ts}.jpg")
    if not unduh_gambar(artikel["gambar"], img_raw):
        print(f"  gambar gagal: {judul[:40]}")
        return False
    img_path = os.path.join(IG_DIR, f"meme_{ts}.jpg")
    try:
        bikin_meme(img_raw, judul, BLOG_KEY.get(artikel["blog"], "kabarviral"), img_path)
    except Exception as e:
        print(f"  meme gagal ({e}), pakai foto asli")
        img_path = img_raw
    vid_path = os.path.join(IG_DIR, f"vid_{ts}.mp4")
    try:
        bikin_video(img_path, vid_path)
    except Exception as e:
        print(f"  video gagal ({str(e)[:60]}), pakai gambar saja")
        vid_path = None
    media = vid_path or img_path
    caption = bikin_caption_fb(artikel)
    r = subprocess.run(
        ["facebook-cli", "pages", "posts", "create",
         "--page-id", PAGE_ID, "--text", caption,
         "--request-id", str(uuid.uuid4()),
         "--privacy", "PUBLIC", "--file", media],
        capture_output=True, text=True, timeout=300)
    ok = r.returncode == 0
    print(f"  {'OK' if ok else 'GAGAL'}: {judul[:50]}")
    if not ok:
        print(f"    err: {r.stderr[:300]}")
    return ok

def main():
    dry = "--dry-run" in sys.argv
    daftar = artikel_hari_ini()[:JUMLAH_SHARE]
    print(f"Artikel siap share FB: {len(daftar)}")
    for a in daftar:
        print(f" - {a['judul'][:60]} ({a['blog']})")
    if dry:
        print("DRY RUN - tidak posting")
        return
    for i, a in enumerate(daftar):
        posting_fb(a)
        if i < len(daftar) - 1:
            time.sleep(120)

if __name__ == "__main__":
    main()
