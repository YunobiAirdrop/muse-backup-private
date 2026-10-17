#!/usr/bin/env python3
"""Download video clips from Wikimedia Commons with per-file license tracking.
Only accepts: CC0 / Public domain / CC BY / CC BY-SA. Rejects NC/ND.
Usage: python3 commons_dl.py "keyword1" "keyword2" ... -> writes clips/*.mp4 + kredit-baru.json
"""
import json, os, sys, time, urllib.request, urllib.parse

API = "https://commons.wikimedia.org/w/api.php"
W = "/home/hatch/workspace/kisah-islami/work/2026-10-17"
OUT = os.path.join(W, "clips")
os.makedirs(OUT, exist_ok=True)
KREDIT_PATH = os.path.join(W, "kredit-baru.json")

def api(params):
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "JejakIslamiBot/1.0 (content pipeline; contact: none)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def lic_ok(short, usage):
    s = (short or "") + " " + (usage or "")
    sl = s.lower()
    if any(x in sl for x in ["nc", "nd", "noncommercial", "no derivatives", "copyrighted", "all rights reserved", "fair use"]):
        return None
    if "cc0" in sl or "public domain" in sl or "pd-" in sl:
        return "PD/CC0"
    if "by-sa" in sl:
        return "CC BY-SA"
    if sl.strip().startswith("cc by") or " cc by " in sl or sl.strip() == "by":
        return "CC BY"
    return None

def search(keyword, limit=15):
    params = {
        "action": "query", "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:video {keyword}",
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size",
    }
    data = api(params)
    pages = data.get("query", {}).get("pages", {})
    out = []
    for pid, p in pages.items():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        lic = lic_ok(em.get("LicenseShortName", {}).get("value", ""),
                     em.get("UsageTerms", {}).get("value", ""))
        if not lic:
            continue
        w = ii.get("width") or 0
        h = ii.get("height") or 0
        if w < 640 or h < 360:
            continue
        out.append({
            "title": p.get("title", "").replace("File:", ""),
            "url": ii.get("url"),
            "license": lic,
            "artist": (em.get("Artist", {}).get("value", "") or "")[:120],
            "page": ii.get("descriptionurl"),
            "w": w, "h": h, "size": ii.get("size", 0),
            "duration": ii.get("duration"),
        })
    return out

def download(url, dest, max_mb=220):
    req = urllib.request.Request(url, headers={"User-Agent": "JejakIslamiBot/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        total = 0
        while True:
            chunk = r.read(1024 * 256)
            if not chunk:
                break
            total += len(chunk)
            if total > max_mb * 1024 * 1024:
                raise RuntimeError("too big, aborting")
            f.write(chunk)
    return dest

def main():
    kredit = {}
    if os.path.exists(KREDIT_PATH):
        kredit = json.load(open(KREDIT_PATH))
    n = len([k for k in kredit])
    for kw in sys.argv[1:]:
        print(f"== search: {kw} ==", flush=True)
        try:
            res = search(kw)
        except Exception as e:
            print("search error:", e); continue
        print(f"  found {len(res)} license-ok candidates", flush=True)
        taken = 0
        for c in res:
            if taken >= 2:
                break
            if any(c["title"] == v.get("title") for v in kredit.values()):
                continue
            ext = os.path.splitext(urllib.parse.urlparse(c["url"]).path)[1] or ".mp4"
            tag = f"c{n+1:02d}"
            dest = os.path.join(OUT, tag + ext)
            print(f"  dl {c['title'][:60]} ({c['w']}x{c['h']}, {c['license']})", flush=True)
            try:
                download(c["url"], dest)
            except Exception as e:
                print("  download error:", e)
                if os.path.exists(dest): os.remove(dest)
                continue
            kredit[tag] = {
                "title": c["title"], "license": c["license"],
                "artist": c["artist"], "page": c["page"],
                "w": c["w"], "h": c["h"],
                "keyword": kw, "file": os.path.basename(dest),
            }
            n += 1; taken += 1
            print(f"  OK {tag}", flush=True)
            time.sleep(1)
    json.dump(kredit, open(KREDIT_PATH, "w"), indent=2, ensure_ascii=False)
    print(f"kredit written: {KREDIT_PATH} ({len(kredit)} clips)")

if __name__ == "__main__":
    main()
