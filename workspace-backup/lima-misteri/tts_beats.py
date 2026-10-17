#!/usr/bin/env python3
"""TTS per beat untuk Lima Misteri: baca script/YYYY-MM-DD.txt, sintesis tiap beat
paralel (6 worker), catat durasi per beat, gabung jadi audio/YYYY-MM-DD.mp3.
Beat dengan NARASI persis [JEDA] -> mp3 hening 2.5 detik (tanpa panggil tts).
Penggunaan: python3 tts_beats.py 2026-10-06
"""
import re, os, sys, subprocess, json
sys.path.insert(0, "/home/hatch/workspace/youtube-otomatis")
try:
    from tts_sanitize import bersihkan_teks_tts
except ImportError:
    def bersihkan_teks_tts(t): return t
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
TTS = "/opt/hatch/bin/tts"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
VOICE = "avocado_v2:mudiwa"
LANG = "id"
JEDA_TEXT = "[JEDA]"

def parse_script(path):
    txt = open(path).read()
    beats = re.findall(r"^BEAT (\d+)\nNARASI: (.*?)\nGAMBAR:", txt, re.M | re.S)
    out = []
    for num, nar in beats:
        nar = " ".join(nar.split())
        out.append((int(num), nar))
    return sorted(out)

def synth(args):
    num, nar, outpath = args
    if os.path.exists(outpath) and os.path.getsize(outpath) > 1000:
        return (num, "skip", outpath)
    if nar == JEDA_TEXT:
        try:
            r = subprocess.run([FFQ, "-y", "-f", "lavfi", "-i",
                                "anullsrc=r=44100:cl=mono", "-t", "2.5",
                                "-c:a", "libmp3lame", "-q:a", "4", outpath],
                               capture_output=True, timeout=300)
            if r.returncode == 0 and os.path.exists(outpath):
                return (num, "ok", outpath)
            return (num, f"FAIL rc={r.returncode} {r.stderr.decode()[:200]}", outpath)
        except Exception as e:
            return (num, f"EXC {e}", outpath)
    nar = bersihkan_teks_tts(nar)  # SANITASI TTS (insiden 2026-10-13): buang label "Narator:" dkk
    try:
        r = subprocess.run([TTS, "speak", "--language", LANG, "--voice", VOICE,
                            "--output", outpath, "--text-stdin", "--timeout-secs", "180"],
                           input=nar.encode("utf-8"), capture_output=True, timeout=240)
        if r.returncode == 0 and os.path.exists(outpath):
            return (num, "ok", outpath)
        return (num, f"FAIL rc={r.returncode} {r.stderr.decode()[:200]}", outpath)
    except Exception as e:
        return (num, f"EXC {e}", outpath)

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    tgl = sys.argv[1]
    beats = parse_script(os.path.join(BASE, "script", f"{tgl}.txt"))
    print(f"{len(beats)} beats")
    bdir = os.path.join(BASE, "audio", "beats", tgl)
    os.makedirs(bdir, exist_ok=True)
    jobs = [(n, nar, os.path.join(bdir, f"b{n:03d}.mp3")) for n, nar in beats]
    results = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for num, st, p in ex.map(synth, jobs):
            results[num] = (st, p)
            print(f"  beat {num:03d}: {st}", flush=True)
    fails = [n for n, (st, _) in results.items() if st not in ("ok", "skip")]
    if fails:
        print("GAGAL:", fails); sys.exit(1)
    # durasi per beat + JSON durations + concat
    durmap = {}
    lst = os.path.join(bdir, "list.txt")
    with open(lst, "w") as f:
        for n, _ in beats:
            p = os.path.join(bdir, f"b{n:03d}.mp3")
            d = dur(p)
            durmap[f"beat-{n:03d}"] = round(d, 3)
            f.write(f"file '{p}'\n")
    with open(os.path.join(BASE, "audio", f"{tgl}-durations.json"), "w") as f:
        json.dump(durmap, f, indent=1)
    with open(os.path.join(BASE, "audio", f"{tgl}.durations.txt"), "w") as f:
        f.write("\n".join(f"{durmap[f'beat-{n:03d}']:.3f}" for n, _ in beats) + "\n")
    out = os.path.join(BASE, "audio", f"{tgl}.mp3")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], capture_output=True, check=True)
    d = dur(out)
    print(f"OK: {out} ({d/60:.1f} mnt), total beats {d:.0f}s")

if __name__ == "__main__":
    main()
