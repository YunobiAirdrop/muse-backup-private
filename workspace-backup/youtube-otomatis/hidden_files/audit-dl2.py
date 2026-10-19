#!/usr/bin/env python3
"""Parallel downloader v2: android player client (bypass bot check). 6 workers."""
import json, os, subprocess, time, random
from concurrent.futures import ThreadPoolExecutor

D = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-19")
inv = json.load(open(os.path.expanduser(
    "~/workspace/youtube-otomatis/hidden_files/audit-inventory-2026-10-19.json")))

BASE = ["yt-dlp","-q","--no-warnings",
        "--extractor-args","youtube:player_client=android",
        "--no-playlist"]

def job(item):
    slug, vid = item
    fn = f"{D}/vids/{slug}__{vid}"
    if os.path.exists(fn + ".mp4"):
        return (slug, vid, "skip")
    url = f"https://www.youtube.com/watch?v={vid}"
    time.sleep(random.uniform(0, 3))
    try:
        # video dulu
        r = subprocess.run(BASE + [
            "-f","b[height<=480]/b","--merge-output-format","mp4",
            "-o",fn+".mp4",url], capture_output=True, text=True, timeout=900)
        ok_v = os.path.exists(fn + ".mp4")
        # subs best-effort
        time.sleep(random.uniform(1, 4))
        subprocess.run(BASE + [
            "--write-auto-subs","--write-subs","--sub-langs","en,id",
            "--sub-format","vtt","--skip-download",
            "-o",fn+".%(ext)s",url], capture_output=True, text=True, timeout=300)
        return (slug, vid, "ok" if ok_v else "novideo")
    except Exception as e:
        return (slug, vid, f"err:{str(e)[:80]}")

jobs = []
for slug, ch in inv["channels"].items():
    for v in ch["videos"]:
        if v.get("missing"): continue
        if v["videoId"] in ("P0XCx7rCbNA","uIGWlXfMQJ4","5JlDQfx5AA8"): continue  # sudah dihapus
        jobs.append((slug, v["videoId"]))
print(f"{len(jobs)} jobs, 6 workers", flush=True)
res = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for r in ex.map(job, jobs):
        res.append(r)
        if r[2] != "skip":
            print(r, flush=True)
json.dump(res, open(f"{D}/dl-result.json","w"))
from collections import Counter
print("DONE", Counter(r[2] for r in res))
