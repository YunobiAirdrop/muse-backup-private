#!/usr/bin/env python3
"""Regenerasi section video yang bocor/kualitas buruk dengan model non-reasoning.
Sesuai pelajaran AGENTS.md: non-reasoning dulu + system prompt anti-monolog + validasi.
"""
import json, os, re, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": os.path.join(BASE, "tulis_ulang.py")}
sys.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, get_api_keys = _g["ROUTER_URL"], _g["get_api_keys"]

# urutan non-reasoning (pelajaran AGENTS.md)
MODELS_NR = ["google/gemma-4-26b-a4b-it:free", "qwen/qwen3.8-27b:free",
             "inclusionai/ling-3.0-flash-sante:free", "google/gemma-4-31b-it:free"]

SYSTEM = ("Jawab LANGSUNG dengan format yang diminta saja. DILARANG keras menulis "
          "proses berpikir, monolog internal, analisis langkah-demi-langkah, atau teks "
          "pembuka/penutup dalam bahasa apapun. Jangan pernah menulis kalimat seperti "
          "'I need to', 'Let me think', 'Saya perlu'. Langsung ke output final.")

PROMPT = """Kamu scriptwriter konten viral Indonesia (TikTok/Reels/Shorts). Buat SCRIPT VIDEO 30-45 detik dari berita ini:

JUDUL: {judul}
ISI SINGKAT: {isi}

Format (Bahasa Indonesia santai):
[HOOK 0-3 detik]: 1 kalimat pembuka yang bikin orang tidak skip (maks 12 kata).
  Pakai SALAH SATU pola hook FYP ini: (a) "Jangan skip — X baru saja terjadi"; (b) curiosity gap — "Ternyata selama ini kita salah soal X"; (c) angka — "3 hal yang berubah setelah X"; (d) kontras — "Bukan X, tapi Y"; (e) pertanyaan langsung — "Kamu kena dampaknya?"; (f) statement berani dari faktanya. Pilih yang paling cocok, tanpa clickbait bohong. Isi X/Y dengan kata konkret dari berita, JANGAN biarkan huruf X/Y.
[ISI 3-30 detik]: 3 poin penting, 1 kalimat per poin, gaya ngobrol
[CTA 30-45 detik]: ajakan komen/follow + "link lengkap di bio"
[TEKS LAYAR]: 3 teks singkat untuk overlay video
[VISUAL]: saran visual per segmen (1 baris per segmen)

Balas dengan format di atas saja, tanpa penjelasan."""

LEAK_PATTERNS = [
    "thinking process", "here's a thinking", "here is a thinking",
    "i need to", "i should", "let me think", "saya perlu memikirkan",
    "pola hook fyp ini", "format strictly", "1 kalimat pembuka yang bikin",
]

def valid(s):
    low = s.lower()
    for p in LEAK_PATTERNS:
        if p in low:
            return False, f"pola leak: {p}"
    for m in ["[HOOK", "[ISI", "[CTA", "[TEKS LAYAR]", "[VISUAL]"]:
        if m not in s:
            return False, f"format hilang: {m}"
    if re.search(r"\bX baru saja\b|\[X\]|\(a\) \"", s):
        return False, "placeholder X/Y"
    return True, "ok"

def bikin(judul, isi):
    msg = PROMPT.format(judul=judul, isi=re.sub(r"<[^>]+>", " ", isi)[:400])
    for key in get_api_keys():
        for model in MODELS_NR:
            try:
                r = requests.post(ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Blog Otomatis",
                }, json={"model": model, "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": msg}],
                    "temperature": 0.9, "max_tokens": 800}, timeout=120)
                if r.status_code in (429, 503):
                    if "per-day" in r.text or "free-models" in r.text:
                        break
                    time.sleep(5); continue
                r.raise_for_status()
                obj, _ = json.JSONDecoder().raw_decode(r.text.strip())
                teks = obj["choices"][0]["message"]["content"].strip()
                ok, why = valid(teks)
                print(f"  [{model.split('/')[1][:20]}] valid={ok} ({why})")
                if ok:
                    return teks
            except Exception as e:
                print(f"  [{model.split('/')[1][:20]}] err: {str(e)[:60]}")
                time.sleep(3)
    return None

def main():
    targets = [
        ("data/artikel-ekonomibisnis.json", "## Video 1 — ekonomibisnis",
         "Efek Rotasi Kapolri terhadap Stabilitas Ekonomi Nasional"),
        ("data/artikel-kabarviral.json", "## Video 3 — KabarViral",
         "Persiapan Mudik Lebaran: Panduan Lengkap & Praktis"),
    ]
    md_path = os.path.join(BASE, "data", "video-script-2026-10-03.md")
    md = open(md_path).read()
    for f, header, judul_frag in targets:
        arts = json.load(open(os.path.join(BASE, f)))
        art = next(a for a in arts if judul_frag in a["judul"])
        print(f"Regen {header}: {art['judul'][:50]}")
        s = bikin(art["judul"], art.get("artikel_html", ""))
        if not s:
            print("  GAGAL semua model"); continue
        # ganti section: dari header sampai '---' berikutnya
        pat = re.compile(re.escape(header) + r".*?\n---\n", re.S)
        new_section = f"{header}\n**Berita:** {art['judul']}\n\n{s}\n\n---\n"
        md, n = pat.subn(new_section, md, count=1)
        print(f"  diganti: {n}")
        time.sleep(2)
    open(md_path, "w").write(md)
    print("Tersimpan:", md_path)

if __name__ == "__main__":
    main()
