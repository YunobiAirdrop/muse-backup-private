#!/usr/bin/env python3
"""Buat playlist tematik per channel + isi video sepi (funnel distribusi ulang).

Untuk tiap slug ber-token: cek playlist yang sudah ada (playlists.list mine),
buat 1 playlist publik berjudul "<frasa niche> | <nama channel>" bila belum ada,
lalu masukkan video publik sepi channel itu (dari scan sepi terbaru) —
long dulu, lalu shorts, maks 15 item.

Biaya kuota: playlists.insert 50u, playlistItems.insert 50u/item.
Berhenti anggun saat kuota habis; progres ditulis INKREMENTAL ke
hidden_files/playlist-funnel-hasil.json supaya tahan restart.
"""
import json
from datetime import date
from pathlib import Path

from auth import api_session, yt_get
from analytics import load_channels

HERE = Path(__file__).parent
LOG = HERE / "hidden_files" / "playlist-funnel-hasil.json"

NICHE = {
    "empires-en": "Ancient Empires & Lost Civilizations",
    "history-en": "History That Changed the World",
    "horor": "Cerita Horor Terseram",
    "horror-en": "Scariest Horror Stories",
    "jejakbuddha": "Kisah & Ajaran Buddha Penuh Makna",
    "jejakislami": "Kisah Nabi & Sejarah Islam",
    "kisahalkitab": "Kisah Alkitab & Tokoh Iman",
    "kisahdharma": "Kisah Dharma & Epos Ramayana",
    "lima-misteri": "Kejadian Aneh & Misteri Nyata",
    "mind-en": "Dark Psychology & Mind Tricks",
    "mystery-en": "Unsolved Mysteries & Strange Cases",
    "space-en": "Space Mysteries & the Unknown Universe",
    "strangetales": "Strangest Tales & Weird True Stories",
    "tinybuilders": "Miniature Builds & Tiny Creations",
    "truecrime-en": "True Crime Cases That Shocked the World",
    "weird-en": "Weird Places & Bizarre World Facts",
    "youtube-pov": "POV Sejarah — Jadi Tokoh di Masa Lalu",
}
PRIORITY = ["youtube-pov", "horor", "truecrime-en", "horror-en", "strangetales",
            "jejakislami", "mystery-en", "mind-en", "space-en", "lima-misteri",
            "empires-en", "jejakbuddha", "kisahalkitab", "tinybuilders",
            "history-en", "weird-en", "kisahdharma"]


def load_scan():
    files = sorted((HERE / "hidden_files").glob("sepi-*.json"))
    files = [f for f in files if "pas2" not in f.name]
    d = json.loads(files[-1].read_text())
    quiet = {}
    for slug, r in d.items():
        vids = [v for v in r.get("videos", []) if v["privacy"] == "public" and
                ((v["format"] == "shorts" and v["views"] < 50) or
                 (v["format"] == "long" and v["views"] < 100))]
        vids.sort(key=lambda v: (v["format"] != "long", -v["views"]))
        quiet[slug] = [v["id"] for v in vids[:15]]
    return quiet


def main():
    chans = load_channels()
    quiet = load_scan()
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    for slug in PRIORITY:
        if slug not in chans or not quiet.get(slug):
            continue
        if log.get(slug, {}).get("done"):
            print(f"{slug}: sudah beres, lewati")
            continue
        s = api_session(slug)
        try:
            mine = yt_get(slug, "/playlists", {"mine": "true", "part": "snippet", "maxResults": 50})
            existing = {it["snippet"]["title"]: it["id"] for it in mine.get("items", [])}
            ch = yt_get(slug, "/channels", {"mine": "true", "part": "snippet"})
            ch_title = ch["items"][0]["snippet"]["title"]
            title = f"{NICHE[slug]} | {ch_title}"[:100]
            pid = existing.get(title)
            if not pid:
                r = s.post("https://www.googleapis.com/youtube/v3/playlists",
                           params={"part": "snippet,status"},
                           json={"snippet": {"title": title,
                                             "description": f"Kumpulan video terbaik dari {ch_title}. Tonton berurutan biar makin seru — jangan lupa SUBSCRIBE!\n\n#foryou"},
                                 "status": {"privacyStatus": "public"}}, timeout=60)
                r.raise_for_status()
                pid = r.json()["id"]
                print(f"{slug}: playlist dibuat {pid}")
            # item yang sudah ada di playlist (playlist kosong bisa 404 di API
            # ini — perlakukan 404 sebagai playlist kosong)
            have = set()
            try:
                pl = yt_get(slug, "/playlistItems", {"playlistId": pid, "part": "contentDetails", "maxResults": 50})
                have = {it["contentDetails"]["videoId"] for it in pl.get("items", [])}
            except Exception:
                have = set()
            added = 0
            for vid in quiet[slug]:
                if vid in have:
                    continue
                r = s.post("https://www.googleapis.com/youtube/v3/playlistItems",
                           params={"part": "snippet"},
                           json={"snippet": {"playlistId": pid,
                                             "resourceId": {"kind": "youtube#video", "videoId": vid}}},
                           timeout=60)
                r.raise_for_status()
                added += 1
            log[slug] = {"done": True, "playlist": pid, "title": title, "added": added}
            LOG.write_text(json.dumps(log, indent=1, ensure_ascii=False))
            print(f"{slug}: +{added} video masuk playlist")
        except Exception as e:
            log[slug] = {"done": False, "error": str(e)[:160]}
            LOG.write_text(json.dumps(log, indent=1, ensure_ascii=False))
            print(f"{slug}: GAGAL {str(e)[:160]}")
            if "quota" in str(e).lower():
                print("KUOTA HABIS — berhenti, sisanya dilanjut besok.")
                break
    print("SELESAI. Log:", LOG)


if __name__ == "__main__":
    main()
