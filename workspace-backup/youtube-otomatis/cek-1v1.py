#!/usr/bin/env python3
"""Cek 1:1 kualitas video — bandingkan output run 2026-10-08 (instruksi baru,
hasil optimasi token) vs video sebelumnya tipe sama (instruksi lama).

Untuk tiap channel: cari video baru (nama file mengandung 2026-10-08),
cari video pembanding (terbaru sebelum tanggal itu, tipe sama: long/short),
probe durasi/resolusi/audio/ukuran, ekstrak 3 frame sampel per video.
Output: report.json + report.md + frames/ untuk dinilai manual oleh agen.
"""
import json, os, subprocess, glob

CHANNELS = {
    "youtube-pov":   "~/workspace/youtube-otomatis",
    "horor":         "~/workspace/horor-otomatis",
    "lima-misteri":  "~/workspace/lima-misteri",
    "strangetales":  "~/workspace/youtube-otomatis/strange-tales",
    "tinybuilders":  "~/workspace/miniatur-ai",
    "truecrime-en":  "~/workspace/youtube-otomatis/truecrime-en",
    "horror-en":     "~/workspace/youtube-otomatis/horror-en",
    "mystery-en":    "~/workspace/youtube-otomatis/mystery-en",
    "history-en":    "~/workspace/youtube-otomatis/history-en",
    "space-en":      "~/workspace/youtube-otomatis/space-en",
    "mind-en":       "~/workspace/youtube-otomatis/mind-en",
    "weird-en":      "~/workspace/youtube-otomatis/weird-en",
    "empires-en":    "~/workspace/youtube-otomatis/empires-en",
    "jejakislami":   "~/workspace/kisah-islami",
    "kisahalkitab":  "~/workspace/kisah-alkitab",
    "kisahdharma":   "~/workspace/kisah-dharma",
    "jejakbuddha":   "~/workspace/jejak-buddha",
}
NEW_DATE = "2026-10-08"
OUT = os.path.expanduser("~/workspace/cek-1v1-output")
FR = os.path.join(OUT, "frames")
os.makedirs(FR, exist_ok=True)

def probe(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", path],
            capture_output=True, text=True, timeout=60)
        j = json.loads(r.stdout)
        dur = float(j.get("format", {}).get("duration", 0) or 0)
        streams = j.get("streams", [])
        v = next((s for s in streams if s.get("codec_type") == "video"), {})
        a = any(s.get("codec_type") == "audio" for s in streams)
        return {"duration_s": round(dur, 1),
                "res": f"{v.get('width')}x{v.get('height')}",
                "audio": a,
                "size_mb": round(os.path.getsize(path) / 1e6, 1)}
    except Exception as e:
        return {"error": str(e)[:120]}

def grab_frames(path, tag, dur):
    out = []
    for i, frac in enumerate([0.25, 0.5, 0.75]):
        fp = os.path.join(FR, f"{tag}-f{i+1}.jpg")
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-v", "quiet", "-ss", str(dur * frac),
                 "-i", path, "-frames:v", "1", "-q:v", "4", fp],
                timeout=90)
            if os.path.exists(fp):
                out.append(fp)
        except Exception:
            pass
    return out

def classify(dur):
    return "long" if dur > 120 else "short"

def find_videos(ws):
    ws = os.path.expanduser(ws)
    if not os.path.isdir(ws):
        return []
    vids = []
    for p in glob.glob(ws + "/**/*.mp4", recursive=True):
        if "_tmp" in p or "tmp_segs" in p or "/frames/" in p:
            continue
        vids.append(p)
    return vids

report = {}
for ch, ws in CHANNELS.items():
    vids = find_videos(ws)
    entry = {"workspace": ws, "baru": [], "pembanding": {}}
    new_vids = [p for p in vids if NEW_DATE in os.path.basename(p)]
    for p in sorted(new_vids):
        pr = probe(p)
        fr = []
        if pr.get("duration_s"):
            fr = grab_frames(p, f"{ch}-baru-{classify(pr['duration_s'])}",
                             pr["duration_s"])
        entry["baru"].append({"file": p, "probe": pr, "frames": fr,
                              "tipe": classify(pr.get("duration_s", 0))})
    # pembanding: video terbaru sebelum NEW_DATE per tipe
    best = {}
    for p in vids:
        if NEW_DATE in os.path.basename(p):
            continue
        pr = probe(p)
        if pr.get("error") or not pr.get("duration_s"):
            continue
        c = classify(pr["duration_s"])
        mt = os.path.getmtime(p)
        if c not in best or mt > best[c][0]:
            best[c] = (mt, p, pr)
    for c, (mt, p, pr) in best.items():
        fr = grab_frames(p, f"{ch}-lama-{c}", pr["duration_s"])
        entry["pembanding"][c] = {"file": p, "probe": pr, "frames": fr}
    report[ch] = entry

with open(os.path.join(OUT, "report.json"), "w") as f:
    json.dump(report, f, indent=1)

lines = ["# Hasil Cek 1:1 — video instruksi baru (2026-10-08) vs lama", ""]
for ch, e in report.items():
    lines.append(f"## {ch}")
    if not e["baru"]:
        lines.append("- TIDAK ADA video baru 2026-10-08 (run gagal / belum selesai)")
    for b in e["baru"]:
        pr = b["probe"]
        tipe = b["tipe"]
        pb = e["pembanding"].get(tipe)
        lines.append(f"- BARU [{tipe}]: {os.path.basename(b['file'])}")
        lines.append(f"  durasi={pr.get('duration_s')}s res={pr.get('res')} "
                     f"audio={'YA' if pr.get('audio') else 'TIDAK'} size={pr.get('size_mb')}MB")
        if pb:
            pp = pb["probe"]
            lines.append(f"  vs LAMA: durasi={pp.get('duration_s')}s res={pp.get('res')} "
                         f"audio={'YA' if pp.get('audio') else 'TIDAK'} size={pp.get('size_mb')}MB")
        else:
            lines.append("  vs LAMA: tidak ketemu pembanding tipe sama")
        lines.append(f"  frames: {', '.join(os.path.basename(x) for x in b['frames'])}")
    lines.append("")
with open(os.path.join(OUT, "report.md"), "w") as f:
    f.write("\n".join(lines))

n_baru = sum(len(e["baru"]) for e in report.values())
print(f"SELESAI: {n_baru} video baru ditemukan di {len(report)} channel. Lihat {OUT}/report.md")
