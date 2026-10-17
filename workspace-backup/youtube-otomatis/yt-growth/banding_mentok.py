#!/usr/bin/env python3
"""Bandingkan scan sepi hari ini vs scan sebelumnya -> daftar video MENTOK.
MENTOK = publik, umur >24 jam, masuk daftar sepi (shorts <50 / long <100 views),
DAN kenaikan views sejak scan lalu <= 2. Video baru pertama kali masuk daftar
sepi juga kandidat.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
CUR = HERE / "hidden_files" / "sepi-2026-10-17.json"
PREV = HERE / "hidden_files" / "sepi-2026-10-12.json"

def quiet(v):
    fmt, views = v["format"], v["views"]
    return (fmt == "shorts" and views < 50) or (fmt == "long" and views < 100)

cur = json.load(open(CUR))
prev = json.load(open(PREV))

prev_views = {}
for slug, ch in prev.items():
    if isinstance(ch, dict) and "videos" in ch:
        for v in ch["videos"]:
            prev_views[(slug, v["id"])] = v["views"]

mentok = []
for slug, ch in cur.items():
    if not (isinstance(ch, dict) and "videos" in ch):
        continue
    for v in ch["videos"]:
        if v["privacy"] != "public" or v["umur_jam"] is None or v["umur_jam"] <= 24:
            continue
        if not quiet(v):
            continue
        key = (slug, v["id"])
        if key in prev_views:
            delta = v["views"] - prev_views[key]
            if delta <= 2:
                v = dict(v); v["slug"] = slug; v["delta_views"] = delta
                v["status_mentok"] = "mentok"
                mentok.append(v)
        else:
            v = dict(v); v["slug"] = slug; v["delta_views"] = None
            v["status_mentok"] = "baru_masuk_sepi"
            mentok.append(v)

out = HERE / "hidden_files" / "mentok-2026-10-17.json"
json.dump(mentok, open(out, "w"), ensure_ascii=False, indent=1)

# ringkasan per channel
from collections import Counter
c = Counter(m["slug"] for m in mentok)
tot = len(mentok)
tot_quiet = sum(1 for slug, ch in cur.items() if isinstance(ch, dict) and "videos" in ch
                for v in ch["videos"] if v["privacy"] == "public" and quiet(v))
print(f"TOTAL MENTOK: {tot} (quiet publik total: {tot_quiet})")
for slug, n in c.most_common():
    totch = sum(1 for slug2, ch in cur.items() if isinstance(ch, dict) and "videos" in ch
                for v in ch["videos"] if slug2 == slug and v["privacy"] == "public" and quiet(v))
    print(f"  {slug}: {n} mentok / {totch} quiet")
