#!/usr/bin/env python3
"""Rakit video Cosmic Unknown 2026-10-11 (black holes): 72 gambar Ken Burns 1280x720
+ voiceover (18 beats + bumper mid) + film grain + grading natural
+ text overlay momen kunci + CTA subscribe + burned subtitles (SRT per kalimat).
Penggunaan: python3 rakit_space_720_20261011.py
"""
import subprocess, os, json, shutil, re

BASE = "/home/hatch/workspace/youtube-otomatis/space-en"
GDIR = os.path.join(BASE, "gambar/2026-10-11")
ADIR = os.path.join(BASE, "audio/2026-10-11")
AUDIO = os.path.join(ADIR, "voiceover-full.mp3")
BUMPER_WAV = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-space-en.wav"
DUR_JSON = os.path.join(BASE, "script/durasi-segmen-2026-10-11.json")
SRT = os.path.join(BASE, "script/subtitle-2026-10-11.srt")
TIMING_JSON = os.path.join(BASE, "script/timing-beat-2026-10-11.json")
OUT = os.path.join(BASE, "video/2026-10-11.mp4")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SIL_DUR = 0.45  # jeda antar beat

BEATS = [f"beat-{k:03d}" for k in range(1, 19)]

# (beat narasi, teks overlay)
OVERLAYS = [
    (5, "PAST THE POINT OF NO RETURN"),
    (7, "4.3 MILLION SUNS \u2014 IN OUR BACKYARD"),
    (8, "66 BILLION TIMES THE SUN"),
    (10, "BLACK HOLES SLOWLY EVAPORATE"),
    (12, "PHOTOGRAPHED: APRIL 10, 2019"),
]

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def beat_text(n):
    p = os.path.join(BASE, "script/script-2026-10-11.md")
    txt = open(p).read()
    m = re.search(rf"\[BEAT {n:03d}\]\n(.*?)(?=\n\[BEAT |\Z)", txt, re.S)
    return m.group(1).strip() if m else ""

def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in parts if s.strip()]

def srt_ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("GAGAL:", " ".join(cmd)); print(r.stderr[-1500:]); raise SystemExit(1)
    return r

def main():
    os.makedirs(ADIR, exist_ok=True)
    beat_durs = {}
    for b in BEATS:
        p = os.path.join(ADIR, f"{b}.mp3")
        d = dur(p)
        if d < 5:
            print(f"AUDIO HILANG/RUSAK: {b}.mp3"); return
        beat_durs[b] = d
    print(f"18 beat OK, total voiceover {sum(beat_durs.values()):.0f}s", flush=True)

    # silence + bumper (konversi ke mp3 agar concat demuxer seragam)
    sil = os.path.join(ADIR, "_sil.mp3")
    run([FFQ, "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=stereo:d={SIL_DUR}",
         "-c:a", "libmp3lame", "-b:a", "128k", sil])
    bumper = os.path.join(ADIR, "_bumper.mp3")
    run([FFQ, "-y", "-i", BUMPER_WAV, "-c:a", "libmp3lame", "-b:a", "128k", bumper])
    bumper_dur = dur(bumper)
    print(f"bumper {bumper_dur:.2f}s", flush=True)

    # pilih batas beat terdekat 50% durasi voiceover -> sisip bumper di jeda natural
    total_vo = sum(beat_durs.values()) + SIL_DUR * 18
    cum, t = {}, 0.0
    for b in BEATS:
        cum[b] = t; t += beat_durs[b] + SIL_DUR
    target = total_vo / 2
    k_insert = min(range(1, 19), key=lambda k: abs((cum[f"beat-{k:03d}"] + beat_durs[f"beat-{k:03d}"] + SIL_DUR) - target))
    print(f"bumper disisip setelah beat-{k_insert:03d} (tengah video)", flush=True)

    # rakit audio: beat, sil, ... + bumper setelah beat k_insert
    parts = []
    for k in range(1, 19):
        b = f"beat-{k:03d}"
        parts += [os.path.join(ADIR, f"{b}.mp3"), sil]
        if k == k_insert:
            parts.append(bumper)
    lst = os.path.join(ADIR, "_audiolist.txt")
    with open(lst, "w") as f:
        for p_ in parts: f.write(f"file '{p_}'\n")
    run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", AUDIO])
    print(f"voiceover-full {dur(AUDIO):.0f}s", flush=True)

    # timing beat pasca-bumper (awal tiap beat dlm timeline video)
    starts, t = {}, 0.0
    for k in range(1, 19):
        b = f"beat-{k:03d}"
        starts[b] = t
        t += beat_durs[b] + SIL_DUR
        if k == k_insert:
            t += bumper_dur
    json.dump({"starts": starts, "beat_durs": beat_durs, "bumper_after": k_insert,
               "bumper_dur": bumper_dur, "total": t}, open(TIMING_JSON, "w"), indent=1)

    # durasi per segmen gambar = (beat_dur + sil) / 4; segmen terakhir beat k_insert += bumper
    seg_durs, seg_names = [], []
    for k in range(1, 19):
        b = f"beat-{k:03d}"
        sd = (beat_durs[b] + SIL_DUR) / 4
        for v in "abcd":
            seg_durs.append(sd); seg_names.append(f"{b}-{v}")
    seg_durs[(k_insert - 1) * 4 + 3] += bumper_dur
    json.dump({f"seg-{i+1:03d}": round(d_, 3) for i, d_ in enumerate(seg_durs)},
              open(DUR_JSON, "w"), indent=1)
    print(f"72 segmen gambar, total {sum(seg_durs):.0f}s", flush=True)

    # SRT: kalimat per beat, timing proporsional karakter
    srt_lines, idx = [], 1
    for k in range(1, 19):
        b = f"beat-{k:03d}"
        sents = sentences(beat_text(k))
        tot_chars = sum(len(s) for s in sents) or 1
        span = beat_durs[b] + SIL_DUR
        t0 = starts[b]
        for s in sents:
            d_ = span * len(s) / tot_chars
            srt_lines.append(f"{idx}\n{srt_ts(t0)} --> {srt_ts(t0 + d_)}\n{s}\n")
            idx += 1; t0 += d_
    open(SRT, "w").write("\n".join(srt_lines))
    print(f"SRT {idx-1} caption ditulis", flush=True)

    # --- render segmen Ken Burns ---
    imgs = []
    for name in seg_names:
        p = os.path.join(GDIR, name + ".webp")
        if not os.path.exists(p):
            print(f"GAMBAR HILANG: {name}.webp"); return
        imgs.append(p)

    tmpd = os.path.join(BASE, "video", "_tmp_segs_2026-10-11")
    os.makedirs(tmpd, exist_ok=True)

    def kenburns(img, seg_dur, i, out):
        total_frames = max(int(seg_dur * 30), 15)
        mode = i % 4
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
        r = subprocess.run([FFQ, "-y", "-loop", "1", "-i", img, "-vf", vf, "-t", str(seg_dur),
                            "-c:v", "libx264", "-preset", "veryfast",
                            "-pix_fmt", "yuv420p", "-r", "30", out], capture_output=True)
        return r.returncode == 0

    segs = []
    for i, img in enumerate(imgs):
        s = os.path.join(tmpd, f"s{i:03d}.mp4")
        ok = os.path.exists(s) and dur(s) >= seg_durs[i] * 0.9
        if not ok:
            if os.path.exists(s): os.remove(s)
            for _ in range(2):
                if kenburns(img, seg_durs[i], i, s) and dur(s) >= seg_durs[i] * 0.9:
                    break
                print(f"  retry s{i:03d}", flush=True)
        segs.append(s)
        if (i + 1) % 12 == 0: print(f"  {i+1}/{len(imgs)} segmen...", flush=True)

    lst = os.path.join(tmpd, "list.txt")
    with open(lst, "w") as f:
        for s in segs: f.write(f"file '{s}'\n")
    concat = os.path.join(tmpd, "concat.mp4")
    run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", concat])
    raw = os.path.join(BASE, "video", "2026-10-11-raw.mp4")
    run([FFQ, "-y", "-i", concat, "-i", AUDIO, "-c:v", "copy", "-c:a", "aac",
         "-b:a", "128k", "-shortest", "-movflags", "+faststart", raw])
    print("mux OK", flush=True)

    # --- final pass: overlay teks momen kunci + CTA subscribe + burned subtitles ---
    filters = []
    for beat, teks in OVERLAYS:
        s = starts[f"beat-{beat:03d}"]
        e = s + beat_durs[f"beat-{beat:03d}"] + SIL_DUR
        filters.append(
            f"drawtext=fontfile={FONT}:text='{teks}':fontsize=54:fontcolor=white:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.78:"
            f"enable='between(t,{s:.2f},{e:.2f})'"
        )
    mid = sum(seg_durs) / 2
    filters.append(
        f"drawtext=fontfile={FONT}:text='SUBSCRIBE FOR DAILY COSMIC MYSTERIES':fontsize=44:"
        f"fontcolor=yellow:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h*0.70:"
        f"enable='between(t,{mid-1.5:.2f},{mid+1.5:.2f})'"
    )
    srt_esc = SRT.replace("'", r"'\''")
    filters.append(
        f"subtitles=filename='{srt_esc}':force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=28,Alignment=2'"
    )
    vf = ",".join(filters)
    run([FFQ, "-y", "-i", raw, "-vf", vf, "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "copy", OUT])
    print(f"OK: {OUT} ({dur(OUT)/60:.1f} menit)")
    shutil.rmtree(tmpd, ignore_errors=True)
    if os.path.exists(raw): os.remove(raw)

if __name__ == "__main__":
    main()
