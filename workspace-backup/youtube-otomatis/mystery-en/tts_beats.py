#!/usr/bin/env python3
"""TTS per beat untuk horor-otomatis: baca script/YYYY-MM-DD.txt, sintesis tiap beat
paralel (6 worker), catat durasi per beat, gabung jadi audio/YYYY-MM-DD.mp3.
Penggunaan: python3 tts_beats.py 2026-10-04
"""
import re, os, sys, subprocess, json
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
TTS = "/opt/hatch/bin/tts"
VOICE = "avocado_v2:magnus"
LANG = "en"

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
            print(f"  beat {num:03d}: {st}")
    fails = [n for n, (st, _) in results.items() if st not in ("ok", "skip")]
    if fails:
        print("GAGAL:", fails); sys.exit(1)
    # durasi + concat
    durs = []
    lst = os.path.join(bdir, "list.txt")
    with open(lst, "w") as f:
        for n, _ in beats:
            p = os.path.join(bdir, f"b{n:03d}.mp3")
            d = dur(p)
            durs.append(d)
            f.write(f"file '{p}'\n")
    with open(os.path.join(BASE, "audio", f"{tgl}.durations.txt"), "w") as f:
        f.write("\n".join(f"{d:.3f}" for d in durs) + "\n")
    out = os.path.join(BASE, "audio", f"{tgl}.mp3")
    subprocess.run(["/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], capture_output=True, check=True)
    print(f"OK: {out} ({dur(out)/60:.1f} mnt), total beats {dur(out):.0f}s")

if __name__ == "__main__":
    main()
