#!/usr/bin/env python3
"""Potong 3 shorts vertikal 9:16 dari video long 2026-10-13 (post-bumper).
- blur-fill 1080x1920, subtitle SRT per beat (burned), hook text 3 dtk pertama,
  endcard CTA 4 dtk (freeze frame + TTS voiceover + teks).
- baca titik bumper dari bumper-info-2026-10-13.json (ditulis sisip_bumper).
Penggunaan: python3 potong_shorts_2026-10-13.py
"""
import subprocess, os, json, sys

WS = "/home/hatch/workspace/youtube-otomatis/horror-en"
VIDEO = f"{WS}/video/2026-10-13.mp4"          # final, sudah termasuk bumper
DURJSON = f"{WS}/audio/durasi-beat-2026-10-13.json"
SCRIPT = f"{WS}/script/2026-10-13.txt"
CTA_MP3 = f"{WS}/shorts/cta-2026-10-11.mp3"
INFO = f"{WS}/bumper-info-2026-10-13.json"
OUTDIR = f"{WS}/shorts"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCARE = {3, 21, 34, 45, 54, 62}

PLANS = [
    dict(a=1, b=4, slug="s1",
         hook="3:33 AM. DEAD MOTHER CALLS",
         judul="3:33 AM — My Dead Mother's Number \U0001F631 #shorts #horror #scarystories #foryou",
         deskripsi="A dead payphone rang at 3:33 AM — and the caller ID showed my mother's number. She died eleven years ago. Full story on Midnight Dread Tales."),
    dict(a=56, b=60, slug="s2",
         hook="HE WAS ME",
         judul="The Man Getting Out Was Me \U0001F631 #shorts #horror #scarystories #foryou",
         deskripsi="The black pickup rolled in with its headlights off. The man getting out was me — thirty years older. Full story on Midnight Dread Tales."),
    dict(a=65, b=69, slug="s3",
         hook="IT RANG AGAIN",
         judul="Two Weeks Later, It Rang Again \U0001F631 #shorts #horror #scarystories #foryou",
         deskripsi="I quit the job. They tore the station down. Then two weeks ago, at 3:33 AM, my cell phone rang. Full story on Midnight Dread Tales."),
]

def sil(i):
    return 2.2 if i in SCARE else 0.4

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL:", " ".join(cmd[:6]), r.stderr[-500:])
        sys.exit(1)

def srt_time(t):
    h, m = int(t // 3600), int((t % 3600) // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

def main():
    dj = json.load(open(DURJSON))
    bi = json.load(open(INFO))
    BUMPER_T, BUMPER_D = bi["t_cut"], bi["bumper_d"]
    lines = [l.rstrip("\n") for l in open(SCRIPT)]
    assert len(dj) == 69 and len(lines) == 69
    # S[i] = pre-bumper time: awal jeda sebelum beat i+1 (S[0]=0)
    S = [3.0]
    for i in range(1, 70):
        S.append(S[-1] + sil(i) + float(dj[f"beat-{i:03d}"]))
    def post(t):
        return t + BUMPER_D if t >= BUMPER_T - 1e-9 else t
    os.makedirs(OUTDIR, exist_ok=True)
    assert os.path.exists(CTA_MP3), f"CTA mp3 belum ada: {CTA_MP3}"
    rencana = []
    for p in PLANS:
        a, b, slug = p["a"], p["b"], p["slug"]
        cut_start = post(S[a - 1])
        cut_dur = post(S[b]) - cut_start
        print(f"{slug}: beats {a}-{b} start={cut_start:.2f} dur={cut_dur:.1f}s", flush=True)
        # --- SRT ---
        srt_path = os.path.join(OUTDIR, f"srt-2026-10-13-{slug}.srt")
        with open(srt_path, "w") as f:
            for n, i in enumerate(range(a, b + 1), 1):
                st = post(S[i - 1] + sil(i)) - cut_start
                en = post(S[i - 1] + sil(i) + float(dj[f"beat-{i:03d}"])) - cut_start
                f.write(f"{n}\n{srt_time(max(st,0))} --> {srt_time(en)}\n{lines[i-1]}\n\n")
        srt_esc = srt_path.replace(":", "\\:").replace("'", "")
        # --- base clip: blur-fill + subtitles + hook text ---
        base = os.path.join(OUTDIR, f"2026-10-13-{slug}-base.mp4")
        hook_esc = p["hook"].replace("'", "").replace(":", "\\:")
        # catatan: apostrof DILARANG di hook drawtext — \' merusak parsing filtergraph
        # bila digabung enable='between(t,0,3)' ("No such filter: '0'").
        hook_dt = (f"drawtext=fontfile='{FONT}':text='{hook_esc}':fontsize=52:fontcolor=white:"
                   f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h*0.10:"
                   f"enable='between(t,0,3)'")
        vf = ("split[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              "gblur=sigma=40,eq=brightness=-0.35[bg];"
              "[b]scale=1080:-2[fg];"
              "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
              f"subtitles='{srt_esc}':force_style='FontName=DejaVu Sans Bold,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=2,MarginV=560',"
              f"{hook_dt},format=yuv420p")
        run([FQ, "-y", "-ss", f"{cut_start:.2f}", "-t", f"{cut_dur:.2f}", "-i", VIDEO,
             "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "128k", "-r", "30", "-movflags", "+faststart", base])
        # --- endcard CTA 4 dtk ---
        last = os.path.join(OUTDIR, f"2026-10-13-{slug}-last.png")
        run([FQ, "-y", "-sseof", "-0.5", "-i", base, "-frames:v", "1", last])
        endcard = os.path.join(OUTDIR, f"2026-10-13-{slug}-end.mp4")
        cta_dt = (f"drawtext=fontfile='{FONT}':text='SUBSCRIBE':fontsize=88:fontcolor=0xFFD400:"
                  f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.38,"
                  f"drawtext=fontfile='{FONT}':text='for more true horror':fontsize=52:fontcolor=white:"
                  f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h*0.50")
        run([FQ, "-y", "-loop", "1", "-i", last, "-i", CTA_MP3,
             "-vf", f"scale=1080:1920,{cta_dt},format=yuv420p",
             "-af", "apad=whole_dur=4",
             "-t", "4", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "128k", "-r", "30", "-shortest", endcard])
        # --- concat ---
        out = os.path.join(OUTDIR, f"2026-10-13-{slug}.mp4")
        run([FQ, "-y", "-i", base, "-i", endcard,
             "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
             "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
             "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
        for f_ in (base, endcard, last):
            if os.path.exists(f_):
                os.remove(f_)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                  "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", out],
                                 capture_output=True, text=True).stdout.strip())
        print(f"OK {out} ({d:.1f}s)", flush=True)
        rencana.append({"slug": slug, "file": out, "durasi_detik": round(d, 1),
                        "beats": [a, b], "judul": p["judul"], "deskripsi": p["deskripsi"]})
    with open(os.path.join(WS, "shorts-rencana-2026-10-13.jsonl"), "w") as f:
        for r_ in rencana:
            f.write(json.dumps(r_, ensure_ascii=False) + "\n")
    print("rencana tersimpan: shorts-rencana-2026-10-13.jsonl")

if __name__ == "__main__":
    main()
