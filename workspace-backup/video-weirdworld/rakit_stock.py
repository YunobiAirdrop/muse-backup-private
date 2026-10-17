#!/usr/bin/env python3
"""Rakit video Strange Tales dari footage stok Pexels + caption + voiceover. 1080x1920."""
import subprocess, os

DL = "/home/hatch/workspace/browser_downloads/sess-3509515118"
D = os.path.expanduser("~/workspace/video-weirdworld")
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FPS = 30

scenes = [
    {"file": "browser-download-20261005T085651.148014653Z-0-uhd_30fps.mp4",
     "ss": 1.0, "dur": 6.5,
     "cap": "A miniature Stonehenge?!\nin the AMAZON"},
    {"file": "browser-download-20261005T090001.245322208Z-2-13360655_3840_2160_60fps.mp4",
     "ss": 2.0, "dur": 11.0,
     "cap": "Peru, 2013\nbarely 2 cm wide"},
    {"file": "browser-download-20261005T090148.480370713Z-3-15481517_2880_2160_30fps.mp4",
     "ss": 8.0, "dur": 9.0,
     "cap": "Builder: UNKNOWN"},
    {"file": "browser-download-20261005T090438.944025177Z-6-15766872_3840_2160_30fps.mp4",
     "ss": 4.0, "dur": 4.388,
     "cap": "Follow for more weird facts"},
]

seg_files = []
for i, s in enumerate(scenes):
    cap = s["cap"].replace(":", "\\:")
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=fontfile={FONT}:text='{cap}':fontsize=54:fontcolor=white:"
        "borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-460:"
        "box=1:boxcolor=black@0.45:boxborderw=24,"
        "format=yuv420p"
    )
    out = os.path.join(D, f"stseg{i}.mp4")
    cmd = ["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-ss", str(s["ss"]), "-i", os.path.join(DL, s["file"]),
           "-t", str(s["dur"]), "-vf", vf, "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
           "-an", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"SCENE {i} FAILED:\n{r.stderr[-1500:]}")
        raise SystemExit(1)
    seg_files.append(out)
    print(f"scene {i} ok ({s['dur']}s)")

lst = os.path.join(D, "stsegs.txt")
with open(lst, "w") as f:
    for p in seg_files:
        f.write(f"file '{p}'\n")
concat = os.path.join(D, "stconcat.mp4")
r = subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, text=True)
if r.returncode != 0:
    print("CONCAT FAILED:\n" + r.stderr[-1500:]); raise SystemExit(1)

final = os.path.join(D, "strangetales-silkhenge-stock.mp4")
r = subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-i", concat, "-i", os.path.join(D, "voiceover.mp3"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", final],
                   capture_output=True, text=True)
if r.returncode != 0:
    print("MUX FAILED:\n" + r.stderr[-1500:]); raise SystemExit(1)
print("FINAL:", final)
