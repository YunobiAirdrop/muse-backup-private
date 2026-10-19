#!/usr/bin/env python3
"""Diagnosis malam 2026-10-19: hanya video mentok BARU (tidak ada di diagnosis pagi).
- fetch snippet via token channel (NO_TOKEN via READER lima-misteri)
- seo_audit in-process -> skor + temuan
- deteksi duplikat judul dalam channel (scan malam + scan pagi)
- retention.py untuk video baru yang masuk 3 terburuk channelnya
Output: hidden_files/diagnosis-2026-10-19-malam.json
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from auth import yt_get
from seo_audit import audit

NO_TOKEN = {"inktime", "macammacam"}
READER = "lima-misteri"

mentok = json.load(open(HERE / "hidden_files" / "mentok-2026-10-19-malam.json"))
baru = [v for v in mentok if v["status"] != "mentok_lama"]
print(f"video baru didiagnosis: {len(baru)}", flush=True)

# index semua video channel (scan malam) untuk deteksi duplikat
scan_malam = json.load(open(HERE / "hidden_files" / "sepi-2026-10-19-malam.json"))
scan_pagi = json.load(open(HERE / "hidden_files" / "sepi-2026-10-19.json"))
chan_videos = {}
for sc in (scan_malam, scan_pagi):
    for slug, ch in sc.items():
        for v in ch.get("videos", []):
            chan_videos.setdefault(slug, {})[v["id"]] = v.get("title", "")

def norm_title(t):
    t = re.sub(r"#\w+", "", t or "").lower()
    t = re.sub(r"[^\w\s]", "", t)
    return re.sub(r"\s+", " ", t).strip()

def fetch_snippet(slug, vid):
    reader = READER if slug in NO_TOKEN else slug
    r = yt_get(reader, "/videos", {"id": vid, "part": "snippet,contentDetails,statistics"})
    items = r.get("items", [])
    return items[0] if items else None

diag = []
by_slug = {}
for v in baru:
    by_slug.setdefault(v["slug"], []).append(v)

for slug, vids in sorted(by_slug.items()):
    for v in vids:
        d = dict(v)
        it = fetch_snippet(slug, v["id"])
        if not it:
            d["fetch_error"] = "video tidak ditemukan via API"
            diag.append(d)
            continue
        sn = it["snippet"]
        d["api_title"] = sn["title"]
        d["api_description"] = sn.get("description", "")
        d["api_tags"] = sn.get("tags", [])
        d["categoryId"] = sn.get("categoryId")
        d["privacy_api"] = it.get("status", {}).get("privacyStatus")
        nt = norm_title(sn["title"])
        dups = [vid for vid, t in chan_videos.get(slug, {}).items()
                if vid != v["id"] and norm_title(t) == nt and nt]
        d["duplikat_judul"] = dups
        try:
            skor, temuan = audit({"title": sn["title"], "description": sn.get("description", ""),
                                  "tags": sn.get("tags", [])}, v["format"])
        except Exception as e:
            skor, temuan = -1, [("ERROR", str(e)[:200])]
        d["seo_skor"] = skor
        d["seo_temuan"] = [{"level": lv, "pesan": ps} for lv, ps in temuan]
        diag.append(d)
    print(f"[{slug}] {len(vids)} video diaudit", flush=True)

# retention: video baru yang masuk 3 terburuk channelnya (berdasar views scan malam)
for slug, vids in sorted(by_slug.items()):
    all_v = [vv for vv in mentok if vv["slug"] == slug]
    worst3 = {vv["id"] for vv in sorted(all_v, key=lambda x: x["views"])[:3]}
    for v in vids:
        if v["id"] not in worst3:
            continue
        for d in diag:
            if d["id"] == v["id"]:
                try:
                    p = subprocess.run([sys.executable, "retention.py", slug, v["id"]],
                                       capture_output=True, text=True, timeout=120, cwd=str(HERE))
                    d["retention"] = (p.stdout or p.stderr)[:600]
                except Exception as e:
                    d["retention"] = f"gagal: {e}"
                break

json.dump(diag, open(HERE / "hidden_files" / "diagnosis-2026-10-19-malam.json", "w"),
          ensure_ascii=False, indent=1)
n_bagus = sum(1 for d in diag if d.get("seo_skor", 0) >= 90)
n_cacat = sum(1 for d in diag if 0 <= d.get("seo_skor", -1) < 90)
n_dup = sum(1 for d in diag if d.get("duplikat_judul"))
print(f"skor>=90: {n_bagus}, skor<90: {n_cacat}, duplikat judul: {n_dup}")
for d in diag:
    print(f"- {d['slug']} {d['id']} skor={d.get('seo_skor')} dup={d.get('duplikat_judul')} | {d.get('api_title','')[:60]}")
