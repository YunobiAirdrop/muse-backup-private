#!/usr/bin/env python3
"""Bandingkan views eksperimen share-7x (video stagnan) vs baseline 2026-10-13.

Eksperimen: 2026-10-13, 95 video yang TIDAK bergerak setelah share-3x
diberi +4x salin link lagi (total 7x per video) atas aturan user.
Baseline views0 dari hidden_files/share3x-master-2026-10-13.json
(list 95 URL: hidden_files/share3x-nochange-urls.json).

Jalan: ./venv/bin/python banding_share7x.py   (dari folder yt-growth/)
Output: hidden_files/banding-share7x-<YYYY-MM-DD>.json + ringkasan stdout.
"""
import json
import re
from datetime import date
from pathlib import Path

from auth import yt_get

ROOT = Path(__file__).parent
MASTER = ROOT / "hidden_files" / "share3x-master-2026-10-13.json"
STAGNAN = ROOT / "hidden_files" / "share3x-nochange-urls.json"
READER = "lima-misteri"  # baca data publik semua channel


def vid_id(url):
    m = re.search(r"(?:shorts/|youtu\.be/|v=)([\w-]{11})", url or "")
    return m.group(1) if m else None


def main():
    master = {vid_id(v.get("url")): v for v in json.loads(MASTER.read_text())}
    urls = json.loads(STAGNAN.read_text())
    ids = [vid_id(u) for u in urls if vid_id(u)]
    print(f"95 video stagnan -> {len(ids)} id valid, "
          f"{sum(1 for i in ids if i in master)} punya baseline views0")
    stats = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i + 50]
        r = yt_get(READER, "/videos",
                   {"id": ",".join(batch), "part": "statistics,status"})
        for it in r.get("items", []):
            stats[it["id"]] = {
                "views": int(it["statistics"].get("viewCount", 0)),
                "privacy": it["status"].get("privacyStatus"),
            }
    hasil = []
    for vid in ids:
        v0 = int(master.get(vid, {}).get("views0", 0) or 0)
        s = stats.get(vid, {})
        v1 = s.get("views")
        hasil.append({
            "url": f"https://youtu.be/{vid}",
            "channel": master.get(vid, {}).get("channel"),
            "title": master.get(vid, {}).get("title"),
            "views0": v0,
            "views1": v1,
            "delta": (v1 - v0) if v1 is not None else None,
            "privacy": s.get("privacy"),
        })
    terukur = [h for h in hasil if h["delta"] is not None]
    naik = [h for h in terukur if h["delta"] > 0]
    tetap = [h for h in terukur if h["delta"] == 0]
    turun = [h for h in terukur if h["delta"] < 0]
    print(f"terukur: {len(terukur)}/{len(ids)} | naik: {len(naik)} | "
          f"tetap: {len(tetap)} | turun: {len(turun)}")
    print(f"total delta views: {sum(h['delta'] for h in terukur)}")
    out_path = (ROOT / "hidden_files" /
                f"banding-share7x-{date.today().isoformat()}.json")
    out_path.write_text(json.dumps(hasil, ensure_ascii=False, indent=1))
    print(f"disimpan: {out_path}")


if __name__ == "__main__":
    main()
