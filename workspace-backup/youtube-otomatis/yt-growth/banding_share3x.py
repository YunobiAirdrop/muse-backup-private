#!/usr/bin/env python3
"""Bandingkan views eksperimen share-3x vs baseline 2026-10-13.

Eksperimen: user minta salin link (share-copy) 3x untuk tiap video di semua
channel (2026-10-13 pagi). Baseline dicatat di
hidden_files/share3x-master-2026-10-13.json (151 video, field views0).

Jalan: ./venv/bin/python banding_share3x.py  (dari folder yt-growth/)
Output: hidden_files/banding-share3x-<YYYY-MM-DD>.json + ringkasan stdout.
"""
import json
import re
from datetime import date
from pathlib import Path

from auth import yt_get

ROOT = Path(__file__).parent
MASTER = ROOT / "hidden_files" / "share3x-master-2026-10-13.json"
READER = "lima-misteri"  # baca data publik semua channel


def vid_id(url):
    m = re.search(r"(?:shorts/|youtu\.be/|v=)([\w-]{11})", url or "")
    return m.group(1) if m else None


def main():
    data = json.loads(MASTER.read_text())
    ids = [i for i in (vid_id(v.get("url")) for v in data) if i]
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
    for v in data:
        vid = vid_id(v.get("url"))
        s = stats.get(vid, {})
        v0 = int(v.get("views0", 0) or 0)
        v1 = s.get("views")
        hasil.append({
            "url": v.get("url"),
            "channel": v.get("channel"),
            "title": v.get("title"),
            "views0": v0,
            "views1": v1,
            "delta": (v1 - v0) if v1 is not None else None,
            "privacy": s.get("privacy"),
        })
    terukur = [h for h in hasil if h["delta"] is not None]
    naik = [h for h in terukur if h["delta"] > 0]
    total0 = sum(h["views0"] for h in terukur)
    total1 = sum(h["views1"] for h in terukur)
    out = {
        "tanggal": date.today().isoformat(),
        "n_video": len(hasil),
        "terukur": len(terukur),
        "naik": len(naik),
        "total_views0": total0,
        "total_views1": total1,
        "delta_total": total1 - total0,
        "hasil": hasil,
    }
    outp = ROOT / "hidden_files" / f"banding-share3x-{date.today().isoformat()}.json"
    outp.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"EKSPERIMEN SHARE-3x — banding vs baseline 2026-10-13")
    print(f"Video terukur: {len(terukur)}/{len(hasil)}")
    print(f"Yang naik: {len(naik)} | tetap/turun: {len(terukur) - len(naik)}")
    print(f"Total views: {total0} -> {total1} (delta {total1 - total0:+d})")
    print("Top 5 kenaikan:")
    for h in sorted(naik, key=lambda h: -h["delta"])[:5]:
        print(f"  +{h['delta']} | {h['title'][:65]} [{h['channel']}]")
    print(f"Detail: {outp}")


if __name__ == "__main__":
    main()
