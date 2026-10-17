#!/usr/bin/env python3
"""Batch upload antrean retry-queue via YouTube Data API (yt-growth).
Urutan: gagal_pada tertua dulu. Stop total saat 403 quotaExceeded.
"""
import json, os, re, shutil, sys, time
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis/yt-growth")
from auth import api_session, YT_BASE

QDIR = "/home/hatch/workspace/youtube-otomatis/retry-queue"
DONE = os.path.join(QDIR, "done")
HIDDEN = "/home/hatch/workspace/youtube-otomatis/yt-growth/hidden_files"
RESULT_FILE = os.path.join(HIDDEN, "upload-batch-2026-10-13.json")
MANIFEST_FILE = os.path.join(HIDDEN, "sisa-browser-manifest-2026-10-13.json")

SLUG_MAP = {
    "history-en": "history-en", "horror-en": "horror-en",
    "jejak-buddha": "jejakbuddha", "kisah-alkitab": "kisahalkitab",
    "kisahdharma": "kisahdharma", "limamisteri": "lima-misteri",
    "mystery-en": "mystery-en", "strangetales": "strangetales",
    "tinybuilders": "tinybuilders", "weird-en": "weird-en",
}
CHANNEL_IDS = {
    "history-en": "UCCBGIbsfMo2TmyhbUzHxD0A",
    "horror-en": "UCR7uhocCg9YZM7-Qoi1sVGA",
    "jejakbuddha": "UC1PNEzhOmAH08p75vwp7n0A",
    "kisahalkitab": "UCGCXDPx3vSHTUOkNiuLezdw",
    "kisahdharma": "UCAhInkFRxF3xkxW8kgFOrJA",
    "lima-misteri": "UCQ0vHTsTqVeYy3zLno6pVfQ",
    "mystery-en": "UCjxESFWyFPOkGTSpajK69Lw",
    "strangetales": "UCAVSqZjG8Af_pm_1uD5wRzA",
    "tinybuilders": "UCjy7bWJU5gULDIYjPmTg9xg",
    "weird-en": "UCJ6KqdYvVJ-PaxhGLfTFVhA",
}
WIB = timezone(timedelta(hours=7))
NOW_WIB = datetime.now(WIB)

STOP_ALL = {"stop": False, "reason": ""}
SKIP_CHANNEL = set()
SESSIONS = {}
RESULTS = []
if os.path.exists(RESULT_FILE):
    try:
        RESULTS = json.load(open(RESULT_FILE))
    except Exception:
        RESULTS = []
SEEN_IDS = {r.get("queue_file") for r in RESULTS}
DUPS = []
ERRORS = []


def log(msg):
    print(f"[{datetime.now(WIB).strftime('%H:%M:%S')}] {msg}", flush=True)


def save_results():
    with open(RESULT_FILE, "w") as f:
        json.dump(RESULTS, f, ensure_ascii=False, indent=1)


def err_reason(resp):
    try:
        errs = resp.json().get("error", {}).get("errors", [])
        return errs[0].get("reason", "") if errs else ""
    except Exception:
        return ""


STOP_DESC = re.compile(
    r"^(Tag(\s+YouTube)?\b|PENTING|Visibilitas|Audience|Thumbnail|Kategori|Bahasa|"
    r"Komentar|Jadwal|Slot|---+|#{1,3}\s|SETELAH|Catatan|Langkah|LANGKAH|"
    r"PENGATURAN|CEK\s|VERIFIKASI|AI DISCLOSURE|Disclaimer|DISCLAIMER|AUDIENS)",
    re.IGNORECASE,
)


def _clean_line(ln):
    ln = ln.strip()
    ln = re.sub(r"^[\s>\-*•]+", "", ln)
    ln = re.sub(r"^\*\*", "", ln)
    return ln


def _strip_wrap(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "`'\"":
        v = v[1:-1].strip()
    return v


def parse_md(text, want_basename):
    n_judul = len(re.findall(r"(?m)^[\s>\-*]*\*?\*?Judul\b", text, re.IGNORECASE))
    doc = text
    if n_judul > 1:
        sections = re.split(r"(?m)^##\s+", text)
        target = None
        for s in sections[1:]:
            files = re.findall(r"(?:File|Video)\s*:?\s*[`'\"]?(\S+?\.mp4)[`'\"]?",
                               s, re.IGNORECASE)
            hdr = s.split("\n", 1)[0]
            names = [os.path.basename(p).strip("`'\"") for p in files] + [hdr]
            if any(want_basename == n or want_basename in n or n in want_basename
                   for n in names if n):
                target = s
                break
        if target is None:
            for s in sections[1:]:
                if want_basename in s:
                    target = s
                    break
        if target is not None:
            doc = target
    lines = doc.split("\n")
    full = text

    # ---- judul ----
    title = ""
    for i, ln in enumerate(lines):
        c = _clean_line(ln)
        m = re.match(r"^Judul\s*(\([^)]*\))?\s*:\s*(.+?)\s*$", c, re.I)
        if m:
            title = _strip_wrap(m.group(2))
            break
        m = re.match(r"^Judul\s*(\([^)]*\))?\s*:\s*\*?\*?\s*$", c, re.I)
        if m:
            for j in range(i + 1, len(lines)):
                t = _strip_wrap(_clean_line(lines[j]))
                if t:
                    title = t
                    break
            break
    if not title:
        for i, ln in enumerate(lines):
            c = _clean_line(ln)
            if re.match(r"^#{1,3}\s+(?:\(?[a-z0-9]+\)?\.?\s*)?JUDUL\b", c, re.I):
                for j in range(i + 1, len(lines)):
                    t = _strip_wrap(_clean_line(lines[j]))
                    if t and not t.startswith("#"):
                        title = t
                        break
                break
    if not title:
        m = re.search(r"Varian [A-D]\s*\(DIPILIH\)\s*:\s*(.+)", doc)
        if m:
            title = _strip_wrap(m.group(1))
    # fallback level-file: seksi "JUDUL LONG" (long + shorts dalam 1 file)
    if not title:
        m = re.search(r"(?m)^#{1,3}\s+.*?JUDUL\s+LONG\s*\n\s*(.+?)\s*$", full)
        if m:
            title = _strip_wrap(m.group(1))

    # ---- deskripsi ----
    desc = ""
    for i, ln in enumerate(lines):
        c = _clean_line(ln)
        m = re.match(r"^Deskripsi\s*(\([^)]*\))?\s*:\s*(.*)$", c, re.I)
        if m:
            raw = m.group(2).strip()
            if raw.startswith("`") and not raw.rstrip().endswith("`"):
                buf = [raw.lstrip("`")]
                for j in range(i + 1, len(lines)):
                    lj = lines[j]
                    if "`" in lj:
                        buf.append(lj.split("`")[0])
                        break
                    buf.append(lj)
                desc = "\n".join(buf).strip()
            else:
                rest = _strip_wrap(raw)
                buf = [rest] if rest else []
                for j in range(i + 1, len(lines)):
                    lj = lines[j]
                    if STOP_DESC.match(lj.strip()):
                        break
                    buf.append(lj)
                desc = "\n".join(buf).strip()
            break
        if re.match(r"^#{1,3}\s+(?:\(?[a-z0-9]+\)?\.?\s*)?DESKRIPSI\b", c, re.I) \
                or re.match(r"^===\s*DESKRIPSI\s*===", c, re.I):
            buf = []
            for j in range(i + 1, len(lines)):
                lj = lines[j]
                if STOP_DESC.match(lj.strip()) or re.match(r"^\s*(#{1,3}\s|===)", lj):
                    break
                buf.append(lj)
            desc = "\n".join(buf).strip()
            break
    # fallback level-file: seksi "DESKRIPSI LONG"
    if not desc:
        secs = re.split(r"(?m)^(?=#{1,3}\s)", full)
        for s in secs:
            if re.match(r"#{1,3}\s+.*?DESKRIPSI\s+LONG\b", s, re.I):
                blines = s.split("\n")[1:]
                buf = []
                for lj in blines:
                    if STOP_DESC.match(lj.strip()) or re.match(r"^\s*#{1,3}\s", lj):
                        break
                    buf.append(lj)
                desc = "\n".join(buf).strip()
                break

    # ---- tags ----
    tags = []
    for ln in lines:
        c = _clean_line(ln)
        m = re.match(r"^Tag(?:\s+YouTube)?[^:]*:\s*(.+?)\s*$", c, re.I)
        if m and "," in m.group(1):
            tags = [t.strip() for t in m.group(1).split(",") if t.strip()]
            break
    if not tags:
        for i, ln in enumerate(lines):
            c = _clean_line(ln)
            if re.match(r"^#{1,3}\s+.*?\bTAGS?\b", c, re.I):
                buf = []
                for j in range(i + 1, len(lines)):
                    lj = lines[j].strip()
                    if not lj or lj.startswith("#") or STOP_DESC.match(lj):
                        break
                    buf.append(lj)
                tags = [t.strip() for t in ",".join(buf).split(",") if t.strip()]
                break
    if not tags:
        secs = re.split(r"(?m)^(?=#{1,3}\s)", full)
        for s in secs:
            if re.match(r"#{1,3}\s+.*?\bTAGS?\b", s, re.I):
                blines = [l.strip() for l in s.split("\n")[1:] if l.strip()]
                blines = [l for l in blines
                          if not l.startswith("#") and not re.match(r"^-+$", l)]
                tags = [t.strip() for t in ",".join(blines).split(",") if t.strip()]
                break

    # ---- info level file ----
    ch_name, handle = "", ""
    m = re.search(r'Channel:\s*"([^"]+)"\s*\((@[\w.\-]+)', full)
    if not m:
        m = re.search(r"\*\*Channel:\*\*\s*(.+?)\s*[—–-]\s*(@[\w.\-]+)", full)
    if not m:
        m = re.search(r"^# Channel:\s*(.+?)\s*\((@[\w.\-]+)", full, re.M)
    if not m:
        m = re.search(r"[—–|-]\s*([A-Za-z][\w .&']{1,40}?)\s*\((@[\w.\-]+)\)", full)
    if m:
        ch_name, handle = m.group(1).strip(), m.group(2)
    if not ch_name and handle:
        ch_name = handle

    thumb = ""
    m = re.search(r"Thumbnail[^:]*:\s*[`'\"]?(\S+?\.(?:jpg|jpeg|png))", full)
    if m:
        thumb = m.group(1)

    made_for_kids = bool(
        re.search(r"untuk anak-anak", full, re.I)
        and not re.search(r"bukan untuk anak", full, re.I)
    )

    return {"title": title, "description": desc, "tags": tags,
            "channel_name": ch_name, "handle": handle,
            "thumbnail_hint": thumb, "made_for_kids": made_for_kids}


def _split_channel(ch, handle_fallback=""):
    m = re.match(r"(.+?)\s*(@[\w.\-]+)\s*$", ch or "")
    if m:
        return m.group(1).strip(), m.group(2)
    ch = (ch or "").strip()
    if ch.startswith("@"):
        return ch, ch
    return ch, handle_fallback


def parse_instruksi(path, want_basename):
    if path.endswith(".json"):
        d = json.load(open(path))
        if isinstance(d.get("shorts"), list):
            entry = None
            for e in d["shorts"]:
                if os.path.basename(e.get("video_path", "")) == want_basename:
                    entry = e
                    break
            if entry is None:
                return None
            cn, hd = _split_channel(d.get("channel", ""), d.get("handle", ""))
            return {"title": entry.get("title", ""),
                    "description": entry.get("description", ""),
                    "tags": entry.get("tags", []) or [],
                    "channel_name": cn, "handle": hd,
                    "thumbnail_hint": entry.get("thumbnail_path", "")
                                      or d.get("thumbnail_path", ""),
                    "made_for_kids": False}
        cn, hd = _split_channel(d.get("channel", ""), d.get("handle", ""))
        return {"title": d.get("title", ""), "description": d.get("description", ""),
                "tags": d.get("tags", []) or [], "channel_name": cn, "handle": hd,
                "thumbnail_hint": d.get("thumbnail_path", ""), "made_for_kids": False}
    text = open(path, encoding="utf-8", errors="replace").read()
    return parse_md(text, want_basename)


def get_channel(slug):
    if slug in SESSIONS:
        return SESSIONS[slug]
    s = api_session(slug)
    r = s.get(YT_BASE + "/channels",
              params={"mine": "true", "part": "snippet,contentDetails"}, timeout=30)
    if r.status_code == 403 and "quotaExceeded" in r.text:
        STOP_ALL["stop"] = True
        STOP_ALL["reason"] = "quotaExceeded saat verifikasi channel"
        return None
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    ch = items[0]
    if ch["id"] != CHANNEL_IDS[slug]:
        log(f"BATAL: token {slug} -> {ch['id']} != {CHANNEL_IDS[slug]}")
        return None
    upl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    SESSIONS[slug] = (s, upl)
    log(f"channel OK: {ch['snippet']['title']} ({slug})")
    return SESSIONS[slug]


def is_duplicate(s, uploads_id, title):
    try:
        r = s.get(YT_BASE + "/playlistItems",
                  params={"playlistId": uploads_id, "part": "snippet",
                          "maxResults": 50}, timeout=30)
        if r.status_code == 403 and "quotaExceeded" in r.text:
            STOP_ALL["stop"] = True
            STOP_ALL["reason"] = "quotaExceeded saat cek duplikat"
            return None
        r.raise_for_status()
        for it in r.json().get("items", []):
            if it["snippet"].get("title", "") == title:
                return True
        return False
    except Exception as e:
        log(f"cek duplikat error: {e}")
        return False


def upload_video(s, video_path, meta, privacy, publish_at):
    size = os.path.getsize(video_path)
    body = {
        "snippet": {"title": meta["title"], "description": meta["description"],
                    "tags": meta["tags"], "categoryId": "27"},
        "status": {"privacyStatus": privacy,
                   "selfDeclaredMadeForKids": meta["made_for_kids"]},
    }
    if publish_at:
        body["status"]["publishAt"] = publish_at
    r = s.post("https://www.googleapis.com/upload/youtube/v3/videos",
               params={"uploadType": "resumable", "part": "snippet,status"},
               json=body,
               headers={"X-Upload-Content-Type": "video/mp4",
                        "X-Upload-Content-Length": str(size)},
               timeout=60)
    if r.status_code == 403:
        reason = err_reason(r)
        if reason == "quotaExceeded":
            return "STOP_QUOTA"
        if reason == "uploadLimitExceeded":
            return "SKIP_CHANNEL"
        return f"INIT403:{reason}"
    if r.status_code not in (200, 201):
        return f"INIT{r.status_code}:{r.text[:120]}"
    up_url = r.headers.get("Location")
    if not up_url:
        return "INIT: no Location header"
    chunk = 8 * 1024 * 1024
    with open(video_path, "rb") as f:
        offset = 0
        while offset < size:
            data = f.read(chunk)
            end = offset + len(data) - 1
            rr = s.put(up_url, data=data,
                       headers={"Content-Length": str(len(data)),
                                "Content-Range": f"bytes {offset}-{end}/{size}"},
                       timeout=300)
            if rr.status_code in (200, 201):
                return ("OK", rr.json()["id"])
            elif rr.status_code == 308:
                rng = rr.headers.get("Range", "")
                if rng:
                    offset = int(rng.split("-")[1]) + 1
                    f.seek(offset)
                else:
                    offset = end + 1
                log(f"  ... {offset}/{size} bytes")
            elif rr.status_code == 403:
                reason = err_reason(rr)
                if reason == "quotaExceeded":
                    return "STOP_QUOTA"
                if reason == "uploadLimitExceeded":
                    return "SKIP_CHANNEL"
                return f"CHUNK403:{reason}"
            else:
                return f"CHUNK{rr.status_code}:{rr.text[:120]}"
    return "INCOMPLETE"


def slot_decision(slot_target):
    m = re.match(r"(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) WIB", slot_target or "")
    if not m:
        return ("public", None)
    dt = datetime.strptime(f"{m.group(1)} {m.group(2)}",
                           "%Y-%m-%d %H:%M").replace(tzinfo=WIB)
    if dt <= NOW_WIB:
        return ("public", None)
    return ("private", dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"))


def manifest_entry(fname, q, qslug, meta):
    meta = meta or {}
    tslug = SLUG_MAP.get(qslug, qslug)
    return {"queue_file": fname, "video_path": q.get("video_path"),
            "instruksi_path": q.get("instruksi_path"),
            "title": meta.get("title", ""), "description": meta.get("description", ""),
            "tags": meta.get("tags", []), "channel_slug": tslug,
            "channel_name": meta.get("channel_name", ""),
            "handle": meta.get("handle", ""),
            "channel_id": CHANNEL_IDS.get(tslug, ""),
            "slot_target": q.get("slot_target"),
            "thumbnail_hint": meta.get("thumbnail_hint", "")}


def main():
    files = sorted(
        (f for f in os.listdir(QDIR) if f.endswith(".json")),
        key=lambda f: json.load(open(os.path.join(QDIR, f))).get("gagal_pada", ""),
    )
    log(f"antrean: {len(files)} file, sekarang {NOW_WIB.strftime('%Y-%m-%d %H:%M')} WIB")
    manifest_left = []
    touched = set()

    for fname in files:
        if STOP_ALL["stop"]:
            break
        qpath = os.path.join(QDIR, fname)
        q = json.load(open(qpath))
        qslug = q.get("channel", "")
        vpath = q.get("video_path", "")
        ipath = q.get("instruksi_path", "")
        slot = q.get("slot_target", "")
        base = os.path.basename(vpath)
        touched.add(fname)

        if fname in SEEN_IDS:
            shutil.move(qpath, os.path.join(DONE, fname))
            log(f"SKIP (sudah sukses tercatat): {fname}")
            continue
        if not os.path.exists(vpath):
            ERRORS.append({"file": fname, "error": "video tidak ada"})
            log(f"SKIP (video hilang): {fname}")
            continue
        if qslug == "inktime" or qslug not in SLUG_MAP:
            meta = parse_instruksi(ipath, base) if os.path.exists(ipath) else None
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            log(f"MANIFEST (tanpa token): {fname}")
            continue

        tslug = SLUG_MAP[qslug]
        meta = parse_instruksi(ipath, base) if os.path.exists(ipath) else None
        if not meta or not meta["title"]:
            ERRORS.append({"file": fname, "error": "parse instruksi gagal/judul kosong"})
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            log(f"MANIFEST (parse gagal): {fname}")
            continue
        if tslug in SKIP_CHANNEL:
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            log(f"MANIFEST (channel limit): {fname}")
            continue

        ch = get_channel(tslug)
        if STOP_ALL["stop"]:
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            break
        if ch is None:
            ERRORS.append({"file": fname, "error": "verifikasi channel gagal"})
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            continue
        s, uploads_id = ch

        dup = is_duplicate(s, uploads_id, meta["title"])
        if STOP_ALL["stop"]:
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            break
        if dup:
            shutil.move(qpath, os.path.join(DONE, fname))
            DUPS.append(fname)
            log(f"DUPLIKAT-SKIP: {meta['title'][:60]}")
            continue

        privacy, publish_at = slot_decision(slot)
        log(f"UPLOAD [{qslug}] {meta['title'][:60]} ({privacy}"
            f"{', pub:' + publish_at if publish_at else ''})")
        res = upload_video(s, vpath, meta, privacy, publish_at)
        if res == "STOP_QUOTA":
            STOP_ALL["stop"] = True
            STOP_ALL["reason"] = "403 quotaExceeded (kuota API harian habis)"
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            break
        if res == "SKIP_CHANNEL":
            SKIP_CHANNEL.add(tslug)
            ERRORS.append({"file": fname, "error": "uploadLimitExceeded"})
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            log(f"channel {tslug} uploadLimitExceeded -> dilewati")
            continue
        if isinstance(res, tuple) and res[0] == "OK":
            vid = res[1]
            RESULTS.append({"queue_file": fname, "video_id": vid,
                            "url": "https://youtu.be/" + vid, "channel": qslug,
                            "title": meta["title"], "visibility": privacy,
                            "uploaded_at_wib": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")})
            save_results()
            shutil.move(qpath, os.path.join(DONE, fname))
            log(f"SUKSES: {vid} https://youtu.be/{vid}")
            continue
        ERRORS.append({"file": fname, "error": str(res)[:200]})
        manifest_left.append(manifest_entry(fname, q, qslug, meta))
        log(f"GAGAL: {fname} -> {str(res)[:120]}")

    if STOP_ALL["stop"]:
        in_m = {e["queue_file"] for e in manifest_left}
        err_files = {e["file"] for e in ERRORS}
        for fname in files:
            if fname in in_m or fname in err_files:
                continue
            qpath = os.path.join(QDIR, fname)
            if not os.path.exists(qpath):
                continue  # sudah pindah ke done/
            q = json.load(open(qpath))
            qslug = q.get("channel", "")
            base = os.path.basename(q.get("video_path", ""))
            ipath = q.get("instruksi_path", "")
            meta = None
            if os.path.exists(ipath):
                try:
                    meta = parse_instruksi(ipath, base)
                except Exception:
                    meta = None
            manifest_left.append(manifest_entry(fname, q, qslug, meta))
            log(f"MANIFEST (sisa antrean): {fname}")

    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest_left, f, ensure_ascii=False, indent=1)

    print("\n===== RINGKASAN =====")
    print("sukses:", len(RESULTS))
    for r in RESULTS:
        print(" -", r["video_id"], r["url"], "|", r["channel"], "|", r["title"][:60])
    print("duplikat-skip:", len(DUPS), DUPS)
    print("error:", len(ERRORS))
    for e in ERRORS:
        print(" -", e["file"], "->", str(e["error"])[:100])
    print("stop:", STOP_ALL)
    print("manifest browser:", len(manifest_left), "->", MANIFEST_FILE)


if __name__ == "__main__":
    os.makedirs(DONE, exist_ok=True)
    main()
