#!/usr/bin/env python3
"""Putaran 2: keyword sisa utk Nuh & bahtera. Maks 2 per keyword."""
import json, os, subprocess, time, urllib.parse, urllib.request

OUT = os.path.expanduser("~/workspace/kisah-alkitab/work/2026-10-16/klip")
MANI = os.path.join(OUT, "lisensi.json")
have = json.load(open(MANI))

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "KisahAlkitabBot/1.0 (content production; contact: local)"}

def api(params):
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(API + "?" + q, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=40))

def lic_ok(em):
    lic = (em.get("LicenseShortName", {}) or {}).get("value", "").lower()
    if any(b in lic for b in ["nc", "nd", "noncommercial", "no derivative", "gfdl"]):
        return None
    for g in ["cc0", "public domain", "cc by-sa", "cc by"]:
        if g in lic:
            return em.get("LicenseShortName", {}).get("value", ""), (em.get("Artist", {}) or {}).get("value", "")
    return None

def search(keyword, n=14):
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

KEYWORDS = ["ocean storm waves", "rain storm dark clouds", "rainbow sky",
            "dove flying", "olive tree", "sunrise desert",
            "wooden ship sea", "candle light dark"]

MAX_PER_KW = 2
DEADLINE = time.time() + 45 * 60
seen_urls = {v["url"] for v in have.values()}
idx = 17
total = 0
for kw in KEYWORDS:
    if time.time() > DEADLINE:
        break
    try:
        cands = search(kw)
    except Exception as e:
        print(f"SEARCH GAGAL {kw}: {e}", flush=True); continue
    got = 0
    for c in cands:
        if got >= MAX_PER_KW or time.time() > DEADLINE:
            break
        if c["url"] in seen_urls:
            continue
        if c["size"] and (c["size"] > 120 * 1024 * 1024 or c["size"] < 800 * 1024):
            continue
        fn = f"n{idx:02d}.orig"
        dst = os.path.join(OUT, fn)
        mb = c["size"] // 1024 // 1024 if c["size"] else 0
        print(f"DL {fn} [{c['license']}] {c['title'][:70]} ({mb}MB) kw={kw}", flush=True)
        ok_dl = False
        for attempt in (1, 2):
            r = subprocess.run(["curl", "-sL", "--max-time", "240", "-o", dst, c["url"]],
                               capture_output=True)
            if r.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 500000:
                ok_dl = True; break
            print(f"  percobaan {attempt} gagal", flush=True)
        if ok_dl:
            c["asal"] = f"commons search '{kw}'"
            have[fn] = c; seen_urls.add(c["url"]); got += 1; total += 1; idx += 1
            json.dump(have, open(MANI, "w"), ensure_ascii=False, indent=1)
            print(f"  OK {fn}", flush=True)
        else:
            print(f"  GAGAL {fn} (2x)", flush=True)
            if os.path.exists(dst): os.remove(dst)
print(f"SELESAI putaran 2: {total} baru. Manifest: {MANI}")
