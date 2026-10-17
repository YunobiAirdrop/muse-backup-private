#!/usr/bin/env python3
"""Assemble Jejak Islami LONG 2026-10-17 (Nabi Ibrahim) — single-pass encode.
20 slots x 19.52s = 390.4s, matched to narration 390.3s. Text overlays + audio mux.
Writes to TEMP first, verifies duration, then moves to final.
"""
import json, math, os, shutil, subprocess, sys

W = "/home/hatch/workspace/kisah-islami/work/2026-10-17"
FF = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NARR = os.path.join(W, "audio/narration-full.mp3")
CL = os.path.join(W, "clips")
SLOT = 32.53
N = 12

# (clip_file, ss_offset) — 12 slots; tiap klip maks 2x, offset beda (aturan anti-macet)
# Terverifikasi frame: c02 api unggun, c07 bintang gurun, c08 milky way,
# c09 masjid Kazimiyah Baghdad (arsip), c10 Baghdad (arsip), c14 bukit dramatis
CLIPS = [
    (f"{CL}/c02.ogv", 0),    # s00 hook: api unggun malam
    (f"{CL}/c10.webm", 0),   # s01 Babilonia: Baghdad arsip
    (f"{CL}/c07.webm", 0),   # s02 malam: bintang (mencari Tuhan)
    (f"{CL}/c09.webm", 0),   # s03 masjid Kazimiyah arsip
    (f"{CL}/c14.webm", 0),   # s04 dramatis: bukit + awan
    (f"{CL}/c08.webm", 0),   # s05 milky way
    (f"{CL}/c02.ogv", 5),    # s06 api dinyalakan (offset beda)
    (f"{CL}/c07.webm", 3),   # s07 mukjizat: langit malam
    (f"{CL}/c10.webm", 40),  # s08 Baghdad offset beda
    (f"{CL}/c09.webm", 12),  # s09 refleksi: masjid offset beda
    (f"{CL}/c14.webm", 4),   # s10 bukit offset beda
    (f"{CL}/c08.webm", 2),   # s11 penutup: milky way offset beda
]

OVERLAYS = [
    # (text, t_start, t_end, fontsize, color)
    ("BABILONIA - NEGERI PENYEMBAH BERHALA", 31, 36, 44, "#FFD700"),
    ("AKU TIDAK SUKA PADA YANG TENGGELAM", 68, 73, 44, "#FFD700"),
    ("TANYAKAN SAJA PADA BERHALA BESAR ITU", 111, 116, 44, "#FFD700"),
    ("NAMRUDZ - RAJA YANG MENGAKU TUHAN", 154, 159, 44, "#FFD700"),
    ("WAHAI API - JADILAH DINGIN", 231, 237, 48, "#FFD700"),
    ("SUBSCRIBE JEJAK ISLAMI", 195, 198, 54, "white"),
    ("SUBSCRIBE - AKTIFKAN LONCENG", 385, 390, 54, "white"),
]

def probe_dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0

def main():
    if len(CLIPS) != N:
        print(f"CLIPS harus {N}, dapat {len(CLIPS)}"); sys.exit(1)
    narr_dur = probe_dur(NARR)
    print(f"narasi: {narr_dur:.1f}s, target video: {SLOT*N:.1f}s", flush=True)

    inputs = []
    fc_parts = []
    for i, (cf, sso) in enumerate(CLIPS):
        dur = probe_dur(cf)
        need = SLOT + sso + 1.0
        loops = max(0, math.ceil(need / max(dur, 0.1)) - 1)
        if loops > 0:
            inputs += ["-stream_loop", str(loops)]
        inputs += ["-ss", str(sso), "-i", cf]
        fc_parts.append(
            f"[{i}:v]trim=start=0:end={SLOT},setpts=PTS-STARTPTS,"
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,setsar=1,fps=25,eq=contrast=1.05:saturation=0.95,"
            f"noise=alls=7:allf=t,format=yuv420p[v{i}]")
    concat_in = "".join(f"[v{i}]" for i in range(N))
    fc_parts.append(f"{concat_in}concat=n={N}:v=1:a=0[vcat]")

    # drawtext overlays (no %, no apostrophe, no colon in text)
    dt = "[vcat]"
    for j, (txt, ts, te, fs, col) in enumerate(OVERLAYS):
        safe = txt.replace("'", "").replace("%", "").replace(":", r"\:")
        dt += (f"drawtext=fontfile={FONT}:text='{safe}':fontsize={fs}:"
               f"fontcolor={col}:borderw=3:bordercolor=black@0.9:"
               f"x=(w-text_w)/2:y=h-170:enable='between(t,{ts},{te})'")
        if j < len(OVERLAYS) - 1:
            dt += ","
    dt += "[vout]"
    fc_parts.append(dt)
    fc = ";".join(fc_parts)

    tmp = os.path.join(W, "jejak-islami-2026-10-17-long-TEMP.mp4")
    final = os.path.join(W, "jejak-islami-2026-10-17-long.mp4")
    narr_idx = N  # audio input index
    cmd = ([FF, "-hide_banner", "-loglevel", "error"] + inputs +
           ["-i", NARR, "-filter_complex", fc,
            "-map", "[vout]", "-map", f"{narr_idx}:a",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", "-shortest", "-y", tmp])
    print("menjalankan ffmpeg (single pass)...", flush=True)
    logf = open(os.path.join(W, "ffmpeg-err.log"), "w")
    r = subprocess.run(cmd, stderr=logf, stdout=logf)
    logf.close()
    if r.returncode != 0:
        print("ffmpeg GAGAL — lihat ffmpeg-err.log"); sys.exit(1)
    vd = probe_dur(tmp)
    print(f"hasil TEMP: {vd:.1f}s (target {SLOT*N:.1f}s)", flush=True)
    if abs(vd - SLOT * N) > 8:
        print("DURASI TIDAK VALID — final tidak ditimpa"); sys.exit(1)
    shutil.move(tmp, final)
    print(f"OK final: {final} ({os.path.getsize(final)//1024//1024}MB)")

if __name__ == "__main__":
    main()
