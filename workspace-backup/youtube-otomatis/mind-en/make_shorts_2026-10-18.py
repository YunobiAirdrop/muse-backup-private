#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari long Dark Mind Files 2026-10-18.
Caption bakar dari SRT (offset per klip), hook text on-screen 3 dtk pertama,
overlay CTA 3 dtk terakhir. Seamless loop: potong keras, tanpa fade.
Penggunaan: python3 make_shorts_2026-10-18.py [--dry]
"""
import json, subprocess, os, sys, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
VIN = f"{BASE}/video/2026-10-18-base.mp4"  # basis TANPA burned subs (hindari double caption)
DURJ = f"{BASE}/audio/durasi-beat-final-2026-10-18.json"
BEATSJ = f"{BASE}/script/beats-2026-10-18.json"
OUTD = f"{BASE}/shorts/2026-10-18"
TMPD = f"{BASE}/video/_tmp_segs-2026-10-18"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (nama, beat_awal, beat_akhir, hook_lines) — hook = kalimat paling menegangkan
SHORTS = [
    ("short1-mirroring", "beat-009", "beat-012",
     ["THEY COPY YOU", "ON PURPOSE"]),
    ("short2-vulnerability", "beat-018", "beat-021",
     ["THEIR PAIN", "IS A TRAP"]),
    ("short3-calmchaos", "beat-043", "beat-046",
     ["CALM IS NOT", "INNOCENCE"]),
]
# gaya caption shorts 1080x1920: di atas safe zone bawah (MarginV=70 ~= 465px)
CAP_STYLE = "FontName=DejaVu Sans,FontSize=14,BorderStyle=1,Outline=2,Alignment=2,MarginV=70"

def ts(s):
    ms = int(round((s - int(s)) * 1000))
    h, r = divmod(int(s), 3600); m, sec = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def wrap(text, width=30):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\\N".join(lines[:3])

def hook_vf(lines):
    parts = []
    for i, ln in enumerate(lines):
        y = 150 + i * 92
        parts.append(
            f"drawtext=fontfile={FONT}:text='{ln}':fontsize=64:fontcolor=white:"
            f"borderw=4:bordercolor=black:x=(w-text_w)/2:y={y}"
        )
    return ",".join(parts)

def main():
    dry = "--dry" in sys.argv
    dj = json.load(open(DURJ))
    beats = {b["id"]: b["narration"] for b in json.load(open(BEATSJ))["beats"]}
    cum, t = {}, 0.0
    for sid in dj["order"]:
        cum[sid] = (t, t + float(dj["durations"][sid]))
        t += float(dj["durations"][sid])
    os.makedirs(OUTD, exist_ok=True)
    for nama, b1, b2, hook_lines in SHORTS:
        s, e = cum[b1][0], cum[b2][1]
        durc = e - s
        print(f"  {nama}: {s:.1f}s -> {e:.1f}s = {durc:.1f} dtk", flush=True)
        if not (25 <= durc <= 50):
            print(f"    PERINGATAN: durasi di luar 25-50 dtk, sesuaikan range beat!")
        # SRT khusus klip (offset)
        srt = os.path.join(TMPD, f"{nama}.srt")
        srtd = os.path.join(OUTD, f"{nama}.srt")
        n = 0
        with open(srt, "w") as f:
            for sid in dj["order"]:
                if sid == "bumper" or sid not in beats:
                    continue
                ss, ee = cum[sid]
                if ee <= s or ss >= e:
                    continue
                n += 1
                f.write(f"{n}\n{ts(max(ss, s) - s)} --> {ts(min(ee, e) - s)}\n"
                        f"{wrap(beats[sid])}\n\n")
        shutil.copy(srt, srtd)
        out = f"{OUTD}/{nama}.mp4"
        if dry:
            continue
        cta = (f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY VIDEOS':fontsize=44:"
               f"fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-260:"
               f"enable='between(t,{durc-3:.2f},{durc:.2f})'")
        vf = (f"crop=608:1080:656:0,scale=1080:1920,"
              f"eq=contrast=1.06:saturation=0.95,"
              f"subtitles={srt}:force_style='{CAP_STYLE}',"
              + hook_vf(hook_lines) + "," + cta)
        r = subprocess.run([FFQ, "-y", "-ss", f"{s:.2f}", "-to", f"{e:.2f}",
                            "-i", VIN, "-vf", vf,
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr[-1500:]); raise SystemExit(1)
        print(f"  OK: {out}", flush=True)

if __name__ == "__main__":
    main()
