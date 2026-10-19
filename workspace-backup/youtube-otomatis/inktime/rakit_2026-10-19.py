#!/usr/bin/env python3
"""InkTime 2026-10-19 LONG assembly: The Day the Sun Didn't Rise (Tambora 1815).
TWO-PASS per AGENTS.md 2026-10-18: pass 1 = per-beat still segments with
draw-reveal wipe + captions (ultrafast, NO fps filter); pass 2 = concat demuxer.
Bumper between beat 5 and 6. Images 1280x1920 portrait -> fit height + white pad.
All ffmpeg via ffmpeg-queue.sh. Write TEMP first, verify per-stream, then move."""
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

def stream_durs(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    out = {}
    for line in r.stdout.strip().splitlines():
        parts = line.split(",")
        if len(parts) == 2 and parts[1] not in ("N/A", ""):
            out[parts[0]] = float(parts[1])
    return out

TITLE_D = 2.5
BUMP_D = dur(BUMPER)
imgs = [os.path.join(BASE, "gambar", f"ink1019-b{i:02d}.jpg") for i in range(1, 11)]
auds = [os.path.join(BASE, "audio", f"ink1019-b{i:02d}.mp3") for i in range(1, 11)]
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
    1: [("THE SUN NEVER ROSE", .05, .35), ("SNOW IN JULY, IN AMERICA", .55, .9)],
    2: [("SUMBAWA, 1815", .1, .3), ("A KINGDOM WITH ITS OWN LANGUAGE", .55, .8)],
    3: [("APRIL 10, 1815", .05, .28), ("HEARD 2,600 KM AWAY", .5, .75)],
    4: [("10,000 KILLED DIRECTLY", .1, .35), ("A LANGUAGE DIED FOREVER", .6, .85)],
    5: [("A VEIL AROUND THE PLANET", .15, .4), ("THE WILDEST PART IS NEXT", .55, .8)],
    6: [("SNOW IN JUNE", .05, .3), ("EIGHTEEN-HUNDRED-AND-FROZE-TO-DEATH", .55, .8)],
    7: [("FRANKENSTEIN, 1816", .1, .3), ("A VOLCANO WROTE IT", .55, .8)],
    8: [("SULFUR SPIKE IN THE ICE", .05, .3), ("STOTHERS 1984: TAMBORA", .5, .75)],
    9: [("CHOLERA, 1817", .1, .3), ("BORN FROM A VOLCANO: THE BICYCLE", .55, .8)],
    10: [("NOT KINGS, A MOUNTAIN", .05, .3), ("COMMENT YOUR WILDEST RIPPLE", .5, .75),
         ("WATCH THE ALEXANDRIA VIDEO", .85, .98)],
}
OVERLAYS = {1: ("THE DAY THE SUN DID NOT RISE", "between(t,0,4)"),
            5: ("SUBSCRIBE!", "between(t,0,3)")}

# ---- PASS 1: per-beat segments (still + wipe + captions), ultrafast ----
segs = []
# title card
title_vf = ",".join([
    dt("INKTIME", size=150, y="(h-text_h)/2-140"),
    dt("THE DAY THE SUN DID NOT RISE", size=58, y="(h-text_h)/2+50"),
    dt("THE TAMBORA ERUPTION OF 1815", size=42, y="(h-text_h)/2+140"),
    "format=yuv420p"])
title_seg = os.path.join(TMP, "seg1019-title.mp4")
qrun(["-y", "-f", "lavfi", "-t", str(TITLE_D), "-i", f"color=white:s={W}x{H}:r=30",
      "-vf", title_vf, "-c:v", "libx264", "-preset", "ultrafast", "-r", "30",
      title_seg])
segs.append(title_seg)

for i in range(1, 11):
    d = durs[i - 1]
    parts = [f"scale=-2:{H}", "setsar=1",
             f"drawbox=x='iw*t/{d:.3f}':y=0:w=iw:h=ih:color=white:t=fill",
             f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=white"]
    if i in OVERLAYS:
        parts.append(dt(OVERLAYS[i][0], enable=OVERLAYS[i][1], size=110, y="(h-text_h)/2"))
    for (t, f0, f1) in CAPS[i]:
        parts.append(cap(t, d, f0, f1))
    parts.append("format=yuv420p")
    vf = ",".join(parts)
    seg = os.path.join(TMP, f"seg1019-b{i:02d}.mp4")
    qrun(["-y", "-loop", "1", "-t", f"{d:.3f}", "-i", imgs[i - 1],
          "-vf", vf, "-c:v", "libx264", "-preset", "ultrafast", "-r", "30",
          "-t", f"{d:.3f}", seg])
    segs.append(seg)
    if i == 5:
        # bumper card (white + InkTime text)
        bvf = ",".join([dt("InkTime", size=130, y="(h-text_h)/2"), "format=yuv420p"])
        bseg = os.path.join(TMP, "seg1019-bumper.mp4")
        qrun(["-y", "-f", "lavfi", "-t", f"{BUMP_D:.3f}", "-i", f"color=white:s={W}x{H}:r=30",
              "-vf", bvf, "-c:v", "libx264", "-preset", "ultrafast", "-r", "30", bseg])
        segs.append(bseg)
print(f"PASS 1 DONE: {len(segs)} segments", flush=True)

# ---- PASS 2a: concat video (demuxer, same codec) ----
vlist = os.path.join(TMP, "vlist1019.txt")
with open(vlist, "w") as f:
    for s in segs:
        f.write(f"file '{s}'\n")
vconcat = os.path.join(TMP, "vconcat1019.mp4")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", vlist, "-c", "copy", vconcat])
expect = TITLE_D + BUMP_D + sum(durs)
v_dur = dur(vconcat)
print(f"vconcat={v_dur:.2f}s expected={expect:.2f}s", flush=True)
assert abs(v_dur - expect) < 2.0, "VIDEO CONCAT DURATION MISMATCH"

# ---- PASS 2b: audio concat (ABSOLUTE paths) ----
qrun(["-y", "-f", "lavfi", "-t", str(TITLE_D), "-i", "anullsrc=r=44100:cl=stereo",
      "-c:a", "libmp3lame", os.path.join(TMP, "silence1019.mp3")])
qrun(["-y", "-i", BUMPER, "-c:a", "libmp3lame", os.path.join(TMP, "bumper1019.mp3")])
alst = os.path.join(TMP, "alist1019.txt")
with open(alst, "w") as f:
    f.write(f"file '{os.path.join(TMP, 'silence1019.mp3')}'\n")
    for a in auds[:5]:
        f.write(f"file '{a}'\n")
    f.write(f"file '{os.path.join(TMP, 'bumper1019.mp3')}'\n")
    for a in auds[5:]:
        f.write(f"file '{a}'\n")
afull = os.path.join(TMP, "afull1019.mp3")
qrun(["-y", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy", afull])
a_dur = dur(afull)
print(f"afull1019.mp3={a_dur:.2f}s expected={expect:.2f}s", flush=True)
assert abs(a_dur - expect) < 1.5, "AUDIO DURATION MISMATCH"

# ---- PASS 3: final to TEMP (grain + mux), per-stream verify, then move ----
final_tmp = os.path.join(TMP, "inktime-2026-10-19-long-TMP.mp4")
qrun(["-y", "-i", vconcat, "-i", afull,
      "-vf", "noise=alls=6:allf=t,format=yuv420p",
      "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-b:a", "128k",
      "-shortest", final_tmp])
sd = stream_durs(final_tmp)
print("FINAL TMP per-stream:", sd, "expected:", round(expect, 2), flush=True)
assert "video" in sd and abs(sd["video"] - expect) < 5.0, "VIDEO STREAM DURATION OFF"
assert "audio" in sd and abs(sd["audio"] - expect) < 5.0, "AUDIO STREAM DURATION OFF"
final = os.path.join(BASE, "video", "inktime-2026-10-19-long.mp4")
shutil.move(final_tmp, final)
print("FINAL MOVED:", final, flush=True)

# ---- chapters ----
titles = {1: "The day the sun did not rise", 2: "Sumbawa, 1815",
          3: "The mountain exploded", 4: "A culture erased",
          5: "A veil around the Earth", 6: "1816: the year without a summer",
          7: "A volcano wrote Frankenstein", 8: "Solved from ice and trees",
          9: "Ripples: cholera and the bicycle", 10: "History's biggest author"}
print("CHAPTERS:", flush=True)
print("0:00 Intro - The Day the Sun Didn't Rise", flush=True)
t = TITLE_D
for i in range(1, 11):
    m, s = int(t // 60), int(t % 60)
    print(f"{m}:{s:02d} {titles[i]}", flush=True)
    t += durs[i - 1]
    if i == 5:
        t += BUMP_D
print(f"TOTAL VIDEO: {TITLE_D + BUMP_D + sum(durs):.1f}s", flush=True)
