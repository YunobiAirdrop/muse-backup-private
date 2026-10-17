#!/usr/bin/env python3
"""Sisipkan 1-2 embed video YouTube MILIK SENDIRI yang relevan ke artikel blog.

Tujuan: pembaca blog -> penonton video (trafik organik legit, bukan trik).

Dipakai dari posting_web.py SETELAH rakit_body (lihat embed_video.patch):
    from embed_video import sisipkan_embed
    html = sisipkan_embed(html, art, blog_slug)

Cara kerja:
1. Baca embed_video_config.json -> daftar channel kandidat per blog.
2. Ambil daftar video publik dari cache lokal data/video_cache/<slug>.json
   (dibangun via yt-growth/video_cache_builder.py; refresh otomatis bila
   cache lebih tua dari 7 hari).
3. Skor relevansi: cocokkan keyword (judul+label+meta+isi artikel) vs
   judul video (bobot 3x) + deskripsi video (bobot 1x). Min skor 3.
4. Urutkan: skor tertinggi dulu; seri -> views TERENDAH dulu (video sepi
   yang butuh dorongan diprioritaskan, tapi tetap relevan).
5. Aturan variasi: 1 video maks dipakai 3x dalam 7 hari (embed_history.json).
6. Sisipkan blok embed responsif + kalimat ajakan setelah paragraf pertama.

Hanya stdlib. Gagal di titik mana pun -> kembalikan HTML apa adanya
(tidak merusak pipeline).
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE, "embed_video_config.json")
CACHE_DIR = os.path.join(BASE, "data", "video_cache")
HISTORY = os.path.join(BASE, "data", "embed_history.json")
BUILDER_PY = "/home/hatch/workspace/youtube-otomatis/yt-growth/venv/bin/python"
BUILDER_SCRIPT = ("/home/hatch/workspace/youtube-otomatis/yt-growth/"
                  "video_cache_builder.py")

CACHE_TTL_HARI = 7
MAX_EMBED_PER_ARTIKEL = 2
MAX_PAKAI_PER_MINGGU = 3
SKOR_MIN = 6  # ~ butuh >=2 kata-kunci judul yang cocok (anti asal tempel)

STOPWORDS = set("""
the a an and or but of to in on for with at by from as is are was were be been
has have had do does did will would can could should shall may might must
this that these those it its you your he she they their we our i my me him
her us what which who whom when where how why not no yes if then than so such
into out about over under between through during before after more most some
any all each other one two three new first top best video videos watch full
part episode vs via per day days today now here there very just like get got
yang dan di ke dari dengan untuk pada adalah ini itu sebagai dalam tidak ada
akan atau juga dapat bisa oleh karena jika serta para sangat lebih kurang
sudah telah sedang saat hingga sampai antara agar supaya bahwa namun tetapi
melalui terhadap atas bawah setiap semua beberapa tahun hari orang cara hal
kita anda kamu mereka dia saya kami baru tonton juga film sebuah inilah itulah
tak tanpa tapi versi bagi demi sambil tengah sekitar
hanya hampir masih tetap cukup amat paling terlalu justru memang bahkan lagi
pun saja kali seperti bagai bagaikan yakni yaitu ialah merupakan tersebut
berbagai seluruh keseluruhan masing tiap jangan
also even ever never always often really much many own same last next every
youtube channel subscribe like comment share shorts hashtag hashtags
""".split())

# Jembatan kata ID -> EN agar artikel Indonesia bisa cocok dengan video
# channel berbahasa Inggris (strangetales, weird-en, space-en, dsb).
ID_EN_BRIDGE = {
    "gerhana": "eclipse", "matahari": "sun", "bulan": "moon", "bintang": "star",
    "angkasa": "space", "luar": "space", "planet": "planet", "bumi": "earth",
    "hantu": "ghost", "misteri": "mystery", "misterius": "mysterious",
    "aneh": "strange", "pembunuhan": "murder", "pembunuh": "killer",
    "pesawat": "plane", "kapal": "ship", "laut": "sea", "samudra": "ocean",
    "gunung": "mountain", "berapi": "volcano", "hutan": "forest",
    "gurun": "desert", "gua": "cave", "sungai": "river", "danau": "lake",
    "uang": "money", "kaya": "rich", "miskin": "poor", "bisnis": "business",
    "ekonomi": "economy", "investasi": "investment", "teknologi": "technology",
    "komputer": "computer", "internet": "internet", "robot": "robot",
    "kesehatan": "health", "penyakit": "disease", "obat": "medicine",
    "dokter": "doctor", "sejarah": "history", "perang": "war",
    "kerajaan": "kingdom", "kekaisaran": "empire", "kuno": "ancient",
    "hewan": "animal", "anjing": "dog", "kucing": "cat", "burung": "bird",
    "ikan": "fish", "ular": "snake", "mobil": "car", "motor": "motorcycle",
    "truk": "truck", "kereta": "train", "makanan": "food", "minuman": "drink",
    "wisata": "travel", "pantai": "beach", "kota": "city", "desa": "village",
    "olahraga": "sport", "sepakbola": "football", "bola": "ball",
    "pendidikan": "education", "sekolah": "school", "guru": "teacher",
    "siswa": "student", "agama": "religion", "doa": "prayer", "nabi": "prophet",
    "malaikat": "angel", "surga": "heaven", "neraka": "hell",
    "kecelakaan": "accident", "bencana": "disaster", "gempa": "earthquake",
    "banjir": "flood", "kebakaran": "fire", "hilang": "missing",
    "penemuan": "discovery", "ditemukan": "discovered", "rahasia": "secret",
    "kutukan": "curse", "alien": "alien", "ufo": "ufo",
    "dinosaurus": "dinosaur", "fosil": "fossil",
}


def _tokenize(teks):
    toks = re.findall(r"[a-z0-9]{3,}", (teks or "").lower())
    return set(t for t in toks if t not in STOPWORDS)


def _teks_artikel(art):
    bagian = [art.get("judul", ""), art.get("meta_deskripsi", ""),
              " ".join(art.get("label", []) or [])]
    html = art.get("artikel_html", "") or ""
    teks = re.sub(r"<[^>]+>", " ", html)
    bagian.append(teks[:2000])
    return " ".join(bagian)


def blog_channels(blog_slug):
    try:
        cfg = json.load(open(CONFIG))
        return cfg.get(blog_slug, [])
    except Exception:
        return []


def pastikan_cache(slug):
    """Pastikan cache ada & segar; refresh via builder bila perlu."""
    p = os.path.join(CACHE_DIR, f"{slug}.json")
    perlu = True
    if os.path.exists(p):
        try:
            d = json.load(open(p))
            umur = (datetime.now(timezone.utc) -
                    datetime.fromisoformat(d["fetched_at"])).days
            perlu = umur > CACHE_TTL_HARI
        except Exception:
            perlu = True
    if perlu:
        try:
            subprocess.run([BUILDER_PY, BUILDER_SCRIPT, slug],
                           timeout=180, capture_output=True, check=False)
        except Exception:
            pass  # gagal refresh -> pakai cache lama / lewati
    if os.path.exists(p):
        try:
            return json.load(open(p)).get("videos", [])
        except Exception:
            return []
    return []


def _riwayat():
    try:
        return json.load(open(HISTORY))
    except Exception:
        return {}


def _simpan_riwayat(pemakaian):
    hist = _riwayat()
    now = datetime.now(timezone.utc).isoformat()
    for vid in pemakaian:
        hist.setdefault(vid, []).append(now)
    # pangkas entri >30 hari agar file tidak membengkak
    batas = datetime.now(timezone.utc) - timedelta(days=30)
    for vid in list(hist):
        hist[vid] = [t for t in hist[vid]
                     if datetime.fromisoformat(t) > batas]
        if not hist[vid]:
            del hist[vid]
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    json.dump(hist, open(HISTORY, "w"), ensure_ascii=False)


def _boleh_pakai(vid):
    hist = _riwayat()
    seminggu = datetime.now(timezone.utc) - timedelta(days=7)
    pakai = [t for t in hist.get(vid, [])
             if datetime.fromisoformat(t) > seminggu]
    return len(pakai) < MAX_PAKAI_PER_MINGGU


def _skor(video, kw):
    tj = _tokenize(video.get("title", ""))
    dj = _tokenize(video.get("desc", ""))
    return 3 * len(kw & tj) + 1 * len(kw & dj)


def pilih_video(blog_slug, artikel, n=MAX_EMBED_PER_ARTIKEL):
    """Kembalikan list dict video terpilih (maks n), atau []."""
    kw = _tokenize(_teks_artikel(artikel))
    # Jembatan ID->EN: artikel Indonesia bisa cocok ke video berbahasa Inggris
    kw |= {ID_EN_BRIDGE[t] for t in kw if t in ID_EN_BRIDGE}
    if not kw:
        return []
    kandidat = []
    for slug in blog_channels(blog_slug):
        for v in pastikan_cache(slug):
            s = _skor(v, kw)
            if s < SKOR_MIN:
                continue
            if not _boleh_pakai(v["id"]):
                continue
            kandidat.append((s, v.get("views", 0), v.get("published", ""), v))
    # urut: skor tertinggi dulu; seri -> views TERENDAH dulu (video sepi
    # diprioritaskan); seri lagi -> yang terbaru dulu. Sort stabil bertahap.
    kandidat.sort(key=lambda x: x[2], reverse=True)  # published desc
    kandidat.sort(key=lambda x: x[1])               # views asc
    kandidat.sort(key=lambda x: -x[0])               # skor desc
    terpilih, dipakai = [], set()
    for s, views, pub, v in kandidat:
        if v["id"] in dipakai:
            continue
        dipakai.add(v["id"])
        terpilih.append(v)
        if len(terpilih) >= n:
            break
    return terpilih


def blok_embed_html(video, channel_nama=""):
    vid = video["id"]
    judul = video.get("title", "").replace('"', "&quot;")
    url = f"https://www.youtube.com/watch?v={vid}"
    return (
        '<div style="margin:20px 0;padding:16px;background:#f8fafc;'
        'border:1px solid #e2e8f0;border-radius:12px;">\n'
        f'<p style="margin:0 0 10px;font-weight:bold;">🎬 Tonton juga: '
        f'<a href="{url}" target="_blank" rel="noopener">{judul}</a>'
        f'{(" — video dari channel " + channel_nama) if channel_nama else ""}</p>\n'
        '<div style="position:relative;padding-bottom:56.25%;height:0;'
        'overflow:hidden;border-radius:8px;">\n'
        f'<iframe src="https://www.youtube.com/embed/{vid}" '
        'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
        f'allowfullscreen loading="lazy" title="{judul}"></iframe>\n'
        '</div>\n</div>'
    )


def sisipkan_embed(html, artikel, blog_slug):
    """Titik integrasi utama. Kembalikan html (+embed) atau html asli bila gagal."""
    try:
        terpilih = pilih_video(blog_slug, artikel)
        if not terpilih:
            return html
        blok = "\n".join(blok_embed_html(v) for v in terpilih)
        # Sisip setelah paragraf teks pertama yang cukup panjang
        # (lewati paragraf gambar pembuka).
        sisip = None
        for m in re.finditer(r"<p>.*?</p>", html, re.DOTALL):
            teks = re.sub(r"<[^>]+>", "", m.group(0)).strip()
            if len(teks) > 80:
                sisip = m.end()
                break
        if sisip is None:  # fallback: setelah </p> pertama
            i = html.find("</p>")
            sisip = i + 4 if i != -1 else len(html)
        html = html[:sisip] + "\n" + blok + "\n" + html[sisip:]
        _simpan_riwayat([v["id"] for v in terpilih])
        return html
    except Exception as e:
        print(f"embed_video dilewati: {e}", file=sys.stderr)
        return html


if __name__ == "__main__":
    # Uji cepat: python3 embed_video.py --blog <slug>
    # pakai artikel pertama dari data/artikel-<slug>.json
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--blog", required=True)
    ap.add_argument("--n", type=int, default=MAX_EMBED_PER_ARTIKEL)
    a = ap.parse_args()
    art_path = os.path.join(BASE, "data", f"artikel-{a.blog}.json")
    arts = json.load(open(art_path))
    art = next((x for x in arts
                if x.get("judul", "").strip() not in ("", "...")), None)
    if not art:
        print("tidak ada artikel valid"); sys.exit(1)
    print("ARTIKEL:", art["judul"])
    print("LABEL:", art.get("label"))
    vids = pilih_video(a.blog, art, n=a.n)
    for v in vids:
        print(f"- [{v['id']}] {v['views']} views | {v['title'][:90]}")
    if vids:
        # Catatan: TIDAK memanggil sisipkan_embed di sini agar uji coba
        # tidak mencatat ke embed_history.json
        print("\nCONTOH BLOK HTML (400 char pertama):")
        print(blok_embed_html(vids[0])[:400], "...")
