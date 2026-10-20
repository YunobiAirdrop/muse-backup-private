#!/usr/bin/env python3
"""SRT + subtitle burn + text overlay Dark Mind Files 2026-10-20 (English).
Penggunaan:
  python3 subs_overlay_2026-10-20.py srt      -> tulis video/subs-2026-10-20.srt
  python3 subs_overlay_2026-10-20.py full    -> burn subs+overlay ke TEMP, verifikasi durasi, pindah ke final
Simpan salinan TANPA subs sebelum burn: video/2026-10-20-base.mp4 (untuk shorts).
Style subs teruji: FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45
Catatan drawtext: tanpa '%', escape ':' jadi '\\:', tanpa apostrof.
"""
import json, subprocess, os, sys, shutil

BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
DURJ = f"{BASE}/audio/durasi-beat-final-2026-10-20.json"
BEATSJ = f"{BASE}/script/beats-2026-10-20.json"
SRT = f"{BASE}/video/subs-2026-10-20.srt"
VIN = f"{BASE}/video/2026-10-20.mp4"
VINBASE = f"{BASE}/video/2026-10-20-base.mp4"
TMPD = f"{BASE}/video/_tmp_segs-2026-10-20"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OVERLAYS = [("beat-010", "YOUR SCROLL IS ENGINEERED"), ("beat-024", "ANGER KEEPS YOU SCROLLING"),
            ("beat-039", "SUBSCRIBE"), ("beat-048", "FOMO IS MANUFACTURED"),
            ("beat-066", "TAKE BACK CONTROL")]
SUBS_STYLE = "FontName=DejaVu Sans,FontSize=22,BorderStyle=1,Outline=2,Alignment=2,MarginV=45"

def cum_times():
    dj = json.load(open(DURJ))
    cum = {}
    t = 0.0
    for sid in dj["order"]:
        cum[sid] = (t, t + float(dj["durations"][sid]))
        t += float(dj["durations"][sid])
    return cum, t

def ts(s):
    ms = int(round((s - int(s)) * 1000))
    h, r = divmod(int(s), 3600); m, sec = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def wrap(text, width=44):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\\N".join(lines[:3])

def cmd_srt():
    beats = {b["id"]: b["narration"] for b in json.load(open(BEATSJ))["beats"]}
    cum, _ = cum_times()
    n = 0
    with open(SRT, "w") as f:
        for sid, (s, e) in cum.items():
            if sid == "bumper" or sid not in beats:
                continue
            n += 1
            f.write(f"{n}\n{ts(s)} --> {ts(e)}\n{wrap(beats[sid])}\n\n")
    print(f"OK SRT: {SRT} ({n} cues)")

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def cmd_full():
    cum, total = cum_times()
    if not os.path.exists(VINBASE):
        shutil.copy2(VIN, VINBASE)
        print(f"base tanpa subs disimpan: {VINBASE}")
    filters = [f"subtitles={SRT}:force_style='{SUBS_STYLE}'"]
    for bid, teks in OVERLAYS:
        s, e = cum[bid]
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.80:"
            f"enable='between(t,{s:.2f},{e:.2f})'"
        )
    vf = ",".join(filters)
    tmp = os.path.join(TMPD, "_video-subs-tmp.mp4")
    r = subprocess.run([FFQ, "-y", "-i", VIN, "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", tmp],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    got = dur(tmp)
    print(f"verifikasi durasi: target={total:.1f}s aktual={got:.1f}s", flush=True)
    if abs(got - total) >= 5:
        print(f"GAGAL verifikasi. Final TIDAK ditimpa: {tmp}"); sys.exit(2)
    shutil.move(tmp, VIN)
    print(f"OK final: {VIN} ({dur(VIN)/60:.2f} menit)")

if __name__ == "__main__":
    {"srt": cmd_srt, "full": cmd_full}[sys.argv[1]]()
