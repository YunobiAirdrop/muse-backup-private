#!/usr/bin/env python3
"""Unduh 8 klip terpilih dari Wikimedia Commons. Maks 2x percobaan/file, skip jika >200MB."""
import json, os, subprocess, sys

UA = "KisahDharmaVideo/1.0 (educational video production)"
OUT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)

PICKS = [
    # (slot, judul persis di candidates.json)
    ("kd-f01", "File:Aerial view of sand beach. Top view sea waves. Drone footage.webm"),
    ("kd-f02", "File:Waves crashing on rocks off Beach 4, Kalaloch Beach, Washington 02.webm"),
    ("kd-f03", "File:Large waves from Hurricane Marie at the Wedge, Newport Beach, California Video Don Ramey Logan.ogv"),
    ("kd-f04", "File:Strong waves from hurricane Erin at white crest beach, Wellfleet, MA august 22, 2025.webm"),
    ("kd-f05", "File:Ocean surface waves 05.ogv"),
    ("kd-f06", "File:Timelapse 2025 Kinnaur Monsoon.webm"),
    ("kd-f07", "File:Sea Waves - Tajpur Beach - East Midnapore 2015-05-02 9090.ogv"),
    ("kd-f08", "File:2022-08-06, Pacific Ocean sunset (Ocean Shores, Washington), 01.webm"),
]
BACKUPS = [
    ("kd-f08", "File:2022-08-06, Pacific Ocean sunset (Ocean Shores, Washington), 02.webm"),
    ("kd-f04", "File:Splashing water waves in Fiesa bay in Slovenia.ogv"),
    ("kd-f06", "File:Asperitas clouds in Santa Barbara in 2023 - timelapse.webm"),
    ("kd-f07", "File:Water waves in Herzliya beach.webm"),
]

cands = {c["title"]: c for c in json.load(open(os.path.join(OUT, "candidates.json")))}

def head_size(url):
    try:
        r = subprocess.run(["curl", "-sI", "-A", UA, "--max-time", "30", url],
                           capture_output=True, text=True, timeout=40)
        for line in r.stdout.splitlines():
            if line.lower().startswith("content-length:"):
                return int(line.split(":", 1)[1].strip())
    except Exception as e:
        print("  head gagal:", e)
    return None

def dl(url, dest):
    for attempt in (1, 2):
        r = subprocess.run(["curl", "-L", "-A", UA, "--max-time", "900",
                            "--retry", "1", "-o", dest, url])
        if r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 100000:
            return True
        print(f"  percobaan {attempt} gagal, rc={r.returncode}")
        if os.path.exists(dest): os.remove(dest)
    return False

results = {}
used_backups = {}
for slot, title in PICKS + BACKUPS:
    if slot in results: continue  # slot utama sudah berhasil
    c = cands.get(title)
    if not c:
        print(f"{slot}: TIDAK ADA di candidates: {title[:60]}"); continue
    url = c["url"]
    ext = os.path.splitext(url.split("?")[0])[1] or ".webm"
    dest = os.path.join(RAW, f"{slot}{ext}")
    sz = head_size(url)
    print(f"{slot}: {title[:60]} | size={sz/1e6 if sz else '?'} MB", flush=True)
    if sz and sz > 200_000_000:
        print("  TERLALU BESAR, skip ke cadangan"); continue
    if dl(url, dest):
        results[slot] = {"title": title, "path": dest, "url": url,
                         "license": c["license"], "author": c["author"],
                         "w": c["w"], "h": c["h"], "kw": c["kw"],
                         "backup_used": slot in [b[0] for b in BACKUPS] and title != dict(PICKS).get(slot)}
        print(f"  OK: {dest} ({os.path.getsize(dest)/1e6:.1f} MB)")
    else:
        print(f"  GAGAL 2x: {title[:60]}")

json.dump(results, open(os.path.join(OUT, "downloads.json"), "w"), indent=1, ensure_ascii=False)
print(f"\nBERHASIL: {len(results)}/8 slot")
for s, r in sorted(results.items()):
    print(f"  {s}: {r['title'][:60]}")
