#!/usr/bin/env python3
"""Radar tren YouTube harian untuk 10 niche channel Yunobi.

Metode (adaptasi dari skill youtube-keyword-research, lisensi MIT):
  1. DEMAND: YouTube autocomplete (suggestqueries.google.com) per seed term —
     apa yang orang KETIK di kolom search YouTube saat ini.
  2. SUPPLY: RSS channel top per niche — apa yang kreator besar TERBITKAN
     7 hari terakhir. Term yang muncul di KEDUANYA = sinyal terkuat.

Keamanan: TANPA API key, TANPA login/OAuth, TANPA kredensial apa pun.
Hanya endpoint publik Google/YouTube + stdlib Python. Tidak ada yang bisa diretas.

Output:
  data/trend-radar-YYYY-MM-DD.md   (laporan human-readable)
  data/trend-radar-YYYY-MM-DD.json (machine-readable untuk pipeline)
  data/yt-channel-ids.json         (cache handle -> channel_id)

Pakai: ./venv/bin/python trend_radar.py
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
CACHE = os.path.join(DATA, "yt-channel-ids.json")
WINDOW_DAYS = 7

# niche_id: label, hl (id/en), seeds, channel top (handle YouTube)
NICHES = {
    "horor_id": {
        "label": "Kisah Horor (@KisahPOV) — cerita horor Indonesia",
        "hl": "id",
        "seeds": ["cerita horor", "kisah horor", "cerita mistis",
                  "horor indonesia", "cerita hantu", "pengalaman horor"],
        "channels": ["nessiejudge"],
    },
    "rakyat_id": {
        "label": "Cerita Rakyat (@ceritarakyat862) — legenda & sejarah Indonesia",
        "hl": "id",
        "seeds": ["cerita rakyat", "legenda indonesia", "sejarah indonesia",
                  "kisah kerajaan", "pov sejarah", "mitos indonesia"],
        "channels": [],
    },
    "truecrime_en": {
        "label": "Dark Case Files (@TrueCaseFilesTV) — true crime",
        "hl": "en",
        "seeds": ["true crime", "true crime stories", "unsolved murders",
                  "serial killer documentary", "true crime documentary"],
        "channels": ["BaileySarian"],
    },
    "horror_en": {
        "label": "Midnight Dread Tales (@TalesOfDreadTV) — English horror",
        "hl": "en",
        "seeds": ["horror stories", "scary stories", "true horror stories",
                  "analog horror", "creepypasta"],
        "channels": ["MrBallen"],
    },
    "mystery_en": {
        "label": "Unsolved Shadows (@MysteryShadowsTV) — unsolved mysteries",
        "hl": "en",
        "seeds": ["unsolved mysteries", "unexplained mysteries",
                  "missing persons mystery", "unsolved cases"],
        "channels": ["BarelySociable"],
    },
    "history_en": {
        "label": "Echoes of History (@EchoesOfThePast-e9m) — world history",
        "hl": "en",
        "seeds": ["world history", "history documentary", "ancient history",
                  "weird history", "history stories"],
        "channels": ["OverSimplified"],
    },
    "space_en": {
        "label": "Cosmic Unknown (@CosmosUnknownTV) — space",
        "hl": "en",
        "seeds": ["space documentary", "universe mysteries", "black hole",
                  "cosmos", "space discoveries"],
        "channels": ["kurzgesagt"],
    },
    "darkpsych_en": {
        "label": "Dark Mind Files (@TheDarkMindFiles-s6i) — dark psychology",
        "hl": "en",
        "seeds": ["dark psychology", "psychology facts", "mind manipulation",
                  "human psychology tricks", "psychology of people"],
        "channels": [],
    },
    "weirdfacts_en": {
        "label": "Weird World Daily (@BizarreWorldDaily) — weird facts",
        "hl": "en",
        "seeds": ["weird facts", "strange facts", "bizarre facts",
                  "did you know", "crazy facts"],
        "channels": [],
    },
    "ancient_en": {
        "label": "Lost Empires (@AncientEmpiresTV) — ancient civilizations",
        "hl": "en",
        "seeds": ["ancient civilizations", "lost civilizations",
                  "ancient egypt", "ancient rome", "lost empire"],
        "channels": [],
    },
}

STOP_ID = set("yang dan di ke dari untuk dengan pada adalah ini itu sebuah".split())
STOP_EN = set(("the a an and of to in on for with is are was were be as at "
               "by from that this it its vs new top best most how why what").split())


def _get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def autocomplete(seed, hl):
    """Return list saran autocomplete YouTube untuk seed."""
    q = urllib.parse.quote(seed)
    url = (f"https://suggestqueries.google.com/complete/search"
           f"?client=youtube&ds=yt&hl={hl}&q={q}")
    try:
        raw = _get(url)
        m = re.search(r"window\.google\.ac\.h\((.*)\)\s*$", raw, re.S)
        data = json.loads(m.group(1))
        return [s[0] for s in data[1] if s and s[0]]
    except Exception:
        return []


def resolve_channel_id(handle):
    """Handle -> UC... id, pakai cache."""
    cache = {}
    if os.path.exists(CACHE):
        try:
            cache = json.load(open(CACHE))
        except Exception:
            pass
    if handle in cache:
        return cache[handle]
    try:
        html = _get(f"https://www.youtube.com/@{handle}")
        m = re.search(r'"externalId":"(UC[^"]+)"', html)
        if m:
            cache[handle] = m.group(1)
            json.dump(cache, open(CACHE, "w"))
            return m.group(1)
    except Exception:
        pass
    time.sleep(1)
    return None


def rss_titles_last_days(channel_id, days=WINDOW_DAYS):
    """Judul video channel dalam N hari terakhir."""
    try:
        xml = _get(f"https://www.youtube.com/feeds/videos.xml"
                   f"?channel_id={channel_id}")
        root = ET.fromstring(xml)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        cutoff = (datetime.datetime.now(datetime.timezone.utc)
                  - datetime.timedelta(days=days))
        out = []
        for e in root.findall("a:entry", ns):
            pub = e.find("a:published", ns)
            title = e.find("a:title", ns)
            if pub is None or title is None:
                continue
            try:
                dt = datetime.datetime.fromisoformat(
                    pub.text.replace("Z", "+00:00"))
            except Exception:
                continue
            if dt >= cutoff:
                out.append(title.text or "")
        return out
    except Exception:
        return []


def tokenize(text, hl):
    words = re.findall(r"[a-zA-Zà-ÿ']{3,}", text.lower())
    stop = STOP_ID if hl == "id" else STOP_EN
    return [w for w in words if w not in stop]


def radar_niche(niche_id, cfg):
    hl = cfg["hl"]
    demand = Counter()      # term -> jumlah seed yang menghasilkannya
    term_seed = {}          # term -> daftar seed
    for seed in cfg["seeds"]:
        for s in autocomplete(seed, hl):
            key = s.strip().lower()
            if not key or key == seed.lower():
                continue
            # filter relevansi ringan: harus mengandung kata kunci seed
            if not any(w in key for w in seed.lower().split()):
                continue
            demand[key] += 1
            term_seed.setdefault(key, set()).add(seed)
        time.sleep(0.4)

    # supply: kata dari judul video channel top 7 hari terakhir
    supply = Counter()
    n_video = 0
    for handle in cfg.get("channels", []):
        cid = resolve_channel_id(handle)
        if not cid:
            continue
        titles = rss_titles_last_days(cid)
        n_video += len(titles)
        for t in titles:
            for w in tokenize(t, hl):
                supply[w] += 1
        time.sleep(0.5)

    # skor: demand dominan; bonus jika kata muncul juga di supply
    ranked = []
    for term, hits in demand.most_common(40):
        words = set(term.split())
        supply_hit = sum(supply.get(w, 0) for w in words)
        both = supply_hit > 0
        skor = hits * 10 + (5 if both else 0) + min(supply_hit, 10)
        ranked.append({"term": term, "skor": skor, "seed_hits": hits,
                       "dari_seed": sorted(term_seed[term]),
                       "juga_di_channel_top": both})
    ranked.sort(key=lambda x: -x["skor"])
    # celah konten (last30days: demand tinggi tapi supply nol = peluang):
    # hanya bermakna bila ada data channel top (n_video > 0)
    celah = ([t["term"] for t in ranked
              if not t["juga_di_channel_top"]][:5]
             if n_video > 0 else [])
    return {"top_terms": ranked[:15], "celah_konten": celah,
            "video_channel_top_7hari": n_video}


def main():
    hari = datetime.date.today().isoformat()
    # term yang muncul kemarin (last30days: tren = yang BARU muncul)
    kemarin = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    terms_kemarin = set()
    _pk = os.path.join(DATA, f"trend-radar-{kemarin}.json")
    if os.path.exists(_pk):
        try:
            _d = json.load(open(_pk))
            for _nid, _n in _d.get("niches", {}).items():
                for _t in _n.get("top_terms", []):
                    terms_kemarin.add((_nid, _t["term"]))
        except Exception:
            pass
    hasil = {"tanggal": hari, "window_hari": WINDOW_DAYS, "niches": {}}
    for nid, cfg in NICHES.items():
        print(f"Radar {nid}...", flush=True)
        try:
            res = radar_niche(nid, cfg)
            for t in res["top_terms"]:
                t["baru_naik"] = (nid, t["term"]) not in terms_kemarin
            hasil["niches"][nid] = {"label": cfg["label"], **res}
        except Exception as e:
            hasil["niches"][nid] = {"label": cfg["label"], "error": str(e)[:120],
                                    "top_terms": []}
    os.makedirs(DATA, exist_ok=True)
    json.dump(hasil, open(os.path.join(DATA, f"trend-radar-{hari}.json"), "w"),
              ensure_ascii=False, indent=1)

    # laporan markdown
    md = [f"# Radar Tren YouTube — {hari}\n",
          f"Jendela: {WINDOW_DAYS} hari terakhir. "
          "Skor = demand (autocomplete) + bonus jika juga muncul di channel top.\n"]
    for nid, cfg in NICHES.items():
        n = hasil["niches"][nid]
        md.append(f"## {cfg['label']}")
        terms = n.get("top_terms", [])
        if not terms:
            md.append("_tidak ada sinyal hari ini_\n")
            continue
        for i, t in enumerate(terms[:10], 1):
            tag = " 🔥" if t["juga_di_channel_top"] else ""
            tag += " 🔺" if t.get("baru_naik") else ""
            md.append(f"{i}. **{t['term']}** (skor {t['skor']}){tag}")
        celah = n.get("celah_konten") or []
        if celah:
            md.append(f"\n🎯 **Celah konten** (demand tinggi, belum digarap channel top): "
                      + ", ".join(f"**{c}**" for c in celah))
        md.append("")
    md.append("Legenda: 🔥 juga dibahas channel top 7 hari terakhir · "
              "🔺 muncul baru vs kemarin")
    open(os.path.join(DATA, f"trend-radar-{hari}.md"), "w").write("\n".join(md))
    print("Tersimpan:", os.path.join(DATA, f"trend-radar-{hari}.md"))


if __name__ == "__main__":
    main()
