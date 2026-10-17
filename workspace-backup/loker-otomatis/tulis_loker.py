#!/usr/bin/env python3
"""Tulis ulang antrean loker jadi artikel pendek orisinal Bahasa Indonesia.

Format antrean: data/antrean-loker.json [{judul_asli, link, ringkasan, sumber, tanggal}]
Output: data/artikel-loker.json (format sama seperti tulis_ulang.py blog-otomatis,
siap dirakit posting_web.py).

Reuse infra OpenRouter (key rotation + model list) dari blog-otomatis/tulis_ulang.py.
PENTING: model hanya diberi judul+sumber berita; ia DILARANG mengarang detail
spesifik (tanggal deadline pasti, link pendaftaran, nominal gaji) — yang tidak
diketahui ditulis sebagai anjuran cek sumber resmi.

Pakai: python3 tulis_loker.py [--limit N]
"""
import json, os, re, sys, time, argparse, hashlib
import importlib.util

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)

# --- reuse infra OpenRouter dari blog-otomatis ---
BLOG_BASE = os.path.expanduser("~/workspace/blog-otomatis")
_sav = sys.argv
sys.argv = ["tulis_ulang.py"]  # cegah argparse tulis_ulang baca argumen kita
try:
    spec = importlib.util.spec_from_file_location(
        "tu", os.path.join(BLOG_BASE, "tulis_ulang.py"))
    tu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tu)
finally:
    sys.argv = _sav

PROMPT = """Kamu penulis portal lowongan kerja Indonesia. HARI INI: {tanggal}. Tahun berjalan 2026 — JANGAN PERNAH menulis tahun lain (2024/2025) di judul atau isi.

Tulis artikel PENDEK orisinal Bahasa Indonesia berdasarkan info lowongan berikut:

JUDUL SUMBER: {judul}
SUMBER: {sumber}
TANGGAL BERITA: {tanggal}

Struktur artikel_html (wajib):
<p>paragraf pembuka: posisi apa, perusahaan/instansi apa, dan kenapa menarik.</p>
<h2>Posisi dan Kualifikasi</h2><p>jabarkan posisi yang dibuka dan kualifikasi umum yang biasanya diminta untuk posisi sejenis (pendidikan, pengalaman, skill). Tandai dengan jelas bagian yang merupakan perkiraan umum. Jangan mengarang nama posisi spesifik yang tidak ada di judul sumber.</p>
<h2>Cara Melamar</h2><p>anjurkan pelamar mengecek pengumuman resmi dari {sumber}/instansi terkait; JANGAN membuat link pendaftaran palsu.</p>
<h2>Tips Agar Lolos Seleksi</h2><p>2-3 tips praktis: CV, persiapan tes, riset perusahaan.</p>
<p>Sumber: {sumber}</p>

ATURAN KERAS ANTI-HALUSINASI:
- DILARANG mengarang: tanggal deadline pasti, link pendaftaran, alamat email HRD,
  nominal gaji spesifik, jumlah formasi pasti — kecuali tertulis jelas di JUDUL SUMBER.
- Untuk info yang tidak diketahui, tulis: "Pantau pengumuman resmi dari perusahaan/instansi terkait."
- Tambahkan 1 kalimat peringatan: waspada penipuan berkedok lowongan kerja; proses rekrutmen resmi tidak memungut biaya.

Balas HANYA dengan JSON valid (tanpa markdown):
{{
  "judul": "judul SEO maks 60 karakter, format: 'Lowongan Kerja [Posisi] [Perusahaan] [Tahun]'",
  "slug": "slug-url-tanpa-spasi",
  "meta_deskripsi": "deskripsi maks 160 karakter",
  "label": ["Lowongan Kerja", "Loker Terbaru"],
  "artikel_html": "<p>...</p>...",
  "varian_judul": ["3 alternatif judul SEO lain"],
  "faq_html": "<h2>Pertanyaan Umum</h2><p><strong>Bagaimana cara melamar?</strong><br>Cek pengumuman resmi...</p><p><strong>Apa syarat umumnya?</strong><br>...</p><p><strong>Apakah ada biaya pendaftaran?</strong><br>Tidak. Waspada penipuan...</p>",
  "alt_gambar": "ilustrasi lowongan kerja [posisi] [perusahaan]"
}}

ATURAN GAYA: bahasa lugas DENGAN tanda baca yang benar (titik, koma); DILARANG pola "bukan X, melainkan Y", pertanyaan yang
dijawab sendiri, dan klise AI ("di era digital ini", "penting untuk dicatat").
Maksimal 2 tanda — per artikel. Judul WAJIB memuat tahun 2026 (bukan tahun lain)."""

def tulis_satu(item):
    msg = PROMPT.format(judul=item["judul_asli"], sumber=item["sumber"],
                        tanggal=item.get("tanggal", "3 Oktober 2026"))
    keys = tu.get_api_keys()
    last_err = None
    for key in keys:
        for model in tu.MODELS:
            try:
                import requests
                r = requests.post(tu.ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Loker Otomatis",
                }, json={"model": model,
                         "messages": [{"role": "user", "content": msg}],
                         "temperature": 0.7, "max_tokens": 2000},
                    timeout=120)
                if r.status_code in (429, 503):
                    last_err = f"{model} {r.status_code}"
                    time.sleep(5)
                    continue
                r.raise_for_status()
                obj = tu.parse_router_response(r)
                ch = obj.get("choices") or []
                text = (ch[0].get("message", {}).get("content") if ch else "") or ""
                if not text.strip():
                    raise ValueError("respons kosong")
                if "thinking process" in text.lower():
                    raise ValueError("reasoning leak terdeteksi")
                art = tu.extract_json(text)
                # validasi field wajib
                for f in ("judul", "artikel_html", "faq_html"):
                    if not art.get(f):
                        raise ValueError(f"field {f} kosong")
                art["link_sumber"] = item["link"]
                art["model"] = model
                # perbaiki tahun salah yang kadang dihalusinasikan model
                art["judul"] = re.sub(r"\b202[0-5]\b", "2026", art["judul"])
                art["artikel_html"] = re.sub(r"\b202[0-5]\b", "2026",
                                             art["artikel_html"])
                seed = hashlib.md5(art["judul"].encode()).hexdigest()[:8]
                art["gambar"] = f"https://picsum.photos/seed/loker{seed}/1080/1080"
                return art
            except Exception as e:
                last_err = f"{model}: {str(e)[:80]}"
                time.sleep(3)
    raise RuntimeError(f"semua model/key gagal: {last_err}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    antrean = json.load(open(os.path.join(DATA, "antrean-loker.json")))
    if a.limit:
        antrean = antrean[:a.limit]
    print(f"mulai tulis {len(antrean)} artikel loker")
    hasil = []
    for i, item in enumerate(antrean, 1):
        try:
            art = tulis_satu(item)
            hasil.append(art)
            print(f"[{i}/{len(antrean)}] OK: {art['judul'][:60]}")
        except Exception as e:
            print(f"[{i}/{len(antrean)}] GAGAL: {str(e)[:100]}")
        time.sleep(2)
    json.dump(hasil, open(os.path.join(DATA, "artikel-loker.json"), "w"),
              ensure_ascii=False, indent=1)
    print(f"Selesai: {len(hasil)} artikel loker siap posting")

if __name__ == "__main__":
    main()
