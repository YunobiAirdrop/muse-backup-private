#!/usr/bin/env python3
"""Guard anti-duplikat untuk retry upload YouTube (disetujui user 2026-10-14).

Sebelum watchdog/retry mengunggah video dari antrean, cek apakah judulnya
SUDAH live di playlist uploads channel. Kalau sudah ada -> JANGAN upload ulang.

Pakai: python cek_duplikat.py SLUG --judul "Judul Video"
   atau: python cek_duplikat.py SLUG --instruksi /path/upload-instruksi.md
Output: JSON {"duplikat": bool, "video_id": str|None, "judul_live": str|None}
Exit code: 0 = AMAN (boleh upload), 1 = DUPLIKAT (jangan upload), 2 = error cek
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

from auth import yt_get

HERE = Path(__file__).parent
CHANNELS_FILE = HERE / "channels.yaml"


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


# Alias slug antrean -> slug yt-growth
SLUG_ALIAS = {
    "macam-macam": "macammacam",
}

# Token cadangan: playlist uploads bersifat publik, jadi token channel mana pun
# bisa dipakai kalau token channel target belum ada.
TOKEN_FALLBACK_SLUG = "mystery-en"


def load_channels():
    return yaml.safe_load(CHANNELS_FILE.read_text())["channels"]


def resolve_channel_id(tslug, slug, info):
    if info.get("channel_id"):
        return info["channel_id"]
    r = yt_get(tslug, "/channels", {"forHandle": info["handle"], "part": "id"})
    items = r.get("items", [])
    if not items:
        raise RuntimeError(f"Handle {info['handle']} tidak ditemukan.")
    return items[0]["id"]


def judul_dari_instruksi(path):
    lines = Path(path).read_text().splitlines()
    # Format 1: "Judul: ..."
    for line in lines:
        m = re.match(r"^\s*Judul\s*:\s*(.+)$", line)
        if m:
            return m.group(1).strip()
    # Format 2: "=== N. JUDUL ... ===" lalu judul di baris non-kosong berikutnya
    for i, line in enumerate(lines):
        if re.match(r"^=+\s*\d+\.\s*JUDUL\b", line):
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.strip().startswith("="):
                    return nxt.strip()
            break
    # Format 4: "=== JUDUL ... ===" tanpa nomor, varian dipilih via "(DIPILIH):"
    for i, line in enumerate(lines):
        if re.match(r"^=+\s*JUDUL\b", line):
            for nxt in lines[i + 1:]:
                m = re.match(r"^\s*Varian\s+\w+\s*\(DIPILIH\)\s*:\s*(.+)$", nxt)
                if m:
                    return m.group(1).strip()
                if nxt.strip() and not nxt.strip().startswith("=") \
                        and not re.match(r"^\s*Varian\s+\w+\s*:", nxt):
                    return nxt.strip()
            break
    # Format 3: "Judul:" sendiri di baris, judul di baris non-kosong berikutnya
    for i, line in enumerate(lines):
        if re.match(r"^\s*Judul\s*:\s*$", line):
            for nxt in lines[i + 1:]:
                if nxt.strip():
                    return nxt.strip()
            break
    return None


def token_aktif(slug):
    """Slug token yang dipakai: milik channel, atau cadangan kalau belum ada."""
    from auth import TOKENS_DIR
    if (TOKENS_DIR / f"{slug}.json").exists():
        return slug
    return TOKEN_FALLBACK_SLUG


def cek(slug, judul):
    slug = SLUG_ALIAS.get(slug, slug)
    tslug = token_aktif(slug)
    info = load_channels()[slug]
    cid = resolve_channel_id(tslug, slug, info)
    uploads = "UU" + cid[2:]
    target = norm(judul)
    page = None
    checked = 0
    while checked < 200:
        params = {"playlistId": uploads, "part": "snippet,contentDetails",
                  "maxResults": 50}
        if page:
            params["pageToken"] = page
        r = yt_get(tslug, "/playlistItems", params)
        for it in r.get("items", []):
            checked += 1
            live = it["snippet"]["title"]
            if norm(live) == target:
                return {"duplikat": True,
                        "video_id": it["contentDetails"]["videoId"],
                        "judul_live": live}
        page = r.get("nextPageToken")
        if not page:
            break
    return {"duplikat": False, "video_id": None, "judul_live": None,
            "dicek": checked}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--judul")
    ap.add_argument("--instruksi")
    a = ap.parse_args()
    judul = a.judul or (judul_dari_instruksi(a.instruksi) if a.instruksi else None)
    if not judul:
        print(json.dumps({"error": "judul tidak ditemukan"}))
        return 2
    try:
        hasil = cek(a.slug, judul)
    except Exception as e:
        print(json.dumps({"error": str(e)[:200]}))
        return 2
    print(json.dumps(hasil, ensure_ascii=False))
    return 1 if hasil["duplikat"] else 0


if __name__ == "__main__":
    sys.exit(main())
