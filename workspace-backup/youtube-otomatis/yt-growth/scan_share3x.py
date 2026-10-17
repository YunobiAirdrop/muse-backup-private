#!/usr/bin/env python3
"""share3x scan: video PUBLIC yang dipublikasikan dalam 24 jam terakhir, 17 channel bertoken.
Menggabung share3x-pending-*.json dari goal hidden_files (video gagal share di run sebelumnya).
Output: JSON {videos: [{videoId, channel, title, publishedAt, url}], skipped_shared: N}"""
import json, sys, os, glob
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yaml
from auth import yt_get

BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, "hidden_files", "share3x-log.json")
GOAL_HF = os.path.join(os.path.expanduser("~"), "workspace", "goals",
                       "toolkit-pertumbuhan-youtube-yt-growth", "hidden_files")

def load_shared():
    if os.path.exists(LOG):
        d = json.load(open(LOG))
        return set(d.get("upload_shared", []))
    return set()

def load_pending():
    """Video dari run sebelumnya yang gagal di-share (browser mati, dsb)."""
    pend = []
    for p in sorted(glob.glob(os.path.join(GOAL_HF, "share3x-pending-*.json"))):
        try:
            for v in json.load(open(p)).get("videos", []):
                v["_pending_file"] = p
                pend.append(v)
        except Exception as e:
            print(f"pending {p}: gagal baca: {e}", file=sys.stderr)
    return pend

def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    with open(os.path.join(BASE, "channels.yaml")) as f:
        channels = yaml.safe_load(f)["channels"]
    shared = load_shared()
    out, skipped = [], 0
    for slug in sorted(channels):
        tokdir = os.path.join(os.path.expanduser("~"), ".hermes", "yt-growth", "tokens")
        if not os.path.exists(os.path.join(tokdir, f"{slug}.json")):
            print(f"{slug}: tanpa token, skip", file=sys.stderr)
            continue
        try:
            ch = yt_get(slug, "/channels", {"part": "contentDetails", "mine": "true"})
            items = ch.get("items", [])
            if not items:
                print(f"{slug}: no channel via token, skip", file=sys.stderr)
                continue
            pid = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except Exception as e:
            print(f"{slug}: channels.list gagal: {e}", file=sys.stderr)
            continue
        vids, pt = [], None
        try:
            while True:
                p = {"part": "snippet,contentDetails", "playlistId": pid,
                     "maxResults": 50, "pageToken": pt or ""}
                r = yt_get(slug, "/playlistItems", p)
                for it in r.get("items", []):
                    pub = it["snippet"]["publishedAt"]
                    if datetime.fromisoformat(pub.replace("Z", "+00:00")) < cutoff:
                        pt = None
                        break
                    vids.append({"videoId": it["contentDetails"]["videoId"],
                                 "title": it["snippet"]["title"],
                                 "publishedAt": pub, "channel": slug})
                else:
                    pt = r.get("nextPageToken")
                    if not pt:
                        break
                    continue
                break
        except Exception as e:
            print(f"{slug}: playlistItems gagal: {e}", file=sys.stderr)
            continue
        for i in range(0, len(vids), 50):
            ids = ",".join(v["videoId"] for v in vids[i:i+50])
            try:
                vr = yt_get(slug, "/videos", {"part": "status", "id": ids})
                pubmap = {v["id"]: v["status"]["privacyStatus"] for v in vr.get("items", [])}
            except Exception as e:
                print(f"{slug}: videos.list gagal: {e}", file=sys.stderr)
                pubmap = {}
            for v in vids[i:i+50]:
                vid = v["videoId"]
                if vid in shared:
                    skipped += 1
                    continue
                if pubmap.get(vid) != "public":
                    continue
                v["url"] = f"https://www.youtube.com/watch?v={vid}"
                out.append(v)
        print(f"{slug}: {len(vids)} kandidat 24h", file=sys.stderr)
    seen = {v["videoId"] for v in out} | shared
    npend = 0
    for v in load_pending():
        if v["videoId"] in seen:
            continue
        v.setdefault("url", f"https://www.youtube.com/watch?v={v['videoId']}")
        out.append(v)
        seen.add(v["videoId"])
        npend += 1
    print(f"pending digabung: {npend}", file=sys.stderr)
    print(json.dumps({"videos": out, "skipped_shared": skipped}, ensure_ascii=False))
    print(f"TOTAL BARU: {len(out)}, skipped_sudah_share: {skipped}", file=sys.stderr)

if __name__ == "__main__":
    main()
