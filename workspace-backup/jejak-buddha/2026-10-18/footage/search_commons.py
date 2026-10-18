#!/usr/bin/env python3
import json, sys, urllib.parse, urllib.request

kw = sys.argv[1]
q = urllib.parse.quote(kw)
url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json"
       "&generator=search&gsrsearch=%s&gsrnamespace=6&gsrlimit=50"
       "&prop=imageinfo&iiprop=url|extmetadata|mime|size" % q)
req = urllib.request.Request(url, headers={"User-Agent": "YunobiFootage/1.0"})
d = json.loads(urllib.request.urlopen(req, timeout=40).read().decode())
pages = d.get('query', {}).get('pages', {})
vids = []
for pid, p in pages.items():
    ii = p.get('imageinfo', [{}])[0]
    mime = ii.get('mime', '')
    if 'video' in mime:
        em = ii.get('extmetadata', {})
        lic = em.get('LicenseShortName', {}).get('value', '?')
        artist = em.get('Artist', {}).get('value', '?')[:120]
        vids.append({
            'title': p['title'],
            'url': ii.get('url'),
            'mime': mime,
            'size': ii.get('size'),
            'w': ii.get('width'), 'h': ii.get('height'),
            'lic': lic, 'artist': artist,
        })
print("KEYWORD:", kw, "| videos found:", len(vids))
for v in vids:
    mb = round(v['size']/1e6, 1) if v['size'] else '?'
    print("---")
    print("title:", v['title'])
    print("mime:", v['mime'], "| size:", mb, "MB |", v['w'], "x", v['h'])
    print("license:", v['lic'])
    print("artist:", v['artist'][:80])
    print("url:", v['url'][:100] if v['url'] else None)
