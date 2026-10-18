#!/usr/bin/env python3
"""Audit SEO/discoverability metadata video — pola DarkzSEO preflight dari AgentTube.

Dua mode:
  python seo_audit.py file METADATA.json [--format shorts|long]
      Audit paket metadata SEBELUM upload (dipakai produksi sebagai preflight).
      JSON berisi: title, description, tags (list), format (shorts|long).
  python seo_audit.py video SLUG VIDEO_ID
      Audit video yang sudah tayang (judul/deskripsi/tags/durasi asli dari API).

Aturan diambil dari protokol-viral.md (bagian 3, 14, 17) + packaging-formulas.md:
  SHORTS: hashtag di AKHIR judul, maks 4, terakhir WAJIB #foryou; judul inti 40-60 krk.
  LONG  : #foryou WAJIB di hashtag deskripsi; deskripsi 6 bagian (hook 150 char
          keyword-rich -> konteks -> chapters -> CTA subscribe -> link terkait
          -> 3-5 hashtag); kata kunci di 100 karakter pertama deskripsi.
  UMUM  : total tags <= 500 karakter (batas YouTube), judul tanpa kata terlarang.

Output: skor 0-100 + daftar PASS/WARN/FAIL. Exit code 1 bila ada FAIL.
"""
import argparse
import json
import re
import sys

HASHTAG_RE = re.compile(r"#[\w\u00C0-\u024F\u1E00-\u1EFF]+")
CTA_WORDS = ("subscribe", "berlangganan", "langganan", "ikuti channel", "follow untuk")
CHAPTER_RE = re.compile(r"\b\d{1,2}:\d{2}\b")


def hashtags(text):
    return HASHTAG_RE.findall(text or "")


def audit(meta, fmt):
    """meta: {title, description, tags}; fmt: 'shorts'|'long'. Return (skor, temuan)."""
    title = meta.get("title", "") or ""
    desc = meta.get("description", "") or ""
    tags = meta.get("tags", []) or []
    findings = []  # (level, pesan) level: PASS/WARN/FAIL

    title_tags = hashtags(title)
    desc_tags = hashtags(desc)
    title_core = HASHTAG_RE.sub("", title).strip()

    # --- Judul ---
    if 40 <= len(title_core) <= 60:
        findings.append(("PASS", f"Judul inti {len(title_core)} karakter (ideal 40-60)."))
    elif len(title_core) < 40:
        findings.append(("WARN", f"Judul inti pendek ({len(title_core)} krk) — ideal 40-60."))
    else:
        findings.append(("WARN", f"Judul inti panjang ({len(title_core)} krk) — ideal 40-60, risiko terpotong di HP."))
    if not title_core:
        findings.append(("FAIL", "Judul kosong."))
    if title_core.isupper() and len(title_core) > 10:
        findings.append(("WARN", "Judul full kapital — terkesan spam, turunkan."))

    if fmt == "shorts":
        # --- Shorts: hashtag di akhir judul ---
        if not title_tags:
            findings.append(("FAIL", "SHORTS tanpa hashtag di judul — wajib diakhiri hashtag (maks 5: #butifyourcloseyoureyesmeme + 3 trending + #foryou, terakhir #foryou)."))
        else:
            if len(title_tags) > 5:
                findings.append(("FAIL", f"Hashtag judul {len(title_tags)} — maksimal 5."))
            else:
                findings.append(("PASS", f"Hashtag judul {len(title_tags)} (<=5)."))
            if title_tags[-1].lower() != "#foryou":
                findings.append(("FAIL", f"Hashtag terakhir judul '{title_tags[-1]}' — WAJIB #foryou (perintah user 2026-10-12)."))
            else:
                findings.append(("PASS", "Hashtag terakhir judul #foryou."))
            tail = title.rstrip()
            if not HASHTAG_RE.search(tail.split()[-1] if tail.split() else ""):
                findings.append(("WARN", "Hashtag tidak menutup judul — pastikan komposisi hashtag di paling akhir."))
    else:
        # --- Long: hashtag di deskripsi ---
        if title_tags:
            findings.append(("WARN", "LONG punya hashtag di judul — aturan kita: hashtag long di deskripsi."))
        if not desc_tags:
            findings.append(("FAIL", "LONG tanpa hashtag di deskripsi — wajib 3-5 hashtag termasuk #foryou."))
        else:
            if "#foryou" not in [t.lower() for t in desc_tags]:
                findings.append(("FAIL", "Hashtag deskripsi TANPA #foryou — wajib ada (perintah user 2026-10-12)."))
            else:
                findings.append(("PASS", "#foryou ada di hashtag deskripsi."))
            if not (3 <= len(desc_tags) <= 5):
                findings.append(("WARN", f"Hashtag deskripsi {len(desc_tags)} — template 3-5."))
        # Template 6 bagian (cek kasar)
        if len(desc) < 300:
            findings.append(("WARN", f"Deskripsi pendek ({len(desc)} krk) — template 6 bagian butuh konteks mini-blog."))
        if not CHAPTER_RE.search(desc):
            findings.append(("WARN", "Tidak ada chapters (timestamp 0:00) di deskripsi long."))
        if not any(w in desc.lower() for w in CTA_WORDS):
            findings.append(("FAIL", "Deskripsi long tanpa CTA subscribe — bagian 4 template wajib ada."))
        else:
            findings.append(("PASS", "CTA subscribe ada di deskripsi."))

    # --- Umum ---
    tag_chars = sum(len(t) for t in tags) + max(0, len(tags) - 1)
    if tags:
        if tag_chars > 500:
            findings.append(("FAIL", f"Total tags {tag_chars} karakter — batas YouTube 500."))
        elif tag_chars < 100:
            findings.append(("WARN", f"Total tags cuma {tag_chars} karakter — manfaatkan ruang tag (target 300-500)."))
        else:
            findings.append(("PASS", f"Total tags {tag_chars} karakter (<=500)."))
    else:
        findings.append(("WARN", "Tanpa tags sama sekali."))

    score = 100 - 15 * sum(1 for lv, _ in findings if lv == "FAIL") \
              - 5 * sum(1 for lv, _ in findings if lv == "WARN")
    return max(0, score), findings


def render(fmt_label, score, findings):
    print(f"== Audit {fmt_label} — skor {score}/100 ==")
    for lv, msg in findings:
        print(f"[{lv}] {msg}")
    return 1 if any(lv == "FAIL" for lv, _ in findings) else 0


def parse_duration(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    pf = sub.add_parser("file")
    pf.add_argument("path")
    pf.add_argument("--format", choices=["shorts", "long"], default=None)

    pv = sub.add_parser("video")
    pv.add_argument("slug")
    pv.add_argument("video_id")

    a = ap.parse_args()

    if a.mode == "file":
        meta = json.loads(open(a.path).read())
        fmt = a.format or meta.get("format", "long")
        score, findings = audit(meta, fmt)
        sys.exit(render(f"file {a.path} ({fmt})", score, findings))
    else:
        from auth import yt_get
        items = yt_get(a.slug, "/videos", {
            "id": a.video_id, "part": "snippet,contentDetails"}).get("items", [])
        if not items:
            sys.exit("Video tidak ditemukan.")
        it = items[0]
        sn = it["snippet"]
        dur = parse_duration(it.get("contentDetails", {}).get("duration", ""))
        fmt = "shorts" if dur <= 61 else "long"
        meta = {"title": sn["title"], "description": sn.get("description", ""),
                "tags": sn.get("tags", [])}
        score, findings = audit(meta, fmt)
        print(f"Video {a.video_id} ({a.slug}) durasi {dur}s -> format {fmt}")
        sys.exit(render("video live", score, findings))


if __name__ == "__main__":
    main()
