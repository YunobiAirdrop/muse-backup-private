#!/usr/bin/env python3
"""Potong shorts vertikal 9:16 + teks hook besar di frame pertama.
Penggunaan: python3 potong_shorts_space.py <video> <outdir> <plan_json>
plan_json: [{"id":"s1","ss":0.0,"dur":32.1,"hook":"TEKS HOOK"}, ...]
"""
import subprocess, json, sys, os

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def ts(sec):
    return f"{int(sec//3600):02d}:{int((sec%3600)//60):02d}:{sec%60:06.3f}"

def main():
    video, outdir, plan_json = sys.argv[1:4]
    os.makedirs(outdir, exist_ok=True)
    plan = json.load(open(plan_json))
    for s in plan:
        out = os.path.join(outdir, s["file"])
        dur = float(s["dur"])
        cta_y = "h-170"  # safe zone: di atas UI tombol shorts
        vf = (
            "crop=406:720:(in_w-406)/2:0,scale=720:1280:flags=lanczos,"
            f"drawtext=fontfile={FONT}:text='{s['hook']}':fontsize=62:fontcolor=white:"
            f"borderw=4:bordercolor=black:x=(w-text_w)/2:y=h*0.12:"
            f"enable='between(t,0,4)',"
            f"drawtext=fontfile={FONT}:text='SUBSCRIBE!':fontsize=54:fontcolor=yellow:"
            f"borderw=4:bordercolor=black:x=(w-text_w)/2:y={cta_y}:"
            f"enable='between(t,{dur-3:.1f},{dur:.1f})'"
        )
        r = subprocess.run([FFQ, "-y", "-ss", ts(s["ss"]), "-i", video,
                            "-t", str(s["dur"]), "-vf", vf,
                            "-c:v", "libx264", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "aac", "-b:a", "128k",
                            "-movflags", "+faststart", out],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"GAGAL {s['id']}: {r.stderr[-800:]}"); continue
        print(f"OK {s['id']}: {s['ss']:.1f}s +{s['dur']:.1f}s -> {out}", flush=True)

if __name__ == "__main__":
    main()
