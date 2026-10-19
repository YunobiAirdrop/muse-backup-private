#!/usr/bin/env python3
"""Scan video private/scheduled terbaru di semua channel → Firebase /yt/review.json
Untuk APK Review Video. Dijalankan tiap 30 menit via cron.
"""
import json, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import urllib.request

BASE = Path.home() / ".hermes" / "yt-growth"
TOKENS_DIR = BASE / "tokens"
FB_DB = "https://yt-dashboard-yunobi-default-rtdb.asia-southeast1.firebasedatabase.app"
FB_AUTH = "zszMpcV3wzsoDXSc9xZZBBwIvM755gBQPPILlyhN"

# slug → (channel_id, nama)
CHANNELS = {
    "empires-en": ("UCd2wADmj47v3XCPcCpk-fSg", "Lost Empires"),
    "history-en": ("UCCBGIbsfMo2TmyhbUzHxD0A", "Echoes of History"),
    "horor": ("UCUEHu-nQXxGuru5Bviy4DKQ", "Kisah Horor"),
    "horror-en": ("UCR7uhocCg9YZM7-Qoi1sVGA", "Midnight Dread Tales"),
    "jejakbuddha": ("UC1PNEzhOmAH08p75vwp7n0A", "Jejak Buddha"),
    "jejakislami": ("UC81zPJnIJbKU5lhTKx-6Hyg", "Jejak Islami"),
    "kisahalkitab": ("UCGCXDPx3vSHTUOkNiuLezdw", "Kisah Alkitab"),
    "kisahdharma": ("UCAhInkFRxF3xkxW8kgFOrJA", "Kisah Dharma"),
    "lima-misteri": ("UCQ0vHTsTqVeYy3zLno6pVfQ", "Lima Misteri"),
    "macammacam": ("UC5ld2qCo0wKeuRKCA1-dbow", "Macam Macam"),
    "mind-en": ("UCAnSrJzQuePS1MJhfwlRJuQ", "Dark Mind Files"),
    "mystery-en": ("UCjxESFWyFPOkGTSpajK69Lw", "Unsolved Shadows"),
    "space-en": ("UCQnUeh4-2AKgCsV_cjgUv4w", "Cosmic Unknown"),
    "strangetales": ("UCAVSqZjG8Af_pm_1uD5wRzA", "Strange Tales"),
    "tinybuilders": ("UCjy7bWJU5gULDIYjPmTg9xg", "Tiny Builders"),
    "truecrime-en": ("UC2df1xY_WqWdX33oLqeXE2w", "Dark Case Files"),
    "weird-en": ("UCJ6KqdYvVJ-PaxhGLfTFVhA", "Weird World Daily"),
    "youtube-pov": ("UC1c8WpKGhFKpUOp5AqVueEg", "Kisah POV"),
    "fakta-bola-dunia": ("UCU9QUVkWqqjnEFtrj6QACDA", "Fakta Bola Dunia"),
    "inktime": ("UCoZl5OaqjXSVkE4S96RY8_g", "InkTime"),
}

def yt_get(slug, path, params=""):
    tok = json.load(open(TOKENS_DIR / f"{slug}.json"))
    at = tok.get("token") or tok.get("access_token", "")
    url = f"https://www.googleapis.com/youtube/v3/{path}?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {at}"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        print(f"  {slug}: {e}", file=sys.stderr)
        return None

def main():
    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    review = {}
    for slug, (cid, nama) in CHANNELS.items():
        # ambil upload terbaru via search (mine=true butuh OAuth per channel)
        r = yt_get(slug, "search", f"part=id,snippet&forMine=true&maxResults=10&order=date&type=video")
        if not r or "items" not in r:
            continue
        vids = [it["id"]["videoId"] for it in r["items"]]
        if not vids:
            continue
        # detail status
        d = yt_get(slug, "videos", f"part=status,snippet,contentDetails&id={','.join(vids)}")
        if not d or "items" not in d:
            continue
        for v in d["items"]:
            st = v["status"]["privacyStatus"]
            pub = v["snippet"]["publishedAt"]
            pdt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            if pdt < cutoff:
                continue
            # hanya yang belum public
            if st == "public":
                continue
            vid = v["id"]
            review[vid] = {
                "videoId": vid,
                "slug": slug,
                "channel": nama,
                "channelId": cid,
                "title": v["snippet"]["title"],
                "privacy": st,
                "publishAt": v["status"].get("publishAt", ""),
                "uploadedAt": pub,
                "duration": v["contentDetails"]["duration"],
                "thumb": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            }
        time.sleep(0.3)
    # tulis ke Firebase
    payload = json.dumps({"updated_at": datetime.now(timezone.utc).isoformat(), "videos": review}).encode()
    url = f"{FB_DB}/yt/review.json?auth={FB_AUTH}"
    req = urllib.request.Request(url, data=payload, method="PUT",
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=30)
    print(f"OK: {len(review)} video pending → Firebase /yt/review.json")

if __name__ == "__main__":
    sys.path.insert(0, str(Path.home() / "workspace" / "youtube-otomatis" / "yt-growth"))
    main()
