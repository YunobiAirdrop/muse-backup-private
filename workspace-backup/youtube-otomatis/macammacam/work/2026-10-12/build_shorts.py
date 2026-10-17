#!/usr/bin/env python3
import json, subprocess, wave, sys
import numpy as np
W="/home/hatch/workspace/youtube-otomatis/macammacam/work/2026-10-12"
FQ="/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER="/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-macammacam.wav"
FPS=25
OUTDIR="/home/hatch/workspace/youtube-otomatis/macammacam"
def dur(p):
    r=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p],capture_output=True,text=True); return float(r.stdout.strip())
def run(cmd):
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode!=0: print(r.stderr[-3000:]); sys.exit(1)
def esc(t): return t.replace("\\","\\\\").replace("'","\\'").replace(":","\\:")
def buat_musik(path,total):
    SR=44100
    def note(f,d,vol=0.5,kind="sine"):
        n=int(d*SR); tt=np.arange(n)/SR
        w_=np.sin(2*np.pi*f*tt) if kind=='sine' else 2*np.abs(2*((f*tt)%1)-1)-1
        env=np.minimum(1,tt/0.02)*np.exp(-tt/(d*1.5)); return (w_*env*vol)[:n]
    N={'C3':130.81,'E3':164.81,'G3':196.00,'G2':98.00,'B3':246.94,'D4':293.66,'A2':110.00,'C4':261.63,'E4':329.63,'F2':87.31,'A3':220.00,'G4':392.00,'A4':440.00,'B4':493.88,'C5':523.25,'F4':349.23}
    chords=[(['C3','E3','G3'],['C4','E4','G4','A4','G4','E4']),(['G2','B3','D4'],['D4','G4','B4','G4','D4','B3']),(['A2','C4','E4'],['E4','A4','C5','A4','E4','C4']),(['F2','A3','C4'],['F4','A4','C5','A4','F4','A4'])]
    # fix missing keys
    N.update({'D4':293.66,'B3':246.94,'G4':392.00})
    track=np.zeros(int(total*SR)); t_=0.0; ci=0; beat=0.333
    while t_<total-2:
        cn,mel=chords[ci%4]
        for c in cn:
            if c not in N: continue
            s=note(N[c],1.8,vol=0.10,kind='tri'); st=int(t_*SR); track[st:st+len(s)]+=s[:max(0,len(track)-st)]
        for m in mel:
            if m not in N: continue
            s=note(N[m],beat*0.95,vol=0.16)+note(N[m]*2,beat*0.95,vol=0.04); st=int(t_*SR)
            if st < len(track): track[st:st+len(s)]+=s[:max(0,len(track)-st)]
            t_+=beat
        ci+=1
    track=track/(np.abs(track).max()+1e-9)*0.85
    f2=int(2*SR); track[:f2]*=np.linspace(0,1,f2); track[-f2:]*=np.linspace(1,0,f2)
    with wave.open(str(path),'w') as w_:
        w_.setnchannels(1); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((track*32767).astype(np.int16).tobytes())

data=json.load(open(f"{W}/shorts.json"))
bdur=dur(BUMPER)
results=[]
for s in data["shorts"]:
    sid=s["id"]; base=f"{W}/shorts/{sid}"
    da=dur(f"{base}/audio/a.mp3"); db=dur(f"{base}/audio/b.mp3"); total=da+bdur+db
    print(sid, round(da,1), round(bdur,1), round(db,1), "total", round(total,1))
    # image
    import glob, os
    imgs=glob.glob(f"{base}/img/*.webp")+glob.glob(f"{base}/img/*.jpg")+glob.glob(f"{base}/img/*.png")
    imgs=[i for i in imgs if "media-generation" in i] or imgs
    img=imgs[0] if imgs else None
    segs=[]
    def render(dur_,top,low,tag,use_img=True,mv="zin"):
        out=f"{base}/seg/{tag}.mp4"; fr=int(round(dur_*FPS))
        import os
        if os.path.exists(out) and os.path.getsize(out)>10000:
            segs.append(out); print("skip existing",out); return
        zp=f"z='min(1+0.0016*on,1.4)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'" if mv=="zin" else f"z='max(1.4-0.0016*on,1.02)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        dt=""
        if top: dt+=f",drawtext=fontfile={FONT}:text='{esc(top)}':fontsize=44:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=90:box=1:boxcolor=black@0.55:boxborderw=12"
        if low: dt+=f",drawtext=fontfile={FONT}:text='{esc(low)}':fontsize=40:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-220:box=1:boxcolor=black@0.55:boxborderw=12"
        if use_img and img:
            vf=f"scale=900:1600,zoompan={zp}:d={fr}:s=720x1280:fps={FPS}{dt},noise=alls=8:allf=t,format=yuv420p"
            run([FQ,"-y","-v","error","-loop","1","-i",img,"-vf",vf,"-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","23",out])
        else:
            vf=f"gradients=s=720x1280:c0=0x1a6b8a:c1=0xf2a541:c2=0x2ec4b6:speed=0.02{dt},noise=alls=8:allf=t,format=yuv420p"
            run([FQ,"-y","-v","error","-f","lavfi","-i",vf,"-frames:v",str(fr),"-c:v","libx264","-preset","veryfast","-crf","23",out])
        segs.append(out)
    render(da,s["on_screen"],None,"segA",use_img=bool(img),mv="zin")
    render(bdur,None,"Macam Macam","segBumper",use_img=bool(img),mv="zin")
    render(db,s["on_screen"],"Subscribe!","segB",use_img=bool(img),mv="zout")
    with open(f"{base}/seg/list.txt","w") as f:
        for x in segs: f.write(f"file '{x}'\n")
    run([FQ,"-y","-v","error","-f","concat","-safe","0","-i",f"{base}/seg/list.txt","-c","copy",f"{base}/base.mp4"])
    # SRT
    def srt_time(x): return f"{int(x//3600):02d}:{int(x%3600//60):02d}:{int(x%60):02d},{int((x%1)*1000):03d}"
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
    open(f"{base}/subs.srt","w").write("\n".join(f"{k}\n{srt_time(a)} --> {srt_time(e)}\n{x}\n" for k,(a,e,x) in enumerate(cues,1)))
    buat_musik(f"{base}/musik.wav",total+3)
    # audio mix: A + bumper + B, music ducked at bumper
    fc=[]
    fc.append("[1:a][2:a][3:a]concat=n=3:v=0:a=1[voall]")
    fc.append(f"[4:a]volume='0.15*if(between(t,{da-0.5:.2f},{da+bdur+0.5:.2f}),0.35,1)',atrim=0:{total:.1f}[mus]")
    fc.append("[voall][mus]amix=inputs=2:duration=first:dropout_transition=0[aout]")
    run([FQ,"-y","-v","error","-i",f"{base}/base.mp4","-i",f"{base}/audio/a.mp3","-i",BUMPER,"-i",f"{base}/audio/b.mp3","-i",f"{base}/musik.wav","-filter_complex",";".join(fc),"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","128k","-shortest",f"{base}/gabung.mp4"])
    style="FontName=DejaVu Sans,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BackColour=&H80000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=60,Alignment=2"
    out=f"{OUTDIR}/macammacam-short-{sid}-2026-10-12.mp4"
    vf2=f"subtitles={base}/subs.srt:force_style='{style}',drawtext=fontfile={FONT}:text='Subscribe!':fontsize=52:fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-340:enable='between(t,{total-3:.1f},{total:.1f})',format=yuv420p"
    run([FQ,"-y","-v","error","-i",f"{base}/gabung.mp4","-vf",vf2,"-c:v","libx264","-preset","veryfast","-crf","21","-c:a","copy",out])
    print("DONE",out,round(dur(out),1))
    results.append({"id":sid,"path":out,"dur":dur(out),"judul":s["judul"]})
json.dump(results,open(f"{W}/results.json","w"),ensure_ascii=False,indent=1)
print(results)
