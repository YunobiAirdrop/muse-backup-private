#!/usr/bin/env python3
"""Posting artikel ke Blogspot via Mail-to-Blogger (Gmail CLI).
Butuh: config.json berisi {"blogger_email": "<alamat-rahasia>@blogger.com"}
dan Gmail yang sudah terhubung (hatch_gws_cli gmail status)."""
import json, os, subprocess, sys, time, glob, argparse

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
CONFIG = os.path.join(BASE, "config.json")

def get_blog(nama):
    with open(CONFIG) as f:
        cfg = json.load(f)
    for b in cfg["blogs"]:
        if b["nama"] == nama:
            return b
    print("Blog tidak ada di config.json: " + nama)
    sys.exit(1)

_ap = argparse.ArgumentParser()
_ap.add_argument("--blog", default="kabarviral")
_blog = get_blog(_ap.parse_args().blog)
BLOG_NAMA = _blog["nama"]

def box_afiliasi(art):
    """Box CTA afiliasi: muncul kalau ada keyword cocok DAN link sudah diisi.
    Config: afiliansi.json. Link kosong = box tidak tampil."""
    try:
        cfg = json.load(open(os.path.join(BASE, "afiliansi.json")))
    except Exception:
        return ""
    daftar = cfg.get(BLOG_NAMA, [])
    teks_cari = (art.get("judul", "") + " " + art.get("artikel_html", "")).lower()
    for item in daftar:
        link = (item.get("link") or "").strip()
        if not link or link == "-":
            continue
        if any(kw.lower() in teks_cari for kw in item.get("keyword", [])):
            return (
                '<div style="background:#f0f7ff;border:2px solid #2563eb;border-radius:12px;'
                'padding:20px;margin:24px 0;text-align:center;">'
                f'<p style="font-size:18px;font-weight:bold;color:#1e3a8a;margin:0 0 8px;">'
                f'{item.get("judul_box", "Penawaran Spesial")}</p>'
                f'<p style="color:#334155;margin:0 0 16px;">{item.get("teks", "")}</p>'
                f'<a href="{link}" rel="sponsored nofollow" style="display:inline-block;'
                f'background:#2563eb;color:#fff;font-weight:bold;padding:12px 32px;'
                f'border-radius:8px;text-decoration:none;">'
                f'{item.get("teks_tombol", "Lihat Selengkapnya")}</a></div>'
            )
    return ""

def main():
    if not os.path.exists(CONFIG):
        print("config.json belum ada. Isi: {\"blogger_email\": \"xxx@blogger.com\"}")
        sys.exit(1)
    target = (_blog.get("blogger_email", "") or _blog.get("email", "")).strip()
    if not target:
        print("email kosong untuk blog " + BLOG_NAMA)
        sys.exit(1)
    print(f"Posting ke blog: {BLOG_NAMA} ({target})")
    art_path = os.path.join(DATA, "artikel-" + BLOG_NAMA + ".json")
    if not os.path.exists(art_path):
        print("artikel.json tidak ada")
        sys.exit(1)
    with open(art_path) as f:
        artikels = json.load(f)
    # Artikel tertunda dari retry sebelumnya (mis. rate-limit Blogger):
    # dikirim paling duluan, sebelum batch baru.
    pending_files = sorted(glob.glob(os.path.join(DATA, "artikel_pending_" + BLOG_NAMA + "_*.json")))
    pending_arts = []
    for pf in pending_files:
        try:
            with open(pf) as f:
                d = json.load(f)
            if isinstance(d, list):
                pending_arts.extend(d)
        except Exception as e:
            print(f"Lewati file pending rusak {os.path.basename(pf)}: {e}")
    if pending_arts:
        print(f"Menambahkan {len(pending_arts)} artikel tertunda dari {len(pending_files)} file pending")
        artikels = pending_arts + artikels
    ok = 0
    blog_url = _blog.get("url", "").rstrip("/")
    for i, art in enumerate(artikels):
        judul = art["judul"]
        body = art["artikel_html"]
        gambar = (art.get("gambar") or "").strip()
        if not gambar:
            # JAMINAN: tidak ada artikel tanpa gambar
            import hashlib
            seed = hashlib.md5(_blog["nama"].encode()).hexdigest()[:8]
            gambar = f"https://picsum.photos/seed/{_blog['nama']}{seed}/1080/1080"
        alt = (art.get("alt_gambar") or judul).strip()[:125]
        # Gambar di awal artikel → jadi featured image/thumbnail di Blogger
        body = f'<p><img src="{gambar}" alt="{alt}" style="max-width:100%;height:auto;"/></p>\n' + body
        # Kotak "Baca juga" (dibuat baca_juga.py, fallback label)
        baca_juga = art.get("baca_juga_html", "")
        if not baca_juga and blog_url:
            labels = art.get("label", [])[:3]
            if labels:
                links = "".join(
                    f'<li><a href="{blog_url}/search/label/{l}">Artikel terkait: {l}</a></li>'
                    for l in labels)
                baca_juga = (f'<div style="background:#f5f7fa;border-left:4px solid #e63946;'
                             f'padding:12px 16px;margin:16px 0;"><strong>Baca juga:</strong>'
                             f'<ul style="margin:8px 0 0 18px;">{links}</ul></div>')
        if baca_juga:
            # sisipkan setelah paragraf pertama
            body = body.replace("</p>", "</p>\n" + baca_juga, 1)
        # FAQ di akhir sebelum baris Sumber
        faq = (art.get("faq_html") or "").strip()
        if faq and "Sumber:" in body:
            body = body.replace("<p>Sumber:", faq + "\n<p>Sumber:", 1)
        elif faq:
            body += "\n" + faq
        # Box afiliasi (hanya tampil kalau link sudah diisi di afiliansi.json)
        box_af = box_afiliasi(art)
        if box_af and "Sumber:" in body:
            body = body.replace("<p>Sumber:", box_af + "\n<p>Sumber:", 1)
        elif box_af:
            body += "\n" + box_af
        if i > 0:
            print("Jeda 300 detik anti-spam Blogger...")
            time.sleep(300)
        try:
            r = subprocess.run(
                ["hatch_gws_cli", "gmail", "+send", "--to", target,
                 "--subject", judul, "--body", body, "--html"],
                capture_output=True, text=True, timeout=90)
            if r.returncode == 0:
                ok += 1
                print(f"TERPOSTING: {judul[:60]}")
            else:
                print(f"GAGAL: {judul[:60]} | {r.stderr[:120]}")
        except Exception as e:
            print(f"GAGAL: {judul[:60]} | {str(e)[:120]}")
    print(f"Selesai: {ok}/{len(artikels)} terposting")
    if ok:
        os.rename(art_path, os.path.join(DATA, "artikel_terkirim-" + BLOG_NAMA + ".json"))
    if ok == len(artikels):
        # Semua terkirim: file pending yang sudah ikut dikirim dihapus agar tidak double.
        for pf in pending_files:
            try:
                os.remove(pf)
                print(f"Hapus file pending terkirim: {os.path.basename(pf)}")
            except Exception as e:
                print(f"Gagal hapus {os.path.basename(pf)}: {e}")

if __name__ == "__main__":
    main()
