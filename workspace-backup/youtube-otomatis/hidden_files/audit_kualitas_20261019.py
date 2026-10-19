#!/usr/bin/env python3
"""Audit kualitas video 20 channel: 10 video terbaru/channel, tandai views=0 & umur>7 hari.
READ-ONLY — tidak hapus/private/upload apapun."""
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace" / "youtube-otomatis" / "yt-growth"))
import yaml
from auth import yt_get

BASE = Path.home() / "workspace" / "youtube-otomatis"
CH = yaml.safe_load(open(BASE / "yt-growth" / "channels.yaml"))["channels"]
NOW = datetime.now(timezone.utc)
OUT = {}

def get_uploads_playlist(slug):
    data = yt_get(slug, "/channels", {"part": "contentDetails", "mine": "true"})
    items = data.get("items", [])
    if not items:
        return None
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

def main():
    for slug, info in CH.items():
        cid = info["channel_id"]
        rec = {"channel_id": cid, "total_video_cek": 0, "video_bermasalah": [], "error": None}
        try:
            upl = get_uploads_playlist(slug)
            if not upl:
                rec["error"] = "channels.list kosong"
                OUT[slug] = rec
                continue
            # ambil 10 terbaru dari uploads playlist
            vids, page = [], None
            while len(vids) < 10:
                p = {"part": "contentDetails", "playlistId": upl, "maxResults": 50}
                if page:
                    p["pageToken"] = page
                d = yt_get(slug, "/playlistItems", p)
                for it in d.get("items", []):
                    cd = it["contentDetails"]
                    vids.append({"videoId": cd["videoId"], "publishedAt": cd["videoPublishedAt"]})
                    if len(vids) >= 10:
                        break
                page = d.get("nextPageToken")
                if not page:
                    break
            rec["total_video_cek"] = len(vids)
            if vids:
                # statistik batch (maks 50 per call)
                for i in range(0, len(vids), 50):
                    batch = vids[i:i+50]
                    ids = ",".join(v["videoId"] for v in batch)
                    sd = yt_get(slug, "/videos", {"part": "snippet,statistics", "id": ids})
                    for item in sd.get("items", []):
                        vid = item["id"]
                        title = item["snippet"]["title"]
                        views = int(item["statistics"].get("viewCount", 0))
                        pub = next(v["publishedAt"] for v in batch if v["videoId"] == vid)
                        pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                        umur = (NOW - pub_dt).days
                        if views == 0 and umur > 7:
                            rec["video_bermasalah"].append({
                                "videoId": vid, "judul": title,
                                "views": views, "umur_hari": umur,
                                "tanggal_upload": pub[:10],
                            })
            time.sleep(1)  # jaga rate limit
        except Exception as e:
            rec["error"] = str(e)[:200]
        OUT[slug] = rec
        n_bad = len(rec["video_bermasalah"])
        print(f"{slug}: {rec['total_video_cek']} video dicek, {n_bad} bermasalah" + (f" ERR={rec['error']}" if rec["error"] else ""), flush=True)

    total_bad = sum(len(r["video_bermasalah"]) for r in OUT.values())
    terparah = max(OUT.items(), key=lambda kv: len(kv[1]["video_bermasalah"]), default=(None, {"video_bermasalah": []}))
    hasil = {
        "tanggal_audit": "2026-10-19",
        "channels": OUT,
        "ringkasan": {
            "total_bermasalah": total_bad,
            "channel_terparah": terparah[0] if terparah[0] else None,
            "channel_terparah_jumlah": len(terparah[1]["video_bermasalah"]),
        },
    }
    out_path = BASE / "hidden_files" / "audit-kualitas-2026-10-19.json"
    out_path.write_text(json.dumps(hasil, ensure_ascii=False, indent=2))
    print(f"\nOK -> {out_path}")
    print(f"Ringkasan: {total_bad} video bermasalah, terparah: {terparah[0]} ({len(terparah[1]['video_bermasalah'])})")

if __name__ == "__main__":
    main()
