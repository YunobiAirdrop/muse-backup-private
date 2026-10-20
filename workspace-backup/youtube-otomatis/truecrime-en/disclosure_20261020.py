#!/usr/bin/env python3
"""Tambah baris AI disclosure ke 3 shorts yg baru diupload + verifikasi status.
Run: ~/workspace/youtube-otomatis/yt-growth/venv/bin/python disclosure_20261020.py
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

VIDS = ["lrK9EGJhSvU", "NNKqYyfLvjM", "fg-wlFcdJMw"]
DISC = ("\n\nAI disclosure: this video uses AI-generated visuals and voiceover "
        "to illustrate a real historical case.")

s = api_session("truecrime-en")
for vid in VIDS:
    r = s.get("https://www.googleapis.com/youtube/v3/videos",
              params={"id": vid, "part": "snippet,status"}, timeout=30)
    r.raise_for_status()
    v = r.json()["items"][0]
    sn, st = v["snippet"], v["status"]
    print(vid, "|", sn["title"][:60], "| privacy:", st["privacyStatus"],
          "| publishAt:", st.get("publishAt"), flush=True)
    if "AI disclosure" not in sn["description"]:
        ur = s.put("https://www.googleapis.com/youtube/v3/videos",
                   params={"part": "snippet,status"},
                   json={"id": vid,
                         "snippet": {**sn, "description": sn["description"] + DISC},
                         "status": st}, timeout=30)
        print("  disclosure:", ur.status_code, flush=True)
    else:
        print("  disclosure sudah ada", flush=True)
