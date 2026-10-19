#!/usr/bin/env python3
"""Batch review retensi: 3 video teratas + 3 terbawah per channel (berdasar views).
Simpan JSON mentah ke hidden_files/retensi-2026-10-19.json
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
FOLDER = HERE / "hidden_files" / "analytics-2026-10-19"
PY = str(HERE / "venv" / "bin" / "python")

slugs = """empires-en fakta-bola-dunia history-en horor horror-en inktime jejakbuddha
jejakislami kisahalkitab kisahdharma lima-misteri macammacam mind-en mystery-en
space-en strangetales tinybuilders truecrime-en weird-en youtube-pov""".split()

result = {}
for slug in slugs:
    f = FOLDER / f"{slug}.json"
    d = json.loads(f.read_text())
    vids = sorted(d.get("videos", []), key=lambda v: v["views"], reverse=True)
    chosen = []
    seen = set()
    for v in vids[:3] + vids[-3:]:
        if v["video_id"] not in seen:
            seen.add(v["video_id"])
            chosen.append(v)
    entries = []
    for v in chosen:
        try:
            r = subprocess.run([PY, str(HERE / "retention.py"), slug, v["video_id"]],
                               capture_output=True, text=True, timeout=60)
            out = r.stdout.strip() or r.stderr.strip() or f"(kosong, exit={r.returncode})"
        except Exception as e:
            out = f"ERROR: {e}"
        entries.append({"video_id": v["video_id"], "title": v["title"], "views": v["views"],
                        "published": v["published"], "output": out})
        print(f"{slug} {v['video_id']} views={v['views']} ok", flush=True)
    result[slug] = entries

out = HERE / "hidden_files" / "retensi-2026-10-19.json"
out.write_text(json.dumps(result, indent=1, ensure_ascii=False))
print("saved", out)
