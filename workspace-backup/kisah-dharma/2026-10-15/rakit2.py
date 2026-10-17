#!/usr/bin/env python3
"""Rakit LONG Kisah Dharma 2026-10-15 v2: MINIM antrian ffmpeg-queue.
Hanya 4x akuisisi slot (bumper, concat besar, audio, final mux) — bukan 29x.
_seg_title.mp4 sudah ada dari run sebelumnya (pakai ulang)."""
import subprocess, os, sys
from PIL import Image

D = "/home/hatch/workspace/kisah-dharma/2026-10-15"
FT = "/home/hatch/workspace/kisah-dharma/2026-10-13/footage"
FTF = os.path.join(D, "footage")
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-kisahdharma.wav"
VO = os.path.join(D, "vo.mp3")
BUMPER_D = 5.366
TITLE_D = 6.0
B = [50.760, 72.048, 75.168, 81.912, 34.872, 73.800, 61.128, 72.792]

# (clip, offset, dur) — "title"/"bumper" = file jadi
SEGS = [
    ("title", None, TITLE_D),
    ("f:kd-f02", 0, 18.00), ("f:kd-f01", 5, 32.76),
    ("kd-08", 10, 36.00), ("kd-06", 5, 36.05),
    ("kd-18", 1, 20.00), ("kd-19", 1, 22.00), ("kd-04", 30, 33.17),
    ("f:kd-f03", 0, 15.00), ("f:kd-f04", 0, 15.00), ("f:kd-f05", 0, 16.00),
    ("f:kd-f01", 30, 20.00), ("f:kd-f08", 0, 15.91),
    ("bumper", None, BUMPER_D),
    ("kd-02", 2, 20.00), ("kd-09", 1, 14.87),
    ("kd-17", 10, 30.00), ("kd-20", 20, 28.00), ("kd-10", 1, 15.80),
    ("f:kd-f06", 0, 20.00), ("kd-14", 1, 25.00), ("kd-21", 10, 16.13),
    ("f:kd-f08", 10, 20.00), ("kd-05", 10, 26.00), ("kd-04", 90, 26.79),
]

def run(cmd, desc):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"GAGAL {desc}:\n{r.stderr[-1500:]}"); sys.exit(1)

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def src_of(clip):
    if clip.startswith("f:"):
        return os.path.join(FTF, clip[2:] + ".mp4")
    return os.path.join(FT, clip + ".mp4")

def main():
    # 1) bumper (title sudah ada; frame pakai ulang _title_frame.jpg biar hemat 1 slot)
    bfr = os.path.join(D, "_title_frame.jpg")
    assert os.path.exists(bfr), "frame title hilang!"
    bseg = os.path.join(D, "_seg_bumper.mp4")
    if not os.path.exists(bseg):
        tf = int(BUMPER_D * 30)
        vf = (f"zoompan=z='1.0+0.0012*on':d={tf}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"s=1280x720:fps=30,eq=contrast=1.05:saturation=1.02,noise=alls=8:allf=t,"
              f"drawtext=fontfile={FONT}:text='KISAH DHARMA':fontsize=44:fontcolor=white:"
              f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-120,format=yuv420p")
        run([FQ, "-y", "-loop", "1", "-i", bfr, "-vf", vf, "-t", str(BUMPER_D),
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-r", "30",
             "-an", bseg], "render bumper")
    print("bumper ok", flush=True)

    # 2) SATU concat besar: semua input + filter per-input + concat
    tseg = os.path.join(D, "_seg_title.mp4")
    assert os.path.exists(tseg), "title hilang!"
    inputs = []
    fparts = []
    n = 0
    for clip, off, durv in SEGS:
        if clip == "title":
            inputs += ["-i", tseg]
        elif clip == "bumper":
            inputs += ["-i", bseg]
        else:
            inputs += ["-ss", str(off), "-t", f"{durv:.2f}", "-i", src_of(clip)]
        fparts.append(
            f"[{n}:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,"
            f"fps=30,eq=contrast=1.05:saturation=1.02,noise=alls=8:allf=t,"
            f"format=yuv420p,setsar=1,setpts=PTS-STARTPTS[v{n}]")
        n += 1
    fparts.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vout]")
    vconcat = os.path.join(D, "_vconcat.mp4")
    run([FQ, "-y"] + inputs + ["-filter_complex", ";".join(fparts),
         "-map", "[vout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
         "-r", "30", vconcat], "concat besar")
    vd = dur(vconcat)
    print(f"_vconcat: {vd:.2f}s", flush=True)

    # 3) audio: 6s hening + vo[0:T_B] + bumper + vo[T_B:end]
    T_B = sum(B[:4])
    afull = os.path.join(D, "_afull.m4a")
    fc = (f"anullsrc=r=44100:cl=stereo:d={TITLE_D}[sil];"
          f"[0:a]atrim=0:{T_B:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a0];"
          f"[0:a]atrim={T_B:.2f},asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo[a2];"
          f"[1:a]aresample=44100,aformat=channel_layouts=stereo[b];"
          f"[sil][a0][b][a2]concat=n=4:v=0:a=1[outa]")
    run([FQ, "-y", "-i", VO, "-i", BUMPER, "-filter_complex", fc,
         "-map", "[outa]", "-c:a", "aac", "-b:a", "128k", afull], "rakit audio")
    ad = dur(afull)
    print(f"_afull: {ad:.2f}s", flush=True)
    assert abs(vd - ad) < 1.5, f"AV mismatch: {vd:.2f} vs {ad:.2f}"

    # 4) final mux + text overlay
    dt = (f"drawtext=fontfile={FONT}:text='SUNDARA KANDA':fontsize=64:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,60,68)',"
          f"drawtext=fontfile={FONT}:text='Kitab Kelima Ramayana':fontsize=40:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,60,68)',"
          f"drawtext=fontfile={FONT}:text='100 YOJANA':fontsize=64:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,124,132)',"
          f"drawtext=fontfile={FONT}:text='Samudra Menuju Alengka':fontsize=40:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,124,132)',"
          f"drawtext=fontfile={FONT}:text='SUBSCRIBE - KISAH DHARMA':fontsize=52:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,272,280)',"
          f"drawtext=fontfile={FONT}:text='DRISHTA SITA':fontsize=64:fontcolor=white:"
          f"borderw=3:bordercolor=black:x=(w-text_w)/2:y=120:enable='between(t,405,413)',"
          f"drawtext=fontfile={FONT}:text='Shinta Telah Ditemukan':fontsize=40:fontcolor=white:"
          f"borderw=2:bordercolor=black:x=(w-text_w)/2:y=200:enable='between(t,405,413)',"
          f"drawtext=fontfile={FONT}:text='Om Shanti\\, Shanti\\, Shanti\\, Om':fontsize=48:"
          f"fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-140:"
          f"enable='between(t,527,533.8)'")
    tmp_master = os.path.join(D, "_master_tmp.mp4")
    run([FQ, "-y", "-i", vconcat, "-i", afull, "-vf", dt,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "copy", "-movflags", "+faststart", "-shortest", tmp_master],
        "final mux")
    md = dur(tmp_master)
    print(f"MASTER tmp: {md:.2f}s", flush=True)
    assert abs(md - vd) < 5, f"durasi master menyimpang: {md:.2f} vs {vd:.2f}"
    master = os.path.join(D, "kisah-dharma-2026-10-15-long.mp4")
    os.replace(tmp_master, master)

    small = os.path.join(D, "kisah-dharma-2026-10-15-long-small.mp4")
    run([FQ, "-y", "-i", master, "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "26", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
         small], "versi small")
    sz = os.path.getsize(small) / 1e6
    print(f"SMALL: {dur(small):.2f}s, {sz:.1f}MB", flush=True)
    assert sz < 100, "small > 100MB!"
    print("SELESAI:", master, flush=True)

if __name__ == "__main__":
    main()
