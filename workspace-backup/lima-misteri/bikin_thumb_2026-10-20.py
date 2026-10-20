#!/usr/bin/env python3
"""Thumbnail Lima Misteri 2026-10-20: frame dari video + teks drawtext.
Teks <=4 kata, tanpa %, :, apostrof. 1280x720 untuk long, 1080x1920 untuk shorts.
"""
import subprocess, os, sys

BASE = "/home/hatch/workspace/lima-misteri"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LONGV = os.path.join(BASE, "video", "video-2026-10-20-final.mp4")
DJ = os.path.join(BASE, "audio", "2026-10-20-durations.json")

def beat_time(durs, n):
    cum = 0.0
    for i, d in enumerate(durs):
        if i + 1 == n:
            return cum + d / 2
        cum += d
    return cum

def grab_frame(src, ss, out, w, h):
    r = subprocess.run([FFQ, "-y", "-ss", str(round(ss, 1)), "-i", src,
                        "-vframes", "1", "-vf", f"scale={w}:{h}", out],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-600:]
    return out

def drawtext(inp, out, text, w, fontsize):
    # dua baris bila ada 3-4 kata: baris1 = kata pertama..?, tampil dramatis
    words = text.split()
    if len(words) >= 3:
        line1, line2 = words[0], " ".join(words[1:])
    else:
        line1, line2 = text, None
    parts = [f"drawtext=fontfile={FONT}:text='{line1}':fontsize={fontsize}:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-{fontsize+20}"]
    if line2:
        parts.append(f"drawtext=fontfile={FONT}:text='{line2}':fontsize={fontsize}:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+20")
    vf = ",".join(parts)
    r = subprocess.run([FFQ, "-y", "-i", inp, "-vf", vf, "-frames:v", "1", out],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-600:]
    return out

def main():
    import json
    durs = [float(v) for v in json.load(open(DJ)).values()]
    jobs = [
        ("thumbnail-2026-10-20-long.jpg", LONGV, beat_time(durs, 12), "PULAU HANTU JEPANG", 1280, 110),
        ("thumbnail-2026-10-20-s1.jpg", os.path.join(BASE, "shorts", "2026-10-20-s1.mp4"), 20, "KOTA MATI", 1080, 120),
        ("thumbnail-2026-10-20-s2.jpg", os.path.join(BASE, "shorts", "2026-10-20-s2.mp4"), 20, "UFO SEGITIGA", 1080, 120),
        ("thumbnail-2026-10-20-s3.jpg", os.path.join(BASE, "shorts", "2026-10-20-s3.mp4"), 20, "IBLIS JERSEY", 1080, 120),
    ]
    for name, src, ss, text, w, fs in jobs:
        h = 720 if w == 1280 else 1920
        raw = os.path.join(BASE, "_thumb_raw.jpg")
        grab_frame(src, ss, raw, w, h)
        out = os.path.join(BASE, name)
        drawtext(raw, out, text, w, fs)
        sz = os.path.getsize(out)
        print(f"OK {name} ({w}x{h}, {sz//1024}KB)")
    os.remove(raw)

if __name__ == "__main__":
    main()
