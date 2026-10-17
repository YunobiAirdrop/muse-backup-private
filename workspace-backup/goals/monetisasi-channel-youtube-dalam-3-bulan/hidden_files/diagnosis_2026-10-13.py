#!/usr/bin/env python3
"""Diagnosis audit 3-harian 2026-10-13.

Baca hidden_files/audit-2026-10-13/<slug>.json, bandingkan dengan baseline
kemarin (yt-growth/hidden_files/analytics-2026-10-12/<slug>.data-api.json),
hasil: diagnosis per channel + daftar koreksi yang diusulkan.
"""
import json
from datetime import date
from pathlib import Path

HOME = Path.home()
AUD = HOME / "workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files/audit-2026-10-13"
BASE = HOME / "workspace/youtube-otomatis/yt-growth/hidden_files/analytics-2026-10-12"
GROWTH = HOME / "workspace/youtube-otomatis/yt-growth"
import sys
sys.path.insert(0, str(GROWTH))
from analytics import load_channels

channels = load_channels()
baseline = {}
for f in BASE.glob("*.data-api.json"):
    slug = f.name.replace(".data-api.json", "")
    try:
        d = json.loads(f.read_text())
        baseline[slug] = d
    except Exception:
        pass

report = {"date": date.today().isoformat(), "channels": {}}

for slug, info in channels.items():
    p = AUD / f"{slug}.json"
    if not p.exists():
        continue
    d = json.loads(p.read_text())
    ana = d.get("analytics", {})
    en = d.get("enrich", {})
    stats = en.get("stats", {}) if isinstance(en, dict) else {}
    subs = int(stats.get("subscriberCount", 0) or 0)
    views_lt = int(stats.get("viewCount", 0) or 0)
    vids = ana.get("videos", []) if isinstance(ana, dict) else []
    summ = ana.get("summary", {}) if isinstance(ana, dict) else {}
    v28 = summ.get("views", 0)
    wm28 = summ.get("watch_minutes", 0)
    sg28 = summ.get("subs_gained", 0)

    # baseline kemarin
    b = baseline.get(slug, {})
    bs = (b.get("channel_stats") or {})
    bsubs = int(bs.get("subscriberCount", 0) or 0)
    bviews = int(b.get("total_views_channel_lifetime", 0) or 0)
    dsubs = subs - bsubs if bsubs else None
    dviews = views_lt - bviews if bviews else None

    # top & flop
    ranked = sorted(vids, key=lambda v: v.get("views", 0), reverse=True)
    top3 = [{"id": v["video_id"], "title": v.get("title"),
             "views": v.get("views"), "ret": v.get("retention_pct"),
             "likes": v.get("likes"), "published": v.get("published")}
            for v in ranked[:3]]
    flops = []
    for v in ranked:
        ret = v.get("retention_pct")
        if ret is not None and ret < 40:
            flops.append(v)
    # video views sangat rendah relatif median juga flop
    if vids:
        med = sorted(v.get("views", 0) for v in vids)[len(vids) // 2]
        for v in ranked:
            if v.get("views", 0) < max(3, med * 0.2) and v not in flops:
                flops.append(v)
    flop3 = [{"id": v["video_id"], "title": v.get("title"),
              "views": v.get("views"), "ret": v.get("retention_pct"),
              "likes": v.get("likes"), "published": v.get("published"),
              "dur_s": v.get("duration_sec"), "no_pl": v["video_id"] in d.get("videos_no_playlist", [])}
             for v in flops[:3]]

    # progres monetisasi: 500 subs / 3000 jam (ekstrapolasi 28d x ~13 utk 12 bln — kasar) / 3M shorts 90d
    wh28 = wm28 / 60
    subs_pct = round(subs / 500 * 100, 1)
    # jam tayang 12 bln: data cuma 28d -> pakai 28d sebagai indikator, % dari 3000 dgn ekstrapolasi x13
    wh_est_12mo = wh28 * 13
    wh_pct = round(min(wh_est_12mo / 3000 * 100, 999), 1)
    shorts_v90 = v28 * 3.2  # aproksimasi kasar
    shorts_pct = round(shorts_v90 / 3_000_000 * 100, 3)

    # diagnosa 3 gerbang
    diag = []
    if v28 < 100:
        diag.append("SEEN rendah: views 28d < 100 — butuh distribusi (playlist funnel, pin comment, end screen).")
    if sg28 is not None and sg28 <= 0 and subs < 500:
        diag.append("CLICKED lemah: subs 28d <= 0 — judul/thumbnail kurang menggigit.")
    lowret = [f for f in flops if (f.get("ret") or 100) < 40]
    if lowret:
        diag.append(f"WATCHED bocor: {len(lowret)} video retensi <40% — perbaiki hook 15 dtk pertama.")

    report["channels"][slug] = {
        "handle": info["handle"], "subs": subs, "views_lt": views_lt,
        "v28": v28, "wh28": round(wh28, 1), "sg28": sg28,
        "dsubs": dsubs, "dviews": dviews,
        "subs_pct": subs_pct, "wh_pct": wh_pct, "shorts_pct": shorts_pct,
        "n_videos_28d": len(vids), "n_flops": len(flops),
        "top3": top3, "flop3": flop3, "diag": diag,
        "videos_no_playlist": d.get("videos_no_playlist", []),
        "playlists": [p["title"] for p in d.get("playlists", [])],
        "analytics_ok": isinstance(ana, dict) and "error" not in ana,
    }

(AUD / "_diagnosis.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))

# ringkasan cepat ke stdout
rows = []
for slug, c in report["channels"].items():
    rows.append((c["dsubs"] or 0, slug, c))
rows.sort(reverse=True)
print("== 5 channel subs naik terbesar (vs kemarin) ==")
for ds, slug, c in rows[:5]:
    print(f"  {slug}: subs={c['subs']} (+{ds}), v28={c['v28']}, sg28={c['sg28']}")
print("== 5 channel paling butuh perhatian ==")
rows2 = sorted(report["channels"].items(),
               key=lambda kv: (kv[1]["v28"] or 0))
for slug, c in rows2[:5]:
    print(f"  {slug}: subs={c['subs']} (dsubs={c['dsubs']}), v28={c['v28']}, flops={c['n_flops']}, diag={c['diag'][:1]}")
print("== progres monetisasi (subs%) ==")
for slug, c in sorted(report["channels"].items(), key=lambda kv: -kv[1]["subs_pct"])[:6]:
    print(f"  {slug}: {c['subs']} subs ({c['subs_pct']}%), ~{c['wh28']} jam/28d, shorts90d~{c['shorts_pct']}%")
