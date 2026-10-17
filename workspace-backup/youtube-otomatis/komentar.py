#!/usr/bin/env python3
"""Auto-reply komentar YouTube 2x sehari (pagi+malam), 13 channel.

Via YouTube Data API resmi (token per-channel yt-growth) untuk baca + balas.
Like & pin tetap via browser (tidak ada API publik untuk keduanya).

  python3 komentar.py fetch PAGI|MALAM   -> candidates JSON di goal hidden_files
  python3 komentar.py post  PAGI|MALAM   -> posting dari decisions JSON
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WS = Path.home() / "workspace" / "youtube-otomatis"
sys.path.insert(0, str(WS / "yt-growth"))
import auth  # noqa: E402

WIB = ZoneInfo("Asia/Jakarta")
HANDLED = WS / "komentar-terbalas.json"
GOAL_HIDDEN = (Path.home() / "workspace" / "goals" /
               "channel-youtube-internasional-berbahasa-inggris" / "hidden_files")

CHANNELS = [
    ("youtube-pov", "@ceritarakyat862", "ID"),
    ("horor", "@KisahPOV", "ID"),
    ("lima-misteri", "@LimaMisteri", "ID"),
    ("truecrime-en", "@TrueCaseFilesTV", "EN"),
    ("horror-en", "@TalesOfDreadTV", "EN"),
    ("mystery-en", "@MysteryShadowsTV", "EN"),
    ("history-en", "@EchoesOfThePast-e9m", "EN"),
    ("space-en", "@CosmosUnknownTV", "EN"),
    ("mind-en", "@TheDarkMindFiles-s6i", "EN"),
    ("weird-en", "@BizarreWorldDaily", "EN"),
    ("empires-en", "@AncientEmpiresTV", "EN"),
    ("strangetales", "@StrangeTales-g6n", "EN"),
    ("tinybuilders", "@tinybuilders-d5z", "EN"),
]


def now_wib():
    return datetime.now(WIB).strftime("%Y-%m-%d %H:%M WIB")


def api_post(slug, path, params, body):
    s = auth.api_session(slug)
    r = s.post(auth.YT_BASE + path, params=params, json=body, timeout=30)
    if r.status_code == 429:
        raise RuntimeError("429 RATE LIMITED dari YouTube - STOP")
    r.raise_for_status()
    return r.json()


def load_handled():
    if HANDLED.exists():
        d = json.loads(HANDLED.read_text())
        d.setdefault("handled", {})
        d.setdefault("like_pending", [])
        return d
    return {"handled": {}, "like_pending": []}


def norm(s):
    import re
    return re.sub(r"\s+", " ", (s or "")).strip()


def already_handled(handled, handle, vid, author, text, thread_id):
    if thread_id in handled["handled"] or thread_id in handled.get("like_pending", []):
        return True
    for v in handled["handled"].values():
        if (v.get("channel") == handle and vid and vid in v.get("video", "")
                and norm(v.get("author")) == norm(author)
                and norm(v.get("text")) == norm(text)):
            return True
    return False


def fetch(tag):
    GOAL_HIDDEN.mkdir(parents=True, exist_ok=True)
    handled = load_handled()
    out = {"tag": tag, "fetched_at": now_wib(), "channels": {}}
    for slug, handle, lang in CHANNELS:
        try:
            ch = auth.yt_get(slug, "/channels", {"mine": "true", "part": "id,contentDetails"})
            item = ch["items"][0]
            cid = item["id"]
            uploads = item["contentDetails"]["relatedPlaylists"]["uploads"]
            pl = auth.yt_get(slug, "/playlistItems",
                             {"playlistId": uploads, "part": "snippet", "maxResults": 3})
            latest = [{"video_id": p["snippet"]["resourceId"]["videoId"],
                       "title": p["snippet"]["title"],
                       "published_at": p["snippet"]["publishedAt"]}
                      for p in pl.get("items", [])]
            th = auth.yt_get(slug, "/commentThreads",
                             {"part": "snippet", "allThreadsRelatedToChannelId": cid,
                              "order": "time", "maxResults": 30, "textFormat": "plainText"})
        except Exception as e:
            print(f"  {handle}: GAGAL fetch API ({type(e).__name__})")
            out["channels"][slug] = {"handle": handle, "lang": lang,
                                     "channel_id": None, "latest_videos": [],
                                     "threads": [], "error": str(e)}
            time.sleep(1)
            continue
        tlist = []
        for t in th.get("items", []):
            sn = t["snippet"]
            top = sn["topLevelComment"]["snippet"]
            thread_id = t["id"]
            comment_id = sn["topLevelComment"]["id"]
            vid = sn.get("videoId")
            author = top.get("authorDisplayName")
            text = top.get("textDisplay")
            replies = []
            if sn.get("totalReplyCount", 0) > 0:
                rl = auth.yt_get(slug, "/comments",
                                 {"part": "snippet", "parentId": comment_id,
                                  "maxResults": 10, "textFormat": "plainText"})
                for rc in rl.get("items", []):
                    rs = rc["snippet"]
                    replies.append({
                        "author": rs.get("authorDisplayName"),
                        "text": rs.get("textDisplay"),
                        "published_at": rs.get("publishedAt"),
                        "is_own": (rs.get("authorChannelId") or {}).get("value") == cid,
                    })
                time.sleep(0.5)
            tlist.append({
                "thread_id": thread_id,
                "comment_id": comment_id,
                "video_id": vid,
                "video_url": f"https://www.youtube.com/watch?v={vid}" if vid else None,
                "author": author,
                "text": text,
                "published_at": top.get("publishedAt"),
                "like_count": top.get("likeCount"),
                "reply_count": sn.get("totalReplyCount", 0),
                "replies": replies,
                "is_own": (top.get("authorChannelId") or {}).get("value") == cid,
                "handled": already_handled(handled, handle, vid, author, text, thread_id),
            })
        out["channels"][slug] = {"handle": handle, "lang": lang, "channel_id": cid,
                                 "latest_videos": latest, "threads": tlist}
        print(f"  {handle}: {len(tlist)} thread, {sum(1 for t in tlist if not t['handled'] and not t['is_own'])} baru")
        time.sleep(1)
    p = GOAL_HIDDEN / f"komentar-candidates-{tag}.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"OK -> {p}")


def post(tag):
    dec_path = GOAL_HIDDEN / f"komentar-decisions-{tag}.json"
    dec = json.loads(dec_path.read_text())
    data = load_handled()
    slug_of = {s: (h, lang) for s, h, lang in CHANNELS}
    total = 0
    per_ch = {}
    # 1) balas
    for d in dec.get("decisions", []):
        if d.get("action") != "balas":
            continue
        slug = d["slug"]
        if total >= 30 or per_ch.get(slug, 0) >= 10:
            continue
        handle, lang = slug_of[slug]
        body = {"snippet": {"parentId": d["comment_id"], "textOriginal": d["reply"]}}
        try:
            r = api_post(slug, "/comments", {"part": "snippet"}, body)
        except Exception as e:
            print(f"  GAGAL {handle}: {e}")
            d["post_error"] = str(e)
            continue
        data["handled"][d["thread_id"]] = {
            "channel": handle,
            "video": d.get("video_url", ""),
            "author": d.get("author", ""),
            "text": d.get("text", ""),
            "handled_at": now_wib(),
            "status": "dibalas",
            "reply": d["reply"],
            "reply_id": r.get("id"),
        }
        HANDLED.write_text(json.dumps(data, ensure_ascii=False, indent=1))
        total += 1
        per_ch[slug] = per_ch.get(slug, 0) + 1
        print(f"  OK balas {handle} -> {r.get('id')}")
        time.sleep(10)  # anti-spam
    # 2) lewati / laporkan -> catat langsung
    for d in dec.get("decisions", []):
        if d.get("action") not in ("lewati", "laporkan"):
            continue
        slug = d["slug"]
        handle, lang = slug_of[slug]
        data["handled"][d["thread_id"]] = {
            "channel": handle,
            "video": d.get("video_url", ""),
            "author": d.get("author", ""),
            "text": d.get("text", ""),
            "handled_at": now_wib(),
            "status": "dilewati" if d["action"] == "lewati" else "dilaporkan",
            "reason": d.get("reason", ""),
        }
    # 3) like -> pending, dikerjakan browser lalu difinalkan
    for d in dec.get("decisions", []):
        if d.get("action") == "like" and d["thread_id"] not in data.get("like_pending", []):
            data.setdefault("like_pending", []).append(d["thread_id"])
    data["last_run"] = f"{now_wib()} ({tag}, via API)"
    HANDLED.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    dec_path.write_text(json.dumps(dec, ensure_ascii=False, indent=1))
    print(f"selesai: {total} balasan diposting")


def seed(tag):
    """Posting komentar diskusi top-level sebagai channel di video terbaru."""
    seeds = json.loads((GOAL_HIDDEN / f"komentar-seeds-{tag}.json").read_text())
    data = load_handled()
    slug_of = {s: h for s, h, _ in CHANNELS}
    for sd in seeds:
        slug = sd["slug"]
        # Komentar top-level WAJIB via commentThreads.insert (comments.insert hanya untuk reply)
        body = {"snippet": {
            "channelId": sd["channel_id"],
            "videoId": sd["video_id"],
            "topLevelComment": {"snippet": {"textOriginal": sd["text"]}},
        }}
        try:
            r = api_post(slug, "/commentThreads", {"part": "snippet"}, body)
        except Exception as e:
            print(f"  GAGAL seed {slug_of[slug]}: {e}")
            continue
        print(f"  OK seed {slug_of[slug]} -> {r.get('id')}")
        data.setdefault("pins", []).append({
            "channel": slug_of[slug],
            "video": f"https://www.youtube.com/watch?v={sd['video_id']}",
            "text": sd["text"],
            "comment_id": r.get("id"),
            "handled_at": now_wib(),
            "pinned": False,
            "pin_pending": True,
        })
        HANDLED.write_text(json.dumps(data, ensure_ascii=False, indent=1))
        time.sleep(5)
    print("seed selesai")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    tag = (sys.argv[2] if len(sys.argv) > 2 else "pagi").lower()
    if tag not in ("pagi", "malam"):
        sys.exit("tag harus 'pagi' atau 'malam'")
    datetag = f"{datetime.now(WIB):%Y-%m-%d}-{tag}"
    if cmd == "fetch":
        fetch(datetag)
    elif cmd == "post":
        post(datetag)
    elif cmd == "seed":
        seed(datetag)
    else:
        print("pakai: komentar.py fetch|post|seed pagi|malam")
