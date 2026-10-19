#!/usr/bin/env python3
"""Pilih kandidat refresh SEO dari analytics-2026-10-19.
Kriteria jadwal: umur >14 hari, views + avg_view_sec di bawah median channel.
Output: ringkasan per channel + daftar kandidat (maks 5/channel).
"""
import json
from datetime import date
from pathlib import Path
from statistics import median

HERE = Path(__file__).parent
FOLDER = HERE / "hidden_files" / "analytics-2026-10-19"
TODAY = date(2026, 10, 19)

slugs = """empires-en fakta-bola-dunia history-en horor horror-en inktime jejakbuddha
jejakislami kisahalkitab kisahdharma lima-misteri macammacam mind-en mystery-en
space-en strangetales tinybuilders truecrime-en weird-en youtube-pov""".split()

out = {}
for slug in slugs:
    f = FOLDER / f"{slug}.json"
    if not f.exists():
        out[slug] = {"error": "file hilang"}
        continue
    d = json.loads(f.read_text())
    vids = d.get("videos", [])
    aged = []
    for v in vids:
        try:
            pub = date.fromisoformat(v["published"][:10])
        except Exception:
            continue
        age = (TODAY - pub).days
        v["age_days"] = age
        if age > 14:
            aged.append(v)
    cand = []
    if aged:
        mv = median([v["views"] for v in aged])
        md = median([v.get("avg_view_sec", 0) for v in aged])
        for v in aged:
            if v["views"] < mv and v.get("avg_view_sec", 0) < md:
                cand.append(v)
        cand.sort(key=lambda v: v["views"])
    out[slug] = {
        "handle": d.get("handle"),
        "n_videos": len(vids),
        "n_aged_14d": len(aged),
        "median_views": median([v["views"] for v in aged]) if aged else 0,
        "median_avg_sec": median([v.get("avg_view_sec", 0) for v in aged]) if aged else 0,
        "candidates": [
            {"video_id": v["video_id"], "title": v["title"], "published": v["published"],
             "age_days": v["age_days"], "views": v["views"], "avg_view_sec": v.get("avg_view_sec", 0),
             "likes": v.get("likes", 0), "watch_minutes": v.get("watch_minutes", 0)}
            for v in cand[:5]
        ],
    }

(FOLDER / "candidate-summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for slug, s in out.items():
    if "error" in s:
        print(f"{slug}: {s['error']}")
    else:
        print(f"{slug}: videos={s['n_videos']} aged>14d={s['n_aged_14d']} "
              f"med_views={s['median_views']} med_avgsec={s['median_avg_sec']} cand={len(s['candidates'])}")
