#!/usr/bin/env python3
"""Perbaikan metadata video sepi 2026-10-12 (perintah user eksplisit).

Mode: --dry (rencana saja) | --apply (eksekusi + verifikasi read-back).
Sumber: hidden_files/sepi-2026-10-12.json. Aturan: protokol-viral bag. 3/14/17
+ packaging-formulas.md. Append-only untuk deskripsi (link afiliasi/atribusi
yang sudah ada TIDAK pernah dihapus).
"""
import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from auth import yt_get, yt_put  # noqa: E402
from seo_audit import audit, hashtags, HASHTAG_RE  # noqa: E402

HERE = Path(__file__).resolve().parent
SEPI = HERE / "sepi-2026-10-12.json"
PLAN = HERE / "perbaikan-sepi-plan.json"
RESULT = HERE / "perbaikan-sepi-hasil.json"

EXCLUDE = {"bGBGROVZfZY"}                 # Macam Macam — menunggu keputusan user
DUP_PRIVATE = {"jhDzosY_vj8", "7mkgmONd89o"}  # TalesOfDreadTV duplikat 0-view

CFG = {
    "empires-en":   dict(lang="EN", tail="#shorts #history #viral #foryou",
                         longtags="#history #viral #archaeology #foryou",
                         tags=["ancient empires", "maya civilization", "ancient history", "archaeology", "lost civilizations", "ancient mysteries", "history documentary", "ancient temples", "lost empires"]),
    "history-en":   dict(lang="EN", tail="#shorts #history #viral #foryou",
                         longtags="#history #documentary #viral #foryou",
                         tags=["history documentary", "ancient history", "historical events", "echoes of the past", "history", "documentary"]),
    "horor":        dict(lang="ID", tail="#shorts #horor #ceritahoror #foryou",
                         longtags="#horor #ceritahoror #viralindonesia #foryou",
                         tags=["cerita horor", "kisah horor", "cerita hantu", "horor indonesia", "kisah pov", "cerita seram", "hantu indonesia", "urban legend indonesia"]),
    "horror-en":    dict(lang="EN", tail="#shorts #horror #scarystories #foryou",
                         longtags="#horror #scarystories #viral #foryou",
                         tags=["scary stories", "horror stories", "tales of dread", "creepy stories", "ghost stories", "horror narration", "scary story"]),
    "jejakbuddha":  dict(lang="ID", tail="#shorts #buddha #kebijaksanaan #foryou",
                         longtags="#buddha #kebijaksanaan #viralindonesia #foryou",
                         tags=["buddha", "kisah buddha", "kebijaksanaan", "siddhartha gautama", "ajaran buddha", "jejak buddha", "cerita buddha"]),
    "jejakislami":  dict(lang="ID", tail="#shorts #islami #kisahnabi #foryou",
                         longtags="#islami #kisahnabi #viralindonesia #foryou",
                         tags=["kisah nabi", "kisah islami", "cerita islami", "jejak islami", "sejarah islam", "kisah nabi yusuf", "kisah nabi musa"]),
    "kisahalkitab": dict(lang="ID", tail="#shorts #alkitab #rohani #foryou",
                         longtags="#alkitab #rohani #viralindonesia #foryou",
                         tags=["kisah alkitab", "alkitab", "cerita alkitab", "rohani kristen", "tokoh alkitab", "kisah yusuf"]),
    "kisahdharma":  dict(lang="ID", tail="#shorts #ramayana #hindu #foryou",
                         longtags="#ramayana #hindu #viralindonesia #foryou",
                         tags=["ramayana", "kisah ramayana", "hindu", "kisah dharma", "cerita hindu", "rama shinta"]),
    "lima-misteri": dict(lang="ID", tail="#shorts #misteri #penampakan #foryou",
                         longtags="#misteri #viral #penampakan #foryou",
                         tags=["lima misteri", "misteri indonesia", "kejadian aneh", "penampakan", "cerita misteri", "misteri dunia"]),
    "mind-en":      dict(lang="EN", tail="#shorts #psychology #mindset #foryou",
                         longtags="#psychology #darkpsychology #viral #foryou",
                         tags=["dark psychology", "psychology", "manipulation", "gaslighting", "body language", "mindset", "dark mind files", "human behavior"]),
    "mystery-en":   dict(lang="EN", tail="#shorts #mystery #unsolved #foryou",
                         longtags="#mystery #unsolved #viral #foryou",
                         tags=["mystery", "unsolved mystery", "true mystery", "mystery shadows", "unsolved cases", "creepy mystery", "dyatlov pass"]),
    "space-en":     dict(lang="EN", tail="#shorts #space #universe #foryou",
                         longtags="#space #universe #viral #foryou",
                         tags=["space", "universe", "cosmos unknown", "astronomy", "space documentary", "space mysteries", "cosmos"]),
    "strangetales": dict(lang="EN", tail="#shorts #weirdfacts #mystery #foryou",
                         longtags="#mystery #weirdfacts #viral #foryou",
                         tags=["strange tales", "weird facts", "unsolved mysteries", "bizarre facts", "strange phenomena", "mystery"]),
    "tinybuilders": dict(lang="EN", tail="#shorts #miniature #diy #foryou",
                         longtags="#miniature #diy #viral #foryou",
                         tags=["miniature", "miniature build", "diy", "tiny builders", "miniature farm", "satisfying build", "mini construction"]),
    "truecrime-en": dict(lang="EN", tail="#shorts #truecrime #mystery #foryou",
                         longtags="#truecrime #mystery #viral #foryou",
                         tags=["true crime", "unsolved mystery", "true case files", "crime documentary", "missing persons", "cold case"]),
    "weird-en":     dict(lang="EN", tail="#shorts #weirdfacts #viral #foryou",
                         longtags="#weirdfacts #viral #history #foryou",
                         tags=["bizarre world", "weird facts", "strange history", "weird places", "amazing facts", "weird world daily"]),
    "youtube-pov":  dict(lang="ID", tail="#shorts #pov #sejarah #foryou",
                         longtags="#sejarah #pov #viralindonesia #foryou",
                         tags=["pov sejarah", "cerita rakyat", "sejarah indonesia", "kisah sejarah", "pov", "sejarah"]),
}

PAIR = {  # short -> long pasangannya (jelas dari seri/topik)
    "x6PMVElw7sU": "iSIaj3nG_vk", "d4_b-f2StmM": "iSIaj3nG_vk", "4QQVBZ_6RoQ": "iSIaj3nG_vk",
    "nadty2jGMfY": "KWjDXPQoOHs", "9cYVddt9wcA": "KWjDXPQoOHs", "eZAfrY0B18c": "KWjDXPQoOHs",
    "MV0mktGVfGk": "2QIHW50JSZU", "4lX8taLE29M": "2QIHW50JSZU", "c5GEtqZZYI4": "2QIHW50JSZU",
    "5H9DWXm1aIs": "SiRjlW__RC0", "4JmORt_5CP0": "SiRjlW__RC0", "EepzwSQli1E": "SiRjlW__RC0",
    "vVdcMjV6MDs": "U6F-BbZ1Lns", "-TgaQlLOdv8": "U6F-BbZ1Lns", "m42ntYlIGSs": "U6F-BbZ1Lns",
    "XBDTTZi5M_Y": "6DwpnronVQQ", "4BnyLMjzWEE": "6DwpnronVQQ", "xD_HOr7GOQ4": "6DwpnronVQQ",
    "SVv6jFBOWkA": "rmkMgiPdLCo", "QnxIQ8J16_M": "rmkMgiPdLCo",
    "P8wVZLH-_8U": "0ZWVx_sDQRk",
    "5H3Y5BnECkw": "zva_d8KCm8I", "arJpVXPCJcs": "zva_d8KCm8I", "Rf14NV4B3Fs": "zva_d8KCm8I",
    "bltnidaQ0ms": "8LdS1kmxEjg", "AjKco8l2Hf0": "8LdS1kmxEjg", "l3G0yeRWSN8": "8LdS1kmxEjg",
    "eHDUZyD8oKw": "9s5iaAecFRw", "ffZFaSuDJdI": "9s5iaAecFRw",
    "Hh6TFHXJh_0": "9s5iaAecFRw", "BAAtIR9AVeU": "9s5iaAecFRw",
    "FZZpx8dT-Xc": "g900Smffbuo", "teVuCq5mvqM": "g900Smffbuo", "bmcSYyeN6Vs": "g900Smffbuo",
    "I-fJeXXkgn8": "Cn6AYK_fvag", "4buKqLS1-DA": "qWsiDK-QWZM",
    "IMBKjW8_uEE": "qWsiDK-QWZM", "5S1A7qDZj0M": "qWsiDK-QWZM",
    "uiTYVHzYzjU": "SbN_Xgr2jq8", "GKvuJopBwcY": "SbN_Xgr2jq8", "-iDVbSSaoHU": "SbN_Xgr2jq8",
    "w2pKB7ndG4Y": "b3KyDWsTyq0", "PrEE5W4ZxrI": "b3KyDWsTyq0", "EXmbjr-MKbs": "b3KyDWsTyq0",
    "zItf87bPxvU": "b3KyDWsTyq0", "W2gByTFLYWU": "b3KyDWsTyq0", "QYS9r3c4glM": "b3KyDWsTyq0",
    "7fb5QMDnja4": "6SE9_KiLafM", "cDji7o2q26U": "6SE9_KiLafM", "7zOMvbK2rjE": "6SE9_KiLafM",
    "JrjO1g38FWo": "zafVpCmFduk", "hvMHCYITXzE": "zafVpCmFduk", "7pSgcSnNT9I": "zafVpCmFduk",
    "HjdAB_44M30": "ESlXhONwvQY", "cUtpnRpB9JU": "ESlXhONwvQY", "5GSghwov0nI": "ESlXhONwvQY",
    "epB4odp8Fhk": "W--QaM2Mm2A", "uODVnY-U17o": "W--QaM2Mm2A", "avEG3PdEZyg": "W--QaM2Mm2A",
    "E4me_PPkkOY": "1_Ly-3dGSjo", "90hW5rScils": "1_Ly-3dGSjo", "rz41otZhx5U": "1_Ly-3dGSjo",
}
# Shorts Lima Misteri -> long hari ini
for _s in ("K8QaZZXVN2Q", "b8D85GnAOfY", "bcPy5OV40po", "DENDsv-ujPg",
           "rgGUFu8m6zw", "CPhKjM7loms", "5ZcgW_6JJSQ", "szbGlu1qdVg"):
    PAIR[_s] = "QyCLNmsFd7g"

TITLE_OVERRIDE = {  # inti hook diperkuat, topik sama (formula packaging + pola pemenang bag.18)
    "eHDUZyD8oKw": "That 'Free' Gift Is a Trap to Control You",
    "I-fJeXXkgn8": "The Boötes Void: 330 Million Light-Years of NOTHING",
}

CTA = {
    "ID": "🔔 Subscribe biar nggak ketinggalan cerita berikutnya — video baru setiap hari!",
    "EN": "🔔 Subscribe for more stories like this — new videos every day!",
}
LINKTXT = {
    "ID": "🎬 Tonton versi lengkapnya: https://youtu.be/{}",
    "EN": "🎬 Watch the full story: https://youtu.be/{}",
}


def _fit(core, tags):
    return core + " " + " ".join(tags)


def fix_shorts_title(title, cfg, vid):
    core = HASHTAG_RE.sub("", title).strip()
    core = re.sub(r"\s+", " ", core).rstrip(" |")
    if vid in TITLE_OVERRIDE:
        core = TITLE_OVERRIDE[vid]
    tags = [t.lower() for t in hashtags(title)]
    if tags and tags[-1] == "#foryou" and 3 <= len(tags) <= 4 and "#shorts" in tags \
            and vid not in TITLE_OVERRIDE:
        return title  # sudah patuh aturan
    if tags and "#shorts" in tags and len(tags) >= 3 and vid not in TITLE_OVERRIDE:
        new_tags = tags[:3] + ["#foryou"]
    else:
        new_tags = cfg["tail"].split()
    # Urutan pengorbanan bila >100 krk: hashtag niche ke-2 dulu, hook utuh.
    cands = [new_tags]
    if len(new_tags) == 4:
        cands.append([new_tags[0], new_tags[1], "#foryou"])
    for cand in cands:
        if len(_fit(core, cand)) <= 100:
            return _fit(core, cand)
    # Terakhir: pangkas kata dari bagian hook (sebelum "| Seri"), seri utuh.
    hook, sep, series = core.partition("|")
    hook = hook.strip()
    tail_min = cands[-1]
    while hook and len(_fit((hook + (" | " + series.strip() if sep else "")), tail_min)) > 100:
        hook = hook.rsplit(" ", 1)[0] if " " in hook else ""
    core2 = hook + (" | " + series.strip() if sep else "")
    return _fit(core2, tail_min)


def fix_desc(desc, fmt, cfg, vid, title_core):
    lang = cfg["lang"]
    d = desc or ""
    dtags = [t.lower() for t in hashtags(d)]
    out = d
    if fmt == "shorts":
        if len(out.strip()) < 30:
            lines = [title_core if title_core.endswith((".", "!", "?")) else title_core + "."]
            if vid in PAIR:
                lines += ["", LINKTXT[lang].format(PAIR[vid])]
            lines += ["", cfg["tail"]]
            out = "\n".join(lines)
        else:
            if vid in PAIR and f"youtu.be/{PAIR[vid]}" not in out:
                out = out.rstrip() + "\n\n" + LINKTXT[lang].format(PAIR[vid])
            if not dtags:
                out = out.rstrip() + "\n\n" + cfg["tail"]
    else:  # long
        if len(out.strip()) < 150:
            hook = title_core if title_core.endswith((".", "!", "?")) else title_core + "."
            out = (hook + "\n\n" + out).strip() if out.strip() else hook
        low = out.lower()
        if not any(w in low for w in ("subscribe", "berlangganan", "langganan")):
            out = out.rstrip() + "\n\n" + CTA[lang]
        if not dtags:
            out = out.rstrip() + "\n\n" + cfg["longtags"]
        elif "#foryou" not in dtags:
            extra = "#foryou #viralindonesia" if lang == "ID" else "#foryou #viral"
            out = out.rstrip() + "\n" + extra
    return out


def fix_tags(tags, cfg, title_core):
    tags = tags or []
    total = sum(len(t) for t in tags) + max(0, len(tags) - 1)
    if tags and total >= 100:
        return tags
    new = list(cfg["tags"])
    core_tag = re.sub(r"[^\w\s-]", "", title_core.lower()).strip()
    core_tag = re.sub(r"\s+", " ", core_tag)
    if 3 <= len(core_tag) <= 45:
        new.insert(0, core_tag)
    seen, out = set(), []
    for t in new:
        if t not in seen:
            seen.add(t)
            out.append(t)
    while sum(len(t) for t in out) + max(0, len(out) - 1) > 480 and len(out) > 3:
        out.pop()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    sepi = json.loads(SEPI.read_text())
    plan, results = {}, {}
    for slug, block in sepi.items():
        if slug == "inktime" or "videos" not in block or slug not in CFG:
            continue
        cfg = CFG[slug]
        vids = [v for v in block["videos"]
                if v["id"] not in EXCLUDE and v["id"] not in DUP_PRIVATE]
        if not vids:
            continue
        ids = [v["id"] for v in vids]
        items = yt_get(slug, "/videos",
                       {"id": ",".join(ids), "part": "snippet"}).get("items", [])
        snmap = {it["id"]: it["snippet"] for it in items}
        plan[slug] = []
        for v in vids:
            sn = snmap.get(v["id"])
            if sn is None:
                plan[slug].append({"id": v["id"], "error": "tidak ditemukan via API"})
                continue
            fmt = v["format"]
            meta = {"title": sn["title"], "description": sn.get("description", ""),
                    "tags": sn.get("tags", [])}
            score0, find0 = audit(meta, fmt)
            core = HASHTAG_RE.sub("", sn["title"]).strip()
            core = re.sub(r"\s+", " ", core).rstrip(" |")
            if fmt == "shorts":
                new_title = fix_shorts_title(sn["title"], cfg, v["id"])
            else:
                new_title = sn["title"]
            new_desc = fix_desc(sn.get("description", ""), fmt, cfg, v["id"],
                                TITLE_OVERRIDE.get(v["id"], core))
            new_tags = fix_tags(sn.get("tags", []), cfg, core)
            changes = []
            if new_title != sn["title"]:
                changes.append("judul")
            if new_desc != (sn.get("description", "") or ""):
                changes.append("deskripsi")
            if new_tags != (sn.get("tags", []) or []):
                changes.append("tags")
            plan[slug].append({
                "id": v["id"], "format": fmt, "views": v["views"],
                "privacy": v["privacy"], "skor_awal": score0,
                "temuan_awal": [f"{lv}: {m}" for lv, m in find0 if lv != "PASS"],
                "changes": changes,
                "title_old": sn["title"], "title_new": new_title,
                "desc_new": new_desc if "deskripsi" in changes else None,
                "tags_new": new_tags if "tags" in changes else None,
                "categoryId": sn["categoryId"],
                "langs": {k: sn[k] for k in ("defaultLanguage", "defaultAudioLanguage")
                          if sn.get(k)},
            })
        n_fix = sum(1 for p in plan[slug] if p.get("changes"))
        print(f"{slug}: {len(vids)} video, {n_fix} perlu diubah")
    PLAN.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    total = sum(len(v) for v in plan.values())
    nfix = sum(1 for v in plan.values() for p in v if p.get("changes"))
    print(f"TOTAL {total} video — {nfix} diubah, {total - nfix} sudah bagus")

    if not a.apply:
        print("[DRY-RUN] rencana ->", PLAN)
        return

    for slug, plist in plan.items():
        changed_ids = []
        for p in plist:
            if not p.get("changes"):
                continue
            items = yt_get(slug, "/videos",
                           {"id": p["id"], "part": "snippet"}).get("items", [])
            sn = items[0]["snippet"]
            new_snippet = {
                "title": p["title_new"],
                "description": p["desc_new"] if p["desc_new"] is not None
                               else sn.get("description", ""),
                "tags": p["tags_new"] if p["tags_new"] is not None
                        else sn.get("tags", []),
                "categoryId": sn["categoryId"],
            }
            new_snippet.update(p["langs"])
            yt_put(slug, "/videos", {"part": "snippet"},
                   {"id": p["id"], "snippet": new_snippet})
            changed_ids.append(p["id"])
            p["applied"] = True
            time.sleep(0.2)
        # verifikasi read-back 2 acak
        ver = []
        for vid in random.sample(changed_ids, min(2, len(changed_ids))):
            it = yt_get(slug, "/videos",
                        {"id": vid, "part": "snippet"}).get("items", [])
            want = next(p for p in plist if p["id"] == vid)
            ok = it and it[0]["snippet"]["title"] == want["title_new"]
            ver.append({"id": vid, "judul_cocok": bool(ok)})
        results[slug] = {"diubah": len(changed_ids), "verifikasi": ver}
        print(f"{slug}: {len(changed_ids)} diterapkan, verifikasi {ver}")
    RESULT.write_text(json.dumps(results, indent=1, ensure_ascii=False))
    print("Hasil ->", RESULT)


if __name__ == "__main__":
    main()
