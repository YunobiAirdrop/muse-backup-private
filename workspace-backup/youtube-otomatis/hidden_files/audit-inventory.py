#!/usr/bin/env python3
"""Inventaris 5 video terbaru per channel untuk audit harian.
Output: audit-inventory-YYYY-MM-DD.json
"""
import json, sys, os, re, datetime
sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
import auth

BASE = os.path.expanduser("~/workspace/youtube-otomatis/yt-growth")
with open(f"{BASE}/channels.yaml") as f:
    import yaml
    channels = yaml.safe_load(f)["channels"]

def parse_dur(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", iso or "")
    if not m: return 0
    h, mn, s = m.groups()
    return int(h or 0)*3600 + int(mn or 0)*60 + float(s or 0)

out = {"date": datetime.date.today().isoformat(), "channels": {}}
for slug, ch in channels.items():
    cid = ch["channel_id"]
    try:
        c = auth.yt_get(slug, "/channels", {"part": "contentDetails", "id": cid})
        upl = c["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = auth.yt_get(slug, "/playlistItems",
                         {"part": "snippet,contentDetails", "playlistId": upl, "maxResults": 5})
        vids = [it["contentDetails"]["videoId"] for it in pl.get("items", [])]
        if not vids:
            out["channels"][slug] = {"videos": [], "note": "no videos"}
            continue
        vs = auth.yt_get(slug, "/videos",
                         {"part": "snippet,contentDetails,statistics,status", "id": ",".join(vids)})
        info = {v["id"]: v for v in vs.get("items", [])}
        arr = []
        for it in pl["items"]:
            vid = it["contentDetails"]["videoId"]
            v = info.get(vid)
            if not v:  # video hilang/private tak terjangkau
                arr.append({"videoId": vid, "missing": True,
                            "publishedAt": it["contentDetails"].get("videoPublishedAt")})
                continue
            sn, cd, st = v["snippet"], v["contentDetails"], v.get("statistics", {})
            arr.append({
                "videoId": vid,
                "title": sn.get("title", ""),
                "publishedAt": sn.get("publishedAt", ""),
                "duration_s": parse_dur(cd.get("duration")),
                "views": int(st.get("viewCount", 0)),
                "comments": int(st.get("commentCount", 0)),
                "privacy": v.get("status", {}).get("privacyStatus"),
                "thumbnail": (sn.get("thumbnails", {}).get("medium") or {}).get("url", ""),
            })
        out["channels"][slug] = {"videos": arr}
        print(f"{slug}: {len(arr)} video", flush=True)
    except Exception as e:
        out["channels"][slug] = {"videos": [], "error": str(e)[:200]}
        print(f"{slug}: ERROR {str(e)[:150]}", flush=True)

p = os.path.expanduser(f"~/workspace/youtube-otomatis/hidden_files/audit-inventory-{out['date']}.json")
with open(p, "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK ->", p)
