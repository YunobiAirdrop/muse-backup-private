#!/usr/bin/env python3
"""YT Dashboard — backend untuk dashboard multi-channel YouTube (PWA mobile).

Memakai toolkit yt-growth yang sudah ada (auth.py: token OAuth per channel).
TIDAK mengubah file apa pun di yt-growth.
"""
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace" / "youtube-otomatis" / "yt-growth"))

from flask import Flask, jsonify, request, send_from_directory, session, abort

ROOT = Path(__file__).parent
CACHE_DIR = ROOT / "cache"
PW_FILE = ROOT / ".pw_hash"          # 600, berisi sha256 hex (+ salt)
SECRET_FILE = ROOT / ".secret"       # 600, flask secret key
PUBLISH_LOG = ROOT / "publish.log"
CACHE_DIR.mkdir(exist_ok=True)

import yaml
from auth import yt_get, yt_put  # noqa: E402

with open(Path.home() / "workspace" / "youtube-otomatis" / "yt-growth" / "channels.yaml") as f:
    CHANNELS = yaml.safe_load(f)["channels"]

# slug -> token slug yang dipakai baca data publik (channel tanpa token pakai reader lain)
READER = "lima-misteri"

app = Flask(__name__, static_folder="static", static_url_path="")
if SECRET_FILE.exists():
    app.secret_key = SECRET_FILE.read_bytes()
else:
    app.secret_key = secrets.token_bytes(32)
    SECRET_FILE.write_bytes(app.secret_key)
    os.chmod(SECRET_FILE, 0o600)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.permanent_session_lifetime = timedelta(days=30)

WIB = timezone(timedelta(hours=7))

# ---------- cache sederhana ----------
_cache = {}

def cached(key, ttl, fn):
    now = time.time()
    if key in _cache and now - _cache[key][0] < ttl:
        return _cache[key][1]
    val = fn()
    _cache[key] = (now, val)
    return val

def has_token(slug):
    return (Path.home() / ".hermes" / "yt-growth" / "tokens" / f"{slug}.json").exists()

# ---------- auth ----------
def _pw_ok(pw):
    if not PW_FILE.exists():
        return False
    try:
        salt, expect = PW_FILE.read_text().split(":")
    except ValueError:
        return False
    got = hashlib.sha256((salt + pw).encode()).hexdigest()
    return hmac.compare_digest(got, expect.strip())

def need_login():
    if not session.get("auth"):
        abort(401)

@app.before_request
def _guard():
    if request.path.startswith("/api/") and request.path not in ("/api/login", "/api/has_password"):
        need_login()

@app.post("/api/login")
def login():
    pw = (request.json or {}).get("password", "")
    if not PW_FILE.exists():
        # setup pertama kali: password yang dimasukkan jadi password
        if len(pw) < 4:
            return jsonify(ok=False, error="Password minimal 4 karakter"), 400
        salt = secrets.token_hex(8)
        h = hashlib.sha256((salt + pw).encode()).hexdigest()
        PW_FILE.write_text(f"{salt}:{h}")
        os.chmod(PW_FILE, 0o600)
        session["auth"] = True
        session.permanent = True
        return jsonify(ok=True, first=True)
    if _pw_ok(pw):
        session["auth"] = True
        session.permanent = True
        return jsonify(ok=True)
    return jsonify(ok=False, error="Password salah"), 401

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

@app.get("/api/has_password")
def has_password():
    return jsonify(has=PW_FILE.exists())

# ---------- helpers YouTube ----------
def fmt_num(n):
    n = int(n or 0)
    if n >= 1_000_000: return f"{n/1_000_000:.1f} jt"
    if n >= 1_000: return f"{n/1_000:.1f} rb"
    return str(n)

def channel_info(slug):
    """Info 1 channel via API (pakai token sendiri kalau ada, kalau tidak pakai reader)."""
    reader = slug if has_token(slug) else READER
    cid = CHANNELS[slug].get("channel_id")
    if cid:
        r = yt_get(reader, "/channels", {"id": cid, "part": "snippet,statistics"})
    else:
        # resolve via handle dulu
        handle = CHANNELS[slug]["handle"]
        s = yt_get(reader, "/search", {"q": handle, "type": "channel", "part": "snippet", "maxResults": 1})
        if not s.get("items"):
            return {"slug": slug, "handle": handle, "error": "channel tidak ketemu"}
        cid = s["items"][0]["id"]["channelId"]
        r = yt_get(reader, "/channels", {"id": cid, "part": "snippet,statistics"})
    if not r.get("items"):
        return {"slug": slug, "handle": CHANNELS[slug]["handle"], "error": "no data"}
    it = r["items"][0]
    sn, st = it["snippet"], it["statistics"]
    thumbs = sn.get("thumbnails", {})
    return {
        "slug": slug,
        "handle": CHANNELS[slug]["handle"],
        "name": sn["title"],
        "channel_id": it["id"],
        "thumb": (thumbs.get("medium") or thumbs.get("default") or {}).get("url", ""),
        "subs": int(st.get("subscriberCount", 0)),
        "subs_fmt": fmt_num(st.get("subscriberCount", 0)),
        "views": int(st.get("viewCount", 0)),
        "views_fmt": fmt_num(st.get("viewCount", 0)),
        "videos": int(st.get("videoCount", 0)),
        "mine": has_token(slug),
    }

# ---------- API ----------
@app.get("/api/channels")
def api_channels():
    def _fetch():
        out = []
        for slug in CHANNELS:
            try:
                out.append(channel_info(slug))
            except Exception as e:
                out.append({"slug": slug, "handle": CHANNELS[slug]["handle"], "error": str(e)[:80]})
        return out
    return jsonify(cached("channels", 900, _fetch))

def _latest_videos(slug, n=10):
    ch = None
    if "channels" in _cache:
        ch = next((c for c in _cache["channels"][1]
                   if c.get("slug") == slug and "channel_id" in c), None)
    if not ch:
        ch = channel_info(slug)
    cid = ch.get("channel_id")
    reader = slug if has_token(slug) else READER
    pl = yt_get(reader, "/channels", {"id": cid, "part": "contentDetails"})
    uploads = pl["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    items = yt_get(reader, "/playlistItems",
                   {"playlistId": uploads, "part": "contentDetails", "maxResults": n})
    vids = [it["contentDetails"]["videoId"] for it in items.get("items", [])]
    if not vids:
        return []
    det = yt_get(reader, "/videos",
                 {"id": ",".join(vids), "part": "snippet,statistics,status"})
    out = []
    for it in det.get("items", []):
        sn, st_, stt = it["snippet"], it["statistics"], it["status"]
        priv = stt.get("privacyStatus", "?")
        sched = ""
        if priv == "private" and stt.get("publishAt"):
            try:
                dt = datetime.fromisoformat(stt["publishAt"].replace("Z", "+00:00")).astimezone(WIB)
                sched = dt.strftime("%d %b %H:%M")
                priv = "scheduled"
            except Exception:
                pass
        out.append({
            "id": it["id"], "title": sn["title"],
            "thumb": (sn["thumbnails"].get("medium") or {}).get("url", ""),
            "views": int(st_.get("viewCount", 0)), "views_fmt": fmt_num(st_.get("viewCount", 0)),
            "published": sn.get("publishedAt", "")[:10],
            "privacy": priv, "scheduled_at": sched,
        })
    return out

@app.get("/api/videos")
def api_videos():
    slug = request.args.get("slug", "")
    if slug not in CHANNELS:
        return jsonify(error="slug tidak dikenal"), 400
    try:
        return jsonify(cached(f"videos:{slug}", 600, lambda: _latest_videos(slug)))
    except Exception as e:
        return jsonify(error=str(e)[:120]), 500

@app.get("/api/pending")
def api_pending():
    """Semua video private/unlisted di channel yang token-nya ada (antrean review)."""
    def _fetch():
        out = []
        for slug in CHANNELS:
            if not has_token(slug):
                continue
            try:
                cid = CHANNELS[slug].get("channel_id")
                reader = slug
                if not cid:
                    info = channel_info(slug)
                    cid = info.get("channel_id")
                if not cid:
                    continue
                pl = yt_get(reader, "/channels", {"id": cid, "part": "contentDetails"})
                uploads = pl["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                items = yt_get(reader, "/playlistItems",
                               {"playlistId": uploads, "part": "contentDetails", "maxResults": 50})
                vids = [it["contentDetails"]["videoId"] for it in items.get("items", [])]
                if not vids:
                    continue
                det = yt_get(reader, "/videos",
                             {"id": ",".join(vids), "part": "snippet,status"})
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
                        out.append({
                            "slug": slug, "handle": CHANNELS[slug]["handle"],
                            "id": it["id"], "title": sn["title"],
                            "thumb": (sn["thumbnails"].get("medium") or {}).get("url", ""),
                            "privacy": priv, "scheduled_at": sched,
                        })
            except Exception as e:
                out.append({"slug": slug, "error": str(e)[:80]})
        return out
    return jsonify(cached("pending", 600, lambda: _fetch()))

@app.post("/api/publish")
def api_publish():
    data = request.json or {}
    slug, vid = data.get("slug", ""), data.get("videoId", "")
    if slug not in CHANNELS or not vid or not has_token(slug):
        return jsonify(ok=False, error="slug/video tidak valid"), 400
    try:
        yt_put(slug, "/videos",
               {"part": "status"},
               {"id": vid, "status": {"privacyStatus": "public"}})
    except Exception as e:
        return jsonify(ok=False, error=str(e)[:150]), 500
    # invalidate cache pending & videos channel tsb
    _cache.pop("pending", None)
    _cache.pop(f"videos:{slug}", None)
    ts = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
    with open(PUBLISH_LOG, "a") as f:
        f.write(f"{ts} {slug} {vid} -> public\n")
    return jsonify(ok=True)

@app.get("/api/publish_log")
def api_publish_log():
    if not PUBLISH_LOG.exists():
        return jsonify([])
    lines = PUBLISH_LOG.read_text().splitlines()[-50:]
    return jsonify(lines)

# ---------- revenue ----------
USD_IDR = 16500  # kurs estimasi untuk tampilan saja

@app.get("/api/revenue")
def api_revenue():
    """Estimasi penghasilan 28 hari terakhir per channel (YouTube Analytics).
    Hanya channel yang SUDAH monetisasi yang punya angka; sisanya 0."""
    def _fetch():
        from auth import ya_get
        end = datetime.now(WIB).date() - timedelta(days=2)  # data analytics delay ~48 jam
        start = end - timedelta(days=27)
        out = []
        for slug in CHANNELS:
            if not has_token(slug):
                continue
            try:
                r = ya_get(slug, {
                    "ids": "channel==MINE",
                    "startDate": start.isoformat(),
                    "endDate": end.isoformat(),
                    "metrics": "estimatedRevenue,monetizedPlaybacks",
                })
                rows = r.get("rows") or []
                rev = float(rows[0][0]) if rows and rows[0] else 0.0
                mpb = int(rows[0][1]) if rows and len(rows[0]) > 1 else 0
                out.append({
                    "slug": slug,
                    "handle": CHANNELS[slug]["handle"],
                    "usd": round(rev, 2),
                    "idr": int(rev * USD_IDR),
                    "monetized": bool(rev > 0 or mpb > 0),
                })
            except Exception as e:
                out.append({"slug": slug, "handle": CHANNELS[slug]["handle"],
                            "error": str(e)[:80]})
        total_usd = round(sum(x.get("usd", 0) for x in out), 2)
        return {"period": f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}",
                "total_usd": total_usd,
                "total_idr": int(total_usd * USD_IDR),
                "channels": out}
    return jsonify(cached("revenue", 3600, _fetch))

# ---------- frontend ----------
@app.get("/")
def index():
    return send_from_directory(ROOT / "static", "index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765)
