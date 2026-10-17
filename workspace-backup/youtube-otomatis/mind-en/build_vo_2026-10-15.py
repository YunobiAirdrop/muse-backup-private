#!/usr/bin/env python3
"""Gabung TTS per beat -> voiceover-final-2026-10-15.mp3 + durasi-beat-final-2026-10-15.json.
Jeda 0.35s antar beat; 0.9s setelah beat insight kunci (dramatis).
Bumper clone (voice-clone-test/bumper-mind-en.wav, 4.1s) disisipkan di TENGAH:
batas chapter terdekat 50% durasi total. Output JSON berisi urutan segmen
[beat-001..k, bumper, beat-k+1..75] dengan durasi masing-masing (bumper sudah
termasuk silence 0.35s sesudahnya).
"""
import subprocess, os, json, sys
BASE = "/home/hatch/workspace/youtube-otomatis/mind-en"
BEATD = f"{BASE}/audio/beat-2026-10-15"
PADD = f"{BASE}/audio/pad-2026-10-15"
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
BUMPER = "/home/hatch/workspace/youtube-otomatis/voice-clone-test/bumper-mind-en.wav"
# beat insight kunci -> jeda dramatis 0.9s
LONG_PAUSE = {"beat-025", "beat-034", "beat-044", "beat-054", "beat-063", "beat-072"}
# batas chapter (beat pertama tiap chapter)
CHAPTERS = {"beat-008": "Confirmation Bias", "beat-017": "Sunk Cost Fallacy",
            "beat-027": "Anchoring", "beat-036": "Loss Aversion",
            "beat-046": "Availability Heuristic", "beat-056": "Bandwagon Effect",
            "beat-065": "Halo Effect"}

def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def main():
    os.makedirs(PADD, exist_ok=True)
    for name, secs in [("_silence035.mp3", 0.35), ("_silence09.mp3", 0.9)]:
        sp = f"{BASE}/audio/{name}"
        if not os.path.exists(sp):
            subprocess.run([FFQ, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                            "-t", str(secs), "-q:a", "9", sp],
                           capture_output=True, check=True)
    segs = []  # (id, dur)
    for i in range(1, 76):
        bid = f"beat-{i:03d}"
        src = f"{BEATD}/{bid}.mp3"
        assert os.path.exists(src) and os.path.getsize(src) > 1000, f"TTS hilang: {src}"
        sil = f"{BASE}/audio/_silence09.mp3" if bid in LONG_PAUSE else f"{BASE}/audio/_silence035.mp3"
        pad = f"{PADD}/{bid}.mp3"
        lst = f"{PADD}/{bid}.txt"
        with open(lst, "w") as f:
            f.write(f"file '{src}'\nfile '{sil}'\n")
        subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", pad], capture_output=True, check=True)
        os.remove(lst)
        segs.append((bid, round(dur(pad), 3)))
    total = sum(x[1] for x in segs)
    # bumper: chapter boundary terdekat 50% durasi
    cum = 0.0
    cands = []
    for bid, d_ in segs:
        if bid in CHAPTERS and bid not in ("beat-008", "beat-017"):
            cands.append((bid, abs(cum - total / 2), cum))
        cum += d_
    cands.sort(key=lambda x: x[1])
    after_bid = cands[0][0]
    print(f"bumper disisipkan sebelum {after_bid} ({CHAPTERS[after_bid]})", flush=True)
    # pad bumper + silence 0.35
    bpad = f"{PADD}/bumper.mp3"
    lst = f"{PADD}/bumper.txt"
    with open(lst, "w") as f:
        f.write(f"file '{BUMPER}'\nfile '{BASE}/audio/_silence035.mp3'\n")
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", bpad], capture_output=True, check=True)
    os.remove(lst)
    bd = round(dur(bpad), 3)
    # susun urutan final
    final = []
    for bid, d_ in segs:
        if bid == after_bid:
            final.append(("bumper", bd))
        final.append((bid, d_))
    json.dump({"order": [x[0] for x in final],
               "durations": {x[0]: x[1] for x in final},
               "bumper_after": after_bid,
               "total": round(sum(x[1] for x in final), 3)},
              open(f"{BASE}/audio/durasi-beat-final-2026-10-15.json", "w"), indent=1)
    lst = f"{BASE}/audio/_concat-final-2026-10-15.txt"
    with open(lst, "w") as f:
        for sid, _ in final:
            p = bpad if sid == "bumper" else f"{PADD}/{sid}.mp3"
            f.write(f"file '{os.path.abspath(p)}'\n")
    out = f"{BASE}/audio/voiceover-final-2026-10-15.mp3"
    subprocess.run([FFQ, "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out], capture_output=True, check=True)
    print(f"OK {out} total={sum(x[1] for x in final)/60:.2f} mnt vo_dur={dur(out)/60:.2f} mnt")

if __name__ == "__main__":
    main()
