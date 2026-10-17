#!/usr/bin/env python3
"""Generate render.sh untuk Macam-macam Jenis Truk Part 1 versi kartun (keyframe)."""
from pathlib import Path

D = Path.home() / "workspace/macam-macam/work/truk-kartun"
W = D / "work"; I = D / "img"; T = D / "txt"
AU = Path.home() / "workspace/macam-macam/work/truk-part1/audio"
OUT = Path.home() / "workspace/macam-macam/output/truk-part1-kartun.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
Q = "~/workspace/youtube-otomatis/ffmpeg-queue.sh"
ENC = "-c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -r 30"

# item: (key, canvasW, canvasH, tw, wheels[(suffix,cx,cy,side)], wheel_bottom, bg_start)
# pusat & jari-jari roda diukur dari kanal alfa PNG keyed (detect_wheels4.py, terverifikasi
# cy+r == baris alfa terbawah gambar); side = 2r+10, crop terpusat di pusat roda.
ITEMS = [
    ("00", 1920, 1280, 920, [("wr", 585, 1043, 310), ("wf", 1326, 1041, 314)], 1193, 600),
    ("01", 1920, 1280, 920, [("wr1", 363, 1011, 310), ("wr2", 680, 1014, 304), ("wf", 1514, 1012, 308)], 1161, 1200),
    ("02", 1920, 1280, 920, [], 1143, 1800),
    ("03", 1920, 1280, 920, [("wf", 1444, 1017, 246), ("wr1", 905, 1016, 248), ("wr2", 635, 1016, 248)], 1135, 2400),
    ("04", 1920, 1280, 920, [("wr1", 414, 963, 282), ("wr2", 680, 965, 278), ("wf", 1410, 958, 288)], 1099, 3000),
    ("05", 1920, 1280, 920, [], 1213, 3600),
    ("06", 2736, 912, 1020, [], 829, 4200),
    ("07", 1920, 1280, 920, [], 1121, 800),
]
VO = {"title": 6.31, "00": 5.16, "01": 5.47, "02": 5.83, "03": 8.52,
      "04": 5.11, "05": 4.08, "06": 4.97, "07": 4.39, "cta": 11.69}
PAD = 0.7

def dt(textfile, fs, color, y, enable="gte(t,0.3)", bw=6):
    return (f"drawtext=fontfile={FONT}:textfile='{textfile}':fontsize={fs}:"
            f"fontcolor={color}:borderw={bw}:bordercolor=black:"
            f"x=(w-text_w)/2:y={y}:enable='{enable}'")

def truck_chain(idx_in, tw, cw, chh, wheels, spin=True):
    """Kembalikan (filter parts, label output, s) untuk layer truk+roda."""
    s = tw / cw
    th = round(chh * s)
    parts = [f"[{idx_in}:v]scale={tw}:{th}[trk]"]
    wparts = []
    for j, (suf, cx, cy, crop) in enumerate(wheels):
        cs = round(crop * s)
        rot = f",rotate=a='-2.4*t':c=none:ow=iw:oh=ih" if spin else ""
        parts.append(f"[{idx_in + 1 + j}:v]scale={cs}:{cs}{rot}[w{j}]")
        wparts.append((j, round((cx - crop / 2) * s), round((cy - crop / 2) * s)))
    return parts, wparts, s

lines = ["#!/bin/bash", "set -eu", f"Q={Q}", f"W={W}", f"I={I}", f"T={T}", f"AU={AU}", ""]
segs = []   # (segname, dur)
starts = {} # key -> start detik
t = 0.0

# ---------- TITLE ----------
dur = VO["title"] + PAD
starts["title"] = t; t += dur
parts, wparts, s = truck_chain(1, 780, 1920, 1280,
                               [("wr", 585, 1043, 310), ("wf", 1326, 1041, 314)])
xf = (1080 - 780) // 2
dist = 780 + xf + 80
yb = 1680 - round(1193 * s)
xexpr = f"{xf}-{dist}*exp(-2.0*t)"
yexpr = f"{yb}+5*sin(13.8*t)"
fc = [f"[0:v]scale=5760:1920,crop=1080:1920:x='4*n':y=0[bg]"] + parts
fc.append(f"[bg][trk]overlay=x='{xexpr}':y='{yexpr}'[v1]")
prev = "v1"
for n, (j, ox, oy) in enumerate(wparts):
    fc.append(f"[{prev}][w{j}]overlay=x='{xexpr}+{ox}':y='{yexpr}+{oy}'[v{n + 2}]")
    prev = f"v{n + 2}"
fc.append(f"[{prev}]" + ",".join([
    dt(f"{T}/title1.txt", 112, "yellow", 250, "gte(t,0.2)", 7),
    dt(f"{T}/title2.txt", 112, "white", 385, "gte(t,0.2)", 7),
    dt(f"{T}/title3.txt", 64, "0xff4040", 530, "gte(t,0.5)", 6),
    dt(f"{T}/sub.txt", 44, "yellow", 110, "gte(t,0.8)", 4)]) + "[out]")
lines.append(f"# TITLE dur={dur:.2f}")
lines.append(f"$Q -y -v error -framerate 30 -loop 1 -t {dur:.2f} -i \"$I/bg.webp\" "
             f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item00_key.png\" "
             f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item00_wr.png\" "
             f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item00_wf.png\" "
             f"-filter_complex \"{';'.join(fc)}\" -map \"[out]\" -t {dur:.2f} {ENC} \"$W/seg_title.mp4\"")
segs.append(("title", dur))

# ---------- ITEMS ----------
for (key, cw, chh, tw, wheels, bottom, bgx) in ITEMS:
    dur = VO[key] + PAD
    starts[key] = t; t += dur
    parts, wparts, s = truck_chain(1, tw, cw, chh, wheels)
    xf = (1080 - tw) // 2
    dist = tw + xf + 80
    yb = 1620 - round(bottom * s)
    xexpr = f"{xf}-{dist}*exp(-2.0*t)"
    yexpr = f"{yb}+5*sin(13.8*t)"
    fc = [f"[0:v]scale=5760:1920,crop=1080:1920:x='{bgx}+4*n':y=0[bg]"] + parts
    fc.append(f"[bg][trk]overlay=x='{xexpr}':y='{yexpr}'[v1]")
    prev = "v1"
    for n, (j, ox, oy) in enumerate(wparts):
        fc.append(f"[{prev}][w{j}]overlay=x='{xexpr}+{ox}':y='{yexpr}+{oy}'[v{n + 2}]")
        prev = f"v{n + 2}"
    fc.append(f"[{prev}]" + ",".join([
        dt(f"{T}/label{key}.txt", 96, "white", 240, "gte(t,0.3)", 6),
        dt(f"{T}/fakta{key}a.txt", 46, "white", 368, "gte(t,0.3)", 4),
        dt(f"{T}/fakta{key}b.txt", 46, "white", 428, "gte(t,0.3)", 4),
        dt(f"{T}/sub.txt", 44, "yellow", 110, "gte(t,0.8)", 4)]) + "[out]")
    ins = (f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$I/bg.webp\" "
           f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item{key}_key.png\"")
    for (suf, *_rest) in wheels:
        ins += f" -framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item{key}_{suf}.png\""
    lines.append(f"# ITEM {key} dur={dur:.2f}")
    lines.append(f"$Q -y -v error {ins} -filter_complex \"{';'.join(fc)}\" "
                 f"-map \"[out]\" -t {dur:.2f} {ENC} \"$W/seg_item{key}.mp4\"")
    segs.append((f"item{key}", dur))

# ---------- CTA ----------
dur = VO["cta"] + PAD
starts["cta"] = t; t += dur
total = t
s5 = 540 / 1920
yb0 = 1700 - round(1193 * s5)
yb5 = 1700 - round(1213 * s5)
fc = ["[0:v]scale=5760:1920,crop=1080:1920:x='2000+4*n':y=0[bg]",
      "[1:v]scale=540:360[t0]",
      "[2:v]scale=540:360[t5]",
      f"[bg][t0]overlay=x='20-620*exp(-2.0*t)':y='{yb0}+3*sin(9*t)'[v1]",
      f"[v1][t5]overlay=x='520+620*exp(-2.0*t)':y='{yb5}+3*sin(9*t+1.5)'[v2]",
      f"[v2]" + ",".join([
          dt(f"{T}/sub.txt", 118, "0xff4040", 240, "gte(t,0.3)", 7),
          dt(f"{T}/cta2.txt", 62, "white", 395, "gte(t,0.3)", 6)]) + "[out]"]
lines.append(f"# CTA dur={dur:.2f}")
lines.append(f"$Q -y -v error -framerate 30 -loop 1 -t {dur:.2f} -i \"$I/bg.webp\" "
             f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item00_key.png\" "
             f"-framerate 30 -loop 1 -t {dur:.2f} -i \"$W/item05_key.png\" "
             f"-filter_complex \"{';'.join(fc)}\" -map \"[out]\" -t {dur:.2f} {ENC} \"$W/seg_cta.mp4\"")
segs.append(("cta", dur))

# ---------- concat ----------
lines.append("")
lines.append("printf \"file '%s'\\n\" " + " ".join(f"\"$W/seg_{n}.mp4\"" for n, _ in segs) + " > \"$W/concat.txt\"")
lines.append("$Q -y -v error -f concat -safe 0 -i \"$W/concat.txt\" -c copy \"$W/video_bisu.mp4\"")

# ---------- audio mix ----------
aud = {"title": "hook", "cta": "cta"}
for k in [f"{i:02d}" for i in range(8)]:
    aud[k] = f"item{k}"
inputs = [f"-stream_loop -1 -i \"{Path.home()}/workspace/macam-macam/work/truk-part1/musik-latar.wav\""]
for k in ["title"] + [f"{i:02d}" for i in range(8)] + ["cta"]:
    inputs.append(f"-i \"$AU/{aud[k]}.mp3\"")
fc = [f"[0:a]atrim=0:{total:.2f},volume=0.14[mus]"]
labels = ["[mus]"]
for n, k in enumerate(["title"] + [f"{i:02d}" for i in range(8)] + ["cta"], start=1):
    dl = round((starts[k] + 0.35) * 1000)
    fc.append(f"[{n}:a]adelay={dl}|{dl}[v{n}]")
    labels.append(f"[v{n}]")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,alimiter=limit=0.95[aout]")
lines.append(f"$Q -y -v error {' '.join(inputs)} -filter_complex \"{';'.join(fc)}\" "
             f"-map \"[aout]\" -t {total:.2f} -c:a aac -b:a 160k \"$W/audio_mix.m4a\"")
lines.append(f"$Q -y -v error -i \"$W/video_bisu.mp4\" -i \"$W/audio_mix.m4a\" -c:v copy -c:a copy -shortest \"{OUT}\"")
lines.append(f"ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height -of default=noprint_wrappers=1 \"{OUT}\"")
lines.append(f"echo TOTAL_DUR={total:.2f}")

(D / "render.sh").write_text("\n".join(lines) + "\n")
print(f"render.sh ditulis: {len(segs)} segmen, total {total:.2f}s")
print("starts:", {k: round(v, 2) for k, v in starts.items()})
