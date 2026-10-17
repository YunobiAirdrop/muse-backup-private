#!/usr/bin/env python3
import json, subprocess, time, os
SCRIPT="/home/hatch/workspace/youtube-otomatis/horror-en/script/2026-10-12.txt"
AUDIO_DIR="/home/hatch/workspace/youtube-otomatis/horror-en/audio"
DATE="2026-10-12"
lines=[ln.rstrip("\n") for ln in open(SCRIPT,encoding="utf-8")]
assert len(lines)==69, len(lines)
failed=[]
for n, text in enumerate(lines,1):
    out=f"{AUDIO_DIR}/beat-{DATE}-{n:03d}.mp3"
    if os.path.exists(out) and os.path.getsize(out)>1000: continue
    ok=False
    for attempt in range(3):
        r=subprocess.run(["/opt/hatch/bin/tts","speak","--voice","avocado_v2:briggs","--language","en","--speed","92","--output",out,"--text-stdin"],input=text.encode(),capture_output=True,timeout=180)
        if r.returncode==0: ok=True; break
        print(f"beat {n} attempt {attempt+1} fail",flush=True); time.sleep(5)
    if not ok: failed.append(n)
    if n%10==0: print(f"{n}/69 done",flush=True)
print("FAILED:",failed,flush=True)
# durations + gabungan with pauses
import subprocess as sp
def dur(p):
    r=sp.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p],capture_output=True,text=True)
    return float(r.stdout.strip())
SCARE={2,31,44,50,55,62}
durs={}
parts=[]
lst=f"{AUDIO_DIR}/list-{DATE}.txt"
with open(lst,"w") as f:
    for n in range(1,70):
        p=f"{AUDIO_DIR}/beat-{DATE}-{n:03d}.mp3"
        d=dur(p); durs[f"beat-{n:03d}"]=d
        sil=2.2 if n in SCARE else 0.4
        # silence file
        silp=f"{AUDIO_DIR}/sil-{DATE}-{n:03d}.mp3"
        if not os.path.exists(silp):
            sp.run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t",str(sil),"-q:a","9",silp],capture_output=True)
        f.write(f"file '{p}'\nfile '{silp}'\n")
json.dump(durs,open(f"{AUDIO_DIR}/durasi-beat-{DATE}.json","w"),indent=1)
# also duration including silence for rakit sync: rakit adds sil itself, so keep pure beat durations above; gabungan includes silences
out=f"{AUDIO_DIR}/gabungan-{DATE}.mp3"
sp.run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c:a","libmp3lame","-q:a","2",out],capture_output=True,check=True)
print("GABUNGAN dur",dur(out),flush=True)
