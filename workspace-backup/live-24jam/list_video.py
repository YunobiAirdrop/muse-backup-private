#!/usr/bin/env python3
"""List semua video ter-upload per channel via YouTube Data API (pakai requests).
Output: daftar link per channel untuk dibagikan ke sosmed."""
import json, sys
from pathlib import Path
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GRequest

TOKENS_DIR = Path.home() / ".hermes" / "yt-growth" / "tokens"
HANDLES = {
    "youtube-pov": "@ceritarakyat862 (Yunobi Bercerita)",
    "horor": "@KisahPOV (Kisah Horor)",
    "lima-misteri": "@LimaMisteri",
    "truecrime-en": "@TrueCaseFilesTV",
    "horror-en": "@TalesOfDreadTV",
    "mystery-en": "@MysteryShadowsTV",
    "history-en": "@EchoesOfThePast-e9m",
    "space-en": "@CosmosUnknownTV",
    "mind-en": "@TheDarkMindFiles-s6i",
    "weird-en": "@BizarreWorldDaily",
    "empires-en": "@AncientEmpiresTV",
    "strangetales": "@StrangeTales-g6n",
    "tinybuilders": "@tinybuilders-d5z",
    "jejakislami": "@JejakIslami",
    "kisahalkitab": "@KisahAlkitab",
    "jejakbuddha": "@JejakBuddha",
    "kisahdharma": "@KisahDharma",
}

def token(slug):
    c = Credentials.from_authorized_user_file(str(TOKENS_DIR / f"{slug}.json"))
    c.refresh(GRequest())
    return c.token

def api(path, params, slug):
    r = requests.get(f"https://www.googleapis.com/youtube/v3/{path}", params=params,
                     headers={"Authorization": f"Bearer {token(slug)}"}, timeout=30)
    r.raise_for_status()
    return r.json()

all_videos = {}
for slug, label in HANDLES.items():
    try:
        ch = api("channels", {"mine": "true", "part": "contentDetails"}, slug)
        uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        vids, page = [], None
        while True:
            p = {"playlistId": uploads, "part": "snippet", "maxResults": 50}
            if page:
                p["pageToken"] = page
            r = api("playlistItems", p, slug)
            for it in r["items"]:
                sn = it["snippet"]
                vid = sn["resourceId"]["videoId"]
                vids.append({"id": vid, "title": sn["title"],
                             "url": f"https://youtu.be/{vid}"})
            page = r.get("nextPageToken")
            if not page:
                break
        all_videos[label] = vids
        print(f"OK {label}: {len(vids)} video", file=sys.stderr)
    except Exception as e:
        print(f"FAIL {label}: {e}", file=sys.stderr)

out = Path.home() / "workspace/live-24jam/daftar-link-video.json"
out.write_text(json.dumps(all_videos, indent=1, ensure_ascii=False))
print(f"\nTersimpan — total {sum(len(v) for v in all_videos.values())} video")
