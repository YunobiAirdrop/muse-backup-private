#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long history-en 2026-10-18.
Offset title card 3.0 dtk; bumper 4.291 dtk setelah beat-018 (berlaku beat-019+).
CTA 'Subscribe!' di 3 detik terakhir (aturan wajib channel). Hook text overlay
3 detik pertama tiap short. Tanpa karakter persen/apostrof/colon di drawtext.
Semua ffmpeg via ffmpeg-queue.sh.
Penggunaan: python3 potong_shorts_2026-10-18.py
Output: shorts/2026-10-18-s{1,2,3}.mp4 + shorts/shorts-plan-2026-10-18.json
"""
import subprocess, json, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
DATE = "2026-10-18"
VIDEO = os.path.join(BASE, "video", f"{DATE}.mp4")
DUR_JSON = os.path.join(BASE, "audio", DATE, f"durasi-beat-{DATE}.json")
PLAN_JSON = os.path.join(BASE, "shorts", f"shorts-plan-{DATE}.json")
OUTDIR = os.path.join(BASE, "shorts")
TITLE_CARD = 3.0
BUMPER = 4.291  # setelah beat-018, berlaku untuk beat-019 ke atas
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (id, beat_start, beat_end, hook_overlay_atas)
# s1: cold open flash -> loop kembali ke pertanyaan "how did we get here?"
# s2: keputusan + Enola Gay lepas landas -> "the decision was made"
# s3: warisan + Oppenheimer -> memorial
SHORTS = [
    ("s1", 1, 3, "THE DAY THE WORLD CHANGED"),
    ("s2", 20, 23, "THE DECISION WAS MADE"),
    ("s3", 30, 33, "A WARNING TO THE WORLD"),
]

def ts(sec):
    return f"{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{sec%60:06.3f}"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    assert os.path.exists(VIDEO), f"video long belum ada: {VIDEO}"
    d = json.load(open(DUR_JSON))
    start = {}
    t = TITLE_CARD
    for i in range(1, 37):
        if i == 19:
            t += BUMPER
        start[i] = t
        t += float(d[f"beat-{i:03d}"])
    meta = json.load(open(os.path.join(BASE, "script", f"meta-{DATE}.json")))
    titles = meta.get("shorts_titles", [])
    plan = {}
    for k, (sid, b0, b1, hook) in enumerate(SHORTS):
        ss = start[b0]
        dur_s = (start[b1] + float(d[f"beat-{b1:03d}"])) - start[b0]
        assert 25.0 <= dur_s <= 65.0, f"{sid}: durasi {dur_s:.1f}s di luar 25-65s"
        out = os.path.join(OUTDIR, f"{DATE}-{sid}.mp4")
        cta_file = f"/tmp/short-he18-cta.txt"
        open(cta_file, "w").write("Subscribe!")
        hook_file = f"/tmp/short-he18-hook-{sid}.txt"
        assert "%" not in hook and ":" not in hook and "'" not in hook
        open(hook_file, "w").write(hook)
        cta_start = max(0.0, dur_s - 3.0)
        vf = ("crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos,"
              f"drawtext=fontfile={FONT}:textfile={hook_file}:fontsize=58:"
              "fontcolor=white:borderw=3:bordercolor=black@0.85:"
              "x=(w-text_w)/2:y=120:box=1:boxcolor=black@0.6:boxborderw=20:"
              "enable='between(t,0,3)',"
              f"drawtext=fontfile={FONT}:textfile={cta_file}:fontsize=52:"
              "fontcolor=#ffd97a:borderw=2:bordercolor=black@0.8:"
              "x=(w-text_w)/2:y=h-220:box=1:boxcolor=black@0.6:boxborderw=20:"
              f"enable='between(t,{cta_start:.2f},{dur_s:.2f})'")
        subprocess.run([FFQ, "-y", "-ss", ts(ss), "-i", VIDEO,
                        "-t", str(round(dur_s, 2)),
                        "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-r", "30", "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", out],
                       capture_output=True, check=True)
        d_out = dur(out)
        assert abs(d_out - dur_s) < 2.0, f"{sid}: {d_out:.1f}s vs target {dur_s:.1f}s"
        vinfo = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=p=0", out],
            capture_output=True, text=True).stdout.strip()
        assert vinfo == "720,1280", f"{sid} RESOLUSI SALAH: {vinfo}"
        title = titles[k] if k < len(titles) else ""
        plan[sid] = {"beats": [b0, b1], "durasi_target": round(dur_s, 2),
                     "durasi_final": round(d_out, 2), "file": out,
                     "hook_overlay": hook, "title": title}
        print(f"OK {sid}: beats {b0}-{b1} = {dur_s:.2f}s -> {out} (final {d_out:.2f}s)", flush=True)
    json.dump(plan, open(PLAN_JSON, "w"), indent=1)
    print(f"plan: {PLAN_JSON}", flush=True)

if __name__ == "__main__":
    main()
