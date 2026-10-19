#!/usr/bin/env python3
"""Private video duplikat per protokol bagian 19 (2026-10-19).
Untuk tiap grup duplikat: pertahankan yang views TERBANYAK (atau terlama bila seri),
private sisanya via API videos.update(privacyStatus=private).
Pakai yt_get/yt_put (requests+proxy), BUKAN get_service (httplib2 gagal proxy).
"""
import json, sys
from pathlib import Path

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import yt_get, yt_put

AUDIT = Path("/home/hatch/workspace/youtube-otomatis/hidden_files/audit-kualitas-2026-10-19.json")
OUT = Path("/home/hatch/workspace/youtube-otomatis/hidden_files/private-duplikat-2026-10-19.json")

def video_stats(slug, video_id):
    r = yt_get(slug, "/videos", {"part": "statistics,snippet,status", "id": video_id})
    items = r.get("items", [])
    if not items:
        return None
    v = items[0]
    return {
        "videoId": video_id,
        "judul": v["snippet"]["title"],
        "views": int(v["statistics"].get("viewCount", 0)),
        "publishedAt": v["snippet"]["publishedAt"],
        "privacy": v["status"]["privacyStatus"],
    }

def private_video(slug, video_id):
    yt_put(slug, "/videos", {"part": "status"},
           {"id": video_id, "status": {"privacyStatus": "private"}})

def main():
    audit = json.loads(AUDIT.read_text())
    hasil = {"tanggal": "2026-10-19", "diprivate": [], "dipertahankan": [], "gagal": []}

    for slug, ch in audit["channels"].items():
        dups = ch.get("duplikat_judul", [])
        if not dups:
            continue
        print(f"\n=== {slug} ({len(dups)} grup) ===", flush=True)
        for grup in dups:
            base = grup["judul_base"]
            vids = [v["videoId"] for v in grup["videos"]]
            stats = []
            for vid in vids:
                try:
                    s = video_stats(slug, vid)
                    if s:
                        stats.append(s)
                        print(f"  {vid}: views={s['views']} published={s['publishedAt'][:10]} privacy={s['privacy']}", flush=True)
                except Exception as e:
                    print(f"  {vid}: ERROR baca stats: {e}", flush=True)
                    hasil["gagal"].append({"channel": slug, "videoId": vid, "sebab": f"stats: {e}"})
            if len(stats) < 2:
                continue
            stats.sort(key=lambda s: (-s["views"], s["publishedAt"]))
            keep = stats[0]
            hasil["dipertahankan"].append({
                "channel": slug, "videoId": keep["videoId"], "judul": keep["judul"],
                "views": keep["views"],
                "alasan": f"views terbanyak ({keep['views']}) di grup '{base[:50]}'",
            })
            print(f"  -> PERTAHANKAN {keep['videoId']} (views={keep['views']})", flush=True)
            for s in stats[1:]:
                if s["privacy"] == "private":
                    print(f"  -> {s['videoId']} sudah private, skip", flush=True)
                    hasil["diprivate"].append({
                        "channel": slug, "videoId": s["videoId"], "judul": s["judul"],
                        "alasan": f"duplikat '{base[:50]}' — sudah private sebelumnya",
                    })
                    continue
                try:
                    private_video(slug, s["videoId"])
                    print(f"  -> PRIVATED {s['videoId']}", flush=True)
                    hasil["diprivate"].append({
                        "channel": slug, "videoId": s["videoId"], "judul": s["judul"],
                        "alasan": f"duplikat '{base[:50]}' — kalah views ({s['views']} vs {keep['views']})",
                    })
                except Exception as e:
                    print(f"  -> GAGAL private {s['videoId']}: {e}", flush=True)
                    hasil["gagal"].append({"channel": slug, "videoId": s["videoId"], "sebab": f"private: {e}"})

    OUT.write_text(json.dumps(hasil, indent=2, ensure_ascii=False))
    print(f"\nSelesai. Hasil: {OUT}")
    print(f"Diprivate: {len(hasil['diprivate'])}, Dipertahankan: {len(hasil['dipertahankan'])}, Gagal: {len(hasil['gagal'])}")

if __name__ == "__main__":
    main()
