#!/usr/bin/env python3
"""Perbaiki judul/deskripsi/audience 2 shorts Trail yang terupload dengan judul '**'
(watchdog 2026-10-13 pagi). Jalankan via yt-growth venv.
"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/workspace/youtube-otomatis/yt-growth"))
from auth import yt_get, yt_put

TRAIL_LONG_URL = "https://youtu.be/3LrCIQNugUo"

FIX = {
    "XvrFFt9PR1A": {
        "title": "The Figure Behind the Rock \U0001f631 #shorts #horror #scarystories #foryou",
        "description": ("I zoomed in on the day-two photo. Behind the rock, half-hidden in the fog, "
                        "stood a figure \u2014 and on the back of his jacket, one word: WARDEN. "
                        "From \"The Trail That Whispers Back\", a Midnight Dread Tales original.\n\n"
                        "Watch the full story: " + TRAIL_LONG_URL),
    },
    "UawznNmKb2M": {
        "title": "The Whisper Around the Tent \U0001f631 #shorts #horror #scarystories #foryou",
        "description": ("At midnight, a whisper circled his tent in his own voice\u2026 then the zipper "
                        "began to move down by itself. From \"The Trail That Whispers Back\", "
                        "a Midnight Dread Tales original.\n\n"
                        "Watch the full story: " + TRAIL_LONG_URL),
    },
}

for vid, meta in FIX.items():
    items = yt_get("horror-en", "/videos", {"id": vid, "part": "snippet,status"}).get("items", [])
    if not items:
        print(vid, "-> TIDAK DITEMUKAN, skip"); continue
    sn, st = items[0]["snippet"], items[0]["status"]
    snippet = {
        "title": meta["title"],
        "description": meta["description"],
        "tags": sn.get("tags", []),
        "categoryId": sn.get("categoryId", "27"),
    }
    status = {
        "privacyStatus": st.get("privacyStatus", "public"),
        "selfDeclaredMadeForKids": False,
        "madeForKids": False,
    }
    yt_put("horror-en", "/videos", {"part": "snippet,status"},
           {"id": vid, "snippet": snippet, "status": status})
    print(vid, "-> OK:", meta["title"][:45])
