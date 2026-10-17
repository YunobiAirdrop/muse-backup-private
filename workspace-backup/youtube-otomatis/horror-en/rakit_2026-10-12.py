#!/usr/bin/env python3
"""Rakit video LONG horror-en 2026-10-12 ("The Watcher").
Pola: resume_rakit.py (ringan 1280x720, veryfast, resume segmen) +
- title card pembuka 3 dtk (drawtext)
- durasi segmen = silence_i + durasi audio beat_i (sinkron dengan gabungan TTS)
- film grain (noise) + vignette (anti full-AI look)
- text overlay 4 momen kunci (drawtext di video final)
- ambience bed crickets CC0 di-mix rendah di bawah voiceover
Penggunaan: python3 rakit_2026-10-12.py
"""
import subprocess, os, glob, sys, json, shutil

WS = "/home/hatch/workspace/youtube-otomatis/horror-en"
GDIR = f"{WS}/gambar/2026-10-12"
AUDIO = f"{WS}/audio/gabungan-2026-10-12.mp3"
DURJSON = f"{WS}/audio/durasi-beat-2026-10-12.json"
SFX = f"{WS}/audio/sfx-crickets-bed.mp3"
OUT = f"{WS}/video/2026-10-12.mp4"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
NIMG = 69
SCARE = {2, 31, 44, 50, 55, 62}
TITLE_DUR = 3.0
STORY_TITLE = "THE STAIRS"

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def find_font():
    for cand in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(cand):
            return cand
    r = subprocess.run(["fc-list", ":style=Bold", "file"], capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        p = ln.split(":")[0].strip()
        if p.endswith(".ttf") and os.path.exists(p):
            return p
    return None

def kenburns_light(img, seg_dur, idx, out):
    total_frames = max(1, int(seg_dur * 30))
    mode = idx % 4
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='(iw-iw/zoom)*on/{total_frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    elif mode == 2:
        zp = f"zoompan=z='max(1.15-0.0012*on,1.0)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    else:
        zp = f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{total_frames}':s=1280x720:fps=30"
    vf = (f"scale=1280:720,{zp},"
          "eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
          "noise=alls=6:allf=t,"
          "vignette=PI/5")
    r = subprocess.run([FQ, "-y", "-loop", "1", "-i", img,
                        "-vf", vf, "-t", str(seg_dur),
                        "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", out],
                       capture_output=True)
    return r.returncode == 0

def render_title_card(out, font):
    dt1 = (f"drawtext=fontfile='{font}':text='{STORY_TITLE}':fontsize=64:fontcolor=white:"
           "borderw=2:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-30")
    dt2 = (f"drawtext=fontfile='{font}':text='A MIDNIGHT DREAD TALES ORIGINAL':fontsize=26:fontcolor=0xbbbbbb:"
           "x=(w-text_w)/2:y=(h-text_h)/2+70")
    vf = (f"color=c=0x0a0a0f:s=1280x720:d={TITLE_DUR}:r=30,{dt1},{dt2},"
          "noise=alls=8:allf=t,vignette=PI/4,format=yuv420p")
    r = subprocess.run([FQ, "-y", "-f", "lavfi", "-i", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-t", str(TITLE_DUR), out],
                       capture_output=True)
    return r.returncode == 0

def main():
    font = find_font()
    assert font, "tidak ada font TTF untuk drawtext"
    imgs = sorted(glob.glob(os.path.join(GDIR, "beat-2026-10-12-*.webp")))
    assert len(imgs) == NIMG, f"butuh {NIMG} gambar, ada {len(imgs)}"
    dj = json.load(open(DURJSON))
    seg_durs = [TITLE_DUR]
    for i in range(NIMG):
        sil = 2.2 if (i + 1) in SCARE else 0.4
        seg_durs.append(sil + float(dj[f"beat-{i+1:03d}"]))
    print(f"{NIMG} gambar + title card, target {sum(seg_durs)/60:.1f} mnt", flush=True)
    tmpd = os.path.join(os.path.dirname(OUT), "_tmp_segs_20261012")
    os.makedirs(tmpd, exist_ok=True)
    tc = os.path.join(tmpd, "s_title.mp4")
    if not (os.path.exists(tc) and dur(tc) >= TITLE_DUR * 0.9):
        print("  render title card...", flush=True)
        assert render_title_card(tc, font), "gagal render title card"
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        if os.path.exists(s) and dur(s) >= seg_durs[i + 1] * 0.9:
            continue
        if os.path.exists(s):
            os.remove(s)
        print(f"  render s{i:03d} ({seg_durs[i+1]:.1f}s)...", flush=True)
        for attempt in range(2):
            if kenburns_light(img, seg_durs[i + 1], i, s) and dur(s) >= seg_durs[i + 1] * 0.9:
                break
            print(f"    retry s{i:03d}", flush=True)
        else:
            print(f"GAGAL: s{i:03d}"); sys.exit(1)
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{NIMG} segmen...", flush=True)
    segs = [tc] + [os.path.join(tmpd, f"s{i:03d}.mp4") for i in range(NIMG)]
    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{os.path.abspath(s)}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    subprocess.run([FQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", concat], capture_output=True, check=True)
    cum = [TITLE_DUR]
    for d in seg_durs[1:]:
        cum.append(cum[-1] + d)
    def t(beat, off=1.0):
        return cum[beat - 1] + off
    overlays = [
        (t(1), t(1) + 4.0, "IT WHISPERED MY FULL NAME"),
        (t(34), t(34) + 3.5, "FOURTEEN STEPS TO NOWHERE"),
        (t(50), t(50) + 3.5, "HE WAS SIMPLY GONE"),
        (t(55), t(55) + 3.0, "ONLY GOES UP WHEN SHE IS HUNGRY"),
    ]
    dt_filters = []
    for ts, te, txt in overlays:
        dt_filters.append(
            f"drawtext=fontfile='{font}':text='{txt}':fontsize=44:fontcolor=white:"
            f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h*0.78:"
            f"enable='between(t,{ts:.2f},{te:.2f})'")
    vf_overlay = ",".join(dt_filters)
    overlaid = os.path.join(tmpd, "overlaid.mp4")
    subprocess.run([FQ, "-y", "-i", concat, "-vf", vf_overlay,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", overlaid], capture_output=True, check=True)
    total = dur(overlaid)
    final_a = os.path.join(tmpd, "final_audio.m4a")
    af = (f"[1:a]volume=0.07,aloop=loop=-1:size=2000000,atrim=0:{total:.2f}[bed];"
          f"[0:a][bed]amix=inputs=2:duration=first:dropout_transition=0,"
          f"afade=t=in:st=0:d=1,afade=t=out:st={total-3:.2f}:d=3[a]")
    subprocess.run([FQ, "-y", "-i", AUDIO, "-stream_loop", "-1", "-i", SFX,
                    "-filter_complex", af, "-map", "[a]",
                    "-c:a", "aac", "-b:a", "128k", final_a],
                   capture_output=True, check=True)
    subprocess.run([FQ, "-y", "-i", overlaid, "-i", final_a,
                    "-c:v", "copy", "-c:a", "copy",
                    "-shortest", "-movflags", "+faststart", OUT],
                   capture_output=True, check=True)
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)", flush=True)
    shutil.rmtree(tmpd)

if __name__ == "__main__":
    main()
