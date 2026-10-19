#!/usr/bin/env python3
"""Scan cepat: blackdetect + silencedetect + volumedetect per video."""
import json, os, re, subprocess, glob
D = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-19")
inv = json.load(open(os.path.expanduser(
    "~/workspace/youtube-otomatis/hidden_files/audit-inventory-2026-10-19.json")))
out = {}
for slug, ch in inv["channels"].items():
    for v in ch["videos"]:
        vid = v["videoId"]
        if vid in ("P0XCx7rCbNA","uIGWlXfMQJ4","5JlDQfx5AA8"):
            out[f"{slug}/{vid}"] = {"deleted": True}; continue
        fn = f"{D}/vids/{slug}__{vid}.mp4"
        if not os.path.exists(fn):
            out[f"{slug}/{vid}"] = {"status": "not_downloaded"}; continue
        r = subprocess.run(["ffmpeg","-v","info","-i",fn,"-vf",
            "blackdetect=d=2:pix_th=0.10","-af",
            "silencedetect=noise=-32dB:d=3,volumedetect","-f","null","-"],
            capture_output=True, text=True, timeout=600)
        e = r.stderr
        blacks = re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)", e)
        sils = re.findall(r"silence_start: ([\d.]+)", e)
        sile = re.findall(r"silence_end: ([\d.]+)", e)
        mv = re.search(r"mean_volume: ([\-\d.]+) dB", e)
        out[f"{slug}/{vid}"] = {
            "black_segs": [(float(a),round(float(b)-float(a),1)) for a,b in blacks],
            "silence_3s": len(sils),
            "mean_vol": mv.group(1) if mv else None,
        }
        fl = []
        if blacks: fl.append(f"BLACK{len(blacks)}")
        if len(sils) >= 2: fl.append(f"SILx{len(sils)}")
        print(f"{slug}/{vid} {' '.join(fl) if fl else 'bersih'}", flush=True)
json.dump(out, open(f"{D}/audit-scan-2026-10-19.json","w"), indent=1)
print("OK")
