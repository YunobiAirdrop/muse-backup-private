#!/usr/bin/env python3
"""Diagnosis massal video mentok 2026-10-18:
- fetch snippet (batch 50) per channel
- seo_audit in-process -> skor + temuan
- deteksi duplikat judul dalam channel
- retention.py untuk 3 video terburuk per channel
Output: hidden_files/diagnosis-2026-10-18.json
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

mentok = json.load(open(HERE / "hidden_files" / "mentok-2026-10-18.json"))
print(f"video mentok: {len(mentok)}", flush=True)

# kelompok per channel
by_slug = {}
for v in mentok:
    by_slug.setdefault(v["slug"], []).append(v)

def fetch_snippets(slug, ids):
    out = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        r = yt_get(slug, "/videos", {"id": ",".join(batch),
                    "part": "snippet,contentDetails,statistics"})
        for it in r.get("items", []):
            out[it["id"]] = it
    return out

def norm_title(t):
    t = re.sub(r"#\w+", "", t or "").lower()
    t = re.sub(r"[^\w\s]", "", t)
    return re.sub(r"\s+", " ", t).strip()

diag = []
for slug, vids in sorted(by_slug.items()):
    ids = [v["id"] for v in vids]
    try:
        snips = fetch_snippets(slug, ids)
    except Exception as e:
        print(f"[{slug}] FETCH GAGAL: {e}", flush=True)
        for v in vids:
            d = dict(v); d["fetch_error"] = str(e)[:200]; diag.append(d)
        continue
    # duplikat dalam channel
    seen = {}
    for v in vids:
        seen.setdefault(norm_title(v["title"]), []).append(v["id"])
    for v in vids:
        d = dict(v)
        it = snips.get(v["id"])
        if not it:
            d["fetch_error"] = "video tidak ditemukan via API"
            diag.append(d)
            continue
        sn = it["snippet"]
        d["api_title"] = sn["title"]
        d["api_description"] = sn.get("description", "")
        d["api_tags"] = sn.get("tags", [])
        d["categoryId"] = sn.get("categoryId")
        d["duplikat_judul"] = [i for i in seen.get(norm_title(v["title"]), []) if i != v["id"]]
        try:
            skor, temuan = audit({"title": sn["title"], "description": sn.get("description", ""),
                                  "tags": sn.get("tags", [])}, v["format"])
        except Exception as e:
            skor, temuan = -1, [("ERROR", str(e)[:200])]
        d["seo_skor"] = skor
        d["seo_temuan"] = [{"level": lv, "pesan": ps} for lv, ps in temuan]
        diag.append(d)
    print(f"[{slug}] {len(vids)} video diaudit", flush=True)

# retention 3 terburuk per channel
for slug, vids in sorted(by_slug.items()):
    worst = sorted(vids, key=lambda v: v["views"])[:3]
    for v in worst:
        for d in diag:
            if d["id"] == v["id"]:
                try:
                    p = subprocess.run([sys.executable, "retention.py", slug, v["id"]],
                                       capture_output=True, text=True, timeout=120, cwd=str(HERE))
                    d["retention"] = (p.stdout or p.stderr)[:600]
                except Exception as e:
                    d["retention"] = f"gagal: {e}"
                break

json.dump(diag, open(HERE / "hidden_files" / "diagnosis-2026-10-18.json", "w"),
          ensure_ascii=False, indent=1)
n_skor = sum(1 for d in diag if d.get("seo_skor", -1) >= 0)
n_bagus = sum(1 for d in diag if d.get("seo_skor", 0) >= 90)
n_cacat = sum(1 for d in diag if 0 <= d.get("seo_skor", -1) < 90)
n_dup = sum(1 for d in diag if d.get("duplikat_judul"))
print(f"diaudit: {n_skor}, skor>=90: {n_bagus}, skor<90: {n_cacat}, duplikat judul: {n_dup}")
