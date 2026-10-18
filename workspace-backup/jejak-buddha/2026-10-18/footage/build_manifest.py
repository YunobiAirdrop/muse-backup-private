#!/usr/bin/env python3
"""Download candidate videos from Commons, strip utm query params."""
import json, os, sys, urllib.parse, urllib.request, subprocess

API = "https://commons.wikimedia.org/w/api.php"
OUT = "/home/hatch/workspace/jejak-buddha/2026-10-18/footage"

JOBS = [
    ("File:Sacred Serenity at Mahabodhi Temple, Bodhgaya, Bihar.webm", "bodhgaya-mahabodhi.webm"),
    ("File:Ruwanwelisseya Dagoba video 01102015.ogg", "ruwanwelisseya-dagoba.ogg"),
    ("File:Chandavaram buddha stupa 360 degree view.webm", "chandavaram-stupa.webm"),
    ("File:Buddhist Monuments - Sanchi Hill 2013-02-21 4508.ogv", "sanchi-stupa.ogv"),
    ("File:Drone footage of temple in Chiang Mai, Thailand.webm", "chiangmai-temple.webm"),
    ("File:Meditation Ritual AGE.webm", "meditation-ritual.webm"),
    ("File:Borobudur, Java, Indonesia, February 2012.ogv", "borobudur-2012.ogv"),
    ("File:Looking Over a Cliff in the Dieng Mountains.webm", "dieng-mountains.webm"),
    ("File:Ajatsatru Stupa - Rajgir 05.webm", "ajatsatru-05.webm"),
    ("File:Ajatsatru Stupa - Rajgir 03.webm", "ajatsatru-03.webm"),
    ("File:New Excavated Stupa - Rajgir 01.webm", "rajgir-stupa-01.webm"),
    ("File:Flameless candle 1.webm", "flameless-candle.webm"),
    ("File:Thimphu, Memorial Chorten, paying respect.webm", "thimphu-chorten.webm"),
    ("File:낙산사 7.webm", "naksansa-temple.webm"),
]

def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "YunobiFootage/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=40).read().decode())

def clean(u):
    return u.split("?")[0]

manifest = []
for title, local in JOBS:
    d = api({"action": "query", "format": "json", "titles": title,
             "prop": "imageinfo", "iiprop": "url|extmetadata|mime|size"})
    pages = d.get("query", {}).get("pages", {})
    got = None
    for pid, p in pages.items():
        if "imageinfo" in p:
            got = p; break
    if not got:
        print("MISS:", title); continue
    ii = got["imageinfo"][0]
    em = ii.get("extmetadata", {})
    url = clean(ii["url"])
    dest = os.path.join(OUT, local)
    manifest.append({"title": got["title"], "local": local, "url": url,
                     "license": em.get("LicenseShortName", {}).get("value", "?"),
                     "artist": (em.get("Artist", {}).get("value", "?") or "?"),
                     "size": ii.get("size"), "w": ii.get("width"), "h": ii.get("height")})

json.dump(manifest, open(os.path.join(OUT, "download_manifest.json"), "w"), indent=1)
print("manifest:", len(manifest), "files")
for m in manifest:
    print(m["local"], round((m["size"] or 0)/1e6, 1), "MB")
