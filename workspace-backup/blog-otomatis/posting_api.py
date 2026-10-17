#!/usr/bin/env python3
"""Posting artikel ke Blogspot via Blogger API v3 (OAuth).
Pengganti posting.py (Mail-to-Blogger) — lebih andal, tanpa rate-limit email.
Pakai: posting_api.py --blog <nama>
"""
import json, os, sys, time, glob, argparse
import urllib.request, urllib.error, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
CONFIG = os.path.join(BASE, "config.json")
TOKEN_FILE = os.path.expanduser("~/.hermes/blogger-tokens.json")
OAUTH_ENV = os.path.expanduser("~/.hermes/google-oauth-blogger.env")

def get_blog(nama):
    with open(CONFIG) as f:
        cfg = json.load(f)
    for b in cfg["blogs"]:
        if b["nama"] == nama:
            return b
    print("Blog tidak ada di config.json: " + nama)
    sys.exit(1)

_ap = argparse.ArgumentParser()
_ap.add_argument("--blog", required=True)
_blog = get_blog(_ap.parse_args().blog)
BLOG_NAMA = _blog["nama"]
BLOG_ID = _blog["blog_id"]

def load_oauth():
    d = {}
    with open(OAUTH_ENV) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                d[k] = v
    return d

def get_token():
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)
    return tokens

def save_token(tokens):
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)
    os.chmod(TOKEN_FILE, 0o600)

def refresh_token(tokens):
    oa = load_oauth()
    data = urllib.parse.urlencode({
        "client_id": oa["GOOGLE_CLIENT_ID"],
        "client_secret": oa["GOOGLE_CLIENT_SECRET"],
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    nt = json.load(urllib.request.urlopen(req, timeout=30))
    tokens["access_token"] = nt["access_token"]
    save_token(tokens)
    return tokens["access_token"]

def api_post(path, payload):
    tokens = get_token()
    for attempt in range(2):
        req = urllib.request.Request(
            f"https://www.googleapis.com/blogger/v3{path}",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {tokens['access_token']}",
                     "Content-Type": "application/json"},
            method="POST")
        try:
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            if e.code == 401 and attempt == 0:
                print("Token expired, refresh...")
                tokens["access_token"] = refresh_token(tokens)
                continue
            print(f"API HTTP {e.code}: {body}")
            return None

def box_afiliasi(art):
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

def rakit_body(art):
    judul = art["judul"]
    body = art["artikel_html"]
    gambar = (art.get("gambar") or "").strip()
    if not gambar:
        import hashlib
        seed = hashlib.md5(BLOG_NAMA.encode()).hexdigest()[:8]
        gambar = f"https://picsum.photos/seed/{BLOG_NAMA}{seed}/1080/1080"
    alt = (art.get("alt_gambar") or judul).strip()[:125]
    # JSON-LD NewsArticle schema (dari skill seo-schema-structured-data)
    import datetime
    tgl = datetime.date.today().isoformat()
    blog_url = _blog.get("url", "").rstrip("/")
    tampil = _blog.get("tampil", BLOG_NAMA)
    faq_items = []
    # Ekstrak Q&A dari faq_html untuk FAQPage schema
    import re as _re
    for m in _re.finditer(r"<strong>(Q\d?\??.*?)</strong><br>(.*?)(?=</p>)", art.get("faq_html", ""), _re.DOTALL):
        q = _re.sub(r"<[^>]+>", "", m.group(1)).strip()
        a = _re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if q and a:
            faq_items.append({"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}})
    ld = {"@context": "https://schema.org", "@type": "NewsArticle",
          "headline": judul, "image": [gambar], "datePublished": tgl,
          "dateModified": tgl,
          "author": {"@type": "Organization", "name": tampil},
          "publisher": {"@type": "Organization", "name": tampil,
                        "logo": {"@type": "ImageObject", "url": blog_url + "/favicon.ico"}},
          "description": (art.get("meta_deskripsi") or judul)[:160]}
    ld_html = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False) + '\n</script>\n'
    if faq_items:
        faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_items}
        ld_html += '<script type="application/ld+json">\n' + json.dumps(faq_ld, ensure_ascii=False) + '\n</script>\n'
    body = ld_html + f'<p><img src="{gambar}" alt="{alt}" style="max-width:100%;height:auto;"/></p>\n' + body
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
        body = body.replace("</p>", "</p>\n" + baca_juga, 1)
    faq = (art.get("faq_html") or "").strip()
    if faq and "Sumber:" in body:
        body = body.replace("<p>Sumber:", faq + "\n<p>Sumber:", 1)
    elif faq:
        body += "\n" + faq
    box_af = box_afiliasi(art)
    if box_af and "Sumber:" in body:
        body = body.replace("<p>Sumber:", box_af + "\n<p>Sumber:", 1)
    elif box_af:
        body += "\n" + box_af
    return judul, body

def main():
    art_path = os.path.join(DATA, "artikel-" + BLOG_NAMA + ".json")
    if not os.path.exists(art_path):
        print("artikel.json tidak ada: " + art_path)
        sys.exit(1)
    with open(art_path) as f:
        artikels = json.load(f)
    pending_files = sorted(glob.glob(os.path.join(DATA, "artikel_pending_" + BLOG_NAMA + "_*.json")))
    pending_arts = []
    for pf in pending_files:
        try:
            with open(pf) as f:
                d = json.load(f)
            if isinstance(d, list):
                pending_arts.extend(d)
        except Exception as e:
            print(f"Lewati pending rusak {os.path.basename(pf)}: {e}")
    if pending_arts:
        print(f"Tambah {len(pending_arts)} artikel tertunda")
        artikels = pending_arts + artikels
    print(f"Posting {len(artikels)} artikel ke {_blog['tampil']} via API...")
    ok = 0
    for i, art in enumerate(artikels):
        judul, body = rakit_body(art)
        labels = art.get("label", [])[:5]
        payload = {"kind": "blogger#post", "blog": {"id": BLOG_ID},
                   "title": judul, "content": body, "labels": labels}
        r = api_post(f"/blogs/{BLOG_ID}/posts", payload)
        if r and r.get("id"):
            ok += 1
            print(f"TERPOSTING [{ok}]: {judul[:60]} -> {r.get('url', '')[:80]}")
        else:
            print(f"GAGAL: {judul[:60]}")
        if i < len(artikels) - 1:
            time.sleep(5)  # jeda sopan antar posting
    print(f"Selesai: {ok}/{len(artikels)} terposting")
    if ok:
        os.rename(art_path, os.path.join(DATA, "artikel_terkirim-" + BLOG_NAMA + ".json"))
    if ok == len(artikels):
        for pf in pending_files:
            try:
                os.remove(pf)
            except Exception:
                pass

if __name__ == "__main__":
    main()
