#!/usr/bin/env python3
"""Download video+subs per audit inventory. Usage: audit-dl.py"""
import json, os, subprocess, sys
D = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-19")
inv = json.load(open(os.path.expanduser(
    "~/workspace/youtube-otomatis/hidden_files/audit-inventory-2026-10-19.json")))
jobs = []
for slug, ch in inv["channels"].items():
    for v in ch["videos"]:
        if v.get("missing") or v.get("error"): continue
        vid = v["videoId"]
        fn = f"{D}/vids/{slug}__{vid}"
        if os.path.exists(fn + ".mp4"):
            print(f"SKIP {slug}/{vid}"); continue
        jobs.append((slug, vid, fn))
print(f"{len(jobs)} jobs")
fails = []
for i, (slug, vid, fn) in enumerate(jobs):
    print(f"[{i+1}/{len(jobs)}] {slug}/{vid}", flush=True)
    r = subprocess.run([
        "yt-dlp", "-q", "--no-warnings",
        "-f", "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]/b[height<=480]/b",
        "--merge-output-format", "mp4",
        "--write-auto-subs", "--write-subs", "--sub-langs", "en,id",
        "--sub-format", "vtt", "--skip-download", "--no-playlist",
        "--convert-subs", "vtt",
        "-o", fn + ".%(ext)s",
        f"https://www.youtube.com/watch?v={vid}",
    ], capture_output=True, text=True, timeout=900)
    # download video (subs already fetched above; do video now)
    r2 = subprocess.run([
        "yt-dlp", "-q", "--no-warnings",
        "-f", "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480][ext=mp4]/b[height<=480]/b",
        "--merge-output-format", "mp4",
        "-o", fn + ".mp4", "--no-playlist",
        f"https://www.youtube.com/watch?v={vid}",
    ], capture_output=True, text=True, timeout=1200)
    if r2.returncode != 0 or not os.path.exists(fn + ".mp4"):
        fails.append((slug, vid, r2.stderr[-300:]))
        print(f"  FAIL {slug}/{vid}", flush=True)
with open(f"{D}/dl-fails.json", "w") as f:
    json.dump(fails, f)
print("DONE, fails:", len(fails))
