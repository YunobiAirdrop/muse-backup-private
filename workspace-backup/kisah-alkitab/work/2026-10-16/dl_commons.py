#!/usr/bin/env python3
"""Download klip Commons utk video Nuh & bahtera -> work/2026-10-16/klip. Lisensi aman saja."""
import json, os, subprocess, sys, time, urllib.parse, urllib.request

OUT = os.path.expanduser("~/workspace/kisah-alkitab/work/2026-10-16/klip")
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

KEYWORDS = ["noah ark", "great flood", "ocean storm waves", "rain storm dark clouds",
            "rainbow sky", "dove flying", "olive tree", "sunrise desert",
            "wooden ship sea", "candle light dark"]

MAX_NEW = 16
DEADLINE = time.time() + 60 * 60  # 60 menit total
seen_urls = {v["url"] for v in have.values()}
n_new = 0
idx = 0
for kw in KEYWORDS:
    if n_new >= MAX_NEW or time.time() > DEADLINE:
        break
    try:
        cands = search(kw)
    except Exception as e:
        print(f"SEARCH GAGAL {kw}: {e}", flush=True); continue
    got = 0
    for c in cands:
        if n_new >= MAX_NEW or time.time() > DEADLINE:
            break
        if c["url"] in seen_urls:
            continue
        if c["size"] and c["size"] > 120 * 1024 * 1024:
            continue
        if c["size"] and c["size"] < 800 * 1024:
            continue
        idx += 1
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
            print(f"  percobaan {attempt} gagal, ulangi", flush=True)
        if ok_dl:
            c["asal"] = f"commons search '{kw}'"
            have[fn] = c; seen_urls.add(c["url"]); n_new += 1; got += 1
            json.dump(have, open(MANI, "w"), ensure_ascii=False, indent=1)
            print(f"  OK {fn} ({got} utk kw ini)", flush=True)
        else:
            print(f"  GAGAL {fn} (2x)", flush=True)
            if os.path.exists(dst): os.remove(dst)
    print(f"kw '{kw}': {got} klip", flush=True)
print(f"SELESAI: {n_new} baru (+ reuse di manifest). Manifest: {MANI}")
