#!/usr/bin/env python3
"""Gabung TTS per beat -> voiceover-2026-10-12.mp3 + durasi-beat-2026-10-12.json.
Jeda 0.35s antar beat; 0.9s setelah beat insight penting (dramatis).
Bumper clone dicatat di instruksi (pipeline rakit lama tidak menyisipkan audio bumper di tengah tanpa mengubah timing segmen; bumper file: voice-clone-test/bumper-mind-en.wav 4.1s).
"""
import subprocess, os, json, sys
BASE="/home/hatch/workspace/youtube-otomatis/mind-en"
BEATD=f"{BASE}/audio/beat-2026-10-12"
PADD=f"{BASE}/audio/pad-2026-10-12"
FFQ="/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
LONG_PAUSE={"beat-048","beat-057","beat-069"}  # insight kunci: gratitude truth, data, framework
def dur(path):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",path],capture_output=True,text=True)
    return float(r.stdout.strip())
os.makedirs(PADD,exist_ok=True)
# silence files
for name,secs in [("_silence035.mp3",0.35),("_silence09.mp3",0.9)]:
    sp=f"{BASE}/audio/{name}"
    if not os.path.exists(sp):
        subprocess.run([FFQ,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t",str(secs),"-q:a","9",sp],capture_output=True,check=True)
durs={}
files=[]
for i in range(1,76):
    bid=f"beat-{i:03d}"
    src=f"{BEATD}/{bid}.mp3"; assert os.path.exists(src), src
    sil=f"{BASE}/audio/_silence09.mp3" if bid in LONG_PAUSE else f"{BASE}/audio/_silence035.mp3"
    pad=f"{PADD}/{bid}.mp3"
    # concat beat + silence via ffmpeg concat demuxer (same codec mp3)
    lst=f"{PADD}/{bid}.txt"
    with open(lst,"w") as f:
        f.write(f"file '{src}'\nfile '{sil}'\n")
    subprocess.run([FFQ,"-y","-f","concat","-safe","0","-i",lst,"-c","copy",pad],capture_output=True,check=True)
    durs[bid]=round(dur(pad),3)
    files.append(pad)
    os.remove(lst)
json.dump(durs,open(f"{BASE}/audio/durasi-beat-2026-10-12.json","w"),indent=1)
lst=f"{BASE}/audio/_concat-2026-10-12.txt"
with open(lst,"w") as f:
    for p in files: f.write(f"file '{os.path.abspath(p)}'\n")
out=f"{BASE}/audio/voiceover-2026-10-12.mp3"
subprocess.run([FFQ,"-y","-f","concat","-safe","0","-i",lst,"-c","copy",out],capture_output=True,check=True)
print(f"OK {out} total={sum(durs.values()):.1f}s vo_dur={dur(out):.1f}s")
