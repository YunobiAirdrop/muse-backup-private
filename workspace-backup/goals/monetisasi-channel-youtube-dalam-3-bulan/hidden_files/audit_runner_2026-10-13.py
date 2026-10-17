#!/usr/bin/env python3
"""Audit 3-harian run 2026-10-13: analytics per channel + enrichment Data API.

Output: hidden_files/audit-2026-10-13/<slug>.json per channel.
Analytics API via analytics.py (venv). Enrichment: channel stats, video details
(durasi, deskripsi, tags, views lifetime), daftar playlist + isi playlist.
"""
import json
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
GROWTH = Path.home() / "workspace" / "youtube-otomatis" / "yt-growth"
OUT = HERE / f"audit-{date.today().isoformat()}"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(GROWTH))

from auth import yt_get  # noqa: E402
from analytics import load_channels  # noqa: E402

READER = "lima-misteri"
NO_TOKEN = {"inkt​ime".replace("​", ""), "macammacam"}


def run_analytics(slug, retries=2):
    for attempt in range(retries):
        try:
            r = subprocess.run(
                [str(GROWTH / ".venv" / "bin" / "python3"),
                 str(GROWTH / "analytics.py"), slug, "--days", "28"],
                capture_output=True, text=True, timeout=150)
            if r.returncode == 0 and r.stdout.strip().startswith("{"):
                return json.loads(r.stdout)
            err = (r.stderr or r.stdout)[-500:]
        except subprocess.TimeoutExpired:
            err = "timeout 150s"
        time.sleep(5)
    return {"error": f"analytics gagal: {err}"}


def enrich(slug, info):
    reader = READER if slug in NO_TOKEN else slug
    cid = info.get("channel_id")
    if not cid:
        r = yt_get(reader, "/channels",
                   {"forHandle": info["handle"], "part": "id"})
        items = r.get("items", [])
        if not items:
            return {"error": "channel tidak ditemukan"}
        cid = items[0]["id"]
    ch = yt_get(reader, "/channels",
                {"id": cid, "part": "statistics,contentDetails"})
    stats = ch["items"][0]["statistics"] if ch.get("items") else {}
    return {"channel_id": cid, "stats": stats, "reader": reader}


def video_details(slug, reader, ids):
    det = {}
    for i in range(0, len(ids), 50):
        r = yt_get(reader, "/videos",
                   {"id": ",".join(ids[i:i + 50]),
                    "part": "snippet,contentDetails,statistics"})
        for it in r.get("items", []):
            sn, cd, st = it["snippet"], it.get("contentDetails", {}), it.get("statistics", {})
            det[it["id"]] = {
                "title": sn.get("title"), "published": sn.get("publishedAt", "")[:10],
                "description": sn.get("description", ""),
                "tags": sn.get("tags", []),
                "duration_iso": cd.get("duration", ""),
                "views_lt": int(st.get("viewCount", 0)),
                "likes_lt": int(st.get("likeCount", 0)),
                "comments_lt": int(st.get("commentCount", 0)),
            }
    return det


def parse_dur(iso):
    import re
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def playlists_with_items(slug, reader, cid):
    pls = yt_get(reader, "/playlists",
                 {"channelId": cid, "part": "snippet,contentDetails",
                  "maxResults": 25}).get("items", [])
    out, in_any = [], set()
    for p in pls:
        pid = p["id"]
        items, tok = [], None
        for _ in range(4):  # maks 200 item per playlist
            r = yt_get(reader, "/playlistItems",
                       {"playlistId": pid, "part": "contentDetails",
                        "maxResults": 50, **({"pageToken": tok} if tok else {})})
            for it in r.get("items", []):
                vid = it["contentDetails"]["videoId"]
                items.append(vid)
                in_any.add(vid)
            tok = r.get("nextPageToken")
            if not tok:
                break
        out.append({"id": pid, "title": p["snippet"]["title"],
                    "count": p["contentDetails"]["itemCount"],
                    "videos": items})
    return out, in_any


def main():
    channels = load_channels()
    summary = {}
    for n, (slug, info) in enumerate(channels.items(), 1):
        print(f"[{n}/{len(channels)}] {slug} ...", flush=True)
        data = {"slug": slug, "handle": info["handle"],
                "date": date.today().isoformat()}
        ana = run_analytics(slug)
        data["analytics"] = ana
        try:
            en = enrich(slug, info)
            data["enrich"] = en
            if "error" not in en:
                vids = ana.get("videos", []) if isinstance(ana, dict) else []
                ids = [v["video_id"] for v in vids]
                det = video_details(slug, en["reader"], ids)
                for v in vids:
                    v.update(det.get(v["video_id"], {}))
                    d = parse_dur(v.get("duration_iso", ""))
                    v["duration_sec"] = d
                    avs = v.get("avg_view_sec") or 0
                    v["retention_pct"] = round(avs / d * 100, 1) if d else None
                pls, in_any = playlists_with_items(slug, en["reader"], en["channel_id"])
                data["playlists"] = [{"id": p["id"], "title": p["title"],
                                      "count": p["count"]} for p in pls]
                data["videos_in_playlists"] = sorted(in_any)
                data["videos_no_playlist"] = [v["video_id"] for v in vids
                                              if v["video_id"] not in in_any]
        except Exception as e:  # noqa: BLE001
            data["enrich_error"] = f"{type(e).__name__}: {e}"
        (OUT / f"{slug}.json").write_text(
            json.dumps(data, indent=1, ensure_ascii=False))
        ana_ok = isinstance(ana, dict) and "error" not in ana
        summary[slug] = "ok" if ana_ok else "analytics-gagal"
        print(f"  -> {summary[slug]}", flush=True)
    (OUT / "_summary.json").write_text(json.dumps(summary, indent=1))
    print("SELESAI:", summary)


if __name__ == "__main__":
    main()
