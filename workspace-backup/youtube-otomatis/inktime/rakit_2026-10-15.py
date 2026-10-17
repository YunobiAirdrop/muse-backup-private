#!/usr/bin/env python3
"""InkTime 2026-10-15 LONG assembly: The Library of Alexandria (10 segs, portrait images + draw-reveal wipe).
No AI video clips (region 403 rule, same as 2026-10-13). Bumper between beat 5 and 6.
Images are 1280x1920 portrait -> fit height 1080 + white pad to 1920x1080.
Audio files: audio/ink1015-bN.mp3 (note: no zero-pad)."""
import subprocess, os, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TMP = os.path.join(BASE, "video", "tmp")
os.makedirs(TMP, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-inktime.wav"
W, H = 1920, 1080

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
imgs = [os.path.join(BASE, "gambar", f"ink1015-b{i:02d}.jpg") for i in range(1, 11)]
auds = [os.path.join(BASE, "audio", f"ink1015-b{i}.mp3") for i in range(1, 11)]
for p in imgs + auds:
    assert os.path.exists(p), f"MISSING {p}"
durs = [dur(a) for a in auds]
print("audio durs:", [round(d, 1) for d in durs], "total:", round(sum(durs), 1),
      "bumper:", round(BUMP_D, 2), flush=True)
assert all(d > 2 for d in durs), "mp3 too short!"

def esc(t):
    return (t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "").replace("%", "")
             .replace(",", "\\,"))

def dt(text, enable=None, size=88, y="(h-text_h)/2", box=0):
    s = (f"drawtext=fontfile={FONT}:text='{esc(text)}':fontcolor=black@0.92:"
         f"fontsize={size}:x=(w-text_w)/2:y={y}:borderw=3:bordercolor=white")
    if box:
        s += ":box=1:boxcolor=white@0.9:boxborderw=12"
    if enable:
        s += f":enable='{enable}'"
    return s

def cap(text, d, f0, f1, size=50):
    return dt(text, enable=f"between(t,{d*f0:.2f},{d*f1:.2f})", size=size, y="h-90", box=1)

CAPS = {
    1: [("THE LIBRARY DID NOT BURN", .05, .35), ("ALMOST ALL OF IT IS GONE", .55, .9)],
    2: [("EVERY BOOK IN THE WORLD", .1, .3), ("SCHOLARS PAID TO THINK", .55, .8)],
    3: [("EVERY SHIP SEARCHED", .05, .28), ("ORIGINALS KEPT\\, COPIES RETURNED", .5, .75)],
    4: [("40\\,000 TO 400\\,000 SCROLLS", .08, .3), ("THE ANCIENT GOOGLE", .55, .8)],
    5: [("A STICK AND A WELL", .05, .28), ("THE SIZE OF THE EARTH\\, WITHIN 2 PERCENT", .5, .75)],
    6: [("SO CONFIDENT\\, SO WRONG", .15, .4), ("THE FIRE PART IS NEXT", .55, .8)],
    7: [("THE HARBOR FIRE\\, 48 BC", .05, .3), ("THE LIBRARY SURVIVED", .55, .8)],
    8: [("NO SINGLE FIRE", .05, .3), ("DEATH BY NEGLECT", .55, .8)],
    9: [("90 PLAYS\\, ONLY 7 SURVIVE", .1, .35), ("WHAT FADED\\, NOT WHAT BURNED", .6, .85)],
    10: [("KNOWLEDGE IS NOT AUTOMATIC", .05, .3), ("SAVE ONE SCROLL - COMMENT", .5, .75), ("WATCH THE BRONZE AGE VIDEO", .85, .98)],
}
OVERLAYS = {1: ("THE LIBRARY DID NOT BURN", "between(t,0,4)"), 6: ("SUBSCRIBE!", "between(t,0,3)")}

# ---- 1. video: title + 10 segs + bumper via filter_complex ----
inputs = ["-f", "lavfi", "-t", str(TITLE_D), "-i", f"color=white:s={W}x{H}:r=30"]
for i in range(1, 11):
    inputs += ["-loop", "1", "-t", f"{durs[i-1]:.3f}", "-i", f"gambar/ink1015-b{i:02d}.jpg"]

fc, labels = [], []
fc.append(
    f"[0:v]format=yuv420p,setsar=1,{dt('INKTIME', size=150, y='(h-text_h)/2-140')},"
    f"{dt('THE LIBRARY OF ALEXANDRIA', size=64, y='(h-text_h)/2+50')},"
    f"{dt('WHAT WE ACTUALLY LOST', size=44, y='(h-text_h)/2+140')},"
    f"trim=0:{TITLE_D},setpts=PTS-STARTPTS[s0]")
labels.append("[s0]")
for i in range(1, 11):
    d = durs[i - 1]
    # fit portrait image to 1080 height, wipe reveals left->right, then pad white to 1920x1080
    chain = (f"[{i}:v]scale=-2:{H},setsar=1,"
             f"drawbox=x='iw*t/{d:.3f}':y=0:w=iw:h=ih:color=white:t=fill,"
             f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white")
    if i in OVERLAYS:
        chain += "," + dt(OVERLAYS[i][0], enable=OVERLAYS[i][1], size=110, y="(h-text_h)/2")
    for (t, f0, f1) in CAPS[i]:
        chain += "," + cap(t, d, f0, f1)
    chain += f",trim=0:{d:.3f},setpts=PTS-STARTPTS[s{i}]"
    fc.append(chain)
    labels.append(f"[s{i}]")
d = BUMP_D
fc.append(
    f"[11:v]format=yuv420p,setsar=1,"
    f"{dt('InkTime', size=130, y='(h-text_h)/2')},"
    f"trim=0:{d:.3f},setpts=PTS-STARTPTS[sb]")
labels.append("[sb]")

order = ["[s0]"] + [f"[s{i}]" for i in range(1, 6)] + ["[sb]"] + [f"[s{i}]" for i in range(6, 11)]
fc.append("".join(order) + f"concat=n={len(order)}:v=1:a=0[vcat]")
inputs += ["-f", "lavfi", "-t", f"{BUMP_D:.3f}", "-i", f"color=white:s={W}x{H}:r=30"]
qrun(["-y"] + inputs + ["-filter_complex", ";".join(fc),
      "-map", "[vcat]", "-c:v", "libx264", "-preset", "veryfast", "-r", "30",
      os.path.join(TMP, "vconcat1015.mp4")])
print("VIDEO CONCAT DONE", flush=True)

# ---- 2. audio: silence + beats 1-5 + bumper + beats 6-10 (ABSOLUTE paths) ----
qrun(["-y", "-f", "lavfi", "-t", str(TITLE_D), "-i", "anullsrc=r=44100:cl=stereo",
      "-c:a", "libmp3lame", os.path.join(TMP, "silence1015.mp3")])
qrun(["-y", "-i", BUMPER, "-c:a", "libmp3lame", os.path.join(TMP, "bumper1015.mp3")])
alst = os.path.join(TMP, "alist1015.txt")
with open(alst, "w") as f:
    f.write(f"file '{os.path.join(TMP, 'silence1015.mp3')}'\n")
    for a in auds[:5]:
        f.write(f"file '{a}'\n")
    f.write(f"file '{os.path.join(TMP, 'bumper1015.mp3')}'\n")
    for a in auds[5:]:
        f.write(f"file '{a}'\n")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy",
      os.path.join(TMP, "afull1015.mp3")])
print("AUDIO DONE", flush=True)
a_dur = dur(os.path.join(TMP, "afull1015.mp3"))
expect = TITLE_D + BUMP_D + sum(durs)
print(f"afull1015.mp3={a_dur:.2f}s expected={expect:.2f}s", flush=True)
assert abs(a_dur - expect) < 1.5, "AUDIO DURATION MISMATCH"

# ---- 3. final to TEMP: grain + mux, verify, then move ----
v_dur = dur(os.path.join(TMP, "vconcat1015.mp4"))
print(f"vconcat={v_dur:.2f}s vs audio expect={expect:.2f}s", flush=True)
assert abs(v_dur - expect) < 2.0, "VIDEO DURATION MISMATCH"
final_tmp = os.path.join(BASE, "video", "tmp", "inktime-2026-10-15-long-TMP.mp4")
qrun(["-y", "-i", os.path.join(TMP, "vconcat1015.mp4"), "-i", os.path.join(TMP, "afull1015.mp3"),
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", final_tmp])
f_dur = dur(final_tmp)
print(f"FINAL TMP={f_dur:.2f}s expected={expect:.2f}s", flush=True)
assert abs(f_dur - expect) < 5.0, "FINAL DURATION MISMATCH — NOT MOVING"
final = os.path.join(BASE, "video", "inktime-2026-10-15-long.mp4")
shutil.move(final_tmp, final)
print("FINAL MOVED:", final, flush=True)

# ---- chapters ----
titles = {1: "The library did not burn", 2: "All the world's books",
          3: "The greatest book heist", 4: "What was inside",
          5: "A stick, a well, the Earth", 6: "Alexandria: the ancient Google",
          7: "The fire that wasn't", 8: "Death by a thousand cuts",
          9: "What we actually lost", 10: "Knowledge is not automatic"}
print("CHAPTERS:", flush=True)
t = 0.0
print("0:00 Intro - The Library of Alexandria", flush=True)
t = TITLE_D
for i in range(1, 11):
    m, s = int(t // 60), int(t % 60)
    print(f"{m}:{s:02d} {titles[i]}", flush=True)
    t += durs[i - 1]
    if i == 5:
        t += BUMP_D
print(f"TOTAL VIDEO: {TITLE_D + BUMP_D + sum(durs):.1f}s", flush=True)
