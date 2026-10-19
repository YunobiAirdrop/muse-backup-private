#!/usr/bin/env python3
"""QC per video: frames tiap 10s -> contact sheet, black-frame check,
silence check audio, parse VTT (hook/CTA/WPM). Output audit-qc-DATE.json"""
import json, os, re, subprocess, glob, math
from PIL import Image
import numpy as np

D = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-19")
inv = json.load(open(os.path.expanduser(
    "~/workspace/youtube-otomatis/hidden_files/audit-inventory-2026-10-19.json")))

def ffprobe_dur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","csv=p=0",p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except: return 0

def parse_vtt(path):
    """return list of (start_s, end_s, text)"""
    if not os.path.exists(path): return []
    txt = open(path, encoding="utf-8", errors="ignore").read()
    segs = []
    for m in re.finditer(r"(\d+):(\d+):(\d+)\.(\d+)\s*-->\s*(\d+):(\d+):(\d+)\.(\d+)\s*\n(.*?)(?=\n\n|\Z)",
                         txt, re.S):
        s = int(m.group(1))*3600+int(m.group(2))*60+int(m.group(3))+int(m.group(4))/1000
        e = int(m.group(5))*3600+int(m.group(6))*60+int(m.group(7))+int(m.group(8))/1000
        t = re.sub(r"<[^>]+>", "", m.group(9)).strip().replace("\n"," ")
        if t: segs.append((s,e,t))
    return segs

CTA = ["subscribe","subscribed","langganan","berlangganan","like","komentar",
       "comment","share","bagikan","l bell","lonceng","notifikasi","notification",
       "follow","ikuti","tonton sampai","watch till","part 2","part2","lanjutannya"]

results = {}
for slug, ch in inv["channels"].items():
    results[slug] = []
    for v in ch["videos"]:
        if v.get("missing"): 
            results[slug].append({**v, "qc": "missing"}); continue
        vid = v["videoId"]
        fn = f"{D}/vids/{slug}__{vid}.mp4"
        if not os.path.exists(fn):
            results[slug].append({**v, "qc": "not_downloaded"}); continue
        dur = ffprobe_dur(fn) or v.get("duration_s", 0)
        # --- frames tiap 10 detik ---
        fdir = f"{D}/frames/{slug}__{vid}"
        os.makedirs(fdir, exist_ok=True)
        if not glob.glob(fdir+"/f*.jpg"):
            subprocess.run(["ffmpeg","-y","-v","error","-i",fn,
                            "-vf",f"fps=1/10,scale=320:180","-q:v","4",
                            fdir+"/f%03d.jpg"], timeout=600)
        frames = sorted(glob.glob(fdir+"/f*.jpg"))
        black, dark, fr_stats = 0, 0, []
        imgs = []
        for fp in frames:
            try:
                im = Image.open(fp).convert("L")
                a = np.asarray(im, dtype=np.float32)
                m_ = a.mean(); sd = a.std()
                fr_stats.append((round(m_,1), round(sd,1)))
                if m_ < 8: black += 1
                elif m_ < 25: dark += 1
                imgs.append(Image.open(fp).convert("RGB"))
            except Exception as e:
                fr_stats.append(("err",)); imgs.append(None)
        # contact sheet (max 64 frames per sheet)
        sheets = []
        for si in range(0, len(imgs), 64):
            chunk = [im for im in imgs[si:si+64] if im]
            if not chunk: continue
            cols = 8; rows = math.ceil(len(chunk)/cols)
            sheet = Image.new("RGB", (320*cols, 180*rows), (20,20,20))
            for i, im in enumerate(chunk):
                sheet.paste(im, ((i%cols)*320, (i//cols)*180))
            sp = f"{D}/sheets/{slug}__{vid}__s{si//64}.jpg"
            sheet.save(sp, quality=70)
            sheets.append(sp)
        # --- audio silence + level ---
        r = subprocess.run(["ffmpeg","-v","info","-i",fn,"-af",
                            "silencedetect=noise=-32dB:d=2","-f","null","-"],
                           capture_output=True, text=True, timeout=300)
        sil = re.findall(r"silence_(start|end): ([\d.]+)", r.stderr)
        sil_segs, cur = [], None
        for k, ts in sil:
            if k=="start": cur=float(ts)
            elif cur is not None: sil_segs.append((cur,float(ts))); cur=None
        long_sil = [(s,e) for s,e in sil_segs if e-s >= 3]
        r2 = subprocess.run(["ffmpeg","-v","info","-i",fn,"-af","volumedetect",
                             "-f","null","-"], capture_output=True, text=True, timeout=300)
        mv = re.search(r"mean_volume: ([\-\d.]+) dB", r2.stderr)
        xv = re.search(r"max_volume: ([\-\d.]+) dB", r2.stderr)
        # --- caption hook/CTA/WPM ---
        subs = glob.glob(f"{D}/vids/{slug}__{vid}.*.vtt")
        segs = []
        for s in subs:
            segs = parse_vtt(s)
            if segs:
                break
        full = " ".join(t for _,_,t in segs)
        words = len(full.split())
        hook_txt = " ".join(t for s,e,t in segs if s < 10)[:300]
        mid = [t for s,e,t in segs if dur*0.35 < s < dur*0.65]
        end = [t for s,e,t in segs if s > dur*0.8]
        mid_txt, end_txt = " ".join(mid).lower(), " ".join(end).lower()
        cta_mid = any(k in mid_txt for k in CTA)
        cta_end = any(k in end_txt for k in CTA)
        results[slug].append({**v,
            "dur_actual": round(dur,1),
            "n_frames": len(frames),
            "black_frames": black, "dark_frames": dark,
            "frame_stats": fr_stats[:80],
            "sheets": sheets,
            "silence_segs_2s": len(sil_segs),
            "long_silence": [(round(s,1),round(e,1)) for s,e in long_sil],
            "mean_vol": mv.group(1) if mv else None,
            "max_vol": xv.group(1) if xv else None,
            "has_subs": bool(segs),
            "wpm": round(words/(dur/60),1) if dur else 0,
            "hook_text": hook_txt,
            "cta_mid": cta_mid, "cta_end": cta_end,
        })
        print(f"QC {slug}/{vid} dur={dur:.0f}s fr={len(frames)} black={black} sil3s={len(long_sil)} wpm={results[slug][-1]['wpm']}", flush=True)

out = f"{D}/audit-qc-2026-10-19.json"
json.dump(results, open(out,"w"), ensure_ascii=False, indent=1)
print("OK ->", out)
