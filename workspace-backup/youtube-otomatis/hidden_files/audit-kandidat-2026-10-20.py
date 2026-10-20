#!/usr/bin/env python3
"""Audit harian 2026-10-20: kumpulkan 5 video BERIKUTNYA per channel (lewati yang sudah dicek).
Output: hidden_files/audit-kandidat-2026-10-20.json
"""
import json, sys, time
from pathlib import Path
import yaml

BASE = Path.home() / "workspace/youtube-otomatis/yt-growth"
sys.path.insert(0, str(BASE))
import auth

HF = Path.home() / "workspace/youtube-otomatis/hidden_files"
channels = yaml.safe_load(open(BASE / "channels.yaml"))["channels"]

inv = json.load(open(HF / "audit-inventory-2026-10-19.json"))
checked = {}
for slug, v in inv["channels"].items():
    checked[slug] = {x["videoId"] for x in v.get("videos", [])}

out = {"date": "2026-10-20", "channels": {}}
for slug, c in channels.items():
    cid = c["channel_id"]
    upl = "UU" + cid[2:]
    try:
        items = []
        token = None
        while len(items) < 50:
            p = {"part": "snippet", "playlistId": upl, "maxResults": 50}
            if token: p["pageToken"] = token
            r = auth.yt_get(slug, "/playlistItems", p)
            items += r.get("items", [])
            token = r.get("nextPageToken")
            if not token: break
        new = [it for it in items if it["snippet"]["resourceId"]["videoId"] not in checked.get(slug, set())][:5]
        ids = [it["snippet"]["resourceId"]["videoId"] for it in new]
        details = []
        if ids:
            vr = auth.yt_get(slug, "/videos", {"part": "snippet,contentDetails,statistics,status", "id": ",".join(ids)})
            import re
            def dur(iso):
                m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
                if not m: return 0
                h, mi, s = (int(x) if x else 0 for x in m.groups())
                return h*3600 + mi*60 + s
            for v in vr.get("items", []):
                details.append({
                    "videoId": v["id"],
                    "title": v["snippet"]["title"],
                    "publishedAt": v["snippet"]["publishedAt"],
                    "duration_s": dur(v.get("contentDetails", {}).get("duration")),
                    "views": int(v.get("statistics", {}).get("viewCount", 0)),
                    "comments": int(v.get("statistics", {}).get("commentCount", 0)),
                    "privacy": v.get("status", {}).get("privacyStatus"),
                    "uploadStatus": v.get("status", {}).get("uploadStatus"),
                    "thumbnail": f"https://i.ytimg.com/vi/{v['id']}/mqdefault.jpg",
                })
        # cek judul duplikat dalam 50 terbaru
        seen = {}
        dupes = []
        for it in items:
            t = it["snippet"]["title"].strip().lower()
            vid = it["snippet"]["resourceId"]["videoId"]
            if t in seen and vid != seen[t]:
                dupes.append({"title": it["snippet"]["title"], "videoId": vid, "lainnya": seen[t]})
            else:
                seen.setdefault(t, vid)
        out["channels"][slug] = {"kandidat": details, "duplikat_dalam_50": dupes[:10]}
        print(f"{slug}: {len(details)} kandidat, {len(items)} item dipindai")
    except Exception as e:
        out["channels"][slug] = {"error": str(e)}
        print(f"{slug}: ERROR {e}")
    time.sleep(0.3)

json.dump(out, open(HF / "audit-kandidat-2026-10-20.json", "w"), ensure_ascii=False, indent=1)
print("OK ->", HF / "audit-kandidat-2026-10-20.json")
