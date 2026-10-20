#!/usr/bin/env python3
"""Bandingkan 2 video: perceptual hash frame + kemiripan transkrip.
Usage: dup_compare.py <workdir> <vidA> <vidB>"""
import sys, subprocess, os, re, glob
from difflib import SequenceMatcher
from PIL import Image

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def find_mp4(work, vid):
    c = glob.glob(f"{work}/*__{vid}.mp4")
    return c[0] if c else None

def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    try: return float(r.stdout.strip())
    except: return 0

def avg_hash(path):
    im = Image.open(path).convert("L").resize((16, 16), Image.LANCZOS)
    px = list(im.getdata())
    avg = sum(px) / len(px)
    return int("".join("1" if p > avg else "0" for p in px), 2)

def hamming(a, b): return bin(a ^ b).count("1")

def vtt_text(work, vid):
    parts = []
    for f in sorted(glob.glob(f"{work}/*__{vid}*.vtt")):
        words = []
        for line in open(f, errors="ignore"):
            line = line.strip()
            if not line or "-->" in line or line.startswith("WEBVTT") \
               or re.match(r"^\d+$", line):
                continue
            line = re.sub(r"<[^>]+>", "", line)
            words.append(line)
        t = " ".join(words)
        if t not in parts: parts.append(t)
    return " ".join(parts)

def main():
    work, vidA, vidB = sys.argv[1], sys.argv[2], sys.argv[3]
    mp4a, mp4b = find_mp4(work, vidA), find_mp4(work, vidB)
    if not mp4a or not mp4b:
        print(f"TIDAK_DAPAT_DIBANDINGKAN: mp4 hilang A={bool(mp4a)} B={bool(mp4b)}")
        return
    da, db = duration(mp4a), duration(mp4b)
    print(f"durasi A={da:.1f}s B={db:.1f}s")
    fracs = [0.05, 0.3, 0.5, 0.7, 0.95]
    dists = []
    for i, f in enumerate(fracs):
        fa, fb = f"/tmp/dup_a_{i}.jpg", f"/tmp/dup_b_{i}.jpg"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{da*f:.1f}", "-i", mp4a,
             "-frames:v", "1", "-vf", "scale=320:-1", fa])
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{db*f:.1f}", "-i", mp4b,
             "-frames:v", "1", "-vf", "scale=320:-1", fb])
        if os.path.exists(fa) and os.path.exists(fb):
            d = hamming(avg_hash(fa), avg_hash(fb))
            dists.append(d)
            print(f"  frame@{f*100:.0f}%: hamming={d}")
    ta, tb = vtt_text(work, vidA), vtt_text(work, vidB)
    na = re.sub(r"\s+", " ", ta.lower()).strip()
    nb = re.sub(r"\s+", " ", tb.lower()).strip()
    ratio = SequenceMatcher(None, na, nb).ratio() if (na and nb) else 0.0
    print(f"transkrip: kata A={len(na.split())} B={len(nb.split())} ratio={ratio:.3f}")
    frame_ok = len(dists) >= 3 and (sum(dists) / len(dists)) < 12
    if frame_ok and ratio > 0.80:
        print("VERDICT: SAMA (konten identik)")
    elif frame_ok or ratio > 0.80:
        print("VERDICT: KEMUNGKINAN_SAMA (satu sinyal cocok)")
    else:
        print("VERDICT: BEDA")

if __name__ == "__main__":
    main()
