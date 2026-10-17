#!/usr/bin/env python3
"""Batch produksi klip Nutriflakes: untuk tiap video materi valid,
jalankan deteksi_momen.py lalu render_klip.py, pindahkan klip ke clips/nutriflakes-<slug>/.

Jalankan di background: nohup venv/bin/python batch_nutriflakes.py > /tmp/clipper-batch.log 2>&1 &
Log progres bisa dipantau di /tmp/clipper-batch.log.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

import yaml

BASE = os.path.expanduser("~/workspace/clipper-bot")
TEMPLATE = os.path.join(BASE, "briefs", "template-nutriflakes.yaml")
VENV_PY = os.path.join(BASE, "venv", "bin", "python")


def slugify(name):
    s = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return (s[:36] or "video")


def main():
    videos = sorted(glob.glob(os.path.join(BASE, "materi", "nutriflakes", "*.mp4")))
    videos = [v for v in videos if os.path.getsize(v) > 5_000_000]
    print(f"[batch] {len(videos)} video valid, mulai.", flush=True)
    for v in videos:
        slug = slugify(os.path.basename(v)[:-4])
        brief = os.path.join(BASE, "briefs", f"brief-nutriflakes-{slug}.yaml")
        with open(TEMPLATE, encoding="utf-8") as f:
            b = yaml.safe_load(f)
        b["sumber_video"] = v
        with open(brief, "w", encoding="utf-8") as f:
            yaml.safe_dump(b, f, allow_unicode=True)
        print(f"[batch] === deteksi: {os.path.basename(v)}", flush=True)
        r = subprocess.run([VENV_PY, os.path.join(BASE, "deteksi_momen.py"),
                            "--brief", brief])
        if r.returncode != 0:
            print(f"[batch] GAGAL deteksi {v} — lanjut video berikutnya", flush=True)
            continue
        print(f"[batch] === render: {os.path.basename(v)}", flush=True)
        r = subprocess.run([VENV_PY, os.path.join(BASE, "render_klip.py"),
                            "--brief", brief])
        if r.returncode != 0:
            print(f"[batch] GAGAL render {v} — lanjut video berikutnya", flush=True)
            continue
        dest = os.path.join(BASE, "clips", f"nutriflakes-{slug}")
        os.makedirs(dest, exist_ok=True)
        moved = 0
        for k in glob.glob(os.path.join(BASE, "clips", "klip-*.mp4")):
            shutil.move(k, dest)
            moved += 1
        print(f"[batch] SELESAI {slug}: {moved} klip -> {dest}", flush=True)
    print("[batch] BATCH SELESAI", flush=True)


if __name__ == "__main__":
    sys.exit(main())
