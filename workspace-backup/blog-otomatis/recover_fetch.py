#!/usr/bin/env python3
"""Recovery fetch untuk blog yang antreannya 0 karena seen terkonsumsi run gagal 09:11.
Langkah per blog:
1. Backup seen-{blog}.json
2. Hapus seen, fetch ulang -> dapat semua item RSS terkini
3. Filter: buang item yang link-nya sudah ada di artikel_terkirim-{blog}.json (link_sumber)
   atau di data/artikel-{blog}.json (link) -> cegah duplikat artikel yang sudah tayang
4. Tulis antrean (maks 10), gabung seen lama + baru (cap 500)
"""
import json, os, re, sys, subprocess, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
HIDDEN = os.path.expanduser("~/workspace/goals/kabarviral-automated-news-blog/hidden_files")
PY = os.path.join(BASE, "venv", "bin", "python")

def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())

def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def posted_links(blog):
    links, titles = set(), set()
    for a in load_json(os.path.join(DATA, f"artikel_terkirim-{blog}.json"), []):
        ls = (a.get("link_sumber") or "").strip()
        if ls:
            links.add(ls)
        t = norm(a.get("judul", ""))[:60]
        if t:
            titles.add(t)
    # sisa format lama di artikel-{blog}.json (key "link")
    for a in load_json(os.path.join(DATA, f"artikel-{blog}.json"), []):
        ls = (a.get("link_sumber") or a.get("link") or "").strip()
        if ls:
            links.add(ls)
    return links, titles

def recover(blog):
    seen_path = os.path.join(DATA, f"seen-{blog}.json")
    antrean_path = os.path.join(DATA, f"antrean-{blog}.json")
    old_seen = set(load_json(seen_path, []))
    if seen_path and os.path.exists(seen_path):
        shutil.copy2(seen_path, os.path.join(HIDDEN, f"seen-{blog}.json.bak-20261004"))
    # 2. hapus seen -> fetch ulang
    if os.path.exists(seen_path):
        os.remove(seen_path)
    r = subprocess.run([PY, os.path.join(BASE, "fetch_berita.py"), "--blog", blog],
                       capture_output=True, text=True, timeout=900, cwd=BASE)
    print(f"[{blog}] fetch rc={r.returncode}")
    if r.returncode != 0:
        print(r.stdout[-500:], r.stderr[-500:])
    fresh = load_json(antrean_path, [])
    print(f"[{blog}] fetch mentah: {len(fresh)} item")
    # 3. filter duplikat vs yang sudah tayang
    links, titles = posted_links(blog)
    kept = []
    for it in fresh:
        link = (it.get("link") or "").strip()
        tj = norm(it.get("judul_asli", ""))[:60]
        if link in links:
            continue
        # judul asli mirip judul artikel tayang -> skip (antisipasi link beda format)
        if any(tj and (tj in t or t in tj) for t in titles):
            continue
        kept.append(it)
    kept = kept[:10]
    with open(antrean_path, "w") as f:
        json.dump(kept, f, ensure_ascii=False, indent=1)
    # 4. gabung seen
    new_seen = set(load_json(seen_path, []))
    merged = sorted(old_seen | new_seen)[-500:]
    with open(seen_path, "w") as f:
        json.dump(merged, f)
    print(f"[{blog}] antrean akhir: {len(kept)} item (buang {len(fresh)-len(kept)} duplikat tayang)")
    for k in kept:
        print("   -", k["judul_asli"][:65])
    return len(kept)

if __name__ == "__main__":
    blogs = sys.argv[1:] or ["teknopedia", "infokesehatan", "ekonomibisnis", "gayahidup",
                             "olahraga", "wisata", "kuliner", "otomotif", "pendidikan"]
    total = {}
    for b in blogs:
        try:
            total[b] = recover(b)
        except Exception as e:
            print(f"[{b}] RECOVERY GAGAL: {e}")
            total[b] = -1
    print("\nRINGKASAN:", total)
