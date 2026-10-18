#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long history-en 2026-10-18 (v2).
Sumber: video/_tmp_mux_2026-10-18.mp4 (BERSIH: tanpa subtitle/overlay burn-in).
Subtitle dibuat ulang sebagai ASS khusus vertikal (PlayRes 720x1280, FontSize 44)
+ overlay drawtext momen kunci + hook 3 dtk pertama + CTA 'Subscribe!' 3 dtk terakhir.
Tanpa karakter persen/colon/apostrof di drawtext. Semua ffmpeg via ffmpeg-queue.sh.
Penggunaan: python3 potong_shorts_2026-10-18.py
Output: shorts/2026-10-18-s{1,2,3}.mp4 + shorts/shorts-plan-2026-10-18.json
"""
import subprocess, json, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
DATE = "2026-10-18"
VIDEO = os.path.join(BASE, "video", "_tmp_mux_2026-10-18.mp4")  # bersih, tanpa burn-in
DUR_JSON = os.path.join(BASE, "audio", DATE, f"durasi-beat-{DATE}.json")
PLAN_JSON = os.path.join(BASE, "shorts", f"shorts-plan-{DATE}.json")
OUTDIR = os.path.join(BASE, "shorts")
TITLE_CARD = 3.0
BUMPER = 4.291  # setelah beat-018, berlaku untuk beat-019 ke atas
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# (id, beat_start, beat_end, hook_overlay_pendek)
SHORTS = [
    ("s1", 1, 3, "THE 8.15 AM FLASH"),
    ("s2", 20, 23, "ONE PLANE. ONE BOMB."),
    ("s3", 30, 33, "I AM BECOME DEATH"),
]

def ts(sec):
    return f"{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{sec%60:06.3f}"

def ass_ts(sec):
    sec = max(0.0, sec)
    h = int(sec // 3600); m = int((sec % 3600) // 60)
    s = int(sec % 60); cs = int(round((sec - int(sec)) * 100))
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def wrap(text, width=26):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\\N".join(lines[:2])

def build_ass(sid, beats, b0, b1, starts, durs, ss):
    lines = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 720",
             "PlayResY: 1280", "WrapStyle: 2", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
             "BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, "
             "MarginL, MarginR, MarginV, Encoding",
             "Style: Default,DejaVu Sans,44,&H00FFFFFF,&H00000000,&H80000000,"
             "0,0,1,2,0,2,20,20,110,1",
             "", "[Events]",
             "Format: Layer, Start, End, Style, Text"]
    for x in beats:
        n = int(x["beat"].split("-")[1])
        if not (b0 <= n <= b1):
            continue
        txt = x["text"].replace("[JEDA]", " ").replace("{", "").replace("}", "")
        while "  " in txt:
            txt = txt.replace("  ", " ")
        s = starts[n] - ss
        e = s + durs[f"beat-{n:03d}"]
        lines.append(f"Dialogue: 0,{ass_ts(s)},{ass_ts(e)},Default,{wrap(txt.strip())}")
    path = f"/tmp/short-he18-{sid}.ass"
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return path

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    assert os.path.exists(VIDEO), f"video bersih belum ada: {VIDEO}"
    d = json.load(open(DUR_JSON))
    beats = json.load(open(os.path.join(BASE, "beats", f"beats-{DATE}.json")))
    start = {}
    t = TITLE_CARD
    for i in range(1, 37):
        if i == 19:
            t += BUMPER
        start[i] = t
        t += float(d[f"beat-{i:03d}"])
    overlays = {}
    for x in beats:
        n = int(x["beat"].split("-")[1])
        if x.get("overlay"):
            assert "%" not in x["overlay"] and ":" not in x["overlay"] \
                and "'" not in x["overlay"], f"overlay berbahaya: {x['overlay']}"
            overlays[n] = x["overlay"]
    meta = json.load(open(os.path.join(BASE, "script", f"meta-{DATE}.json")))
    titles = meta.get("shorts_titles", [])
    plan = {}
    for k, (sid, b0, b1, hook) in enumerate(SHORTS):
        assert "%" not in hook and ":" not in hook and "'" not in hook
        ss = start[b0]
        dur_s = (start[b1] + float(d[f"beat-{b1:03d}"])) - start[b0]
        assert 25.0 <= dur_s <= 65.0, f"{sid}: durasi {dur_s:.1f}s di luar 25-65s"
        out = os.path.join(OUTDIR, f"{DATE}-{sid}.mp4")
        ass = build_ass(sid, beats, b0, b1, start, d, ss)
        cta_file = "/tmp/short-he18-cta.txt"
        open(cta_file, "w").write("Subscribe!")
        hook_file = f"/tmp/short-he18-hook-{sid}.txt"
        open(hook_file, "w").write(hook)
        cta_start = max(0.0, dur_s - 3.0)
        filters = ["crop=406:720:(in_w-406)/2:0", "scale=720:1280:flags=lanczos",
                   f"subtitles={ass}"]
        # overlay momen kunci (waktu relatif thd awal short)
        for n in range(b0, b1 + 1):
            if n in overlays:
                of = f"/tmp/short-he18-ovl-{sid}-{n}.txt"
                open(of, "w").write(overlays[n])
                os_ = start[n] - ss
                oe = os_ + float(d[f"beat-{n:03d}"]) * 0.55
                filters.append(
                    f"drawtext=fontfile={FONT}:textfile={of}:fontsize=44:"
                    "fontcolor=white:borderw=2:bordercolor=black@0.8:"
                    "x=(w-text_w)/2:y=h-430:box=1:boxcolor=black@0.55:boxborderw=20:"
                    f"enable='between(t,{os_:.2f},{oe:.2f})'")
        filters.append(
            f"drawtext=fontfile={FONT}:textfile={hook_file}:fontsize=48:"
            "fontcolor=white:borderw=3:bordercolor=black@0.85:"
            "x=(w-text_w)/2:y=90:box=1:boxcolor=black@0.6:boxborderw=18:"
            "enable='between(t,0,3)'")
        filters.append(
            f"drawtext=fontfile={FONT}:textfile={cta_file}:fontsize=52:"
            "fontcolor=#ffd97a:borderw=2:bordercolor=black@0.8:"
            "x=(w-text_w)/2:y=h-330:box=1:boxcolor=black@0.6:boxborderw=20:"
            f"enable='between(t,{cta_start:.2f},{dur_s:.2f})'")
        vf = ",".join(filters)
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
