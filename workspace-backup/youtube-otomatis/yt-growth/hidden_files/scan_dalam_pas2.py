#!/usr/bin/env python3
"""Scan DALAM pas 2 (2026-10-12 malam): sampai 50 upload terbaru per channel
(playlistItems + pageToken). Kandidat mentok = publik, umur >48 jam,
shorts <300 views / long <200 views, di luar daftar pas pertama.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from auth import yt_get  # noqa: E402
from analytics import load_channels  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "sepi-pas2-scan-2026-10-12.json"
PLAN1 = HERE / "perbaikan-sepi-plan.json"
READER = "lima-misteri"
NO_TOKEN = {"inktime", "macammacam"}
EXTRA_EXCLUDE = {"5ijR6apbCps", "E4OjHTPQbeU", "5hHQlZvoYqk", "zafVpCmFduk",
                 "bGBGROVZfZY", "jhDzosY_vj8", "7mkgmONd89o"}


def parse_dur(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def resolve_cid(reader, slug, info):
    cid = info.get("channel_id")
    if cid:
        return cid
    r = yt_get(reader, "/channels", {"forHandle": info["handle"], "part": "id"})
    items = r.get("items", [])
    return items[0]["id"] if items else None


def scan(slug, info):
    reader = READER if slug in NO_TOKEN else slug
    cid = resolve_cid(reader, slug, info)
    if not cid:
        return {"slug": slug, "error": "channel tidak ditemukan"}
    ch = yt_get(reader, "/channels", {"id": cid, "part": "contentDetails"})
    items0 = ch.get("items", [])
    if not items0:
        return {"slug": slug, "error": "contentDetails kosong"}
    uploads = items0[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while len(ids) < 50:
        params = {"playlistId": uploads, "part": "contentDetails", "maxResults": 50}
        if token:
            params["pageToken"] = token
        pl = yt_get(reader, "/playlistItems", params)
        ids += [it["contentDetails"]["videoId"] for it in pl.get("items", [])]
        token = pl.get("nextPageToken")
        if not token:
            break
    ids = ids[:50]
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
            vids.append({
                "id": it["id"], "title": sn["title"],
                "format": "shorts" if dur <= 61 else "long",
                "durasi_detik": dur, "privacy": st["privacyStatus"],
                "umur_jam": round(age_h, 1),
                "views": int(it["statistics"].get("viewCount", 0)),
                "likes": int(it["statistics"].get("likeCount", 0)),
                "comments": int(it["statistics"].get("commentCount", 0)),
            })
    return {"slug": slug, "handle": info["handle"], "channel_id": cid, "videos": vids}


def main():
    plan1 = json.loads(PLAN1.read_text())
    fixed1 = {p["id"] for plist in plan1.values() for p in plist}
    chans = load_channels()
    result, summary = {}, []
    tot_scan = tot_cand = 0
    for slug, info in chans.items():
        try:
            r = scan(slug, info)
        except Exception as e:
            r = {"slug": slug, "error": str(e)[:200]}
        result[slug] = r
        if "error" in r:
            summary.append(f"{slug}: ERROR {r['error']}")
            continue
        cands = []
        for v in r["videos"]:
            if v["privacy"] != "public" or v["umur_jam"] <= 48:
                continue
            if v["id"] in fixed1 or v["id"] in EXTRA_EXCLUDE:
                continue
            if (v["format"] == "shorts" and v["views"] < 300) or \
               (v["format"] == "long" and v["views"] < 200):
                cands.append(v)
        for c in cands:
            c["kandidat"] = True
        tot_scan += len(r["videos"])
        tot_cand += len(cands)
        summary.append(f"{r['handle']} ({slug}): discan {len(r['videos'])}, kandidat baru {len(cands)}")
        for c in cands:
            summary.append(f"  KAND [{c['format']}] {c['views']} views / {c['umur_jam']}j — {c['id']} — {c['title'][:80]}")
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print("\n".join(summary))
    print(f"\nTOTAL discan: {tot_scan} | kandidat mentok BARU: {tot_cand}")
    print("Scan ->", OUT)


if __name__ == "__main__":
    main()
