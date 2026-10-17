#!/usr/bin/env python3
"""InkTime 2026-10-13 LONG assembly: The Bronze Age Collapse (10 segs, images + draw-reveal wipe).
Adapted from rakit_2026-10-11.py (proven template). No AI video clips (region 403 rule).
Bumper (4.593s) between beat 5 and 6 on clean white InkTime card.
Audio files: audio/beat-1013-NN.mp3 (NEW for Oct 13)."""
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
durs = [dur(os.path.join(BASE, "audio", f"beat-1013-{i:02d}.mp3")) for i in range(1, 11)]
print("audio durs:", [round(d, 1) for d in durs], "total:", round(sum(durs), 1),
      "bumper:", round(BUMP_D, 2), flush=True)
assert all(d > 2 for d in durs), "mp3 too short!"

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

CAPS = {
    1: [("THE WORLD ENDED IN 50 YEARS", .3, .55), ("HISTORY GREATEST MYSTERY", .6, .9)],
    2: [("A FIRST GLOBAL CIVILIZATION", .1, .3), ("MY BROTHER - AMARNA LETTERS", .4, .62), ("BRONZE = THE STEEL OF ITS DAY", .7, .92)],
    3: [("UGARIT DESTROYED ~1190 BC", .08, .28), ("ENEMY SHIPS APPROACHING", .45, .65), ("UNFIRED TABLETS", .75, .92)],
    4: [("MEDINET HABU INSCRIPTION", .05, .3), ("FIRST NAVAL BATTLE IN HISTORY", .55, .78)],
    5: [("A PERFECT STORM", .05, .25), ("WORST DROUGHT IN 3,000 YEARS", .45, .68), ("NO TIN = NO BRONZE", .75, .95)],
    6: [("THE ALIEN THEORY", .15, .4), ("THEORIES KEEP CHANGING", .5, .75)],
    7: [("HATTUSA BURNED, NEVER REBUILT", .1, .35), ("GREECE FORGOT HOW TO WRITE", .55, .8)],
    8: [("PHOENICIANS RISE", .05, .25), ("IRON BROKE THE MONOPOLY", .6, .85)],
    9: [("CHIPS = OUR NEW BRONZE", .15, .4), ("COMPLEXITY = FATAL FLAW", .55, .8)],
    10: [("MYSTERY STILL OPEN", .05, .3), ("COMMENT YOUR THEORY", .55, .8), ("WATCH THE 536 VIDEO", .85, .98)],
}
OVERLAYS = {1: ("THE WORLD ENDED", "between(t,0,4)"), 6: ("SUBSCRIBE!", "between(t,0,3)")}

# ---- 1. video: title + 10 segs + bumper via filter_complex ----
inputs = ["-f", "lavfi", "-t", str(TITLE_D), "-i", "color=white:s=1280x720:r=30"]
for i in range(1, 11):
    inputs += ["-loop", "1", "-t", f"{durs[i-1]:.3f}", "-i", f"gambar/ink1013-b{i:02d}.jpg"]

fc, labels = [], []
TITLE_SUB = "THE GREATEST MYSTERY"
fc.append(
    f"[0:v]format=yuv420p,setsar=1,{dt('INKTIME', size=110, y='(h-text_h)/2-100')},"
    f"{dt('THE BRONZE AGE COLLAPSE', size=44, y='(h-text_h)/2+40')},"
    f"{dt(TITLE_SUB, size=30, y='(h-text_h)/2+110')},"
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
        f.write(f"file '{os.path.join(BASE, 'audio', f'beat-1013-{i:02d}.mp3')}'\n")
    f.write(f"file '{os.path.join(TMP, 'bumper.mp3')}'\n")
    for i in range(6, 11):
        f.write(f"file '{os.path.join(BASE, 'audio', f'beat-1013-{i:02d}.mp3')}'\n")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy",
      os.path.join(TMP, "afull.mp3")])
print("AUDIO DONE", flush=True)
a_dur = dur(os.path.join(TMP, "afull.mp3"))
expect = TITLE_D + BUMP_D + sum(durs)
print(f"afull.mp3={a_dur:.2f}s expected={expect:.2f}s", flush=True)
assert abs(a_dur - expect) < 1.5, "AUDIO DURATION MISMATCH"

# ---- 3. final: grain + mux ----
qrun(["-y", "-i", os.path.join(TMP, "vconcat.mp4"), "-i", os.path.join(TMP, "afull.mp3"),
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k",
      os.path.join(BASE, "video", "inktime-2026-10-13-long.mp4")])
print("FINAL DONE", flush=True)

# ---- chapters ----
titles = {1: "The world ended in 50 years", 2: "A golden, global world",
          3: "The last letters of Ugarit", 4: "The Sea Peoples",
          5: "A perfect storm", 6: "No simple answer",
          7: "A civilizational hard reset", 8: "From ashes: the Iron Age",
          9: "Are we the Bronze Age?", 10: "History can go backward"}
print("CHAPTERS:", flush=True)
t = 0.0
print(f"0:00 Intro - The Bronze Age Collapse", flush=True)
t = TITLE_D
for i in range(1, 11):
    m, s = int(t // 60), int(t % 60)
    print(f"{m}:{s:02d} {titles[i]}", flush=True)
    t += durs[i - 1]
    if i == 5:
        t += BUMP_D
print(f"TOTAL VIDEO: {TITLE_D + BUMP_D + sum(durs):.1f}s", flush=True)
