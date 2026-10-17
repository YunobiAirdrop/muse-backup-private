#!/usr/bin/env python3
"""Perbaiki metadata video mentok skor<90 (2026-10-17).
Hanya sentuh: hashtag judul shorts, CTA deskripsi long, blok hashtag deskripsi,
dan tags. Judul inti TIDAK diubah. Link afiliasi/atribusi dipertahankan
(edit hanya append/normalisasi, tidak menghapus baris ber-URL).
Pakai: perbaiki_sepi.py [--apply]
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from auth import yt_get, yt_put
from seo_audit import hashtags, HASHTAG_RE

APPLY = "--apply" in sys.argv

# hashtag paket per channel (long: 3-5, shorts: 3-4 di judul, terakhir #foryou)
NICHE_TAGS = {
    "empires-en": ["#history", "#archaeology", "#ancientcivilizations"],
    "fakta-bola-dunia": ["#faktaunik", "#sepakbola", "#faktabola"],
    "history-en": ["#history", "#ancienthistory", "#historicalfacts"],
    "horor": ["#horor", "#ceritahoror", "#viralindonesia"],
    "horror-en": ["#horror", "#horrorstories", "#scarystories"],
    "inktime": ["#history", "#explainer", "#facts"],
    "jejakbuddha": ["#buddha", "#buddhism", "#inspirasi"],
    "jejakislami": ["#islami", "#kisahislami", "#dakwah"],
    "kisahalkitab": ["#alkitab", "#rohani", "#kristen"],
    "kisahdharma": ["#hindu", "#ramayana", "#kebijaksanaan"],
    "lima-misteri": ["#mystery", "#misteri", "#viralindonesia"],
    "macammacam": ["#edukasi", "#anakkreatif", "#belajarseru"],
    "mind-en": ["#psychology", "#mindset", "#facts"],
    "mystery-en": ["#mystery", "#unsolved", "#mysteryfiles"],
    "space-en": ["#space", "#kosmos", "#universe"],
    "strangetales": ["#strange", "#weird", "#mystery"],
    "tinybuilders": ["#miniature", "#diy", "#miniatures"],
    "truecrime-en": ["#truecrime", "#mystery", "#crime"],
    "weird-en": ["#weirdfacts", "#facts", "#didyouknow"],
    "youtube-pov": ["#pov", "#sejarah", "#viralindonesia"],
}
ID_LANG = {"horor", "jejakbuddha", "jejakislami", "kisahalkitab", "kisahdharma",
           "lima-misteri", "macammacam", "youtube-pov", "fakta-bola-dunia"}
CTA = {
    True: "\n\nJangan lupa SUBSCRIBE dan nyalakan loncengnya agar tidak ketinggalan video terbaru! 🔔",
    False: "\n\nSubscribe for new videos every day! 🔔",
}

diag = json.load(open(HERE / "hidden_files" / "diagnosis-2026-10-17.json"))
targets = [d for d in diag if d.get("seo_skor", -1) >= 0 and d["seo_skor"] < 90
           and not d.get("fetch_error")]
print(f"target perbaikan: {len(targets)} video", flush=True)

STOPWORDS = {"the", "a", "an", "and", "or", "of", "in", "on", "to", "for",
             "with", "yang", "dan", "di", "ke", "dari", "ini", "itu", "adalah"}

def build_tags(slug, title, niche):
    words = re.findall(r"[A-Za-zÀ-ÿ\u1E00-\u1EFF]{3,}", title or "")
    kws, seen = [], set()
    for w in words:
        wl = w.lower()
        if wl not in STOPWORDS and wl not in seen:
            seen.add(wl); kws.append(wl)
    # frasa 2 kata
    toks = [w.lower() for w in words if w.lower() not in STOPWORDS]
    phrases = [f"{toks[i]} {toks[i+1]}" for i in range(len(toks) - 1)]
    tags = phrases[:6] + kws[:10]
    for n in niche:
        tags.append(n.lstrip("#"))
    tags.append(slug.replace("-", " "))
    out, total = [], 0
    for t in tags:
        t = t.strip()
        if not t or t in out:
            continue
        if total + len(t) + 1 > 480:
            break
        out.append(t); total += len(t) + 1
    return out[:30]

def fix_title(slug, title, fmt):
    """Kembalikan judul baru atau None bila tidak ada cacat judul."""
    tags = hashtags(title)
    if fmt == "shorts":
        core = HASHTAG_RE.sub("", title).strip()
        niche = NICHE_TAGS.get(slug, ["#viral"])[:2]
        new_tags = niche + ["#foryou"]
        # pertahankan hashtag relevan yang sudah ada (maks 2 selain #foryou)
        keep = [t for t in tags if t.lower() != "#foryou" and t.lower() in
                [n.lower() for n in NICHE_TAGS.get(slug, [])]]
        final = (keep[:2] + [t for t in niche if t.lower() not in
                 [k.lower() for k in keep]])[:2] + ["#foryou"]
        new = core + " " + " ".join(final)
        return new if new != title else None
    else:
        # long: pindahkan hashtag dari judul ke deskripsi
        core = HASHTAG_RE.sub("", title).strip()
        core = re.sub(r"\s{2,}", " ", core)
        return core if core != title else None

def fix_description(slug, desc, fmt, moved_tags):
    desc = desc or ""
    lines = desc.rstrip().split("\n")
    # pisahkan blok hashtag di ekor
    body_lines = list(lines)
    trailing = []
    while body_lines and body_lines[-1].strip() and \
            re.fullmatch(r"(\s*#[\w\u00C0-\u024F\u1E00-\u1EFF]+\s*)+", body_lines[-1].strip()):
        trailing.insert(0, body_lines.pop())
    body = "\n".join(body_lines).rstrip()
    changed = False
    # CTA untuk long
    if fmt == "long":
        low = body.lower()
        if not any(w in low for w in ("subscribe", "berlangganan", "langganan")):
            body = body + CTA[slug in ID_LANG]
            changed = True
        # blok hashtag 3-5 termasuk #foryou
        niche = NICHE_TAGS.get(slug, ["#viral", "#trending"])[:3]
        block = " ".join(["#foryou"] + [t for t in niche if t.lower() != "#foryou"][:3])
        new_desc = body + "\n\n" + block
        if new_desc != desc:
            changed = True
        return new_desc, changed
    return desc, changed

plan = []
for d in targets:
    slug, vid, fmt = d["slug"], d["id"], d["format"]
    new_title = fix_title(slug, d["api_title"], fmt)
    # hanya perbaiki judul shorts bila ada cacat hashtag nyata
    msgs = " ".join(t["pesan"] for t in d["seo_temuan"])
    title_hashtag_issue = ("Hashtag terakhir judul" in msgs or "tanpa hashtag di judul" in msgs
                           or (fmt == "long" and "hashtag di judul" in msgs))
    if not title_hashtag_issue:
        new_title = None
    new_desc, desc_changed = fix_description(slug, d["api_description"], fmt, [])
    tags = d.get("api_tags") or []
    total_chars = sum(len(t) for t in tags) + len(tags)
    new_tags = None
    if not tags or total_chars < 300:
        new_tags = build_tags(slug, d["api_title"], NICHE_TAGS.get(slug, ["#viral"]))
    entry = {"slug": slug, "video_id": vid, "format": fmt,
             "views": d["views"], "seo_skor": d["seo_skor"],
             "judul_lama": d["api_title"],
             "judul_baru": new_title,
             "deskripsi_berubah": desc_changed,
             "tags_lama_n": len(tags), "tags_baru_n": len(new_tags) if new_tags else len(tags)}
    if new_title:
        entry["judul_baru_full"] = new_title
    if desc_changed:
        entry["deskripsi_baru_tail"] = new_desc[-300:]
    if new_tags:
        entry["tags_baru"] = new_tags
    entry["_new_snippet"] = {"title": new_title or d["api_title"],
                             "description": new_desc,
                             "tags": new_tags if new_tags else tags}
    if new_title or desc_changed or new_tags:
        plan.append(entry)

json.dump([{k: v for k, v in e.items() if k != "_new_snippet"} for e in plan],
          open(HERE / "hidden_files" / "perbaikan-sepi-2026-10-17-plan.json", "w"),
          ensure_ascii=False, indent=1)
print(f"rencana: {len(plan)} video akan diubah "
      f"(judul: {sum(1 for e in plan if e['judul_baru'])}, "
      f"deskripsi: {sum(1 for e in plan if e['deskripsi_berubah'])}, "
      f"tags: {sum(1 for e in plan if e.get('tags_baru'))})", flush=True)

if not APPLY:
    print("[DRY-RUN] tambah --apply untuk eksekusi.", flush=True)
    sys.exit(0)

ok, gagal = 0, []
for e in plan:
    slug, vid = e["slug"], e["video_id"]
    try:
        cur = yt_get(slug, "/videos", {"id": vid, "part": "snippet"}).get("items", [])
        if not cur:
            gagal.append((vid, "tidak ditemukan")); continue
        sn = cur[0]["snippet"]
        ns = e["_new_snippet"]
        body_snippet = {"title": ns["title"][:100], "description": ns["description"],
                        "tags": ns["tags"], "categoryId": sn["categoryId"]}
        for k in ("defaultLanguage", "defaultAudioLanguage"):
            if sn.get(k):
                body_snippet[k] = sn[k]
        yt_put(slug, "/videos", {"part": "snippet"},
               {"id": vid, "snippet": body_snippet})
        ok += 1
        print(f"OK {slug} {vid}", flush=True)
    except Exception as ex:
        gagal.append((vid, str(ex)[:150]))
        print(f"GAGAL {slug} {vid}: {str(ex)[:120]}", flush=True)

print(f"\nSELESAI: {ok} berhasil, {len(gagal)} gagal")
json.dump({"ok": ok, "gagal": gagal},
          open(HERE / "hidden_files" / "perbaikan-sepi-2026-10-17-hasil.json", "w"),
          ensure_ascii=False, indent=1)
