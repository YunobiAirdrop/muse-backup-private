#!/usr/bin/env python3
"""Script video pendek (TikTok/Reels/Shorts) dari 3 artikel terpanas hari ini.
Tiap script membawa 3 varian HOOK (A/B/C, pola berbeda) — siap untuk uji A/B
hook YouTube saat fiturnya live. Output: data/video-script-YYYY-MM-DD.md.
Pakai: ./venv/bin/python video_script.py  (3 req/hari)
"""
import datetime, glob, json, os, sys, time
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
sys.path.insert(0, BASE)
_src = open(os.path.join(BASE, "tulis_ulang.py")).read()
_g = {"__name__": "__lib__", "__file__": "tulis_ulang.py"}
sys.argv = ["tulis_ulang.py", "--blog", "kabarviral"]
exec(compile(_src.split("def main():")[0], "tulis_ulang.py", "exec"), _g)
ROUTER_URL, MODELS, get_api_keys = _g["ROUTER_URL"], _g["MODELS"], _g["get_api_keys"]

NAMES = {"kabarviral": "KabarViral", "cuanpintar": "CuanPintar",
         "teknogebrakan": "TeknoGebrakan", "sehatbugar": "SehatBugar"}

PROMPT = """Kamu scriptwriter konten viral Indonesia (TikTok/Reels/Shorts). Buat SCRIPT VIDEO 30-45 detik dari berita ini:

JUDUL: {judul}
ISI SINGKAT: {isi}

Format (Bahasa Indonesia santai):
[HOOK A 0-3 detik]: 1 kalimat pembuka yang bikin orang tidak skip (maks 12 kata).
[HOOK B 0-3 detik]: 1 kalimat pembuka ALTERNATIF, pola berbeda dari HOOK A (maks 12 kata).
[HOOK C 0-3 detik]: 1 kalimat pembuka ALTERNATIF ke-2, pola berbeda dari HOOK A dan B (maks 12 kata).
  Ketiga hook pakai pola BERBEDA dari daftar pola hook FYP ini: (a) "Jangan skip — X baru saja terjadi"; (b) curiosity gap — "Ternyata selama ini kita salah soal X"; (c) angka — "3 hal yang berubah setelah X"; (d) kontras — "Bukan X, tapi Y"; (e) pertanyaan langsung — "Kamu kena dampaknya?"; (f) statement berani dari faktanya. Tanpa clickbait bohong.
[ISI 3-30 detik]: 3 poin penting, 1 kalimat per poin, gaya ngobrol
[CTA 30-45 detik]: ajakan komen/follow + "link lengkap di bio"
[TEKS LAYAR]: 3 teks singkat untuk overlay video
[VISUAL]: saran visual per segmen (1 baris per segmen)

Balas dengan format di atas saja, tanpa penjelasan."""

def _artikel_hari_ini():
    hasil = []
    for f in glob.glob(os.path.join(DATA, "artikel-*.json")):
        if "terkirim" in f or "pending" in f:
            continue
        blog = os.path.basename(f).replace("artikel-", "").replace(".json", "")
        try:
            for a in json.load(open(f)):
                if a.get("judul") and not a["judul"].startswith("Terpopuler Hari Ini"):
                    hasil.append({"blog": blog, "judul": a["judul"],
                                  "isi": (a.get("artikel_html", "")[:500])})
        except Exception:
            pass
    return hasil

def _bersihkan_html(h):
    import re
    return re.sub(r"<[^>]+>", " ", h)[:400]

def bikin_script(art):
    msg = PROMPT.format(judul=art["judul"], isi=_bersihkan_html(art["isi"]))
    for key in get_api_keys():
        for model in MODELS[:4]:
            try:
                r = requests.post(ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Blog Otomatis",
                }, json={"model": model, "messages": [{"role": "user", "content": msg}],
                          "temperature": 0.9, "max_tokens": 1000}, timeout=120)
                if r.status_code in (429, 503):
                    if "per-day" in r.text or "free-models" in r.text:
                        break
                    time.sleep(5)
                    continue
                r.raise_for_status()
                dec = json.JSONDecoder()
                obj, _ = dec.raw_decode(r.text.strip())
                return obj["choices"][0]["message"]["content"].strip()
            except Exception:
                time.sleep(3)
    return None

def main():
    semua = _artikel_hari_ini()
    # 3 artikel, beda blog kalau bisa
    pilihan, blog_dipakai = [], set()
    for a in semua:
        if a["blog"] not in blog_dipakai:
            pilihan.append(a)
            blog_dipakai.add(a["blog"])
        if len(pilihan) == 3:
            break
    if not pilihan:
        print("tidak ada artikel hari ini")
        return
    hari = datetime.date.today().isoformat()
    md = [f"# Script Video Pendek — {hari}\n"]
    for i, art in enumerate(pilihan, 1):
        print(f"Script {i}/3: {art['judul'][:50]}...")
        s = bikin_script(art)
        md.append(f"## Video {i} — {NAMES.get(art['blog'], art['blog'])}")
        md.append(f"**Berita:** {art['judul']}\n")
        md.append(s if s else "_(gagal generate)_")
        md.append("\n---\n")
        time.sleep(2)
    out = os.path.join(DATA, f"video-script-{hari}.md")
    open(out, "w").write("\n".join(md))
    print("Tersimpan:", out)

if __name__ == "__main__":
    main()
