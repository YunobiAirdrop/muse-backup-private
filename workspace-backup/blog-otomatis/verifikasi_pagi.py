#!/usr/bin/env python3
"""Verifikasi pagi hasil posting blog.

Menghitung artikel terbit per blog via feed publik Blogger, membandingkan
dengan snapshot kemarin, dan mencetak ringkasan JSON untuk laporan harian.
Daftar blog dibaca dinamis dari config.json (mengikuti ekspansi berkala).
"""
import json
import os
import sys
import urllib.request
import datetime

BASE = os.path.expanduser("~/workspace/blog-otomatis")
GOAL_HIDDEN = os.path.expanduser(
    "~/workspace/goals/kabarviral-automated-news-blog/hidden_files")
SNAP = os.path.join(GOAL_HIDDEN, "verifikasi-snapshot.json")


def get_blogs():
    cfg = json.load(open(os.path.join(BASE, "config.json")))
    blogs = cfg.get("blogs", cfg)
    out = []
    if isinstance(blogs, dict):
        for name, b in blogs.items():
            url = b.get("url") if isinstance(b, dict) else b
            if url:
                out.append((name, url.rstrip("/")))
    elif isinstance(blogs, list):
        for b in blogs:
            if isinstance(b, dict):
                url = b.get("url", "")
                out.append((b.get("name", url), url.rstrip("/")))
            elif b:
                out.append((b, b))
    return out


def fetch_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def main():
    today = datetime.date.today().isoformat()
    snap = json.load(open(SNAP)) if os.path.exists(SNAP) else {}
    result = {"tanggal": today, "blogs": {}}
    for name, url in get_blogs():
        nama = name.split("//")[-1].split(".")[0] if "://" in name else name
        try:
            feed = fetch_json(
                f"{url}/feeds/posts/default?alt=json&max-results=5")
            f = feed.get("feed", {})
            total = int(f.get("openSearch$totalResults", {}).get("$t", 0))
            new_today = []
            for e in f.get("entry", []):
                pub = e.get("published", {}).get("$t", "")[:10]
                if pub == today:
                    new_today.append(e.get("title", {}).get("$t", ""))
            prev = snap.get(nama, {}).get("total")
            delta = (total - prev) if isinstance(prev, int) else None
            result["blogs"][nama] = {
                "url": url,
                "total": total,
                "selisih_vs_kemarin": delta,
                "judul_baru_hari_ini": new_today,
                "status": "ok",
            }
        except Exception as ex:  # noqa: BLE001 - laporkan sebagai gagal cek
            result["blogs"][nama] = {
                "url": url,
                "status": "gagal_cek",
                "error": str(ex)[:150],
            }
    os.makedirs(GOAL_HIDDEN, exist_ok=True)
    json.dump(
        {n: {"total": v.get("total")}
         for n, v in result["blogs"].items() if v.get("status") == "ok"},
        open(SNAP, "w"), indent=1)
    print(json.dumps(result, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
