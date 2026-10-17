#!/usr/bin/env python3
"""Ambil 8 foto hewan dari Wikimedia Commons (lisensi aman komersial saja).

Untuk tiap query: cari file via Commons API, cek extmetadata LicenseShortName
per file (terima CC0 / Public domain / CC BY / CC BY-SA; tolak NC/ND),
unduh thumbnail 1280px, cek kecerahan rata-rata (foto gelap gagal cutout),
simpan ke work/hewan-part1/foto/itemNN.jpg + tulis kredit ke tema/hewan.json.
"""
import html, json, re, sys, urllib.request, urllib.parse
from pathlib import Path

BASE = Path.home() / "workspace" / "macam-macam"
FOTO_DIR = BASE / "work" / "hewan-part1" / "foto"
FOTO_DIR.mkdir(parents=True, exist_ok=True)
API = "https://commons.wikimedia.org/w/api.php"

QUERIES = [("lion", "Singa"), ("elephant", "Gajah"), ("giraffe", "Jerapah"),
           ("tiger", "Harimau"), ("polar bear", "Beruang Kutub"),
           ("penguin", "Pinguin"), ("dolphin", "Lumba-lumba"),
           ("kangaroo", "Kanguru")]

def api(params):
    params = {"action": "query", "format": "json", "formatversion": "2", **params}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "MacamMacamBot/1.0 (kids-edu)"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)

def lisensi_ok(short):
    s = (short or "").upper()
    if "NC" in s or "ND" in s:
        return False
    return ("CC0" in s or "PUBLIC DOMAIN" in s or "CC BY-SA" in s
            or ("CC BY" in s))

def strip_html(t):
    return re.sub(r"<[^>]+>", "", html.unescape(t or "")).strip()

def kecerahan(path):
    from PIL import Image, ImageStat
    im = Image.open(path).convert("L").resize((120, 120))
    return ImageStat.Stat(im).mean[0]

def cari(query):
    data = api({"generator": "search", "gsrsearch": f"{query} filetype:bitmap",
                "gsrnamespace": "6", "gsrlimit": "25",
                "prop": "imageinfo", "iiprop": "url|size|extmetadata",
                "iiurlwidth": "1280",
                "iiextmetadatafilter": "LicenseShortName|Artist|LicenseUrl"})
    return data.get("query", {}).get("pages", [])

def unduh(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "MacamMacamBot/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())

hasil = []
tema = json.load(open(BASE / "tema" / "hewan.json"))
for idx, (q, nama_id) in enumerate(QUERIES):
    dest = FOTO_DIR / f"item{idx:02d}.jpg"
    dipilih = None
    for pg in cari(q):
        ii = (pg.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        short = (em.get("LicenseShortName") or {}).get("value", "")
        if not lisensi_ok(short):
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if min(w, h) < 500:
            continue
        artist = strip_html((em.get("Artist") or {}).get("value", ""))
        if not artist:
            artist = "Wikimedia Commons"
        url = ii.get("thumburl") or ii.get("url")
        try:
            unduh(url, dest)
        except Exception as e:
            print(f"  ! unduh gagal {pg.get('title')}: {e}")
            continue
        br = kecerahan(dest)
        if br < 60:
            print(f"  ~ {pg.get('title')} terlalu gelap (mean={br:.0f}), cari lain")
            continue
        dipilih = (pg.get("title"), short, artist, br)
        break
    if not dipilih:
        print(f"GAGAL: tidak ada foto layak untuk '{q}'")
        sys.exit(1)
    title, short, artist, br = dipilih
    kredit = f"{artist} / Wikimedia Commons ({short})"
    print(f"OK item{idx:02d} {nama_id}: {title} | {short} | mean={br:.0f}")
    hasil.append({"query": q, "nama": nama_id, "file": str(dest),
                  "commons_title": title, "lisensi": short, "kredit": kredit})

# update tema json
for i, h in enumerate(hasil):
    tema["items"][i]["foto_lokal"] = h["file"]
    tema["items"][i]["kredit"] = h["kredit"]
json.dump(tema, open(BASE / "tema" / "hewan.json", "w"), indent=1, ensure_ascii=False)
json.dump(hasil, open(FOTO_DIR / "kredit.json", "w"), indent=1, ensure_ascii=False)
print("SELESAI: tema/hewan.json terupdate dengan foto_lokal + kredit")
