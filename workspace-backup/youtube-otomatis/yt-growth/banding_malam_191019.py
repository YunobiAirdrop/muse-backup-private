#!/usr/bin/env python3
"""Bandingkan scan malam vs scan pagi 2026-10-19.
MENTOK malam = publik, umur>24j, masuk daftar sepi (shorts<50/long<100 views)
DAN kenaikan views sejak scan pagi <=2. Video yang baru pertama kali masuk
daftar sepi juga kandidat.
Output: hidden_files/mentok-2026-10-19-malam.json
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
HF = HERE / "hidden_files"

pagi = json.load(open(HF / "sepi-2026-10-19.json"))
malam = json.load(open(HF / "sepi-2026-10-19-malam.json"))
mentok_pagi = json.load(open(HF / "mentok-2026-10-19.json"))
pagi_mentok_ids = {v["id"] for v in mentok_pagi}

# index scan pagi per video id
idx_pagi = {}
for ch in pagi.values():
    for v in ch.get("videos", []):
        idx_pagi[v["id"]] = v

# video yang sudah ditangani pagi ini
plan = json.load(open(HF / "perbaikan-sepi-2026-10-19-plan.json"))
fixed_ids = {t["video_id"] for t in plan}
skip_pagi = {"F0Malo5MCoA"}  # di-private pagi ini

def sepi(v):
    views = v.get("views", 0) or 0
    return (v["format"] == "shorts" and views < 50) or \
           (v["format"] == "long" and views < 100)

mentok = []
n_discan_pub = 0
n_sepi = 0
for ch in malam.values():
    slug = ch.get("slug", "?")
    for v in ch.get("videos", []):
        if v.get("privacy") != "public" or (v.get("umur_jam") or 0) <= 24:
            continue
        n_discan_pub += 1
        if not sepi(v):
            continue
        n_sepi += 1
        pv = idx_pagi.get(v["id"])
        if pv is None:
            status = "baru (tidak ada di scan pagi)"
            delta = None
        else:
            delta = (v.get("views") or 0) - (pv.get("views") or 0)
            was_sepi_pagi = sepi(pv)
            if not was_sepi_pagi:
                status = "baru masuk sepi"
            elif delta is None or delta <= 2:
                status = "mentok_lama" if v["id"] in pagi_mentok_ids else "mentok_baru"
            else:
                continue  # tumbuh >2 views -> bukan mentok
        if v["id"] in skip_pagi:
            continue
        mentok.append({
            "slug": slug, "id": v["id"], "title": v.get("title"),
            "format": v["format"], "views": v.get("views"),
            "views_pagi": pv.get("views") if pv else None,
            "delta_views": delta, "umur_jam": v.get("umur_jam"),
            "status": status,
            "ditangani_pagi": v["id"] in fixed_ids,
        })

json.dump(mentok, open(HF / "mentok-2026-10-19-malam.json", "w"),
          ensure_ascii=False, indent=1)
baru = [m for m in mentok if m["status"].startswith("baru")]
lama = [m for m in mentok if m["status"] == "mentok_lama"]
mentok_baru = [m for m in mentok if m["status"] == "mentok_baru"]
print(f"publik>24j discan: {n_discan_pub}, daftar sepi: {n_sepi}")
print(f"mentok total: {len(mentok)} (lama: {len(lama)}, mentok_baru: {len(mentok_baru)}, baru: {len(baru)})")
from collections import Counter
print(Counter(m["slug"] for m in mentok))
