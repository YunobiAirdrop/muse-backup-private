#!/usr/bin/env python3
"""Masukkan video long b16 ke playlist tematik channel via API.
Cari playlist 'weird' yang ada; bila tidak ada, buat 'Weird Facts'."""
import json, os, sys

sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import api_session

VIDEO_ID = "U4UwccK9vdI"
s = api_session("weird-en")

pls = s.get("https://www.googleapis.com/youtube/v3/playlists",
            params={"mine": "true", "part": "snippet", "maxResults": 25}).json().get("items", [])
print("playlist ada:", [(p["id"], p["snippet"]["title"]) for p in pls], flush=True)
target = None
for p in pls:
    if "weird" in p["snippet"]["title"].lower():
        target = p["id"]
        break
if not target:
    r = s.post("https://www.googleapis.com/youtube/v3/playlists",
               params={"part": "snippet,status"},
               json={"snippet": {"title": "Weird Facts",
                                 "description": "The weirdest real facts on Earth, ranked and explained."},
                     "status": {"privacyStatus": "public"}})
    if r.status_code not in (200, 201):
        sys.exit(f"BUAT PLAYLIST GAGAL: {r.status_code} {r.text[:200]}")
    target = r.json()["id"]
    print("playlist baru dibuat:", target, flush=True)
r = s.post("https://www.googleapis.com/youtube/v3/playlistItems",
           params={"part": "snippet"},
           json={"snippet": {"playlistId": target,
                             "resourceId": {"kind": "youtube#video", "videoId": VIDEO_ID}}})
if r.status_code in (200, 201):
    print("OK: video masuk playlist", target, flush=True)
else:
    print(f"INSERT GAGAL: {r.status_code} {r.text[:200]}", flush=True)
    sys.exit(1)
