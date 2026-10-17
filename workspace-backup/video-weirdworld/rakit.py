#!/usr/bin/env python3
"""Rakit video Weird World Daily: 4 scene Ken Burns + caption + voiceover. 1080x1920."""
import subprocess, os

D = os.path.expanduser("~/workspace/video-weirdworld")
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FPS = 30

scenes = [
    {"img": "media-generation-silkhenge-scene1-hook-0-3a4563a7-68b1-4f4d-ba42-60994798bb5f.webp",
     "dur": 6.5, "zoom": "in",
     "cap": "A miniature Stonehenge?!\nin the AMAZON"},
    {"img": "media-generation-silkhenge-scene2-discovery-0-4aef8006-55bb-4cde-95d4-9a779e0e41f2.webp",
     "dur": 11.0, "zoom": "out",
     "cap": "Peru, 2013\nbarely 2 cm wide"},
    {"img": "media-generation-silkhenge-scene3-macro-0-a6bf26db-ea78-4e14-bff4-8c358d4fdc0d.webp",
     "dur": 9.0, "zoom": "in",
     "cap": "Builder: UNKNOWN"},
    {"img": "media-generation-silkhenge-scene4-mystery-0-9ccae220-5d52-4cd7-85c7-0e2584450ac7.webp",
     "dur": 4.388, "zoom": "out",
     "cap": "Follow for more weird facts"},
]

seg_files = []
for i, s in enumerate(scenes):
    frames = int(s["dur"] * FPS)
    cap = s["cap"].replace(":", "\\:")  # escape titik dua untuk drawtext
    if s["zoom"] == "in":
        z = f"min(1+0.12*on/{frames}\\,1.12)"
    else:
        z = f"max(1.12-0.12*on/{frames}\\,1.0)"
    vf = (
        "scale=2304:4096:force_original_aspect_ratio=increase,crop=2304:4096,"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={FPS},"
        f"drawtext=fontfile={FONT}:text='{cap}':fontsize=54:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-460:"
        "box=1:boxcolor=black@0.45:boxborderw=24,"
        "format=yuv420p"
    )
    out = os.path.join(D, f"seg{i}.mp4")
    cmd = ["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-loop", "1", "-i", os.path.join(D, s["img"]),
           "-vf", vf, "-t", str(s["dur"]), "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"SCENE {i} FAILED:\n{r.stderr[-1500:]}")
        raise SystemExit(1)
    seg_files.append(out)
    print(f"scene {i} ok ({s['dur']}s)")

# concat
lst = os.path.join(D, "segs.txt")
with open(lst, "w") as f:
    for p in seg_files:
        f.write(f"file '{p}'\n")
concat = os.path.join(D, "concat.mp4")
r = subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, text=True)
if r.returncode != 0:
    print("CONCAT FAILED:\n" + r.stderr[-1500:]); raise SystemExit(1)

# mux voiceover
final = os.path.join(D, "weirdworld-silkhenge-final.mp4")
r = subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-i", concat, "-i", os.path.join(D, "voiceover.mp3"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", final],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("MUX FAILED:\n" + r.stderr[-1500:]); raise SystemExit(1)
print("FINAL:", final)
