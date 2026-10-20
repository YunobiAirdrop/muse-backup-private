#!/usr/bin/env python3
"""Diagnosis 2026-10-20: hanya video mentok BARU (bukan mentok_lama).
- fetch snippet via token channel (NO_TOKEN via READER lima-misteri)
- seo_audit in-process -> skor + temuan
- deteksi duplikat judul dalam channel (scan kini + scan lalu)
- retention.py untuk video baru yang masuk 3 terburuk channelnya
Output: hidden_files/diagnosis-2026-10-20.json
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

mentok = json.load(open(HERE / "hidden_files" / "mentok-2026-10-20.json"))
baru = [v for v in mentok if v["status"] != "mentok_lama"]
print(f"video baru didiagnosis: {len(baru)}", flush=True)

scan_kini = json.load(open(HERE / "hidden_files" / "sepi-2026-10-20.json"))
scan_lalu = json.load(open(HERE / "hidden_files" / "sepi-2026-10-19-malam.json"))
chan_videos = {}
for sc in (scan_kini, scan_lalu):
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

for slug, vs in sorted(by_slug.items()):
    vs_sorted = sorted(vs, key=lambda x: x["views"])
    worst3 = {v["id"] for v in vs_sorted[:3]}
    for v in vs:
        vid = v["id"]
        try:
            item = fetch_snippet(slug, vid)
        except Exception as e:
            diag.append({"id": vid, "slug": slug, "error": str(e)[:150]})
            continue
        sn = item["snippet"]
        try:
            skor, temuan = audit({"title": sn.get("title", ""),
                                  "description": sn.get("description", ""),
                                  "tags": sn.get("tags", [])}, v["format"])
        except Exception as e:
            skor, temuan = -1, [("ERROR", str(e)[:200])]
        # duplikat judul dalam channel
        nt = norm_title(sn.get("title", ""))
        dup = [oid for oid, ot in chan_videos.get(slug, {}).items()
               if oid != vid and norm_title(ot) == nt and nt]
        entry = {
            "id": vid, "slug": slug, "format": v["format"],
            "views": v["views"], "umur_jam": v["umur_jam"],
            "status_mentok": v["status"],
            "api_title": sn.get("title", ""),
            "api_description": sn.get("description", ""),
            "api_tags": sn.get("tags", []),
            "api_category": sn.get("categoryId", ""),
            "seo_skor": skor,
            "seo_temuan": [{"level": lv, "pesan": ps} for lv, ps in temuan],
            "duplikat_dalam_channel": dup,
            "retensi": None,
        }
        if vid in worst3:
            try:
                p = subprocess.run(
                    [str(HERE / "venv" / "bin" / "python"), "retention.py", slug, vid],
                    capture_output=True, text=True, timeout=120, cwd=str(HERE))
                entry["retensi"] = (p.stdout.strip() or p.stderr.strip())[:800]
            except Exception as e:
                entry["retensi"] = f"gagal: {e}"
        diag.append(entry)
        print(f"  {slug} {vid} skor={entry['seo_skor']} dup={len(dup)}", flush=True)

json.dump(diag, open(HERE / "hidden_files" / "diagnosis-2026-10-20.json", "w"),
          indent=1, ensure_ascii=False)
print(f"tersimpan: diagnosis-2026-10-20.json ({len(diag)} video)")
