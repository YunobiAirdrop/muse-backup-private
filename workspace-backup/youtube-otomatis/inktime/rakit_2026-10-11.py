#!/usr/bin/env python3
"""InkTime 2026-10-11 assembly: 1 render video (filter_complex) + bumper + concat audio + final mux.
All 10 segments from sketch images + draw-reveal wipe (AI clips blocked region 403, fallback to images).
Bumper (4.593s, owner voice) inserted between beat 5 and 6."""
import subprocess, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")
os.makedirs(TMP, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-inktime.wav"

def qrun(args):
    print("Q:", " ".join(args[:6]), "...", flush=True)
    r = subprocess.run([Q] + args, capture_output=True, text=True, cwd=BASE)
    if r.returncode != 0:
        print("FFMPEG FAIL:", r.stderr[-3000:], file=sys.stderr)
        sys.exit(1)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

TITLE_D = 2.5
BUMP_D = dur(BUMPER)
durs = [dur(os.path.join(BASE, "audio", f"beat-{i:02d}.mp3")) for i in range(1, 11)]
print("audio durs:", [round(d, 1) for d in durs], "total:", round(sum(durs), 1),
      "bumper:", round(BUMP_D, 2), flush=True)

def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

def dt(text, enable=None, size=64, y="h-120", box=0):
    s = (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontcolor=black@0.92:"
         f"fontsize={size}:x=(w-text_w)/2:y={y}:borderw=3:bordercolor=white")
    if box:
        s += ":box=1:boxcolor=white@0.9:boxborderw=12"
    if enable:
        s += f":enable='{enable}'"
    return s

def cap(text, d, f0, f1, size=36):
    return dt(text, enable=f"between(t,{d*f0:.2f},{d*f1:.2f})", size=size, y="h-64", box=1)

# ---- captions per beat: (text, start_frac, end_frac) ----
CAPS = {
    1: [("A MEDIEVAL PEASANT", .25, .45), ("ECONOMISTS DID THE MATH", .55, .8)],
    2: [("1,620 HOURS A YEAR", .1, .28), ("1,791 HOURS TODAY", .45, .62), ("THE GAP: 170 HOURS", .72, .92)],
    3: [("80 FEAST DAYS", .1, .3), ("130 DAYS OFF A YEAR", .6, .85)],
    4: [("THE INDUSTRIOUS REVOLUTION", .05, .3), ("THEY CHOSE TO WORK MORE", .45, .7), ("SUGAR. TEA. COFFEE.", .75, .95)],
    5: [("PEASANT LIFE WAS BRUTAL", .05, .25), ("16-HOUR HARVEST DAYS", .4, .6), ("DEAD BY 45", .72, .92)],
    6: [("FEWER HOURS, HARDER LIFE", .12, .35), ("MY STUDENT ASKED ME", .5, .75)],
    7: [("WHO CONTROLS YOUR HOURS?", .05, .3), ("THE INBOX REPLACED THE HARVEST", .6, .85)],
    8: [("THE MODERN TRAP", .05, .25), ("RICHER, MORE EXHAUSTED", .45, .7)],
    9: [("GERMANY: UNDER 1,400 HRS", .05, .3), ("FREE TIME IS TAKEN", .55, .8)],
    10: [("WOULD YOU TRADE?", .05, .3), ("SUBSCRIBE + COMMENT", .6, .85)],
}
OVERLAYS = {1: ("YOU WORK MORE", "between(t,0,4)"), 6: ("SUBSCRIBE!", "between(t,0,3)")}

# ---- 1. video: title + 10 segs + bumper via filter_complex ----
inputs = ["-f", "lavfi", "-t", str(TITLE_D), "-i", "color=white:s=1280x720:r=30"]
for i in range(1, 11):
    inputs += ["-loop", "1", "-t", f"{durs[i-1]:.3f}", "-i", f"gambar/ink1011-b{i:02d}.jpg"]

fc, labels = [], []
fc.append(
    f"[0:v]format=yuv420p,setsar=1,{dt('INKTIME', size=110, y='(h-text_h)/2-100')},"
    f"{dt('YOU WORK MORE THAN A MEDIEVAL PEASANT', size=40, y='(h-text_h)/2+60')},"
    f"trim=0:{TITLE_D},setpts=PTS-STARTPTS[s0]")
labels.append("[s0]")
for i in range(1, 11):
    d = durs[i - 1]
    chain = f"[{i}:v]scale=1280:720,setsar=1,drawbox=x='iw*t/{d:.3f}':y=0:w=iw:h=ih:color=white:t=fill"
    if i in OVERLAYS:
        chain += "," + dt(OVERLAYS[i][0], enable=OVERLAYS[i][1], size=72, y="(h-text_h)/2")
    for (t, f0, f1) in CAPS[i]:
        chain += "," + cap(t, d, f0, f1)
    chain += f",trim=0:{d:.3f},setpts=PTS-STARTPTS[s{i}]"
    fc.append(chain)
    labels.append(f"[s{i}]")
# bumper seg: plain white card + centered "InkTime" (clean, no collision with image text)
d = BUMP_D
fc.append(
    f"[11:v]format=yuv420p,setsar=1,"
    f"{dt('InkTime', size=96, y='(h-text_h)/2')},"
    f"trim=0:{d:.3f},setpts=PTS-STARTPTS[sb]")
labels.append("[sb]")

order = ["[s0]"] + [f"[s{i}]" for i in range(1, 6)] + ["[sb]"] + [f"[s{i}]" for i in range(6, 11)]
fc.append("".join(order) + f"concat=n={len(order)}:v=1:a=0[vcat]")
inputs += ["-f", "lavfi", "-t", f"{BUMP_D:.3f}", "-i", "color=white:s=1280x720:r=30"]
qrun(["-y"] + inputs + ["-filter_complex", ";".join(fc),
      "-map", "[vcat]", "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
      os.path.join(TMP, "vconcat.mp4")])
print("VIDEO CONCAT DONE", flush=True)

# ---- 2. audio: silence + beats 1-5 + bumper + beats 6-10 ----
qrun(["-y", "-f", "lavfi", "-t", str(TITLE_D), "-i", "anullsrc=r=44100:cl=stereo",
      "-c:a", "libmp3lame", os.path.join(TMP, "silence.mp3")])
qrun(["-y", "-i", BUMPER, "-c:a", "libmp3lame", os.path.join(TMP, "bumper.mp3")])
alst = os.path.join(TMP, "alist.txt")
with open(alst, "w") as f:
    f.write(f"file '{os.path.join(TMP, 'silence.mp3')}'\n")
    for i in range(1, 6):
        f.write(f"file '{os.path.join(BASE, 'audio', f'beat-{i:02d}.mp3')}'\n")
    f.write(f"file '{os.path.join(TMP, 'bumper.mp3')}'\n")
    for i in range(6, 11):
        f.write(f"file '{os.path.join(BASE, 'audio', f'beat-{i:02d}.mp3')}'\n")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy",
      os.path.join(TMP, "afull.mp3")])
print("AUDIO DONE", flush=True)

# ---- 3. final: grain + mux ----
qrun(["-y", "-i", os.path.join(TMP, "vconcat.mp4"), "-i", os.path.join(TMP, "afull.mp3"),
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", os.path.join(BASE, "video", "inktime-2026-10-11-long.mp4")])
print("FINAL DONE", flush=True)

# ---- chapters ----
titles = {1: "You work MORE than a medieval peasant", 2: "The shocking math",
          3: "Why: 130 days off", 4: "The industrious revolution",
          5: "The brutal trade-off", 6: "Fewer hours, harder life",
          7: "It is about control", 8: "The modern trap",
          9: "Free time is taken, not given", 10: "Would YOU trade?"}
t = 0.0
print("CHAPTERS:", flush=True)
m, s = int(t // 60), int(t % 60)
print(f"{m}:{s:02d} {titles[1]}", flush=True)
t = TITLE_D + durs[0]
for i in range(2, 11):
    m, s = int(t // 60), int(t % 60)
    print(f"{m}:{s:02d} {titles[i]}", flush=True)
    t += durs[i - 1]
    if i == 5:
        t += BUMP_D  # bumper sits between beat 5 and 6
print(f"TOTAL VIDEO: {TITLE_D + BUMP_D + sum(durs):.1f}s", flush=True)
