#!/usr/bin/env python3
"""Bangun cache daftar video PUBLIK per channel untuk fitur embed video blog.

Dipakai oleh embed_video.py (blog-otomatis) via subprocess memakai venv yt-growth:
    yt-growth/venv/bin/python video_cache_builder.py <slug> [<slug> ...]

Output: ~/workspace/blog-otomatis/data/video_cache/<slug>.json
Isi: 50 upload terbaru yang statusnya public (judul, deskripsi singkat, views,
tanggal tayang, format shorts/long). Video terjadwal/private TIDAK masuk.

File BARU untuk fitur embed-video (2026-10-14). Tidak dipakai pipeline lain.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from auth import yt_get
from analytics import load_channels

READER_FALLBACK = "lima-misteri"  # channel tanpa token sendiri (inktime, macammacam)
OUT_DIR = Path("/home/hatch/workspace/blog-otomatis/data/video_cache")
MAX_VIDEOS = 50


def parse_dur(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def build(slug):
    chans = load_channels()
    info = chans.get(slug)
    if not info:
        return {"slug": slug, "error": f"slug {slug} tidak ada di channels.yaml"}
    # reader: token sendiri bila ada, fallback lima-misteri (data publik)
    try:
        from auth import get_credentials
        get_credentials(slug)
        reader = slug
    except SystemExit:
        reader = READER_FALLBACK
    except Exception:
        reader = READER_FALLBACK

    cid = info.get("channel_id")
    if not cid:
        r = yt_get(reader, "/channels", {"forHandle": info["handle"], "part": "id"})
        items = r.get("items", [])
        if not items:
            return {"slug": slug, "error": "channel tidak ditemukan"}
        cid = items[0]["id"]
    ch = yt_get(reader, "/channels", {"id": cid, "part": "contentDetails"})
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = yt_get(reader, "/playlistItems",
                {"playlistId": uploads, "part": "contentDetails",
                 "maxResults": MAX_VIDEOS})
    ids = [it["contentDetails"]["videoId"] for it in pl.get("items", [])]
    vids = []
    for i in range(0, len(ids), 50):
        det = yt_get(reader, "/videos", {
            "id": ",".join(ids[i:i + 50]),
            "part": "snippet,status,statistics,contentDetails"})
        for it in det.get("items", []):
            if it["status"].get("privacyStatus") != "public":
                continue  # hanya video publik yang boleh di-embed
            sn = it["snippet"]
            dur = parse_dur(it["contentDetails"].get("duration"))
            vids.append({
                "id": it["id"],
                "title": sn.get("title", ""),
                "desc": (sn.get("description", "") or "")[:600],
                "views": int(it["statistics"].get("viewCount", 0)),
                "published": sn.get("publishedAt", ""),
                "format": "shorts" if dur <= 61 else "long",
            })
    out = {
        "slug": slug,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "videos": vids,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"{slug}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    return {"slug": slug, "videos": len(vids), "file": str(p)}


def main():
    slugs = sys.argv[1:]
    if not slugs:
        print("Pakai: video_cache_builder.py <slug> [<slug> ...]")
        sys.exit(1)
    for s in slugs:
        try:
            print(json.dumps(build(s), ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"slug": s, "error": str(e)[:200]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
