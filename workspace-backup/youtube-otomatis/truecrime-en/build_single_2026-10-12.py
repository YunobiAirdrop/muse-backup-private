#!/usr/bin/env python3
"""Render SATU panggilan ffmpeg via ffmpeg-queue: 73 gambar zoompan -> concat -> overlay -> mux audio.
Fallback dari build per-segmen karena antrean slot sangat padat (27 penunggu)."""
import subprocess, os, json, sys
BASE="/home/hatch/workspace/youtube-otomatis/truecrime-en"
GDIR=f"{BASE}/gambar/2026-10-12"
AUDIO=f"{BASE}/audio/gabungan-2026-10-12.mp3"
OUT=f"{BASE}/video/2026-10-12.mp4"
FFQ="/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
dj=json.load(open(f"{BASE}/audio/durasi-beat-2026-10-12.json"))
beats=json.load(open(f"{BASE}/script/beats-2026-10-12.json"))
bj=json.load(open(f"{BASE}/audio/bumper-2026-10-12.json"))
durs=[float(dj[f"beat-{i+1:03d}"]) for i in range(73)]
# overlays
cum=0.0; overlays=[]
for i,b in enumerate(beats):
    if "overlay" in b: overlays.append((b["overlay"],cum,cum+durs[i]))
    if b["id"]=="beat-037": overlays.append(("SUBSCRIBE - DARK CASE FILES",cum,cum+durs[i]-bj["dur"]))
    if i==len(beats)-1: overlays.append(("SUBSCRIBE FOR THE NEXT FILE",cum,cum+durs[i]))
    cum+=durs[i]
overlays.append(("HI, I'M YUNOBI - DARK CASE FILES",bj["start"],bj["start"]+bj["dur"]))
os.makedirs("/tmp/tc-ov",exist_ok=True)
args=[FFQ,"-y"]
for i in range(73):
    args+=["-loop","1","-i",f"{GDIR}/beat-{i+1:03d}.jpg"]
args+=["-i",AUDIO]
fc=[]
for i,d in enumerate(durs):
    frames=max(1,int(d*30)); mode=i%4
    if mode==0: zp=f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode==1: zp=f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode==2: zp=f"zoompan=z='max(1.15-0.0012*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else: zp=f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{frames}':s=1280x720:fps=30"
    fc.append(f"[{i}:v]scale=1280:720,{zp},eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5,setsar=1,trim=duration={d:.3f},setpts=PTS-STARTPTS[v{i}]")
fc.append("".join(f"[v{i}]" for i in range(73))+f"concat=n=73:v=1:a=0[vc]")
cur="[vc]"
for k,(text,a,c) in enumerate(overlays):
    tf=f"/tmp/tc-ov/ov{k}.txt"; open(tf,"w").write(text)
    fc.append(f"{cur}drawtext=fontfile={FONT}:textfile={tf}:fontsize=44:fontcolor=white:borderw=2:bordercolor=black@0.8:box=1:boxcolor=black@0.55:boxborderw=18:x=(w-text_w)/2:y=90:enable='between(t,{a:.2f},{c:.2f})'[vo{k}]")
    cur=f"[vo{k}]"
fc.append(f"{cur}null[vout]")
args+=["-filter_complex",";".join(fc),"-map","[vout]","-map","73:a","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",OUT]
print("overlays:",[(t,round(a,1)) for t,a,c in overlays],flush=True)
r=subprocess.run(args,capture_output=True,text=True)
if r.returncode!=0:
    print("FFMPEG FAIL:",r.stderr[-1500:]); sys.exit(1)
print("OK single build ->",OUT,flush=True)
