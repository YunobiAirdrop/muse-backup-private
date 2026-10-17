#!/usr/bin/env python3
"""Rakit single-pass history-en 2026-10-11 (The Black Death).
Satu panggilan ffmpeg-queue.sh: concat demuxer gambar (durasi per beat) + concat filter
audio (3s hening + beats 1-35 + bumper + beats 36-70) + drawtext terjadwal
(judul 0-3s, overlay beats, CTA Subscribe! di jendela bumper ~50% dan 5 detik terakhir).
Tanpa karakter persen di semua teks drawtext.
"""
import subprocess, json, os, sys

FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BASE = "/home/hatch/workspace/youtube-otomatis/history-en"
ADIR = os.path.join(BASE, "audio", "2026-10-11")
OUT = os.path.join(BASE, "video", "2026-10-11.mp4")
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-history-en.wav"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W = json.load(open("/tmp/he11_windows.json"))
WINS = {int(k): v for k, v in W["wins"].items()}
BUMPER_WIN = W["bumper"]
TOTAL = W["total"]
OVERLAYS = {int(k): v for k, v in W["overlays"].items()}

def tf(name, text):
    p = f"/tmp/he11-{name}.txt"
    open(p, "w").write(text)
    return p

def main():
    inputs = ["-f", "concat", "-safe", "0", "-i", "/tmp/imglist_he11.txt",
              "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    audio_files = [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(1, 36)] \
                  + [BUMPER] \
                  + [os.path.join(ADIR, f"beat-{i:03d}.mp3") for i in range(36, 71)]
    for f in audio_files:
        inputs += ["-i", f]
    n_audio = 1 + len(audio_files)  # silence + 71 file audio

    fc = []
    fc.append("[1:a]atrim=0:3,asetpts=PTS-STARTPTS,aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a0]")
    for j in range(len(audio_files)):
        fc.append(f"[{j+2}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{j+1}]")
    fc.append("".join(f"[a{j}]" for j in range(n_audio)) + f"concat=n={n_audio}:v=0:a=1[aout]")

    vf = ("scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=30,"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5")
    vf += (f",drawtext=fontfile={FONT}:textfile={tf('t1','1347:')}:fontsize=110:fontcolor=white:"
           "x=(w-text_w)/2:y=h/2-140:enable='between(t,0,3)'")
    vf += (f",drawtext=fontfile={FONT}:textfile={tf('t2','THE BLACK DEATH CAME ON SHIPS')}:fontsize=46:fontcolor=#ffd97a:"
           "x=(w-text_w)/2:y=h/2+10:enable='between(t,0,3)'")
    for idx, text in OVERLAYS.items():
        s, e = WINS[idx]
        vf += (f",drawtext=fontfile={FONT}:textfile={tf(f'ov{idx}', text)}:fontsize=46:"
               "fontcolor=white:borderw=2:bordercolor=black@0.8:"
               f"x=(w-text_w)/2:y=h-150:box=1:boxcolor=black@0.55:boxborderw=24:enable='between(t,{s:.2f},{e:.2f})'")
    cta = tf('cta', 'Subscribe!')
    bs, be = BUMPER_WIN
    vf += (f",drawtext=fontfile={FONT}:textfile={cta}:fontsize=54:fontcolor=#ffd97a:"
           "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20:"
           f"enable='between(t,{bs:.2f},{be:.2f})'")
    vf += (f",drawtext=fontfile={FONT}:textfile={cta}:fontsize=54:fontcolor=#ffd97a:"
           "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.55:boxborderw=20:"
           f"enable='between(t,{TOTAL-5:.2f},{TOTAL:.2f})'")
    vf += ",format=yuv420p"
    fc.append(f"[0:v]{vf}[vout]")
    filter_complex = ";".join(fc)

    cmd = [FFQ, "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        "-movflags", "+faststart", OUT]
    print("menjalankan single-pass...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL:", r.stderr[-3000:]); sys.exit(1)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", OUT],
                       capture_output=True, text=True)
    print(f"OK: {OUT} durasi {d.stdout.strip()}s", flush=True)

if __name__ == "__main__":
    main()
