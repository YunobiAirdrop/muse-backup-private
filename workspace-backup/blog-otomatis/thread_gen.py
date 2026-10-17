#!/usr/bin/env python3
"""Thread X/Threads otomatis dari 3 artikel terpanas hari ini.
Output: data/thread-YYYY-MM-DD.json (+ .md readable).
Untuk sekarang disimpan dulu; begitu akun X/Threads connect, tinggal posting.
Nanti: integrasi ke xurl / threads-cli.
Pakai: ./venv/bin/python thread_gen.py  (3 req/hari)
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

PROMPT = """Kamu admin X/Twitter Indonesia yang jago bikin thread viral. Ubah berita ini jadi THREAD 6 post:

JUDUL: {judul}
ISI SINGKAT: {isi}
LINK BLOG: {url}

Aturan:
- Post 1: hook maksimal 15 kata + bikin penasaran (tanpa clickbait bohong).
  Pakai SALAH SATU pola hook FYP ini: (a) curiosity gap — "Ternyata selama ini kita salah soal X"; (b) angka spesifik — "3 hal yang berubah setelah X"; (c) kontras — "Bukan X, tapi Y yang bikin ..."; (d) statement berani dari faktanya; (e) pertanyaan langsung ke pembaca; (f) urgensi — "Sebelum kamu X, baca ini". Pilih yang paling cocok, jangan dipaksa.
- Post 2-5: 1 fakta/poin penting per post, gaya ngobrol, maks 240 karakter per post
- Post 6: CTA baca lengkap + link blog + 2-3 hashtag
- Tiap post maks 270 karakter, tanpa emoji berlebihan (maks 1 per post)
- Balas HANYA JSON: {{"thread": ["post 1", "post 2", ...]}}"""

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
                                  "isi": a.get("artikel_html", "")})
        except Exception:
            pass
    return hasil

def bikin_thread(art, url):
    import re
    isi = re.sub(r"<[^>]+>", " ", art["isi"])[:400]
    msg = PROMPT.format(judul=art["judul"], isi=isi, url=url)
    for key in get_api_keys():
        for model in MODELS[:4]:
            try:
                r = requests.post(ROUTER_URL, headers={
                    "Authorization": f"Bearer {key}", "Content-Type": "application/json",
                    "HTTP-Referer": "https://kabarviralterkiniterbaru.blogspot.com/",
                    "X-Title": "Blog Otomatis",
                }, json={"model": model, "messages": [{"role": "user", "content": msg}],
                          "temperature": 0.8, "max_tokens": 1200}, timeout=120)
                if r.status_code in (429, 503):
                    if "per-day" in r.text or "free-models" in r.text:
                        break
                    time.sleep(5)
                    continue
                r.raise_for_status()
                dec = json.JSONDecoder()
                obj, _ = dec.raw_decode(r.text.strip())
                teks = obj["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
                return json.loads(teks[teks.find("{"):])["thread"]
            except Exception:
                time.sleep(3)
    return None

def main():
    cfg = json.load(open(os.path.join(BASE, "config.json")))
    urlmap = {b["nama"]: b.get("url", "") for b in cfg["blogs"]}
    semua = _artikel_hari_ini()
    pilihan, dipakai = [], set()
    for a in semua:
        if a["blog"] not in dipakai:
            pilihan.append(a)
            dipakai.add(a["blog"])
        if len(pilihan) == 3:
            break
    if not pilihan:
        print("tidak ada artikel hari ini")
        return
    hari = datetime.date.today().isoformat()
    hasil, md = [], [f"# Thread X/Threads — {hari}\n"]
    for i, art in enumerate(pilihan, 1):
        print(f"Thread {i}/3: {art['judul'][:50]}...")
        t = bikin_thread(art, urlmap.get(art["blog"], ""))
        hasil.append({"blog": art["blog"], "judul": art["judul"], "thread": t or []})
        md.append(f"## Thread {i} — {NAMES.get(art['blog'], art['blog'])}")
        md.append(f"**Berita:** {art['judul']}\n")
        for j, p in enumerate(t or ["_(gagal)_"], 1):
            md.append(f"{j}. {p}\n")
        md.append("---\n")
        time.sleep(2)
    json.dump(hasil, open(os.path.join(DATA, f"thread-{hari}.json"), "w"), ensure_ascii=False, indent=1)
    open(os.path.join(DATA, f"thread-{hari}.md"), "w").write("\n".join(md))
    print(f"Tersimpan: thread-{hari}.json/md")

if __name__ == "__main__":
    main()
