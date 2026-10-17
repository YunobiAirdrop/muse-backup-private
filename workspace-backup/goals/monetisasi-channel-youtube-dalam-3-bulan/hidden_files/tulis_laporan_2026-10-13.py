#!/usr/bin/env python3
"""Tulis audit-2026-10-13.md (daftar koreksi browser) + scoreboard.md."""
import json
from datetime import date
from pathlib import Path

HOME = Path.home()
HF = HOME / "workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/hidden_files"
AUD = HF / "audit-2026-10-13"
d = json.load(open(AUD / "_diagnosis.json"))["channels"]

# ---------- audit-YYYY-MM-DD.md : koreksi yang butuh browser ----------
lines = [f"# Audit channel 3-harian — {date.today().isoformat()}",
         "",
         "Koreksi OTOMATIS yang sudah diterapkan run ini (via API):",
         "- 19 video flop di-re-title ikut formula packaging + deskripsi/hashtag diperbaiki",
         "  (6 shorts dapat #foryou, 2 shorts horror-en dapat tags baru).",
         "- 9 video flop tanpa playlist dimasukkan ke playlist funnel tematik.",
         "- Log: `corrections-apply.log`, `playlists-apply.log`.",
         "",
         "## Koreksi yang BUTUH BROWSER (tidak bisa via API)",
         "",
         "### A. Perbaiki 15 detik pertama via YouTube Studio Editor (retensi <40%)",
         "Prioritas = video dengan views lumayan tapi retensi bocor (judl sudah diperbaiki,",
         "yang bocor tinggal hook/15 detik pertama):",
         ""]
for slug in ["horor", "tinybuilders", "lima-misteri", "mystery-en", "jejakislami",
             "mind-en", "space-en", "youtube-pov", "empires-en"]:
    c = d[slug]
    bad = [f for f in c["flop3"] if (f["ret"] or 100) < 40]
    if not bad:
        continue
    lines.append(f"**{slug}** ({c['handle']})")
    for f in bad:
        lines.append(f"- https://youtu.be/{f['id']} — retensi {f['ret']}%, "
                     f"{f['views']} views/28d — \"{(f['title'] or '')[:70]}\"")
    lines.append("")

lines += [
    "### B. Ganti thumbnail / Test & Compare",
    "Video flop 0-3 views (judul baru sudah dipasang; thumbnail adalah gerbang 'clicked'):",
    ""]
for slug in ["empires-en", "history-en", "horror-en", "mystery-en", "truecrime-en",
             "weird-en", "strangetales", "jejakislami"]:
    c = d[slug]
    zero = [f for f in c["flop3"] if (f["views"] or 0) <= 3]
    if not zero:
        continue
    lines.append(f"**{slug}** ({c['handle']})")
    for f in zero:
        lines.append(f"- https://youtu.be/{f['id']} — \"{(f['title'] or '')[:70]}\"")
    lines.append("")

lines += [
    "### C. Channel 0 views lifetime (video baru 1-2 hari, belum bisa dinilai)",
    "- @JejakBuddha, @KisahAlkitab-k9j, @KisahDharma: 8-9 video publik, 0 views — "
    "video baru tayang 12-13 Okt. Pantau di audit berikutnya; bila tetap 0 setelah 7 hari, "
    "cek distribusi (apakah masuk rekomendasi/penelusuran).",
    "- @InkTime-d3t, @MacamMacamID: tanpa token Analytics (Data API saja via token lima-misteri).",
    "",
    "### D. Komentar & CTA",
    "- Aturan tetap: komentar ON di semua video, CTA subscribe verbal + overlay 50% & akhir.",
    "- Audit komentar terakhir: 2026-10-10 bersih (4 video @ceritarakyat862 sudah dinyalakan).",
]
(HF / f"audit-{date.today().isoformat()}.md").write_text("\n".join(lines), encoding="utf-8")

# ---------- scoreboard.md ----------
sb = ["# Papan Skor Monetisasi — update " + date.today().isoformat(),
      "",
      "Ambang jalur cepat: **500 subs** + **3.000 jam tayang/12 bln** ATAU **3 jt views Shorts/90 hari**.",
      "Kolom jam = jam tayang 28 hari terakhir (API); % jam = ekstrapolasi kasar ×13 ke 12 bulan.",
      "",
      "| Channel | Subs | % ke 500 | Jam/28d | % ke 3.000 jam* | Shorts 90d (est) | % ke 3 jt | Views 28d |",
      "|---|---|---|---|---|---|---|---|"]
for slug, c in sorted(d.items(), key=lambda kv: -kv[1]["subs"]):
    sb.append(f"| {c['handle']} | {c['subs']} | {c['subs_pct']}% | {c['wh28']} | "
              f"{c['wh_pct']}% | ~{int(c['v28']*3.2):,} | {c['shorts_pct']}% | {c['v28']:,} |")
sb += ["",
       "\\* Ekstrapolasi kasar: laju 28 hari × 13. Angka jam 12-bulan sebenarnya perlu riwayat penuh.",
       "",
       "## Perubahan vs kemarin (2026-10-12)",
       ""]
movers = sorted(((c["dsubs"] or 0), slug, c) for slug, c in d.items() if c["dsubs"] is not None)
movers.sort(reverse=True)
for ds, slug, c in movers[:5]:
    sb.append(f"- {c['handle']}: {c['subs']} subs ({'+' if ds >= 0 else ''}{ds})")
sb.append("")
sb.append("## Koreksi run ini")
sb.append("- 19 re-title + perbaikan deskripsi/hashtag (detail: `audit-2026-10-13.md`)")
sb.append("- 9 video masuk playlist funnel")
(HF / "scoreboard.md").write_text("\n".join(sb), encoding="utf-8")
print("ditulis:", HF / f"audit-{date.today().isoformat()}.md", "dan scoreboard.md")
