#!/usr/bin/env python3
"""Fix audio concat 2026-10-19: re-encode (bukan -c copy) lalu final mux + verifikasi."""
import subprocess, os, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")

def qrun(args):
    print("Q:", " ".join(args[:5]), "...", flush=True)
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-3000:], file=sys.stderr); sys.exit(1)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def stream_durs(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    out = {}
    for line in r.stdout.strip().splitlines():
        p = line.split(",")
        if len(p) == 2 and p[1] not in ("N/A", ""):
            out[p[0]] = float(p[1])
    return out

auds = [os.path.join(BASE, "audio", f"ink1019-b{i:02d}.mp3") for i in range(1, 11)]
BUMP_D = dur("/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-inktime.wav")
expect = 2.5 + BUMP_D + sum(dur(a) for a in auds)
print("expected:", round(expect, 2), flush=True)

alst = os.path.join(TMP, "alist1019.txt")
afull = os.path.join(TMP, "afull1019.mp3")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c:a", "libmp3lame", afull])
a_dur = dur(afull)
print(f"afull={a_dur:.2f}s expected={expect:.2f}s", flush=True)
assert abs(a_dur - expect) < 2.0, "AUDIO STILL MISMATCH"

vconcat = os.path.join(TMP, "vconcat1019.mp4")
v_dur = dur(vconcat)
print(f"vconcat={v_dur:.2f}s", flush=True)
assert abs(v_dur - expect) < 2.0, "VIDEO MISMATCH"

final_tmp = os.path.join(TMP, "inktime-2026-10-19-long-TMP.mp4")
qrun(["-y", "-i", vconcat, "-i", afull,
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", final_tmp])
sd = stream_durs(final_tmp)
print("FINAL TMP per-stream:", sd, "expected:", round(expect, 2), flush=True)
assert "video" in sd and abs(sd["video"] - expect) < 5.0, "VIDEO STREAM OFF"
assert "audio" in sd and abs(sd["audio"] - expect) < 5.0, "AUDIO STREAM OFF"
final = os.path.join(BASE, "video", "inktime-2026-10-19-long.mp4")
shutil.move(final_tmp, final)
print("FINAL MOVED:", final, round(sd['video'], 1), "s", flush=True)
