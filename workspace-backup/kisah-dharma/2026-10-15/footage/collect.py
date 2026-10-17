#!/usr/bin/env python3
"""Kandidat klip LAUT/SAMUDRA + LANGIT/AWAN dari Wikimedia Commons API (Kisah Dharma 2026-10-15)."""
import json, urllib.request, urllib.parse, os

UA = "KisahDharmaVideo/1.0 (educational video production)"
OUT = os.path.dirname(os.path.abspath(__file__))

KEYWORDS = [
    "ocean waves aerial", "sea horizon sunset", "clouds timelapse",
    "ocean surface", "stormy sea waves", "tropical island aerial",
    "sunset ocean", "big waves rocks", "ocean waves slow motion",
    "sea waves beach", "clouds sky timelapse", "calm sea aerial",
]

def lic_ok(shortname):
    if not shortname: return False
    s = shortname.lower()
    if "nc" in s or "nd" in s: return False
    if "fair use" in s or "copyrighted" in s: return False
    for ok in ("cc0", "public domain", "cc by-sa", "cc by"):
        if s.startswith(ok): return True
    return False

def query(kw):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrnamespace": "6", "gsrlimit": "50", "prop": "imageinfo",
        "iiprop": "url|size|extmetadata",
        "gsrsearch": f"filetype:video {kw}",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

seen = {}
for kw in KEYWORDS:
    try:
        d = query(kw)
    except Exception as e:
        print("QUERY GAGAL:", kw, e); continue
    pages = d.get("query", {}).get("pages", {})
    for pid, p in pages.items():
        title = p.get("title", "")
        ii = (p.get("imageinfo") or [{}])[0]
        w, h = ii.get("width", 0), ii.get("height", 0)
        url = ii.get("url", "")
        em = ii.get("extmetadata", {})
        lic = (em.get("LicenseShortName") or {}).get("value", "")
        author = (em.get("Artist") or {}).get("value", "")
        if not url: continue
        if not lic_ok(lic): continue
        if w < 1280 or h <= 0 or w <= h: continue
        ratio = w / h
        if not (1.6 <= ratio <= 1.9): continue
        if url not in seen:
            seen[url] = {"title": title, "url": url, "w": w, "h": h,
                         "license": lic, "author": author, "kw": kw}
    print(f"{kw}: {len(pages)} hasil", flush=True)

cands = list(seen.values())
json.dump(cands, open(os.path.join(OUT, "candidates.json"), "w"), indent=1, ensure_ascii=False)
print("\nTOTAL KANDIDAT LOLOS FILTER:", len(cands))
for c in cands:
    print(f"- {c['title']} | {c['w']}x{c['h']} | {c['license']} | {c['url'][-40:]}")
