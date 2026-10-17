#!/usr/bin/env python3
"""Assembly video long Macam Macam 2026-10-11. Semua ffmpeg via ffmpeg-queue.sh."""
import json, subprocess, wave, sys
import numpy as np

W = "/home/hatch/workspace/youtube-otomatis/macammacam/work/2026-10-11"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-macammacam.wav"
FPS = 25
OUT = "/home/hatch/workspace/youtube-otomatis/macammacam/macammacam-long-2026-10-11.mp4"

def ffprobe_dur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",p], capture_output=True, text=True)
    return float(r.stdout.strip())

def run(cmd):
    print(">>", cmd[0], cmd[4] if len(cmd)>4 else "", "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:]); sys.exit(1)

def esc(t):
    return t.replace("\\","\\\\").replace("'","\\'").replace(":","\\:")

beats = json.load(open(f"{W}/beats.json"))["beats"]
durs = [ffprobe_dur(f"{W}/audio/{b['id']}.mp3") for b in beats]
bdur = ffprobe_dur(BUMPER)
bumper_mulai = sum(durs[:5])  # setelah beat05, sebelum beat06
print("bumper mulai:", round(bumper_mulai,1), "dur:", round(bdur,2))

moves = ["zin","panr","zin2","panl","zin","zout","zin_slow","panr2","zin","panl2","zout2","zin_slow","zin"]
segfiles = []
seg_idx = 0

def render_seg(img, dur, top_text, low_text, mv, tag):
    global seg_idx
    fr = int(round(dur*FPS))
    if mv=="zin":   zp = f"z='min(1+0.0016*on,1.45)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif mv=="zin2":zp = f"z='min(1+0.0022*on,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif mv=="zout":zp = f"z='max(1.45-0.0018*on,1.02)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif mv=="zout2":zp = f"z='max(1.35-0.0012*on,1.02)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif mv=="panr":zp = f"z='1.28':x='(iw-iw/zoom)*on/{fr}':y='ih/2-(ih/zoom/2)'"
    elif mv=="panr2":zp = f"z='1.35':x='(iw-iw/zoom)*on/{fr}':y='(ih-ih/zoom)*on/{fr}'"
    elif mv=="panl":zp = f"z='1.28':x='(iw-iw/zoom)*(1-on/{fr})':y='ih/2-(ih/zoom/2)'"
    elif mv=="panl2":zp = f"z='1.35':x='(iw-iw/zoom)*(1-on/{fr})':y='(ih-ih/zoom)*(1-on/{fr})'"
    else:           zp = f"z='min(1+0.001*on,1.35)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    dt = ""
    if top_text:
        dt += (f",drawtext=fontfile={FONT}:text='{esc(top_text)}':fontsize=54:fontcolor=white:"
               f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=64:box=1:boxcolor=black@0.55:boxborderw=14")
    if low_text:
        dt += (f",drawtext=fontfile={FONT}:text='{esc(low_text)}':fontsize=44:fontcolor=white:"
               f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-140:box=1:boxcolor=black@0.55:boxborderw=12")
    vf = (f"scale=1440:810,zoompan={zp}:d={fr}:s=1280x720:fps={FPS}{dt},"
          f"noise=alls=8:allf=t,format=yuv420p")
    seg = f"{W}/seg/seg{seg_idx:02d}.mp4"
    run([FQ,"-y","-v","error","-loop","1","-i",img,"-vf",vf,
         "-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","23",seg])
    segfiles.append(seg); seg_idx += 1
    print(f"{tag} OK ({dur:.1f}s, {mv})")

for i,(b,d,mv) in enumerate(zip(beats,durs,moves)):
    render_seg(f"{W}/img/img{i+1:02d}.jpg", d, b["on_screen"], None, mv, f"seg-beat{i+1:02d}")
    if i==4:  # bumper setelah beat05 (udang pistol), sebelum beat06 — 41% durasi
        render_seg(f"{W}/img/img02.jpg", bdur, None, "Macam Macam", "zin_slow", "seg-bumper")

# concat
with open(f"{W}/seg/list.txt","w") as f:
    for s in segfiles: f.write(f"file '{s}'\n")
run([FQ,"-y","-v","error","-f","concat","-safe","0","-i",f"{W}/seg/list.txt",
     "-c","copy",f"{W}/base.mp4"])

# chapters (dengan offset bumper)
t = 0.0; chapters = []
for i,(b,d) in enumerate(zip(beats,durs)):
    chapters.append((f"{int(t//60):02d}:{int(t%60):02d}", b["chapter"]))
    t += d + (bdur if i==4 else 0)
total = t
print("total:", round(total,1))
json.dump({"chapters":chapters,"total_detik":total,"durs":durs,"bumper_mulai":bumper_mulai},
          open(f"{W}/chapters.json","w"), ensure_ascii=False, indent=1)

# SRT (dengan offset bumper)
def srt_time(s):
    return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d},{int((s%1)*1000):03d}"
cues=[]; t=0.0
for i,(b,d) in enumerate(zip(beats,durs)):
    words=b["text"].split(); lines=[]; cur=""
    for w_ in words:
        if len(cur)+len(w_)+1<=40: cur=(cur+" "+w_).strip()
        else: lines.append(cur); cur=w_
    if cur: lines.append(cur)
    groups=[lines[j:j+2] for j in range(0,len(lines),2)]
    cd=d/len(groups)
    for g in groups:
        cues.append((t,t+cd,"\\N".join(g))); t+=cd
    if i==4: t += bdur
open(f"{W}/subs.srt","w").write("\n".join(
    f"{k}\n{srt_time(a)} --> {srt_time(e)}\n{x}\n" for k,(a,e,x) in enumerate(cues,1)))
print("SRT cues:", len(cues))

# musik ceria (tiru buat_musik_ceria produksi.py)
def buat_musik_ceria(path, dur):
    SR=44100
    def note(freq,dur_,vol=0.5,kind='sine'):
        n=int(dur_*SR); tt=np.arange(n)/SR
        w_=np.sin(2*np.pi*freq*tt) if kind=='sine' else 2*np.abs(2*((freq*tt)%1)-1)-1
        env=np.minimum(1,tt/0.02)*np.exp(-tt/(dur_*1.5))
        return (w_*env*vol)[:n]
    N={'C3':130.81,'D3':146.83,'E3':164.81,'F3':174.61,'G3':196.00,'A3':220.00,'B3':246.94,
       'C4':261.63,'D4':293.66,'E4':329.63,'F4':349.23,'G4':392.00,'A4':440.00,'B4':493.88,
       'C5':523.25,'D5':587.33,'E5':659.25,'F5':698.46,'G5':783.99,'A5':880.00,
       'C2':65.41,'G2':98.00,'A2':110.00,'F2':87.31}
    chords=[(['C3','E3','G3'],['C4','E4','G4','A4','G4','E4']),
            (['G2','B3','D4'],['D4','G4','B4','G4','D4','B3']),
            (['A2','C4','E4'],['E4','A4','C5','A4','E4','C4']),
            (['F2','A3','C4'],['F4','A4','C5','A4','F4','A4'])]
    track=np.zeros(int(dur*SR)); t_,ci,beat=0.0,0,0.333
    while t_<dur-2:
        cn,mel=chords[ci%4]
        for c in cn:
            s=note(N[c],1.8,vol=0.10,kind='tri'); st=int(t_*SR); track[st:st+len(s)]+=s
        for m in mel:
            s=note(N[m],beat*0.95,vol=0.16)+note(N[m]*2,beat*0.95,vol=0.04)
            st=int(t_*SR); track[st:st+len(s)]+=s; t_+=beat
        ci+=1
    track=track/(np.abs(track).max()+1e-9)*0.85
    f2=int(2*SR); track[:f2]*=np.linspace(0,1,f2); track[-f2:]*=np.linspace(1,0,f2)
    with wave.open(str(path),'w') as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR)
        w_.writeframes((track*32767).astype(np.int16).tobytes())
buat_musik_ceria(f"{W}/musik.wav", total+5)
print("musik OK")

# rakit audio: VO + bumper + musik (duck saat bumper)
n=len(beats); vo_in=[]
for b in beats: vo_in+=["-i",f"{W}/audio/{b['id']}.mp3"]
fc=[]
fc.append("".join(f"[{k+1}:a]" for k in range(n))+f"concat=n={n}:v=0:a=1[vo]")
fc.append("[vo]asplit=2[voA][voB]")
fc.append(f"[voA]atrim=0:{bumper_mulai:.3f},asetpts=PTS-STARTPTS[pre]")
fc.append(f"[voB]atrim={bumper_mulai:.3f},asetpts=PTS-STARTPTS[post]")
fc.append(f"[pre][{n+2}:a][post]concat=n=3:v=0:a=1[voall]")
fc.append(f"[{n+3}:a]volume='0.16*if(between(t,{bumper_mulai-0.5:.2f},{bumper_mulai+bdur+0.5:.2f}),0.35,1)',"
          f"atrim=0:{total:.1f}[mus]")
fc.append("[voall][mus]amix=inputs=2:duration=first:dropout_transition=0[aout]")
run([FQ,"-y","-v","error","-i",f"{W}/base.mp4"]+vo_in+["-i",BUMPER,"-i",f"{W}/musik.wav",
     "-filter_complex",";".join(fc),
     "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","128k",
     "-shortest",f"{W}/gabung.mp4"])
print("audio mix OK")

# final: burn subtitle
sub_style=("FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,"
           "OutlineColour=&H80000000,BackColour=&H80000000,BorderStyle=1,"
           "Outline=1,Shadow=0,MarginV=34,Alignment=2")
vf2=f"subtitles={W}/subs.srt:force_style='{sub_style}',format=yuv420p"
run([FQ,"-y","-v","error","-i",f"{W}/gabung.mp4","-vf",vf2,
     "-c:v","libx264","-preset","veryfast","-crf","21","-c:a","copy",OUT])
print("SELESAI durasi:", round(ffprobe_dur(OUT),1))
