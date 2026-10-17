#!/usr/bin/env python3
"""Posting artikel loker via web UI Blogger (pola sama seperti blog-otomatis/posting_web.py).

1. Baca data/artikel-loker.json, rakit body HTML (JSON-LD + gambar + FAQ + baca juga)
2. Tulis data/webpost/loker.json berisi [{judul, html}]
3. Tulis instruksi ke data/webpost/instruksi-loker.txt + cetak "SPAWN_BROWSER_TASK:loker:N"
4. AGEN membaca webpost/loker.json lalu spawn browser task dengan artikel ditempel
   langsung di deskripsi task (browser tidak bisa akses localhost VM ini).

Syarat: config.json -> blogs[0].blog_id SUDAH diisi (oleh parent agent setelah
blog loker dibuat via browser). Jika kosong, script berhenti dengan pesan jelas.

Pakai: python3 posting_web.py
"""
import json, os, re, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
WEBDIR = os.path.join(DATA, "webpost")
os.makedirs(WEBDIR, exist_ok=True)

TASK_TEMPLATE = """Posting {n} artikel ke blog Blogger "{tampil}" ({blog_id}) via web UI.

Konteks: Login sebagai khususstokyunobi@gmail.com di blogger.com (sesi sudah ada).

DATA ARTIKEL (dari agen, ditempel langsung):
{artikel_data}

Untuk SETIAP artikel di atas (urutan sesuai):
1. Buka https://www.blogger.com/blog/posts/{blog_id}
2. Klik "POSTINGAN BARU" / "Buat Entri Baru".
3. Isi judul dengan "Judul" artikel (teks biasa).
4. Klik "Tampilan HTML" (ikon pensil/HTML di editor), tempel SELURUH "HTML" artikel.
5. Klik "Publikasikan", konfirmasi "KONFIRMASI" jika diminta.
6. Tunggu notifikasi "Pos dipublikasikan", lalu lanjut ke artikel berikutnya.
7. Jeda ~20 detik antar postingan agar tidak terdeteksi spam.

PENTING:
- Jangan ubah isi HTML, tempel apa adanya.
- Jika ada artikel yang gagal (error/timeout), catat judulnya dan lanjut ke berikutnya.
- Jangan posting artikel yang sama 2x.

LAPORAN AKHIR:
Tulis daftar: [judul] → TERPOSTING / GAGAL (alasan)."""

def rakit_body(art, blog):
    judul = art["judul"]
    tampil = blog.get("tampil", "LokerHarian")
    blog_url = blog.get("url", "").rstrip("/")
    tgl = datetime.date.today().isoformat()
    gambar = (art.get("gambar") or "").strip()
    alt = (art.get("alt_gambar") or judul).strip()[:125]
    ld = {"@context": "https://schema.org", "@type": "NewsArticle",
          "headline": judul, "image": [gambar], "datePublished": tgl,
          "dateModified": tgl,
          "author": {"@type": "Organization", "name": tampil},
          "publisher": {"@type": "Organization", "name": tampil,
                        "logo": {"@type": "ImageObject",
                                 "url": (blog_url + "/favicon.ico") if blog_url else ""}},
          "description": (art.get("meta_deskripsi") or judul)[:160]}
    body = ('<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False)
            + '\n</script>\n')
    faq_items = []
    for m in re.finditer(r"<strong>(.*?)</strong><br>(.*?)(?=</p>)",
                         art.get("faq_html", ""), re.DOTALL):
        q = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        a_ = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if q and a_:
            faq_items.append({"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a_}})
    if faq_items:
        body += ('<script type="application/ld+json">\n'
                 + json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                               "mainEntity": faq_items}, ensure_ascii=False)
                 + '\n</script>\n')
    body += f'<p><img src="{gambar}" alt="{alt}" style="max-width:100%;height:auto;"/></p>\n'
    body += art["artikel_html"]
    labels = art.get("label", [])[:3]
    if labels and blog_url:
        links = "".join(
            f'<li><a href="{blog_url}/search/label/{l}">Artikel terkait: {l}</a></li>'
            for l in labels)
        baca_juga = ('<div style="background:#f5f7fa;border-left:4px solid #e63946;'
                     'padding:12px 16px;margin:16px 0;"><strong>Baca juga:</strong>'
                     f'<ul style="margin:8px 0 0 18px;">{links}</ul></div>')
        body = body.replace("</p>", "</p>\n" + baca_juga, 1)
    faq = (art.get("faq_html") or "").strip()
    if faq:
        if "<p>Sumber:" in body:
            body = body.replace("<p>Sumber:", faq + "\n<p>Sumber:", 1)
        else:
            body += "\n" + faq
    return judul, body

def main():
    cfg = json.load(open(os.path.join(BASE, "config.json")))
    blog = cfg["blogs"][0]
    if not blog.get("blog_id"):
        print("BLOG_ID KOSONG: blog loker belum dibuat. Parent agent harus membuat "
              "blog via browser dulu, lalu isi blogs[0].blog_id (+url, +blogger_email) "
              "di config.json.")
        return

    art_path = os.path.join(DATA, "artikel-loker.json")
    artikels = json.load(open(art_path)) if os.path.exists(art_path) else []
    artikels = [x for x in artikels if x.get("judul", "").strip() not in ("", "...")]
    if not artikels:
        print("Tidak ada artikel loker untuk diposting")
        return
    print(f"Siapkan {len(artikels)} artikel loker")

    out = []
    for art in artikels:
        try:
            judul, html = rakit_body(art, blog)
            out.append({"judul": judul, "html": html})
        except Exception as e:
            print(f"rakit gagal untuk {art.get('judul','')[:40]}: {e}")
    if not out:
        print("Tidak ada artikel yang bisa dirakit")
        return

    json.dump(out, open(os.path.join(WEBDIR, "loker.json"), "w"), ensure_ascii=False)
    artikel_data = ""
    for i, a in enumerate(out, 1):
        artikel_data += f"\nARTIKEL {i}:\nJudul: {a['judul']}\nHTML:\n{a['html']}\n"
    task = TASK_TEMPLATE.format(n=len(out), tampil=blog["tampil"],
                                blog_id=blog["blog_id"], artikel_data=artikel_data)
    instr = os.path.join(WEBDIR, "instruksi-loker.txt")
    open(instr, "w").write(task)
    print(f"Instruksi browser task: {instr} ({len(task)} karakter)")
    print(f"SPAWN_BROWSER_TASK:loker:{len(out)}")

if __name__ == "__main__":
    main()
