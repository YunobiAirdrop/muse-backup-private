#!/usr/bin/env python3
"""Perbaiki metadata 3 video mentok-baru skor<90 (malam 2026-10-19).
Hanya sentuh cacat nyata (FAIL/WARN): hashtag judul, CTA deskripsi,
blok hashtag, tags. Judul inti TIDAK diubah. Link/atribusi dipertahankan.
Pakai: perbaiki_malam_191019.py [--apply]
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from auth import yt_get, yt_put

APPLY = "--apply" in sys.argv
HF = HERE / "hidden_files"

CTA_ID = ("\n\nJangan lupa SUBSCRIBE dan nyalakan loncengnya "
          "agar tidak ketinggalan video terbaru! 🔔")

diag = {d["id"]: d for d in
        json.load(open(HF / "diagnosis-2026-10-19-malam.json"))}

def plan_entry(slug, vid, new_title=None, new_desc=None, new_tags=None,
               catatan=""):
    d = diag[vid]
    old_tags = d.get("api_tags") or []
    entry = {
        "slug": slug, "video_id": vid, "format": d["format"],
        "views": d["views"], "seo_skor": d["seo_skor"],
        "judul_lama": d["api_title"], "judul_baru": new_title,
        "deskripsi_berubah": new_desc is not None,
        "tags_lama_n": len(old_tags),
        "tags_baru_n": len(new_tags) if new_tags is not None else len(old_tags),
        "catatan": catatan,
        "_new": {"title": new_title or d["api_title"],
                 "description": new_desc if new_desc is not None else d["api_description"],
                 "tags": new_tags if new_tags is not None else old_tags},
    }
    return entry

plan = []

# --- 1. jejakbuddha 0xG5W7rbDt4 (long): hashtag keluar dari judul, +CTA, +tags
d = diag["0xG5W7rbDt4"]
t1 = "Bayinya Meninggal, Buddha Malah Memberi Tugas Mustahil"
desc1 = d["api_description"].replace(
    "\n#buddha #jejakbuddha #foryou",
    CTA_ID + "\n\n#butifyourcloseyoureyesmeme #foryou #buddha #buddhism #inspirasi")
assert desc1 != d["api_description"], "pola hashtag jejakbuddha tidak ketemu"
tags1 = ["kisah buddha", "buddha", "kisah inspiratif", "duka cita", "kehilangan",
         "ajaran buddha", "buddhism", "kisah teladan", "motivasi hidup",
         "renungan", "spiritual", "kisah nyata", "inspirasi", "jejak buddha",
         "pengertian"]
assert sum(len(t) for t in tags1) + len(tags1) <= 500
plan.append(plan_entry("jejakbuddha", "0xG5W7rbDt4", new_title=t1,
                       new_desc=desc1, new_tags=tags1,
                       catatan="judul: hashtag keluar (aturan long); desc +CTA ID + blok 5 hashtag; tags 0->15"))

# --- 2. mind-en w_riNbyiOW8 (shorts): hashtag judul diakhiri #foryou, +tags
d = diag["w_riNbyiOW8"]
t2 = ("Scientists Planted Fake Memories in Strangers "
      "#butifyourcloseyoureyesmeme #shorts #psychology #mindset #foryou")
desc2 = d["api_description"].replace(
    "#psychology #darkpsychology #mindblown #brainfacts #shorts",
    "#butifyourcloseyoureyesmeme #psychology #darkpsychology #mindblown #foryou")
assert desc2 != d["api_description"], "pola hashtag mind-en tidak ketemu"
tags2 = ["fake memories", "false memory", "elizabeth loftus", "memory experiment",
         "psychology facts", "dark psychology", "brain facts", "mind tricks",
         "psychology", "memory manipulation"]
assert sum(len(t) for t in tags2) + len(tags2) <= 500
plan.append(plan_entry("mind-en", "w_riNbyiOW8", new_title=t2,
                       new_desc=desc2, new_tags=tags2,
                       catatan="judul: 5 hashtag diakhiri #foryou; desc hashtag dinormalisasi; tags 0->10"))

# --- 3. jejakislami uIGWlXfMQJ4 (shorts): +5 hashtag judul, +CTA, hashtag desc
#     CATATAN: duplikat persis 2 video yg kini private — TIDAK di-private agar
#     topik tetap punya 1 copy publik; hanya metadata diperbaiki.
d = diag["uIGWlXfMQJ4"]
t3 = ("Dibakar Hidup-Hidup, Api Justru Menjadi Dingin "
      "#butifyourcloseyoureyesmeme #shorts #islami #kisahislami #foryou")
old_block = ("#foryou #kisahislami #nabiibrahim #kisahnabi #mukjizat #alquran "
             "#sejarahislam #dakwah #islam #tawakal")
new_block = ("#butifyourcloseyoureyesmeme #foryou #kisahislami #nabiibrahim "
             "#kisahnabi #mukjizat #alquran #sejarahislam #dakwah #islam #tawakal")
desc3 = d["api_description"].replace(old_block, CTA_ID + "\n\n" + new_block)
assert desc3 != d["api_description"], "pola hashtag jejakislami tidak ketemu"
plan.append(plan_entry("jejakislami", "uIGWlXfMQJ4", new_title=t3,
                       new_desc=desc3, new_tags=None,
                       catatan="judul +5 hashtag; desc +CTA ID + #butifyourcloseyoureyesmeme; tags sudah bagus (13) tidak diubah; TIDAK di-private (duplikatnya sudah private, copy publik ini dipertahankan)"))

json.dump([{k: v for k, v in e.items() if k != "_new"} for e in plan],
          open(HF / "perbaikan-sepi-2026-10-19-malam-plan.json", "w"),
          ensure_ascii=False, indent=1)
print(f"rencana: {len(plan)} video "
      f"(judul: {sum(1 for e in plan if e['judul_baru'])}, "
      f"deskripsi: {sum(1 for e in plan if e['deskripsi_berubah'])}, "
      f"tags: {sum(1 for e in plan if e['tags_baru_n'] > e['tags_lama_n'])})")
for e in plan:
    print(f"- {e['slug']} {e['video_id']}: {e['catatan']}")

if not APPLY:
    print("[DRY-RUN] tambah --apply untuk eksekusi.")
    sys.exit(0)

ok, gagal = 0, []
readback = {}
for e in plan:
    slug, vid = e["slug"], e["video_id"]
    try:
        cur = yt_get(slug, "/videos", {"id": vid, "part": "snippet"}).get("items", [])
        if not cur:
            gagal.append((vid, "tidak ditemukan"))
            continue
        sn = cur[0]["snippet"]
        ns = e["_new"]
        body = {"title": ns["title"][:100], "description": ns["description"],
                "tags": ns["tags"], "categoryId": sn["categoryId"]}
        for k in ("defaultLanguage", "defaultAudioLanguage"):
            if sn.get(k):
                body[k] = sn[k]
        yt_put(slug, "/videos", {"part": "snippet"},
               {"id": vid, "snippet": body})
        # read-back
        rb = yt_get(slug, "/videos", {"id": vid, "part": "snippet"}).get("items", [])[0]["snippet"]
        readback[vid] = {
            "judul_cocok": rb["title"] == ns["title"][:100],
            "deskripsi_cocok": rb.get("description", "") == ns["description"],
            "tags_cocok": sorted(rb.get("tags", [])) == sorted(ns["tags"]),
        }
        ok += 1
        print(f"OK {slug} {vid} readback={readback[vid]}", flush=True)
    except Exception as ex:
        gagal.append((vid, str(ex)[:150]))
        print(f"GAGAL {slug} {vid}: {str(ex)[:120]}", flush=True)

print(f"\nSELESAI: {ok} berhasil, {len(gagal)} gagal")
json.dump({"ok": ok, "gagal": gagal, "readback": readback},
          open(HF / "perbaikan-sepi-2026-10-19-malam-hasil.json", "w"),
          ensure_ascii=False, indent=1)
