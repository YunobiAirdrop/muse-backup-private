#!/usr/bin/env python3
"""Sisipkan bumper suara (clone user) di tengah video long 2026-10-14.
Titik: awal jeda sebelum beat 49 (dihitung dinamis dari durasi-beat JSON).
Bumper: bumper-horror-en.wav, visual = gambar beat-048 (kenburns ringan) + bed crickets rendah.
Output: video/2026-10-14.mp4 (timpa, backup .pre-bumper).
Info titik+durasi -> bumper-info-2026-10-14.json (dibaca potong_shorts).
Penggunaan: python3 sisip_bumper_2026-10-14.py
"""
import subprocess, os, sys, json, shutil

WS = "/home/hatch/workspace/youtube-otomatis/horror-en"
VIDEO = f"{WS}/video/2026-10-14.mp4"
BUMPER_WAV = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-horror-en.wav"
SFX = f"{WS}/audio/sfx-crickets-bed.mp3"
IMG = f"{WS}/gambar/2026-10-14/beat-2026-10-14-048.webp"
DURJSON = f"{WS}/audio/durasi-beat-2026-10-14.json"
INFO = f"{WS}/bumper-info-2026-10-14.json"
FQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
SCARE = {4, 24, 33, 47, 58, 66}
N = 72

def run(cmd, desc):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"GAGAL {desc}: {r.stderr[-400:]}")
        sys.exit(1)

def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    assert os.path.exists(VIDEO), "video final belum ada"
    assert os.path.exists(IMG), f"gambar bumper belum ada: {IMG}"
    dj = json.load(open(DURJSON))
    # S[i] = awal jeda sebelum beat i+1 (S[0]=0); title card 3.0 dtk
    S = [3.0]
    for i in range(1, N + 1):
        sil = 2.2 if i in SCARE else 0.4
        S.append(S[-1] + sil + float(dj[f"beat-{i:03d}"]))
    T_CUT = S[48]  # awal jeda sebelum beat 49
    BUMPER_D = dur(BUMPER_WAV)
    print(f"titik sisip: {T_CUT:.2f}s (awal jeda beat 49), bumper {BUMPER_D:.2f}s", flush=True)
    tmpd = f"{WS}/video/_bumper_tmp_1014"
    os.makedirs(tmpd, exist_ok=True)
    bvid = os.path.join(tmpd, "bumper_vid.mp4")
    tf = int(BUMPER_D * 30)
    vf = (f"scale=1280:720,"
          f"zoompan=z='min(zoom+0.0012,1.15)':d={tf}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30,"
          f"eq=contrast=1.08:saturation=0.92:brightness=-0.02,noise=alls=6:allf=t,vignette=PI/5")
    run([FQ, "-y", "-loop", "1", "-i", IMG, "-vf", vf, "-t", str(BUMPER_D),
         "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", bvid],
        "render bumper video")
    baud = os.path.join(tmpd, "bumper_aud.m4a")
    run([FQ, "-y", "-i", BUMPER_WAV, "-stream_loop", "-1", "-i", SFX,
         "-filter_complex",
         f"[1:a]volume=0.07,atrim=0:{BUMPER_D}[bed];[0:a][bed]amix=inputs=2:duration=first[a]",
         "-map", "[a]", "-c:a", "aac", "-b:a", "128k", "-t", str(BUMPER_D), baud],
        "mix bumper audio")
    bseg = os.path.join(tmpd, "bumper_seg.mp4")
    run([FQ, "-y", "-i", bvid, "-i", baud, "-c:v", "copy", "-c:a", "copy",
         "-shortest", bseg], "gabung bumper seg")
    out = os.path.join(tmpd, "final_bumper.mp4")
    fc = (f"[0:v]trim=0:{T_CUT},setpts=PTS-STARTPTS[v0];"
          f"[0:a]atrim=0:{T_CUT},asetpts=PTS-STARTPTS[a0];"
          f"[1:v]setpts=PTS-STARTPTS[v1];[1:a]asetpts=PTS-STARTPTS[a1];"
          f"[0:v]trim={T_CUT},setpts=PTS-STARTPTS[v2];"
          f"[0:a]atrim={T_CUT},asetpts=PTS-STARTPTS[a2];"
          f"[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]")
    run([FQ, "-y", "-i", VIDEO, "-i", bseg, "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        "splice bumper")
    d0 = dur(VIDEO)
    d1 = dur(out)
    print(f"durasi: {d0:.1f}s -> {d1:.1f}s (selisih {d1-d0:.2f}s, harap ~{BUMPER_D:.2f})", flush=True)
    assert abs((d1 - d0) - BUMPER_D) < 1.0, "selisih durasi tidak wajar!"
    shutil.copy2(VIDEO, VIDEO + ".pre-bumper")
    os.replace(out, VIDEO)
    shutil.rmtree(tmpd)
    json.dump({"t_cut": round(T_CUT, 2), "bumper_d": round(d1 - d0, 2)}, open(INFO, "w"))
    print(f"OK: bumper tersisip di {T_CUT:.2f}s -> {VIDEO}; info -> {INFO}", flush=True)

if __name__ == "__main__":
    main()
