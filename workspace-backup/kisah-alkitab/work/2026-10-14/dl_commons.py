#!/usr/bin/env python3
"""Download cepat klip Commons -> workspace (BUKAN /tmp). Lisensi aman saja."""
import json, os, subprocess, sys, urllib.parse, urllib.request

OUT = os.path.expanduser("~/workspace/kisah-alkitab/work/2026-10-14/klip-baru")
os.makedirs(OUT, exist_ok=True)
MANI = os.path.join(OUT, "lisensi.json")
have = {}
if os.path.exists(MANI):
    have = json.load(open(MANI))

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "KisahAlkitabBot/1.0 (content production; contact: local)"}

def api(params):
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(API + "?" + q, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=40))

def lic_ok(em):
    lic = (em.get("LicenseShortName", {}) or {}).get("value", "")
    lic = lic.lower()
    bad = ["nc", "nd", "noncommercial", "no derivative", "gfdl"]
    if any(b in lic for b in bad):
        return None
    good = ["cc0", "public domain", "cc by-sa", "cc by"]
    for g in good:
        if g in lic:
            return em.get("LicenseShortName", {}).get("value", ""), (em.get("Artist", {}) or {}).get("value", "")
    return None

def search(keyword, n=12):
    d = api({"action": "query", "generator": "search", "gsrsearch": f"filetype:video {keyword}",
             "gsrnamespace": "6", "gsrlimit": str(n), "prop": "imageinfo",
             "iiprop": "url|size|extmetadata", "iiurlwidth": "1", "format": "json"})
    out = []
    for p in (d.get("query") or {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        url = ii.get("url", "")
        if not url.startswith("https://upload.wikimedia.org/"):
            continue
        em = ii.get("extmetadata") or {}
        ok = lic_ok(em)
        if not ok:
            continue
        lic, artist = ok
        out.append({"title": p["title"], "url": url, "size": ii.get("size", 0),
                    "license": lic, "artist": artist})
    return out

KEYWORDS = ["ocean waves crashing rocks", "sea waves storm", "Red Sea waves",
            "desert sunrise", "candle flame dark background", "starry night sky timelapse"]
seen_urls = {v["url"] for v in have.values()}
count = 0
for kw in KEYWORDS:
    if count >= 8:
        break
    try:
        cands = search(kw)
    except Exception as e:
        print(f"SEARCH GAGAL {kw}: {e}", flush=True); continue
    for c in cands:
        if count >= 8:
            break
        if c["url"] in seen_urls:
            continue
        if c["size"] and c["size"] > 120 * 1024 * 1024:
            continue
        fn = f"w{count+1:02d}.orig"
        dst = os.path.join(OUT, fn)
        print(f"DL {fn} [{c['license']}] {c['title'][:60]} ({c['size']//1024//1024 if c['size'] else '?'}MB)", flush=True)
        r = subprocess.run(["curl", "-sL", "--max-time", "300", "-o", dst, c["url"]],
                           capture_output=True)
        if r.returncode == 0 and os.path.getsize(dst) > 500000:
            have[fn] = c; seen_urls.add(c["url"]); count += 1
            json.dump(have, open(MANI, "w"), ensure_ascii=False, indent=1)
            print(f"  OK {fn}", flush=True)
        else:
            print(f"  GAGAL {fn}", flush=True)
            if os.path.exists(dst): os.remove(dst)
print(f"SELESAI: {count} file. Manifest: {MANI}")
