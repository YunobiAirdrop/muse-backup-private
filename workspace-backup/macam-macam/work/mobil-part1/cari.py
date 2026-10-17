#!/usr/bin/env python3
"""Cari kandidat foto di Wikimedia Commons per query. Output JSON: judul, thumb, lisensi, artis."""
import json, sys, urllib.request, urllib.parse

QUERY = sys.argv[1]
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 12
params = {
    "action": "query", "format": "json",
    "generator": "search", "gsrsearch": QUERY, "gsrlimit": LIMIT, "gsrnamespace": 6,
    "prop": "imageinfo", "iiprop": "url|extmetadata",
    "iiurlwidth": 1280,
    "iiextmetadatafilter": "ImageDescription|LicenseShortName|Artist|Credit|UsageTerms",
}
url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
req = urllib.request.Request(url, headers={"User-Agent": "macam-macam-cron/1.0"})
d = json.load(urllib.request.urlopen(req, timeout=30))
out = []
for p in (d.get("query") or {}).get("pages", {}).values():
    ii = (p.get("imageinfo") or [{}])[0]
    em = ii.get("extmetadata", {})
    lic = em.get("LicenseShortName", {}).get("value", "")
    art = em.get("Artist", {}).get("value", "") or em.get("Credit", {}).get("value", "")
    out.append({
        "title": p["title"].replace("File:", ""),
        "thumb": ii.get("thumburl") or ii.get("url"),
        "orig": ii.get("url"),
        "license": lic,
        "artist": art[:120],
        "width": ii.get("thumbwidth"),
    })
print(json.dumps({"query": QUERY, "results": out}, indent=1, ensure_ascii=False))
