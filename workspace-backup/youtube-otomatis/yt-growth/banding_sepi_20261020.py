#!/usr/bin/env python3
"""Bandingkan scan 2026-10-20 vs scan malam 2026-10-19.
MENTOK = publik, umur>24j, masuk daftar sepi (shorts<50/long<100 views)
DAN kenaikan views sejak scan lalu <=2. Video yang baru pertama kali masuk
daftar sepi juga kandidat.
Output: hidden_files/mentok-2026-10-20.json
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
HF = HERE / "hidden_files"

lalu = json.load(open(HF / "sepi-2026-10-19-malam.json"))
kini = json.load(open(HF / "sepi-2026-10-20.json"))
mentok_lalu = json.load(open(HF / "mentok-2026-10-19-malam.json"))
lalu_mentok_ids = {v["id"] for v in mentok_lalu}

idx_lalu = {}
for ch in lalu.values():
    for v in ch.get("videos", []):
        idx_lalu[v["id"]] = v

try:
    plan = json.load(open(HF / "perbaikan-sepi-2026-10-19-malam-plan.json"))
    fixed_ids = {t["video_id"] for t in plan}
except FileNotFoundError:
    fixed_ids = set()

def sepi(v):
    views = v.get("views", 0) or 0
    return (v["format"] == "shorts" and views < 50) or \
           (v["format"] == "long" and views < 100)

mentok = []
n_discan_pub = 0
n_sepi = 0
n_error = 0
for slug, ch in kini.items():
    if "error" in ch:
        n_error += 1
        continue
    for v in ch.get("videos", []):
        if v.get("privacy") != "public" or (v.get("umur_jam") or 0) <= 24:
            continue
        n_discan_pub += 1
        if not sepi(v):
            continue
        n_sepi += 1
        pv = idx_lalu.get(v["id"])
        if pv is None:
            status = "baru (tidak ada di scan lalu)"
            delta = None
        else:
            delta = (v.get("views") or 0) - (pv.get("views") or 0)
            if not sepi(pv):
                status = "baru masuk sepi"
            elif delta is None or delta <= 2:
                status = "mentok_lama" if v["id"] in lalu_mentok_ids else "mentok_baru"
            else:
                continue  # tumbuh >2 views -> bukan mentok
        mentok.append({
            "slug": slug, "id": v["id"], "title": v["title"],
            "format": v["format"], "views": v["views"],
            "views_lalu": pv["views"] if pv else None,
            "delta_views": delta,
            "umur_jam": v["umur_jam"],
            "status": status,
            "ditangani_malam": v["id"] in fixed_ids,
        })

mentok.sort(key=lambda x: (x["slug"], x["views"]))
json.dump(mentok, open(HF / "mentok-2026-10-20.json", "w"),
          indent=1, ensure_ascii=False)
baru = [m for m in mentok if m["status"] not in ("mentok_lama",)]
print(f"discan publik>24j: {n_discan_pub}, sepi: {n_sepi}, "
      f"mentok: {len(mentok)} (baru: {len(baru)}), channel error: {n_error}")
for m in baru:
    print(f"  BARU [{m['slug']}/{m['format']}] {m['views']}v {m['id']} "
          f"{m['title'][:70]}")
