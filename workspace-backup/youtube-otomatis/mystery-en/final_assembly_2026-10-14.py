#!/usr/bin/env python3
"""Final assembly mystery-en 2026-10-14: base video (sudah ada audio voiceover)
+ ASS subtitle terbakar + text overlay momen kunci + CTA overlay + bumper
voice-clone disisipkan di tengah (bukan detik 0).
Penggunaan: python3 final_assembly_2026-10-14.py <base_mp4> <out_mp4>
"""
import re, subprocess, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
TGL = "2026-10-14"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-mystery-en.wav"

# overlay: (beat_1based, teks)
OVERLAYS = [
    (2, "A GHOST TESTIFIED"),
    (22, "IMPOSSIBLE"),
    (29, "BROKEN NECK"),
    (49, "MY PERSONAL THEORY"),
    (55, "WHAT DO YOU THINK"),
]

def esc_ass(s):
    return s.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")

def esc_dt(s):
    return s.replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")

def fmt_ass(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def main():
    base, out = sys.argv[1], sys.argv[2]
    durs = [float(x) for x in open(os.path.join(BASE, "audio", f"{TGL}.durations.txt")).read().split()]
    txt = open(os.path.join(BASE, "script", f"{TGL}.txt")).read()
    beats = re.findall(r"^BEAT (\d+)\nNARASI: (.*?)\nGAMBAR:", txt, re.M | re.S)
    assert len(beats) == len(durs), f"beats {len(beats)} != durs {len(durs)}"
    cum = [0.0]
    for d in durs:
        cum.append(cum[-1] + d)
    total = cum[-1]
    print(f"total {total:.0f}s ({total/60:.1f} mnt), {len(beats)} beats")

    # --- ASS subtitle ---
    ass = os.path.join(BASE, "video", f"{TGL}.ass")
    with open(ass, "w") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\n"
                "[V1 Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, "
                "BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginV\n"
                "Style: Nar,DejaVu Sans,44,&H00FFFFFF,&H00000000,&H80000000,-1,0,1,2.5,0,2,60\n"
                "[Events]\nFormat: Layer, Start, End, Style, Text\n")
        for i, (num, nar) in enumerate(beats):
            nar = esc_ass(" ".join(nar.split()))
            # pecah baris tiap ~42 karakter di spasi
            words, lines, cur = nar.split(), [], ""
            for w in words:
                if len(cur) + len(w) + 1 > 42 and cur:
                    lines.append(cur); cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur: lines.append(cur)
            f.write(f"Dialogue: 0,{fmt_ass(cum[i])},{fmt_ass(cum[i+1])},Nar,{'\\N'.join(lines)}\n")

    # --- titik sisip bumper: beat terdekat ke 50% ---
    mid = total / 2
    bumper_beat = min(range(len(durs)), key=lambda i: abs((cum[i] + cum[i+1]) / 2 - mid))
    bumper_t = cum[bumper_beat]  # awal beat
    print(f"bumper disisipkan di t={bumper_t:.1f}s (beat {bumper_beat+1})")

    # --- filter video: subtitles + overlays + CTA ---
    vf_parts = [f"subtitles={ass}"]
    for beat, teks in OVERLAYS:
        s, e = cum[beat - 1], cum[beat]
        vf_parts.append(
            f"drawtext=fontfile={FONT}:text='{esc_dt(teks)}':fontsize=58:fontcolor=white:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.80:"
            f"enable='between(t\\,{s:.2f}\\,{e:.2f})'")
    # CTA overlay 3 detik di 50%
    vf_parts.append(
        f"drawtext=fontfile={FONT}:text='SUBSCRIBE!':fontsize=72:fontcolor=yellow:"
        f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.12:"
        f"enable='between(t\\,{mid:.2f}\\,{mid+3:.2f})'")
    vf = ",".join(vf_parts)

    # --- filter audio: voiceover + bumper di tengah ---
    bd = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", BUMPER],
                        capture_output=True, text=True)
    bdur = float(bd.stdout.strip())
    print(f"bumper {bdur:.1f}s")
    af = (f"[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[vo];"
          f"[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,"
          f"adelay={int(bumper_t*1000)}|{int(bumper_t*1000)}[bp];"
          f"[vo][bp]amix=inputs=2:duration=first:dropout_transition=0[aout]")

    r = subprocess.run([FFQ, "-y", "-i", base, "-i", BUMPER,
                        "-filter_complex", af, "-map", "0:v", "-map", "[aout]",
                        "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-b:a", "128k",
                        "-movflags", "+faststart", "-shortest", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:]); sys.exit(1)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", out],
                       capture_output=True, text=True)
    print(f"OK: {out} ({float(d.stdout.strip())/60:.1f} menit)")
    print(f"BUMPER_AT={bumper_t:.1f}")

if __name__ == "__main__":
    main()
