#!/usr/bin/env python3
"""Scan video sepi semua channel — Data API v3 (publik + milik sendiri).

Untuk tiap channel di channels.yaml: ambil 20 upload terbaru, catat status
(publik / terjadwal / private), durasi (shorts vs long), umur, views.
Video publik yang sudah tayang >24 jam tapi views sangat rendah ditandai SEPI.

Channel tanpa token sendiri (inkt​ime, macammacam) dibaca dengan token
lima-misteri (data publik tetap terbaca).

Output: JSON lengkap + ringkasan teks per channel.
"""
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from auth import yt_get
from analytics import load_channels, resolve_channel_id

READER = "lima-misteri"
NO_TOKEN = {"inktime", "macammacam"}
OUT = Path(__file__).parent / "hidden_files" / f"sepi-{date.today().isoformat()}.json"


def parse_dur(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def scan(slug, info):
    reader = READER if slug in NO_TOKEN else slug
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
                {"playlistId": uploads, "part": "contentDetails", "maxResults": 20})
    ids = [it["contentDetails"]["videoId"] for it in pl.get("items", [])]
    vids = []
    now = datetime.now(timezone.utc)
    for i in range(0, len(ids), 50):
        det = yt_get(reader, "/videos", {
            "id": ",".join(ids[i:i + 50]),
            "part": "snippet,status,statistics,contentDetails"})
        for it in det.get("items", []):
            sn, st = it["snippet"], it["status"]
            dur = parse_dur(it["contentDetails"]["duration"])
            pub = datetime.fromisoformat(sn["publishedAt"].replace("Z", "+00:00"))
            age_h = (now - pub).total_seconds() / 3600
            views = int(it["statistics"].get("viewCount", 0))
            fmt = "shorts" if dur <= 61 else "long"
            vids.append({
                "id": it["id"], "title": sn["title"], "format": fmt,
                "durasi_detik": dur, "privacy": st["privacyStatus"],
                "publish_at": st.get("publishAt"),
                "made_for_kids": st.get("madeForKids"),
                "umur_jam": round(age_h, 1), "views": views,
                "likes": int(it["statistics"].get("likeCount", 0)),
                "comments": int(it["statistics"].get("commentCount", 0)),
            })
    return {"slug": slug, "handle": info["handle"], "channel_id": cid, "videos": vids}


def main():
    chans = load_channels()
    result = {}
    for slug, info in chans.items():
        try:
            result[slug] = scan(slug, info)
        except Exception as e:
            result[slug] = {"slug": slug, "error": str(e)[:200]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(f"Tersimpan: {OUT}\n")
    tot_pub = tot_sepi = 0
    for slug, r in result.items():
        if "error" in r:
            print(f"{slug}: ERROR {r['error']}")
            continue
        pub = [v for v in r["videos"] if v["privacy"] == "public"]
        sched = [v for v in r["videos"] if v["privacy"] != "public"]
        sepi = [v for v in pub if v["umur_jam"] > 24 and
                ((v["format"] == "shorts" and v["views"] < 50) or
                 (v["format"] == "long" and v["views"] < 100))]
        tot_pub += len(pub)
        tot_sepi += len(sepi)
        print(f"{r['handle']}: {len(pub)} publik, {len(sched)} belum tayang, {len(sepi)} SEPI")
        for v in sepi:
            print(f"  SEPI [{v['format']}] {v['views']} views / {v['umur_jam']}j — {v['id']} — {v['title'][:80]}")
    print(f"\nTOTAL: {tot_pub} video publik, {tot_sepi} sepi")


if __name__ == "__main__":
    main()
