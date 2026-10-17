#!/usr/bin/env python3
"""Hapus video lokal yang SUDAH terupload ke YouTube (kebijakan user 2026-10-15:
habis upload langsung hapus; YouTube jadi arsip).

Bukti upload = upload-*.json berisi video_id/url, atau retry-queue/done/*.json.
DILINDUNGI (jangan hapus): semua video_path di retry-queue/*.json (bank aktif),
dan shorts_bank (shorts belum tentu terupload).

Mode: --dry-run (default) hanya daftar; --execute benar-benar hapus.
"""
import json, os, re, sys, glob

ROOT = os.path.expanduser("~/workspace/youtube-otomatis")
DRY = "--execute" not in sys.argv

def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return None

# 1. Kumpulkan path yang DILINDUNGI (bank aktif)
protected = set()
for p in glob.glob(f"{ROOT}/retry-queue/*.json"):
    d = load(p)
    if d and d.get("video_path"):
        protected.add(os.path.abspath(os.path.expanduser(d["video_path"])))
print(f"Bank aktif dilindungi: {len(protected)} video")

# 2. Kumpulkan kandidat hapus dari bukti upload JSON
candidates = {}  # abspath -> sumber bukti
patterns = ["upload-*.json", "upload-result*.json", "upload-hasil*.json"]
seen = set()
for pat in patterns:
    for p in glob.glob(f"{os.path.expanduser('~/workspace')}/**/{pat}", recursive=True):
        if p in seen or "/retry-queue/" in p:
            continue
        seen.add(p)
        d = load(p)
        if isinstance(d, list):
            d = d[0] if d and isinstance(d[0], dict) else None
        if not isinstance(d, dict):
            continue
        # ambil video ID dari berbagai nama field
        vid = d.get("video_id") or d.get("videoId") or d.get("id")
        if not vid and d.get("url"):
            m = re.search(r"(?:youtu\.be/|v=)([\w-]{6,})", d["url"])
            vid = m.group(1) if m else None
        if not vid:
            continue  # bukan bukti upload sukses
        chdir = os.path.dirname(p)
        # cari path lokal: field eksplisit dulu
        local = None
        for key in ("video_path", "video", "file", "local_path"):
            if d.get(key):
                v = os.path.expanduser(d[key])
                local = v if os.path.isabs(v) else os.path.join(chdir, v)
                break
        # konvensi: upload-YYYY-MM-DD*.json -> video/YYYY-MM-DD.mp4
        if not local:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p))
            if m:
                for cand in (os.path.join(chdir, "video", f"{m.group(1)}.mp4"),
                             os.path.join(chdir, f"{m.group(1)}.mp4")):
                    if os.path.exists(cand):
                        local = cand
                        break
        # shorts_bank = BELUM tentu upload -> jangan hapus
        # (tanpa fallback tebak-tebakan: lebih baik kelewat daripada salah hapus)
        if local:
            ap = os.path.abspath(local)
            if os.path.exists(ap) and ap not in protected:
                candidates[ap] = f"{p} -> yt:{vid}"

# 3. Dari retry-queue/done/*.json (pasti sudah terupload)
for p in glob.glob(f"{ROOT}/retry-queue/done/*.json"):
    d = load(p)
    if d and d.get("video_path"):
        ap = os.path.abspath(os.path.expanduser(d["video_path"]))
        if os.path.exists(ap) and ap not in protected:
            candidates[ap] = f"{p} (done)"

print(f"Kandidat hapus: {len(candidates)} file")
total = 0
for ap, src in sorted(candidates.items()):
    sz = os.path.getsize(ap)
    total += sz
    print(f"  {sz/1024/1024:8.1f} MB  {ap}\n           bukti: {src}")
print(f"Total: {total/1024/1024:.1f} MB")

if DRY:
    print("\n[DRY-RUN] tambah --execute untuk hapus beneran.")
else:
    for ap in candidates:
        os.remove(ap)
        print(f"HAPUS: {ap}")
    print(f"\nSelesai: {len(candidates)} file dihapus, {total/1024/1024:.1f} MB bebas.")
