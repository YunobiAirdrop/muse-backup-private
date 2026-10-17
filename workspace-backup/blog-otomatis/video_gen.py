#!/usr/bin/env python3
"""Video berita 9:16 (1080x1920) dari gambar meme: efek Ken Burns (zoom pelan)
di atas background blur. Untuk Reels IG / FB / Threads.
Pakai: bikin_video(meme_jpg, out_mp4, durasi=12)
"""
import os, subprocess

DURASI = 12
FPS = 30

def bikin_video(meme_path, out_path, durasi=DURASI):
    frames = durasi * FPS
    # zoom 1.0 -> ~1.25 selama durasi
    zstep = 0.25 / frames
    fc = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=25:2[bg];"
        f"[0:v]scale=1400:1400,"
        f"zoompan=z='1.0+{zstep:.6f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s=1080x1080:fps={FPS}[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]"
    )
    cmd = ["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-loop", "1", "-i", meme_path,
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-filter_complex", fc, "-map", "[v]", "-map", "1:a",
           "-t", str(durasi), "-r", str(FPS),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-shortest",
           "-movflags", "+faststart", out_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(out_path):
        raise RuntimeError(f"ffmpeg gagal: {r.stderr[-500:]}")
    return out_path

if __name__ == "__main__":
    import sys
    print(bikin_video(sys.argv[1], sys.argv[2]))
