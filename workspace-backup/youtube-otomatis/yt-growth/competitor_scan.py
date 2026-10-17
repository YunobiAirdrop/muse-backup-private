#!/usr/bin/env python3
"""Scan pola kompetitor — versi gratis ala VidIQ dari AgentTube.

  python competitor_scan.py [--limit 15]

Untuk tiap kompetitor acuan (dari trend_radar.py): ambil ~15 video terbaru
via YouTube Data API resmi (kuota hemat ±3 unit/channel: channels.list +
playlistItems + videos.list), lalu analisis:
  - pola judul: panjang rata-rata, % pakai angka, % tanda tanya, % kata CAPS,
    kata paling sering muncul
  - kadens upload (video/minggu), rata-rata views, 3 judul terlaris
  - hashtag yang dipakai di judul/deskripsi

Output: ~/workspace/blog-otomatis/data/competitor-YYYY-MM-DD.md
Data PUBLIK dibaca dengan token channel mana pun (default lima-misteri).
Hasil scan = bahan trend radar + packaging produksi berikutnya.
"""
import argparse
import json
import re
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from auth import yt_get

READER_SLUG = "lima-misteri"
OUT_DIR = Path.home() / "workspace/blog-otomatis/data"

COMPETITORS = [
    ("nessiejudge", "Horor/misteri ID — acuan Kisah Horor & Lima Misteri"),
    ("BaileySarian", "True crime EN — acuan Dark Case Files"),
    ("MrBallen", "Misteri EN — acuan MysteryShadowsTV"),
    ("BarelySociable", "Internet mystery EN — acuan Dark Mind"),
    ("OverSimplified", "Sejarah animasi EN — acuan Echoes/InkTime"),
    ("kurzgesagt", "Sains/space EN — acuan Cosmos Unknown"),
]

WORD_RE = re.compile(r"[A-Za-zÀ-ÿ]{3,}")
HASHTAG_RE = re.compile(r"#[\wÀ-ÿ]+")
STOP = set("yang dan the and for with this that dari untuk adalah ini itu "
           "dalam pada video shorts youtube episode part".split())


def channel_uploads(handle):
    r = yt_get(READER_SLUG, "/channels", {
        "forHandle": handle, "part": "contentDetails,snippet,statistics"})
    items = r.get("items", [])
    if not items:
        return None, []
    ch = items[0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = yt_get(READER_SLUG, "/playlistItems", {
        "playlistId": uploads, "part": "contentDetails", "maxResults": 50})
    ids = [it["contentDetails"]["videoId"] for it in pl.get("items", [])]
    vids = []
    for i in range(0, len(ids), 50):
        det = yt_get(READER_SLUG, "/videos", {
            "id": ",".join(ids[i:i + 50]), "part": "snippet,statistics"})
        vids.extend(det.get("items", []))
    return ch, vids


def analyze(handle, note, limit):
    ch, vids = channel_uploads(handle)
    if ch is None:
        return f"## @{handle}\n\nTidak ditemukan / gagal dibaca.\n"
    vids = vids[:limit]
    titles = [v["snippet"]["title"] for v in vids]
    views = [int(v["statistics"].get("viewCount", 0)) for v in vids]
    dates = sorted(v["snippet"]["publishedAt"] for v in vids)
    words = Counter()
    tags = Counter()
    for t in titles:
        tags.update(HASHTAG_RE.findall(t))
        for w in WORD_RE.findall(t.lower()):
            if w not in STOP:
                words[w] += 1
    span_days = 1
    if len(dates) > 1:
        d0 = datetime.fromisoformat(dates[0].replace("Z", "+00:00"))
        d1 = datetime.fromisoformat(dates[-1].replace("Z", "+00:00"))
        span_days = max((d1 - d0).days, 1)
    top = sorted(zip(views, titles), reverse=True)[:3]
    avg_len = sum(len(t) for t in titles) / max(len(titles), 1)
    pct_num = sum(bool(re.search(r"\d", t)) for t in titles) / max(len(titles), 1)
    pct_q = sum("?" in t for t in titles) / max(len(titles), 1)
    pct_caps = sum(bool(re.search(r"\b[A-Z]{3,}\b", t)) for t in titles) / max(len(titles), 1)
    lines = [
        f"## @{handle} — {ch['snippet']['title']}",
        f"{note}. Subscriber: {int(ch['statistics'].get('subscriberCount', 0)):,} · "
        f"total video: {ch['statistics'].get('videoCount', '?')}",
        "",
        f"- Dianalisis: {len(vids)} video terbaru · kadens ±{len(vids) / span_days * 7:.1f} video/minggu",
        f"- Rata-rata views video terbaru: {sum(views) / max(len(views), 1):,.0f}",
        f"- Pola judul: panjang rata-rata {avg_len:.0f} karakter · {pct_num:.0%} pakai angka · "
        f"{pct_q:.0%} tanda tanya · {pct_caps:.0%} ada kata CAPS",
        f"- Kata tersering di judul: {', '.join(w for w, _ in words.most_common(8))}",
    ]
    if tags:
        lines.append(f"- Hashtag di judul: {', '.join(t for t, _ in tags.most_common(5))}")
    lines.append("- 3 judul terlaris (dari sampel):")
    for v, t in top:
        lines.append(f"  - {v:,} views — {t}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=15)
    a = ap.parse_args()
    today = date.today()
    parts = [f"# Scan Kompetitor — {today.isoformat()}",
             "Pola nyata dari channel acuan (Data API publik). Bahan trend radar + packaging.\n"]
    for handle, note in COMPETITORS:
        try:
            parts.append(analyze(handle, note, a.limit))
        except Exception as e:
            parts.append(f"## @{handle}\n\nGagal: {e}\n")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"competitor-{today.isoformat()}.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"Tersimpan: {out}")
    print("\n".join(parts))


if __name__ == "__main__":
    main()
