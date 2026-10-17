#!/usr/bin/env python3
"""Lanjutan rakit_2026-10-13.py: hanya audio final + mux (segmen/overlay sudah OK).
Fix: amix duration=longest agar afull == durasi video (465.4s)."""
import subprocess, os, shutil

WS = "/home/hatch/workspace/youtube-otomatis/horror-en"
AUDIO = f"{WS}/audio/gabungan-2026-10-13.mp3"
SFX = f"{WS}/audio/sfx-crickets-bed.mp3"
TMPD = f"{WS}/video/_tmp_segs_20261013"
OUT = f"{WS}/video/2026-10-13.mp4"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

overlaid = os.path.join(TMPD, "overlaid.mp4")
total = dur(overlaid)
print(f"video overlaid: {total:.1f}s", flush=True)
final_a = os.path.join(TMPD, "final_audio.m4a")
af = (f"[1:a]volume=0.07,aloop=loop=-1:size=2000000,atrim=0:{total:.2f}[bed];"
      f"[0:a][bed]amix=inputs=2:duration=longest:dropout_transition=0,"
      f"afade=t=in:st=0:d=1,afade=t=out:st={total-3:.2f}:d=3[a]")
subprocess.run([FQ, "-y", "-i", AUDIO, "-stream_loop", "-1", "-i", SFX,
                "-filter_complex", af, "-map", "[a]",
                "-c:a", "aac", "-b:a", "128k", final_a],
               capture_output=True, check=True)
da = dur(final_a)
print(f"afull {da:.1f}s vs video {total:.1f}s", flush=True)
assert abs(da - total) < 1.5, f"afull {da:.1f}s vs video {total:.1f}s!"
subprocess.run([FQ, "-y", "-i", overlaid, "-i", final_a,
                "-c:v", "copy", "-c:a", "copy",
                "-shortest", "-movflags", "+faststart", OUT],
               capture_output=True, check=True)
d = dur(OUT)
print(f"OK: {OUT} ({d/60:.1f} menit)", flush=True)
shutil.rmtree(TMPD)
