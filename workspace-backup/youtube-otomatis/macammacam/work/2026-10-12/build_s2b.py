#!/usr/bin/env python3
import json, subprocess, wave, sys, glob
import numpy as np
W="/home/hatch/workspace/youtube-otomatis/macammacam/work/2026-10-12"
FQ="/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER="/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-macammacam.wav"
OUTDIR="/home/hatch/workspace/youtube-otomatis/macammacam"
def dur(p):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True); return float(r.stdout.strip())
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: print(r.stderr[-3000:]); sys.exit(1)
def esc(t): return t.replace("\\","\\\\").replace("'","\\'").replace(":","\\:")
def buat_musik(path,total):
    SR=44100
    def note(f,d,vol=0.5,kind='sine'):
        n=int(d*SR); tt=np.arange(n)/SR
        w_=np.sin(2*np.pi*f*tt) if kind=='sine' else 2*np.abs(2*((f*tt)%1)-1)-1
        env=np.minimum(1,tt/0.02)*np.exp(-tt/(d*1.5)); return (w_*env*vol)[:n]
    N={'C3':130.81,'E3':164.81,'G3':196.00,'G2':98.00,'B3':246.94,'D4':293.66,'A2':110.00,'C4':261.63,'E4':329.63,'F2':87.31,'A3':220.00,'G4':392.00,'A4':440.00,'B4':493.88,'C5':523.25,'F4':349.23}
    chords=[(['C3','E3','G3'],['C4','E4','G4','A4','G4','E4']),(['G2','B3','D4'],['D4','G4','B4','G4','D4','B3']),(['A2','C4','E4'],['E4','A4','C5','A4','E4','C4']),(['F2','A3','C4'],['F4','A4','C5','A4','F4','A4'])]
    track=np.zeros(int(total*SR)); t_=0.0; ci=0; beat=0.333
    while t_<total-2:
        cn,mel=chords[ci%4]
        for c in cn:
            s=note(N[c],1.8,vol=0.10,kind='tri'); st=int(t_*SR)
            if st<len(track): track[st:st+len(s)]+=s[:max(0,len(track)-st)]
        for m in mel:
            s=note(N[m],beat*0.95,vol=0.16)+note(N[m]*2,beat*0.95,vol=0.04); st=int(t_*SR)
            if st<len(track): track[st:st+len(s)]+=s[:max(0,len(track)-st)]
            t_+=beat
        ci+=1
    track=track/(np.abs(track).max()+1e-9)*0.85
    f2=int(2*SR); track[:f2]*=np.linspace(0,1,f2); track[-f2:]*=np.linspace(1,0,f2)
    with wave.open(str(path),'w') as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((track*32767).astype(np.int16).tobytes())
def make_srt(s,base,da,db,bdur):
    def st(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int((x%1)*1000):03d}"
    cues=[]; t=0.0
    for txt,d in [(s["a"],da),(s["b"],db)]:
        words=txt.split(); lines=[]; cur=""
        for wd in words:
            if len(cur)+len(wd)+1<=32: cur=(cur+" "+wd).strip()
            else: lines.append(cur); cur=wd
        if cur: lines.append(cur)
        groups=[lines[j:j+2] for j in range(0,len(lines),2)]; cd=d/len(groups)
        for g in groups: cues.append((t,t+cd,"\\N".join(g))); t+=cd
        if txt==s["a"]: t+=bdur
    open(f"{base}/subs.srt","w").write("\n".join(f"{k}\n{st(a)} --> {st(e)}\n{x}\n" for k,(a,e,x) in enumerate(cues,1)))
data=json.load(open(f"{W}/shorts.json")); bdur=dur(BUMPER)
style="FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BackColour=&H80000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=60,Alignment=2"
results=[]
# S2: 1 call from existing segs
s=data["shorts"][1]; base=f"{W}/shorts/s2"; da=dur(f"{base}/audio/a.mp3"); db=dur(f"{base}/audio/b.mp3"); total=da+bdur+db
make_srt(s,base,da,db,bdur); buat_musik(f"{base}/musik.wav",total+3)
fc=[]
fc.append("[0:v][1:v][2:v]concat=n=3:v=1:a=0[vcat]")
fc.append(f"[vcat]subtitles={base}/subs.srt:force_style='{style}',drawtext=fontfile={FONT}:text='Subscribe!':fontsize=52:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-340:enable='between(t,{total-3:.1f},{total:.1f})',format=yuv420p[vout]")
fc.append("[3:a][4:a][5:a]concat=n=3:v=0:a=1[voall]")
fc.append(f"[6:a]volume='0.15*if(between(t,{da-0.5:.2f},{da+bdur+0.5:.2f}),0.35,1)',atrim=0:{total:.1f}[mus]")
fc.append("[voall][mus]amix=inputs=2:duration=first:dropout_transition=0[aout]")
out=f"{OUTDIR}/macammacam-short-s2alt-2026-10-12.mp4"
run([FQ,"-y","-v","error","-i",f"{base}/seg/segA.mp4","-i",f"{base}/seg/segBumper.mp4","-i",f"{base}/seg/segB.mp4","-i",f"{base}/audio/a.mp3","-i",BUMPER,"-i",f"{base}/audio/b.mp3","-i",f"{base}/musik.wav","-filter_complex",";".join(fc),"-map","[vout]","-map","[aout]","-c:v","libx264","-preset","veryfast","-crf","21","-c:a","aac","-b:a","128k","-shortest",out])
print("S2 DONE",round(dur(out),1)); results.append({"id":"s2","path":out,"dur":dur(out),"judul":s["judul"]})
print("S2B SCRIPT DONE")
