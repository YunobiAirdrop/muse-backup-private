#!/usr/bin/env python3
"""Auto-share artikel terbaik hari ini ke Instagram feed.
Dipanggil setelah pipeline posting selesai. Pilih 3 artikel terbaik,
posting sebagai feed post dengan gambar + caption + hashtag.
"""
import json, os, re, sys, time, subprocess, urllib.request
from datetime import datetime, timezone, timedelta
import feedparser

BASE = os.path.dirname(os.path.abspath(__file__))
IG_DIR = os.path.join(BASE, "ig")
os.makedirs(IG_DIR, exist_ok=True)

WIB = timezone(timedelta(hours=7))
ACCOUNT_ID = "17841462795414201"  # falcon_esport537
JUMLAH_SHARE = 3

cfg = json.load(open(os.path.join(BASE, "config.json")))

def skor(judul):
    """Skor sederhana: judul spesifik + kata kunci menarik."""
    s = 0
    kata = judul.lower()
    for kw in ["viral", "heboh", "kecelakaan", "demo", "bencana", "gempa",
               "banjir", "korupsi", "kpk", "harga", "emas", "gratis",
               "bantuan", "timnas", "gol", "anies", "prabowo", "jokowi",
               "mencengangkan", "terungkap", "resmi"]:
        if kw in kata:
            s += 2
    if 40 < len(judul) < 120:
        s += 1
    return s

def artikel_hari_ini():
    hasil = []
    today = datetime.now(WIB).date()
    for b in cfg["blogs"]:
        if not b.get("url"):
            continue  # url blog belum diisi
        feed_url = f"{b['url']}/feeds/posts/default?max-results=15"
        try:
            d = feedparser.parse(feed_url)
        except Exception:
            continue
        # peta judul -> gambar dari artikel json
        gambar_map = {}
        aj = os.path.join(BASE, f"artikel-{b['nama']}.json")
        if os.path.exists(aj):
            for a in json.load(open(aj)):
                gambar_map[a["judul"]] = a.get("gambar", "")
        for e in d.entries:
            try:
                pub = datetime(*e.published_parsed[:6], tzinfo=timezone.utc).astimezone(WIB)
            except Exception:
                continue
            if pub.date() != today:
                continue
            judul = e.get("title", "")
            link = e.get("link", "")
            gambar = gambar_map.get(judul, "")
            if not gambar:
                continue  # butuh gambar untuk IG
            hasil.append({
                "judul": judul, "link": link, "gambar": gambar,
                "blog": b["tampil"], "blog_url": b["url"],
                "skor": skor(judul),
            })
    # dedup berdasar judul
    unik = {}
    for a in hasil:
        unik.setdefault(a["judul"], a)
    # gambar ASLI dari berita didahulukan; gambar cadangan (random) paling belakang
    def _asli(a):
        g = a.get("gambar", "")
        return 0 if ("picsum.photos" in g) else 1
    return sorted(unik.values(), key=lambda x: (-_asli(x), -x["skor"]))

def unduh_gambar(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r, open(path, "wb") as f:
        f.write(r.read())
    if os.path.getsize(path) < 5000:
        return False
    # pastikan benar-benar file gambar (bukan HTML error / hotlink-blocked)
    with open(path, "rb") as f:
        magic = f.read(12)
    return (magic[:3] == b"\xff\xd8\xff" or          # JPEG
            magic[:8] == b"\x89PNG\r\n\x1a\n" or     # PNG
            magic[:4] == b"RIFF" or                  # WEBP
            magic[:6] in (b"GIF87a", b"GIF89a"))     # GIF

TAG_POOL = {
    "KabarViral": ["beritaterkini", "kabarviral", "indonesia", "viralindonesia",
                   "beritaindonesia", "infohariini", "kabarterkini", "beritaviral",
                   "infoterkini", "warganet"],
    "CuanPintar": ["keuangan", "investasi", "cuan", "finansial", "menabung",
                   "saham", "emas", "tipskeuangan", "melekfinansial",
                   "investasipemula"],
    "TeknoGebrakan": ["teknologi", "gadget", "techindonesia", "smartphone",
                      "inovasi", "digital", "gadgetindonesia", "teknologiterkini",
                      "reviewgadget", "duniadigital"],
    "SehatBugar": ["kesehatan", "hidupsehat", "tipssehat", "sehatalami",
                   "olahraga", "gayahidupsehat", "kesehatanmental",
                   "polamakansehat", "infokesehatan", "sehatitumahal"],
}
TAG_FYP = ["fyp", "viral", "foryoupage"]  # khusus konten video

def hashtag_niche(blog, n=6, pakai_fyp=False):
    """Hashtag rotasi harian: tidak itu-itu saja, anti-spam.
    2 slot untuk tag FYP/besar + sisanya rotasi dari pool niche."""
    pool = TAG_POOL.get(blog, TAG_POOL["KabarViral"])
    start = datetime.now(WIB).timetuple().tm_yday % len(pool)
    urut = [pool[(start + i) % len(pool)] for i in range(len(pool))]
    pilih = []
    if pakai_fyp:
        pilih += TAG_FYP[:2]
    pilih += urut[:n - len(pilih)]
    return " ".join(f"#{t}" for t in pilih)

def posting_ig(artikel):
    judul = artikel["judul"]
    img_raw = os.path.join(IG_DIR, f"raw_{int(time.time())}.jpg")
    if not unduh_gambar(artikel["gambar"], img_raw):
        print(f"  gambar gagal: {judul[:40]}")
        return False
    # ubah jadi meme berita viral
    from meme_gen import bikin_meme
    img_path = os.path.join(IG_DIR, f"meme_{int(time.time())}.jpg")
    blog_key = {"KabarViral": "kabarviral", "CuanPintar": "cuanpintar",
                "TeknoGebrakan": "teknogebrakan", "SehatBugar": "sehatbugar"}.get(artikel["blog"], "kabarviral")
    try:
        bikin_meme(img_raw, judul, blog_key, img_path)
    except Exception as e:
        print(f"  meme gagal ({e}), pakai foto asli")
        img_path = img_raw
    # ubah jadi video berita 9:16 (reel) dari meme
    from video_gen import bikin_video
    vid_path = os.path.join(IG_DIR, f"vid_{int(time.time())}.mp4")
    try:
        bikin_video(img_path, vid_path)
    except Exception as e:
        print(f"  video gagal ({str(e)[:80]}), pakai gambar saja")
        vid_path = None
    try:
        from caption_viral import bikin_caption
        caption = bikin_caption(judul, artikel["blog"])
    except Exception as e:
        print(f"  caption AI gagal ({str(e)[:60]}), pakai template")
        caption = (f"{judul}\n\nBaca selengkapnya di {artikel['blog_url']}\n\n"
                   f"{hashtag_niche(artikel['blog'], pakai_fyp=True)}")
    if len(caption) > 2100:
        caption = caption[:2100]
    if vid_path:
        cmd = ["instagram-cli", "post-feed", "--account-id", ACCOUNT_ID,
               "--file", vid_path, "--cover", img_path, "--caption", caption]
    else:
        cmd = ["instagram-cli", "post-feed", "--account-id", ACCOUNT_ID,
               "--file", img_path, "--caption", caption]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    ok = r.returncode == 0
    print(f"  {'OK' if ok else 'GAGAL'}: {judul[:50]}")
    if not ok:
        print(f"    err: {r.stderr[:200]}")
    return ok

def main():
    dry = "--dry-run" in sys.argv
    daftar = artikel_hari_ini()
    print(f"Artikel hari ini bergambar: {len(daftar)}")
    pilihan = daftar[:JUMLAH_SHARE]
    for a in pilihan:
        print(f" - [{a['skor']}] {a['judul'][:60]} ({a['blog']})")
    if dry:
        print("DRY RUN - tidak posting")
        return
    for i, a in enumerate(pilihan):
        posting_ig(a)
        if i < len(pilihan) - 1:
            time.sleep(120)  # jeda 2 menit antar posting

if __name__ == "__main__":
    main()
