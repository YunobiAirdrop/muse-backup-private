#!/usr/bin/env python3
"""Lanjutan build: audio mix + final (perbaikan index input)."""
import json, subprocess, sys
W = "/home/hatch/workspace/youtube-otomatis/macammacam/work/2026-10-11"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-macammacam.wav"
OUT = "/home/hatch/workspace/youtube-otomatis/macammacam/macammacam-long-2026-10-11.mp4"

def run(cmd):
    print(">>", cmd[0], cmd[4] if len(cmd)>4 else "", "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:]); sys.exit(1)

ch = json.load(open(f"{W}/chapters.json"))
bumper_mulai = ch["bumper_mulai"]; total = ch["total_detik"]
beats = json.load(open(f"{W}/beats.json"))["beats"]
bdur = 4.906
n = len(beats)  # input 0=base, 1..13=beats, 14=bumper, 15=musik
vo_in = []
for b in beats: vo_in += ["-i", f"{W}/audio/{b['id']}.mp3"]
fc = []
fc.append("".join(f"[{k+1}:a]" for k in range(n)) + f"concat=n={n}:v=0:a=1[vo]")
fc.append("[vo]asplit=2[voA][voB]")
fc.append(f"[voA]atrim=0:{bumper_mulai:.3f},asetpts=PTS-STARTPTS[pre]")
fc.append(f"[voB]atrim={bumper_mulai:.3f},asetpts=PTS-STARTPTS[post]")
fc.append(f"[pre][{n+1}:a][post]concat=n=3:v=0:a=1[voall]")
fc.append(f"[{n+2}:a]volume='0.16*if(between(t,{bumper_mulai-0.5:.2f},{bumper_mulai+bdur+0.5:.2f}),0.35,1)',"
          f"atrim=0:{total:.1f}[mus]")
fc.append("[voall][mus]amix=inputs=2:duration=first:dropout_transition=0[aout]")
run([FQ,"-y","-v","error","-i",f"{W}/base.mp4"]+vo_in+["-i",BUMPER,"-i",f"{W}/musik.wav",
     "-filter_complex",";".join(fc),
     "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","128k",
     "-shortest",f"{W}/gabung.mp4"])
print("audio mix OK")

sub_style=("FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,"
           "OutlineColour=&H80000000,BackColour=&H80000000,BorderStyle=1,"
           "Outline=1,Shadow=0,MarginV=34,Alignment=2")
vf2=f"subtitles={W}/subs.srt:force_style='{sub_style}',format=yuv420p"
run([FQ,"-y","-v","error","-i",f"{W}/gabung.mp4","-vf",vf2,
     "-c:v","libx264","-preset","veryfast","-crf","21","-c:a","copy",OUT])
r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                    "-of","csv=p=0",OUT], capture_output=True, text=True)
print("SELESAI durasi:", round(float(r.stdout.strip()),1))
