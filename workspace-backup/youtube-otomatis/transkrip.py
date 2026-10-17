#!/usr/bin/env python3
"""Ambil transkrip video YouTube via TranscriptAPI (gratis 100 kredit, tanpa kartu).
Butuh TRANSCRIPT_API_KEY — daftar gratis di https://transcriptapi.com,
simpan key di ~/.hermes/transcriptapi.key (600) atau env TRANSCRIPT_API_KEY.

Pakai: python3 transkrip.py <url-atau-id-video> [--out file.txt]
Contoh riset kompetitor: transkrip video topik se-niche -> pelajari hook & struktur script.
Skill: ~/workspace/skills/youtube-skills (ZeroPointRepo, 1032*)
"""
import json, os, re, sys
import requests

KEY_FILE = os.path.expanduser("~/.hermes/transcriptapi.key")
API = "https://transcriptapi.com/api/v2/youtube/transcript"

def get_key():
    k = os.environ.get("TRANSCRIPT_API_KEY", "").strip()
    if k:
        return k
    if os.path.exists(KEY_FILE):
        return open(KEY_FILE).read().strip()
    print("TRANSCRIPT_API_KEY belum diset.")
    print("Daftar gratis (100 kredit, tanpa kartu): https://transcriptapi.com")
    print(f"Lalu simpan key ke {KEY_FILE} (chmod 600).")
    sys.exit(2)

def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url.strip()):
        return url.strip()
    print("URL/ID video tidak dikenali:", url)
    sys.exit(2)

def ambil_transkrip(vid, key):
    r = requests.get(API, params={
        "video_url": vid, "format": "text",
        "include_timestamp": "false", "send_metadata": "true",
    }, headers={"Authorization": f"Bearer {key}",
                "User-Agent": "YunobiBot/1.0"}, timeout=60)
    r.raise_for_status()
    d = r.json()
    teks = d.get("transcript", "") if isinstance(d.get("transcript"), str) \
        else " ".join(s.get("text", "") for s in d.get("transcript", []))
    meta = d.get("metadata", {}) or {}
    return teks.strip(), {"judul": meta.get("title", ""),
                          "channel": meta.get("author_name", "")}

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    vid = video_id(sys.argv[1])
    key = get_key()
    teks, meta = ambil_transkrip(vid, key)
    if not teks:
        print("Transkrip kosong / tidak tersedia untuk video ini.")
        sys.exit(1)
    out = None
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    else:
        out = f"transkrip-{vid}.txt"
    with open(out, "w") as f:
        f.write(f"Judul: {meta['judul']}\nChannel: {meta['channel']}\n"
                f"Video: https://www.youtube.com/watch?v={vid}\n\n{teks}\n")
    print(f"OK: {len(teks)} karakter -> {out}")
    print(f"Judul: {meta['judul'][:80]}")

if __name__ == "__main__":
    main()
