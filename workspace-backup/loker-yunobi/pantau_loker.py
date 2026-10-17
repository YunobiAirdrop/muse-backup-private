#!/usr/bin/env python3
"""Pantau postingan loker baru di grup FB untuk M. Abdul Aziez.
Dipakai oleh cron harian. Output: ringkasan postingan loker <=26 jam terakhir
yang cocok (operator/produksi/pabrik/gudang/helper/packing) di area Tangerang.
"""
import json, subprocess, time, re, sys

GROUPS = {
    "383042389875315": "Info loker Tangerang (Cadas & sekitarnya)",
    "556619746513707": "INFO LOKER TANGERANG (NEWS)",
}
KEYWORDS = ["operator", "produksi", "pabrik", "gudang", "helper",
            "packing", "packer", "bongkar muat", "staff gudang"]
# Postingan yang jelas BUKAN tawaran kerja / tidak relevan
EXCLUDE = ["info loker dong", "cari loker", "nyari loker", "inpo loker",
           "loker buat", "buat cewe", "buat cowo", "umur", "jaga toko",
           "angkringan", "salon", "baby sister", "babysitter", "art ",
           "kurir", "sales promotor", "jual", "dijual", "lelang"]
SCAM_HINTS = ["adm ", "adm,", "admin fee", "pungli", "transfer dulu",
              "dijamin keterima", "no hoax"]

SINCE = time.time() - 26 * 3600


def fetch(gid):
    try:
        out = subprocess.run(["facebook-cli", "groups", "posts",
                              "--group-id", gid],
                             capture_output=True, text=True, timeout=60).stdout
        return json.loads(out).get("data", [])
    except Exception as e:
        print(f"[WARN] gagal baca grup {gid}: {e}", file=sys.stderr)
        return []


def main():
    hits = []
    for gid, gname in GROUPS.items():
        for p in fetch(gid):
            ts = p.get("creation_time", 0) or 0
            if ts < SINCE:
                continue
            content = (p.get("content") or "").strip()
            if not content:
                continue
            low = content.lower()
            if not any(k in low for k in KEYWORDS):
                continue
            if any(e in low for e in EXCLUDE):
                continue
            scam = [s for s in SCAM_HINTS if s in low]
            hits.append({
                "grup": gname,
                "waktu": time.strftime("%d %b %H:%M",
                                       time.localtime(ts)),
                "url": p.get("post_url", ""),
                "komentar": p.get("comment_count", 0),
                "scam_hint": bool(scam),
                "isi": content[:600],
            })
    hits.sort(key=lambda h: h["waktu"])
    print(json.dumps(hits, ensure_ascii=False, indent=1))
    print(f"\nTOTAL_HITS={len(hits)}", file=sys.stderr)


if __name__ == "__main__":
    main()
