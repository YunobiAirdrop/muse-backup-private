#!/usr/bin/env python3
"""Analisis retensi per posisi video — pola 'find the exact scene that lost
viewers' dari AgentTube, di atas YouTube Analytics API resmi.

  python retention.py SLUG VIDEO_ID [--days 90]

Mengambil kurva audienceWatchRatio per elapsedVideoTimeRatio, lalu melaporkan:
  - retensi di 25% / 50% / 75% / akhir video
  - 3 titik JATUH TERBESAR (selisih antar titik kurva) dalam detik video
    -> titik-titik ini yang dicek ke naskah/adegan saat produksi berikutnya.

CATATAN KEJUJURAN DATA: endpoint ini butuh waktu proses YouTube (video baru
bisa kosong) dan endpoint Analytics di VM ini pernah timeout total
(2026-10-12). Bila gagal/kosong, skrip melapor apa adanya — tidak mengarang.
"""
import argparse
import re
import sys
from datetime import date, timedelta

from auth import ya_get, yt_get
from analytics import load_channels, resolve_channel_id


def parse_duration(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def mmss(sec):
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("video_id")
    ap.add_argument("--days", type=int, default=90)
    a = ap.parse_args()

    info = load_channels()[a.slug]
    cid = resolve_channel_id(a.slug, info)

    items = yt_get(a.slug, "/videos", {
        "id": a.video_id, "part": "snippet,contentDetails,statistics"}).get("items", [])
    if not items:
        sys.exit("Video tidak ditemukan.")
    it = items[0]
    dur = parse_duration(it.get("contentDetails", {}).get("duration", ""))
    views = int(it.get("statistics", {}).get("viewCount", 0))
    print(f"Video: {it['snippet']['title']}")
    print(f"Durasi {mmss(dur)} | views {views} | channel {info['handle']}")

    end = date.today()
    start = end - timedelta(days=a.days)
    try:
        r = ya_get(a.slug, {
            "ids": f"channel=={cid}",
            "startDate": str(start), "endDate": str(end),
            "metrics": "audienceWatchRatio",
            "dimensions": "elapsedVideoTimeRatio",
            "filters": f"video=={a.video_id}",
            "sort": "elapsedVideoTimeRatio",
        })
    except Exception as e:
        print(f"\nTIDAK ADA DATA: Analytics API gagal ({type(e).__name__}). "
              "Tidak ada angka yang dikarang — coba lagi di run mingguan.")
        return
    rows = r.get("rows", [])
    if not rows:
        print("\nTIDAK ADA DATA: kurva retensi kosong (video terlalu baru / "
              "views terlalu sedikit untuk diproses YouTube).")
        return

    curve = [(float(x[0]), float(x[1])) for x in rows]
    def at(ratio):
        return min(curve, key=lambda p: abs(p[0] - ratio))[1]
    print(f"\nRetensi relatif (1.00 = rata-rata video sejenis di titik itu):")
    for label, rr in (("25%", 0.25), ("50%", 0.50), ("75%", 0.75), ("akhir", 1.0)):
        print(f"  {label:6s} {at(rr):.2f}")

    drops = []
    for (r0, w0), (r1, w1) in zip(curve, curve[1:]):
        drops.append((w0 - w1, r0, r1))
    drops.sort(reverse=True)
    print("\n3 titik jatuh terbesar (di sini penonton kabur):")
    for d, r0, r1 in drops[:3]:
        print(f"  {mmss(r0 * dur)} -> {mmss(r1 * dur)}  (jatuh {d:.2f})")
    print("\nPakai titik jatuh ini untuk mengecek adegan/naskah di detik tersebut.")


if __name__ == "__main__":
    main()
