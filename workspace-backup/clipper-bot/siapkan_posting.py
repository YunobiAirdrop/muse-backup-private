#!/usr/bin/env python3
"""
siapkan_posting.py — Siapkan paket posting untuk tiap klip.

Membaca brief.yaml + data/candidates.json + clips/klip-*.mp4, lalu membuat:
  - captions.txt : caption siap copy-paste per klip (hook + CTA + hashtag wajib)
  - manifest.json: daftar klip + durasi aktual (ffprobe) + status posting

Pemakaian:
  venv/bin/python siapkan_posting.py --brief brief.yaml
"""
import argparse
import glob
import json
import os
import subprocess

import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
CLIPS = os.path.join(BASE, "clips")


def durasi_video(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 1)
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default=os.path.join(BASE, "brief.yaml"))
    args = ap.parse_args()

    with open(args.brief, encoding="utf-8") as f:
        brief = yaml.safe_load(f)
    cand_path = os.path.join(DATA, "candidates.json")
    kandidat = {}
    if os.path.exists(cand_path):
        with open(cand_path, encoding="utf-8") as f:
            for k in json.load(f):
                kandidat[k["id"]] = k

    hashtags = " ".join(brief.get("hashtag_wajib", []))
    cta = str(brief.get("cta", {}).get("teks", ""))
    template = brief.get("caption_template", "{hook}\n\n{cta}\n{hashtags}")
    platform = brief.get("platform", [])
    campaign = brief.get("campaign", "")

    files = sorted(glob.glob(os.path.join(CLIPS, "klip-*.mp4")))
    if not files:
        print("Tidak ada klip di clips/ — jalankan render_klip.py dulu.")
        return

    captions = []
    manifest = []
    for fp in files:
        kid = int(os.path.basename(fp).split("-")[1].split(".")[0])
        k = kandidat.get(kid, {})
        # Hook caption = frasa viral yg sama dgn badge di video (data/hook-klip-NN.txt)
        hook_file = os.path.join(DATA, f"hook-klip-{kid:02d}.txt")
        if os.path.exists(hook_file):
            with open(hook_file, encoding="utf-8") as f:
                hook = " ".join(f.read().split()).capitalize()
        else:
            hook = " ".join(k.get("teks", "").split()[:12])
        dur = durasi_video(fp)
        captions.append(
            f"=== KLIP {kid:02d}: {os.path.basename(fp)} ({dur} dtk) ===\n"
            + template.format(hook=hook, cta=cta, hashtags=hashtags).strip()
            + "\n")
        manifest.append({
            "id": kid,
            "file": os.path.relpath(fp, BASE),
            "campaign": campaign,
            "durasi_detik": dur,
            "momen_sumber": {"mulai": k.get("mulai"), "selesai": k.get("selesai")},
            "skor_viral": k.get("skor"),
            "alasan": k.get("alasan", []),
            "platform": platform,
            "status": "siap_posting",
        })

    with open(os.path.join(BASE, "captions.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(captions))
    with open(os.path.join(BASE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"OK: {len(files)} klip -> captions.txt + manifest.json")


if __name__ == "__main__":
    main()
