#!/usr/bin/env python3
"""A/B test judul & thumbnail TERUKUR — pola AgentTube/VidIQ versi gratis.

Alur aman (default = PROPOSAL, tidak mengubah apa pun di YouTube):
  python ab_test.py propose SLUG VIDEO_ID --title "Judul B" [--thumb path.jpg]
      Simpan usulan test ke ab_tests.json (status: proposal).
  python ab_test.py start SLUG VIDEO_ID --apply
      Terapkan varian B (judul via videos.update; thumbnail via thumbnails.set
      bila --thumb diberikan saat propose). Baseline metrik dicatat dulu.
      --apply WAJIB: mengubah channel user = butuh persetujuan (aturan yt_push).
  python ab_test.py status
      Semua test + metrik berjalan: views & rata-rata durasi tonton sejak start,
      dibandingkan baseline periode sama sebelum start.
  python ab_test.py revert SLUG VIDEO_ID --apply
      Kembalikan judul varian A, tutup test.

Metrik dari YouTube Analytics API resmi (views, averageViewDuration).
CTR/impresi TIDAK tersedia di API — keputusan menang/kalah dari views/hari +
rata-rata durasi tonton, dinyatakan apa adanya.
"""
import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

from auth import yt_get, yt_put, ya_get, api_session

HERE = Path(__file__).parent
STATE = HERE / "ab_tests.json"


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"tests": []}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=1, ensure_ascii=False))


def find_test(st, slug, vid):
    for t in st["tests"]:
        if t["slug"] == slug and t["video_id"] == vid and t["status"] in ("proposal", "running"):
            return t
    return None


def metrics(slug, vid, start, end):
    r = ya_get(slug, {
        "ids": "channel==MINE", "startDate": str(start), "endDate": str(end),
        "metrics": "views,averageViewDuration",
        "dimensions": "video", "filters": f"video=={vid}",
    })
    rows = r.get("rows", [])
    if not rows:
        return {"views": 0, "avg_view_sec": 0.0}
    return {"views": rows[0][1], "avg_view_sec": round(rows[0][2], 1)}


def get_title(slug, vid):
    items = yt_get(slug, "/videos", {"id": vid, "part": "snippet"}).get("items", [])
    if not items:
        sys.exit(f"Video {vid} tidak ditemukan / bukan milik channel ini.")
    return items[0]["snippet"]


def set_title(slug, vid, title):
    sn = get_title(slug, vid)
    new = {"title": title, "description": sn["description"],
           "tags": sn.get("tags", []), "categoryId": sn["categoryId"]}
    for k in ("defaultLanguage", "defaultAudioLanguage"):
        if sn.get(k):
            new[k] = sn[k]
    yt_put(slug, "/videos", {"part": "snippet"}, {"id": vid, "snippet": new})


def set_thumbnail(slug, vid, path):
    s = api_session(slug)
    with open(path, "rb") as f:
        r = s.post("https://www.googleapis.com/upload/youtube/v3/thumbnails/set",
                   params={"videoId": vid, "uploadType": "media"},
                   data=f, headers={"Content-Type": "image/jpeg"}, timeout=60)
    r.raise_for_status()
    return True


def cmd_propose(a):
    st = load_state()
    if find_test(st, a.slug, a.video):
        sys.exit("Sudah ada test aktif/proposal untuk video ini.")
    sn = get_title(a.slug, a.video)
    t = {"slug": a.slug, "video_id": a.video, "status": "proposal",
         "title_a": sn["title"], "title_b": a.title,
         "thumb_b": a.thumb, "created": str(date.today()),
         "started": None, "baseline": None}
    st["tests"].append(t)
    save_state(st)
    print(f"PROPOSAL tersimpan untuk {a.video}:")
    print(f"  A (sekarang): {t['title_a']}")
    print(f"  B (usulan)  : {t['title_b']}")
    if a.thumb:
        print(f"  Thumbnail B : {a.thumb}")
    print("Jalankan 'start --apply' (dengan persetujuan user) untuk menerapkan.")


def cmd_start(a):
    st = load_state()
    t = find_test(st, a.slug, a.video)
    if not t or t["status"] != "proposal":
        sys.exit("Tidak ada proposal untuk video ini. Buat dulu dengan 'propose'.")
    if not a.apply:
        print("[DRY-RUN] start butuh --apply (mengubah judul/thumbnail channel).")
        return
    today = date.today()
    t["baseline"] = metrics(a.slug, a.video, today - timedelta(days=7), today - timedelta(days=1))
    set_title(a.slug, a.video, t["title_b"])
    if t.get("thumb_b"):
        try:
            set_thumbnail(a.slug, a.video, t["thumb_b"])
        except Exception as e:
            print(f"Thumbnail B gagal dipasang ({e}); judul B tetap jalan.")
    t["status"] = "running"
    t["started"] = str(today)
    save_state(st)
    print(f"Test jalan sejak {today}. Baseline 7 hari: {t['baseline']}")


def cmd_status(a):
    st = load_state()
    if not st["tests"]:
        print("Belum ada A/B test.")
        return
    today = date.today()
    for t in st["tests"]:
        print(f"[{t['status']}] {t['slug']} {t['video_id']}")
        print(f"  A: {t['title_a']}\n  B: {t['title_b']}")
        if t["status"] == "running":
            start = date.fromisoformat(t["started"])
            days = max((today - start).days, 1)
            now = metrics(t["slug"], t["video_id"], start, today)
            base = t["baseline"] or {"views": 0, "avg_view_sec": 0}
            print(f"  Berjalan {days} hari: views {now['views']} "
                  f"({now['views'] / days:.1f}/hari), avg view {now['avg_view_sec']}s")
            print(f"  Baseline 7 hari sebelum: views {base['views']} "
                  f"({base['views'] / 7:.1f}/hari), avg view {base['avg_view_sec']}s")


def cmd_revert(a):
    st = load_state()
    t = find_test(st, a.slug, a.video)
    if not t or t["status"] != "running":
        sys.exit("Tidak ada test yang sedang jalan untuk video ini.")
    if not a.apply:
        print("[DRY-RUN] revert butuh --apply.")
        return
    set_title(a.slug, a.video, t["title_a"])
    t["status"] = "closed"
    t["closed"] = str(date.today())
    save_state(st)
    print(f"Judul dikembalikan ke varian A. Test ditutup.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("propose", "start", "revert"):
        p = sub.add_parser(name)
        p.add_argument("slug")
        p.add_argument("video")
        if name == "propose":
            p.add_argument("--title", required=True)
            p.add_argument("--thumb", default=None)
        else:
            p.add_argument("--apply", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()
    {"propose": cmd_propose, "start": cmd_start,
     "status": cmd_status, "revert": cmd_revert}[a.cmd](a)
