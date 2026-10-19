#!/usr/bin/env python3
"""Jembatan YT Dashboard -> Firebase Realtime Database.

Dijalankan via cron tiap 5 menit. Hemat kuota YouTube API:
- commands (publish) + video requests: tiap run (murah)
- pending (antrean review): tiap 20 menit (~51 unit)
- channels (statistik): tiap 3 jam (~17 unit)
- revenue: tiap 6 jam (analytics, kuota terpisah)
- blogs (statistik 10 blog via feed publik): tiap 6 jam

Kredensial Firebase di ~/.hermes/yt-firebase.json (600): {"db_url": ..., "secret": ...}
RTDB rules: locked (false/false) — semua akses pakai ?auth=<secret>.
"""
import json
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
sys.path.insert(0, str(HOME / "workspace" / "yt-dashboard"))
sys.path.insert(0, str(HOME / "workspace" / "youtube-otomatis" / "yt-growth"))

import app as dash  # reuse channel_info, _latest_videos, CHANNELS, PUBLISH_LOG
from auth import yt_get, yt_put

WIB = timezone(timedelta(hours=7))
ROOT = HOME / "workspace" / "yt-dashboard"
SEC_FILE = HOME / ".hermes" / "yt-firebase.json"
STATE_FILE = ROOT / "fb_state.json"

_sec = json.loads(SEC_FILE.read_text())
DB = _sec["db_url"].rstrip("/")
SECRET = _sec["secret"]


def fb(path, method="GET", data=None, tries=3):
    url = f"{DB}/yt/{path}.json?auth={SECRET}"
    body = json.dumps(data).encode() if data is not None else None
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, method=method,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode() or "null")
        except urllib.error.HTTPError as e:
            print(f"FB {method} {path}: HTTP {e.code}", flush=True)
            return None
        except Exception as e:
            last = e
            print(f"FB {method} {path}: {type(e).__name__} (coba {i+1}/{tries})", flush=True)
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"fb {path} gagal {tries}x: {last}")


def section(name, fn):
    """Jalankan satu bagian sync; gagal = catat, lanjut ke bagian lain."""
    for i in range(2):
        try:
            fn()
            print(f"[{name}] ok", flush=True)
            return True
        except Exception as e:
            print(f"[{name}] gagal ({type(e).__name__}: {str(e)[:80]})", flush=True)
            time.sleep(5)
    return False


def safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        return {"error": str(e)[:80]}


def fetch_pending():
    out = []
    for slug in dash.CHANNELS:
        if not dash.has_token(slug):
            continue
        try:
            cid = dash.CHANNELS[slug].get("channel_id")
            if not cid:
                info = dash.channel_info(slug)
                cid = info.get("channel_id")
            if not cid:
                continue
            pl = yt_get(slug, "/channels", {"id": cid, "part": "contentDetails"})
            uploads = pl["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            items = yt_get(slug, "/playlistItems",
                           {"playlistId": uploads, "part": "contentDetails", "maxResults": 50})
            vids = [it["contentDetails"]["videoId"] for it in items.get("items", [])]
            if not vids:
                continue
            det = yt_get(slug, "/videos", {"id": ",".join(vids), "part": "snippet,status"})
            for it in det.get("items", []):
                priv = it["status"].get("privacyStatus", "")
                if priv in ("private", "unlisted"):
                    sn = it["snippet"]
                    sched = ""
                    if it["status"].get("publishAt"):
                        try:
                            dt = datetime.fromisoformat(
                                it["status"]["publishAt"].replace("Z", "+00:00")).astimezone(WIB)
                            sched = dt.strftime("%d %b %H:%M")
                        except Exception:
                            pass
                    out.append({"slug": slug, "handle": dash.CHANNELS[slug]["handle"],
                                "id": it["id"], "title": sn["title"],
                                "thumb": (sn["thumbnails"].get("medium") or {}).get("url", ""),
                                "privacy": priv, "scheduled_at": sched})
        except Exception as e:
            out.append({"slug": slug, "error": str(e)[:80]})
    return out


def fetch_revenue():
    from auth import ya_get
    end = datetime.now(WIB).date() - timedelta(days=2)
    start = end - timedelta(days=27)
    out = []
    for slug in dash.CHANNELS:
        if not dash.has_token(slug):
            continue
        try:
            r = ya_get(slug, {"ids": "channel==MINE", "startDate": start.isoformat(),
                              "endDate": end.isoformat(),
                              "metrics": "estimatedRevenue,monetizedPlaybacks"})
            rows = r.get("rows") or []
            rev = float(rows[0][0]) if rows and rows[0] else 0.0
            mpb = int(rows[0][1]) if rows and len(rows[0]) > 1 else 0
            out.append({"slug": slug, "handle": dash.CHANNELS[slug]["handle"],
                        "usd": round(rev, 2), "idr": int(rev * 16500),
                        "monetized": bool(rev > 0 or mpb > 0)})
        except Exception as e:
            out.append({"slug": slug, "handle": dash.CHANNELS[slug]["handle"],
                        "error": str(e)[:80]})
    total = round(sum(x.get("usd", 0) for x in out), 2)
    return {"period": f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}",
            "total_usd": total, "total_idr": int(total * 16500), "channels": out}


def fetch_blogs():
    """Statistik 10 blog via feed publik (tanpa API key)."""
    try:
        cfg = json.load(open(HOME / "workspace" / "blog-otomatis" / "config.json"))
    except Exception as e:
        return {"error": str(e)[:80], "blogs": []}
    out = []
    for b in cfg.get("blogs", []):
        url = (b.get("url") or "").rstrip("/")
        name = b.get("tampil") or b.get("nama")
        try:
            req = urllib.request.Request(
                f"{url}/feeds/posts/default?alt=json&max-results=1&orderby=published",
                headers={"User-Agent": "Mozilla/5.0"})
            d = json.load(urllib.request.urlopen(req, timeout=25))
            feed = d.get("feed", {})
            total = int(feed.get("openSearch$totalResults", {}).get("$t", 0))
            entry = (feed.get("entry") or [None])[0] or {}
            title = entry.get("title", {}).get("$t", "")
            pub = entry.get("published", {}).get("$t", "")[:10]
            out.append({"name": name, "url": url, "posts": total,
                        "latest": title[:80], "latest_date": pub})
        except Exception as e:
            out.append({"name": name, "url": url, "error": str(e)[:60]})
    return {"updated": datetime.now(WIB).strftime("%d %b %H:%M"),
            "total_posts": sum(x.get("posts", 0) for x in out), "blogs": out}


def do_publish(cmd):
    slug, vid = cmd.get("slug", ""), cmd.get("videoId", "")
    if slug not in dash.CHANNELS or not vid or not dash.has_token(slug):
        return {"ok": False, "error": "slug/video tidak valid", "ts": int(time.time())}
    try:
        yt_put(slug, "/videos", {"part": "status"},
               {"id": vid, "status": {"privacyStatus": "public"}})
    except Exception as e:
        return {"ok": False, "error": str(e)[:150], "ts": int(time.time())}
    ts = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
    with open(dash.PUBLISH_LOG, "a") as f:
        f.write(f"{ts} {slug} {vid} -> public (via firebase)\n")
    return {"ok": True, "ts": int(time.time())}


def do_delete(cmd):
    slug, vid = cmd.get("slug", ""), cmd.get("videoId", "")
    if slug not in dash.CHANNELS or not vid or not dash.has_token(slug):
        return {"ok": False, "error": "slug/video tidak valid", "ts": int(time.time())}
    try:
        yt_delete(slug, f"/videos/{vid}")
    except Exception as e:
        return {"ok": False, "error": str(e)[:150], "ts": int(time.time())}
    ts = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
    with open(dash.PUBLISH_LOG, "a") as f:
        f.write(f"{ts} {slug} {vid} -> DELETED (via firebase)\n")
    return {"ok": True, "ts": int(time.time())}


def _load_state():
    try:
        raw = STATE_FILE.read_text().strip()
        return json.loads(raw) if raw else {}
    except Exception:
        return {}


def main():
    st = _load_state()
    now = time.time()

    # 1. perintah publish (tiap run)
    published_any = []
    def _cmd():
        cmds = fb("commands") or {}
        for cid, c in cmds.items():
            if isinstance(c, dict) and c.get("status") == "pending":
                print(f"publish {c.get('slug')}/{c.get('videoId')}", flush=True)
                res = do_publish(c)
                fb(f"results/{cid}", "PUT", res)
                fb(f"commands/{cid}", "PUT", {"status": "done", "ts": int(now)})
                if res.get("ok"):
                    published_any.append(c.get("videoId"))
    section("commands", _cmd)

    # 2. permintaan video per channel (tiap run)
    def _vid():
        reqs = fb("req_videos") or {}
        vts = fb("state/videos_ts") or {}
        for slug, ts in reqs.items():
            if not isinstance(ts, (int, float)):
                continue
            if slug in dash.CHANNELS and ts > (vts.get(slug) or 0):
                vids = safe(dash._latest_videos, slug)
                if isinstance(vids, list):
                    fb(f"state/videos/{slug}", "PUT", vids)
                    fb(f"state/videos_ts/{slug}", "PUT", int(now))
            fb(f"req_videos/{slug}", "DELETE")  # hapus antrean
    section("vidreq", _vid)

    # 3. pending tiap 20 menit, atau langsung bila ada publish barusan
    if published_any or now - st.get("pending", 0) > 1200:
        def _p():
            fb("state/pending", "PUT", fetch_pending())
        if section("pending", _p):
            st["pending"] = now

    # 4. channel stats tiap 3 jam
    if now - st.get("channels", 0) > 10800:
        def _c():
            chs = [safe(dash.channel_info, s) for s in dash.CHANNELS]
            fb("state/channels", "PUT", chs)
        if section("channels", _c):
            st["channels"] = now

    # 5. revenue tiap 6 jam
    if now - st.get("revenue", 0) > 21600:
        def _r():
            fb("state/revenue", "PUT", fetch_revenue())
        if section("revenue", _r):
            st["revenue"] = now

    # 6. statistik blog tiap 6 jam (feed publik, tanpa API key)
    if now - st.get("blogs", 0) > 21600:
        def _b():
            fb("state/blogs", "PUT", fetch_blogs())
        if section("blogs", _b):
            st["blogs"] = now

    try:
        fb("state/updated_at", "PUT", datetime.now(WIB).strftime("%d %b %H:%M"))
    except Exception as e:
        print(f"[updated_at] gagal: {e}", flush=True)
    STATE_FILE.write_text(json.dumps(st))
    print("bridge ok", flush=True)


if __name__ == "__main__":
    main()
