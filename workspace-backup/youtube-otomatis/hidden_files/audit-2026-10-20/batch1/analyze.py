#!/usr/bin/env python3
"""Analisis 1 video: frames->contact sheets, keyframes, audio, vtt parse."""
import subprocess, os, sys, json, re, glob
from PIL import Image, ImageDraw

WDIR = os.path.expanduser("~/workspace/youtube-otomatis/hidden_files/audit-2026-10-20/batch1")
os.chdir(WDIR)

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def get_duration(f):
    r = run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{f}"')
    return float(r.stdout.strip() or 0)

def extract_frames(f, vid):
    d = f"fr_{vid}"
    if not os.path.isdir(d):
        os.makedirs(d)
    n = len(glob.glob(f"{d}/f*.jpg"))
    if n == 0:
        run(f'ffmpeg -y -v error -i "{f}" -vf "fps=1/10,scale=320:-1" "{d}/f%04d.jpg"')
        n = len(glob.glob(f"{d}/f*.jpg"))
    return sorted(glob.glob(f"{d}/f*.jpg"))

def make_sheets(frames, vid, per_sheet=24, cols=6):
    rows = per_sheet // cols
    sheets = []
    for si in range(0, len(frames), per_sheet):
        chunk = frames[si:si+per_sheet]
        im = Image.open(chunk[0]); tw, th = im.size
        lbl = 16
        sheet = Image.new("RGB", (cols*tw, rows*(th+lbl)), (0,0,0))
        dr = ImageDraw.Draw(sheet)
        for i, fp in enumerate(chunk):
            im2 = Image.open(fp)
            x, y = (i%cols)*tw, (i//cols)*(th+lbl)
            sheet.paste(im2, (x, y))
            secs = int(re.search(r'f(\d+)', fp).group(1)) * 10
            dr.text((x+2, y+th+2), f"t={secs}s", fill=(255,255,0))
        p = f"sheet_{vid}_{si//per_sheet:02d}.jpg"
        sheet.save(p, quality=82)
        sheets.append(p)
    return sheets

def keyframes(f, vid, dur):
    outs = []
    for name, ss in [("start", 1), ("mid", dur/2), ("end", max(1, dur-3))]:
        p = f"kf_{vid}_{name}.jpg"
        if not os.path.exists(p):
            run(f'ffmpeg -y -v error -ss {ss} -i "{f}" -frames:v 1 -q:v 3 "{p}"')
        outs.append(p)
    return outs

def audio_stats(f):
    r = run(f'ffmpeg -y -v info -i "{f}" -af "volumedetect,silencedetect=noise=-35dB:d=2" -vn -f null - 2>&1')
    out = r.stdout + r.stderr
    maxv = re.search(r'max_volume: ([\-\d\.]+|n/a)', out)
    meanv = re.search(r'mean_volume: ([\-\d\.]+|n/a)', out)
    sil = re.findall(r'silence_start: ([\d\.]+)', out)
    sil_end = re.findall(r'silence_end: ([\d\.]+)', out)
    segs = []
    for s, e in zip(sil, sil_end):
        s, e = float(s), float(e)
        if e - s > 2.0:
            segs.append({"start": round(s,1), "end": round(e,1), "dur": round(e-s,1)})
    return {"max_volume": maxv.group(1) if maxv else "?", "mean_volume": meanv.group(1) if meanv else "?",
            "silent_segs": segs}

def parse_vtt(slug, vid, dur):
    vtts = glob.glob(f"{slug}__{vid}*.vtt")
    if not vtts:
        return {"ada": False}
    vp = vtts[0]
    txt = open(vp, encoding="utf-8", errors="ignore").read()
    # hapus tags
    clean = re.sub(r'<[^>]+>', '', txt)
    cues = re.findall(r'(\d+):(\d+):(\d+)\.(\d+)\s*-->\s*(\d+):(\d+):(\d+)\.(\d+)\s*\n(.*?)(?=\n\d+:|\Z)', clean, re.S)
    if not cues:
        # fallback: parse line by line
        lines = [l.strip() for l in clean.split('\n') if l.strip() and '-->' not in l and 'WEBVTT' not in l and 'Kind' not in l and 'Language' not in l and 'align' not in l]
        return {"ada": True, "raw_lines": lines[:40], "raw": True}
    def ts(h, m, s, ms):
        return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000
    words = 0; first_start = None; last_end = 0; texts = []
    for c in cues:
        st = ts(c[0],c[1],c[2],c[3]); en = ts(c[4],c[5],c[6],c[7])
        t = ' '.join(c[8].strip().split())
        if first_start is None: first_start = st
        last_end = max(last_end, en)
        words += len(t.split()); texts.append(t)
    full = ' '.join(texts).lower()
    cta_words = ['subscribe','langganan','like','komen','comment','share','bagikan','follow','ikuti','tonton sampai akhir','watch till the end']
    return {"ada": True, "raw": False, "first_start_s": round(first_start,1), "last_end_s": round(last_end,1),
            "words": words, "wpm": round(words/(dur/60),1) if dur else 0,
            "cta_hit": [w for w in cta_words if w in full], "sampel": texts[:6] + (["..."] if len(texts)>6 else []) + texts[-2:]}

def main():
    slug, vid = sys.argv[1], sys.argv[2]
    f = f"{slug}__{vid}.mp4"
    if not os.path.exists(f):
        print(json.dumps({"videoId": vid, "error": "tidak_terdownload"})); return
    dur = get_duration(f)
    frames = extract_frames(f, vid)
    sheets = make_sheets(frames, vid)
    kfs = keyframes(f, vid, dur)
    aud = audio_stats(f)
    vtt = parse_vtt(slug, vid, dur)
    # cek frame hitam
    black = []
    for fp in frames:
        im = Image.open(fp).convert("L")
        px = list(im.getdata())
        avg = sum(px)/len(px)
        if avg < 8: black.append(fp)
    res = {"videoId": vid, "slug": slug, "durasi_file_s": round(dur,1), "n_frames": len(frames),
           "sheets": sheets, "keyframes": kfs, "audio": aud, "vtt": vtt,
           "frame_hitam": [os.path.basename(b) for b in black]}
    print(json.dumps(res, ensure_ascii=False, indent=1))
    # simpan ringkasan
    with open(f"anal_{vid}.json", "w") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)

main()
