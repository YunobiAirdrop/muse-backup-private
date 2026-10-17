#!/usr/bin/env python3
"""Rakit POV 2026-10-14 gaya chunk (hemat antrean ffmpeg): tiap chunk = ~22 gambar
dalam SATU panggilan ffmpeg (filter_complex), lalu concat + mux audio.
Pakai ulang segmen s000-s009 yang sudah jadi di _tmp_segs_2026-10-14 bila ada.
Output: TEMP dulu -> verifikasi durasi -> pindah ke final (aturan AGENTS.md)."""
import subprocess, os, sys, json, shutil, glob

BASE = "/home/hatch/workspace/youtube-otomatis"
FFQ = os.path.join(BASE, "ffmpeg-queue.sh")
GDIR = os.path.join(BASE, "gambar/2026-10-14")
AUDIO = os.path.join(BASE, "audio/gabungan-2026-10-14-fast.mp3")
DJ = os.path.join(BASE, "audio/durasi-beat-2026-10-14.json")
TMPD = os.path.join(BASE, "video/_tmp_segs_2026-10-14")
OUT_FINAL = os.path.join(BASE, "video/2026-10-14.mp4")
OUT_TMP = os.path.join(BASE, "video/_tmp_2026-10-14.mp4")
CHUNK = 22

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

def zp(idx, frames):
    mode = idx % 4
    if mode == 0:
        return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    if mode == 1:
        return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    if mode == 2:
        return f"zoompan=z='max(1.15-0.0012*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30"
    return f"zoompan=z='min(zoom+0.0012,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*on/{frames}':s=1280x720:fps=30"

def render_chunk(idxs, seg_durs, out):
    if os.path.exists(out):
        exp = sum(seg_durs[i] for i in idxs)
        if abs(dur(out) - exp) < 3:
            print(f"  chunk ada: {out}", flush=True); return
        os.remove(out)
    cmd = [FFQ, "-y"]
    for i in idxs:
        cmd += ["-i", os.path.join(GDIR, f"beat-{i+1:03d}.webp")]
    parts, vlabels = [], []
    for k, i in enumerate(idxs):
        frames = int(seg_durs[i] * 30)
        parts.append(
            f"[{k}:v]scale=1280:720,{zp(i, frames)},"
            f"eq=contrast=1.08:saturation=0.92:brightness=-0.02,"
            f"noise=alls=6:allf=t,vignette=PI/5,setsar=1,"
            f"trim=duration={seg_durs[i]:.3f},setpts=PTS-STARTPTS[v{k}]")
        vlabels.append(f"[v{k}]")
    fc = ";".join(parts) + ";" + "".join(vlabels) + f"concat=n={len(idxs)}:v=1:a=0[vout]"
    cmd += ["-filter_complex", fc, "-map", "[vout]",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)
    print(f"  OK chunk -> {out} ({dur(out):.1f}s)", flush=True)

def main():
    dj = json.load(open(DJ))
    n = len(dj)
    seg_durs = [float(dj[f"beat-{i+1:03d}"]) for i in range(n)]
    os.makedirs(TMPD, exist_ok=True)
    # segmen per-beat yang sudah jadi (s000..s009 dari run sebelumnya)
    have = sorted(glob.glob(os.path.join(TMPD, "s[0-9][0-9][0-9].mp4")))
    have_idx = set()
    for s in have:
        i = int(os.path.basename(s)[1:4])
        if dur(s) >= seg_durs[i] * 0.9:
            have_idx.add(i)
        else:
            os.remove(s)
    print(f"{len(have_idx)} segmen per-beat dipakai ulang", flush=True)
    todo = [i for i in range(n) if i not in have_idx]
    chunks = [todo[i:i+CHUNK] for i in range(0, len(todo), CHUNK)]
    chunk_files = []
    for c, idxs in enumerate(chunks):
        out = os.path.join(TMPD, f"chunk{c}.mp4")
        print(f"render chunk{c}: beat {idxs[0]+1}-{idxs[-1]+1} ...", flush=True)
        render_chunk(idxs, seg_durs, out)
        chunk_files.append(out)
    # urutan final: gabung segmen per-beat + chunk, urut by beat
    order = []
    ci = 0
    i = 0
    # bangun daftar file berurutan
    segs = {}
    for s in glob.glob(os.path.join(TMPD, "s[0-9][0-9][0-9].mp4")):
        segs[int(os.path.basename(s)[1:4])] = s
    chunk_map = {}
    for c, idxs in enumerate(chunks):
        for j in idxs:
            chunk_map[j] = (c, idxs[0], idxs[-1])
    ordered, used_chunks = [], set()
    for i in range(n):
        if i in segs:
            ordered.append(segs[i])
        else:
            c = chunk_map[i][0]
            if c not in used_chunks:
                ordered.append(os.path.join(TMPD, f"chunk{c}.mp4"))
                used_chunks.add(c)
    assert len(ordered) == len(have_idx) + len(chunks), f"urutan janggal: {len(ordered)}"
    lst = os.path.join(TMPD, "list.txt")
    with open(lst, "w") as f:
        for p in ordered:
            f.write(f"file '{os.path.abspath(p)}'\n")
    concat = os.path.join(TMPD, "concat.mp4")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", concat], capture_output=True, check=True)
    subprocess.run([FFQ, "-y", "-i", concat, "-i", AUDIO,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", OUT_TMP],
                   capture_output=True, check=True)
    expected = sum(seg_durs)
    got = dur(OUT_TMP)
    print(f"verifikasi: expected {expected:.1f}s, got {got:.1f}s", flush=True)
    assert abs(got - expected) < 5, "DURASI TIDAK COCOK - final tidak ditimpa"
    shutil.move(OUT_TMP, OUT_FINAL)
    print(f"OK: {OUT_FINAL} ({got/60:.1f} menit)")
    shutil.rmtree(TMPD)

if __name__ == "__main__":
    main()
