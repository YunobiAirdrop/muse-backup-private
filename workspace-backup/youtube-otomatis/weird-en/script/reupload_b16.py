#!/usr/bin/env python3
"""Hapus video lama G3mCu5nqleM (A/V tidak sinkron) lalu upload ulang hasil
two-pass fix. Metadata sama dari upload-2026-10-18.json."""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

W = os.path.expanduser("~/workspace/youtube-otomatis/weird-en")
OLD_ID = "G3mCu5nqleM"
s = api_session("weird-en")

# 1. hapus video lama (masih private, belum tayang)
r = s.delete("https://www.googleapis.com/youtube/v3/videos",
             params={"id": OLD_ID})
print("DELETE", OLD_ID, "->", r.status_code, flush=True)
if r.status_code not in (200, 204):
    print("DELETE body:", r.text[:200])
    sys.exit("DELETE GAGAL — batalkan re-upload agar tidak dobel")

# 2. upload ulang via logika yang sama seperti upload_api_b16.py
sys.argv = ["upload_api_b16.py"]
exec(open(os.path.join(W, "script", "upload_api_b16.py")).read())
