#!/usr/bin/env python3
"""Search Commons for videos, return candidates with license info."""
import json, sys, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "YunobiFootage/1.0 (contact: local)"}

def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=40).read().decode())

def search(keyword, limit=50):
    d = api({"action": "query", "format": "json", "list": "search",
             "srsearch": keyword + " filetype:video", "srnamespace": 6,
             "srlimit": limit})
    return [r["title"] for r in d.get("query", {}).get("search", [])]

def imageinfo(titles):
    out = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i+40]
        d = api({"action": "query", "format": "json", "titles": "|".join(chunk),
                 "prop": "imageinfo", "iiprop": "url|extmetadata|mime|size"})
        for pid, p in d.get("query", {}).get("pages", {}).items():
            if "imageinfo" in p:
                out[p["title"]] = p["imageinfo"][0]
    return out

if __name__ == "__main__":
    kw = sys.argv[1]
    titles = search(kw)
    print("KEYWORD:", kw, "| titles:", len(titles))
    if not titles:
        sys.exit(0)
    infos = imageinfo(titles)
    for t in titles:
        ii = infos.get(t)
        if not ii:
            continue
        em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "?")
        artist = em.get("Artist", {}).get("value", "?") or "?"
        artist = artist.replace("\n", " ")[:90]
        mb = round(ii.get("size", 0)/1e6, 1) if ii.get("size") else "?"
        print("---")
        print("title:", t)
        print("mime:", ii.get("mime"), "| size:", mb, "MB |", ii.get("width"), "x", ii.get("height"))
        print("license:", lic)
        print("artist:", artist)
        print("url:", (ii.get("url") or "")[:110])
