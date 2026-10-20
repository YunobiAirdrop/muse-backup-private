#!/usr/bin/env python3
"""Rakit 3 Shorts Strange Tales 2026-10-20 — pola 2026-10-19 (foto Ken Burns).
MAKS 2 chain decode per operasi ffmpeg -> 3 operasi per short:
  op1: seg0+seg1 -> partA.mp4 ; op2: seg2+seg3 -> partB.mp4
  op3: concat partA+partB + caption word-chunked + grain + VO -> tmp.mp4,
       verifikasi durasi (format + PER STREAM), pindah ke final.
SEMUA ffmpeg WAJIB lewat ffmpeg-queue.sh. setsar=1 setelah crop.
Teks drawtext: TANPA '%', TANPA apostrof, ':' di-escape.
Caption: chunk 6 kata, maks 2 baris, timing proporsional per kata;
chunk terakhir "HIT SUBSCRIBE FOR MORE STRANGE TALES" menempati ~3.5 dtk terakhir.
"""
import subprocess, os, shutil, glob

D = "/home/hatch/workspace/youtube-otomatis/strange-tales/2026-10-20"
C = os.path.join(D, "clips")
FFQ = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
FONT = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FPS = 30

CTA_TAIL = "HIT SUBSCRIBE\\\\nFOR MORE STRANGE TALES"
CTA_SECONDS = 3.5

def esc(t):
    assert "%" not in t, f"%% terlarang: {t}"
    return t.replace(":", "\\:").replace("'", "\u2019")

def drawtext(cap, t0, t1):
    return (f"drawtext=text='{esc(cap)}':fontfile={FONT}:fontsize=54:fontcolor=white:"
            f"borderw=3:bordercolor=black@0.8:x=(w-text_w)/2:y=h-460:"
            f"box=1:boxcolor=black@0.45:boxborderw=24:"
            f"enable='between(t\\,{t0:.2f}\\,{t1:.2f})'")

def chunk_captions(naskah, vo_dur):
    """Pecah naskah jadi chunk 6 kata (2 baris), timing proporsional per kata.
    Chunk terakhir = CTA, dipin di CTA_SECONDS terakhir."""
    words = naskah.split()
    cta_words = ["Hit", "subscribe", "for", "more", "strange", "tales."]
    assert words[-6:] == cta_words, f"CTA tidak di akhir: {words[-6:]}"
    body = words[:-6]
    chunks = []
    i = 0
    while i < len(body):
        take = 6
        rest = len(body) - i - take
        if 0 < rest < 5:
            take = len(body) - i  # gabung sisa ke chunk terakhir body
        chunks.append(body[i:i+take])
        i += take
    body_time = vo_dur - CTA_SECONDS
    per_word = body_time / len(body)
    caps = []
    wpos = 0
    for ch in chunks:
        t0 = wpos * per_word
        t1 = (wpos + len(ch)) * per_word
        half = (len(ch) + 1) // 2
        # drawtext butuh '\\n' di argv agar filter parser meneruskan '\n' ke drawtext
        text = " ".join(ch[:half]).upper() + "\\\\n" + " ".join(ch[half:]).upper()
        caps.append((text, t0, t1))
        wpos += len(ch)
    caps.append((CTA_TAIL, vo_dur - CTA_SECONDS, vo_dur))
    return caps

GRAIN = "noise=alls=8:allf=t,format=yuv420p"
COVER = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"

def zoompan(motion, dframes):
    n = dframes - 1
    if motion == "zin":
        zp = f"z='1+0.0012*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    elif motion == "zout":
        zp = f"z='1.32-0.0012*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    else:  # pan
        zp = f"z='1.25':x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'"
    return f"zoompan={zp}:d={dframes}:s=1080x1920:fps={FPS}"

def run(args, label):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAILED {label}:\n{r.stderr[-2000:]}", flush=True)
        raise SystemExit(1)
    print(f"OK {label}", flush=True)

def durations(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    d = {}
    for line in r.stdout.strip().splitlines():
        parts = [p for p in line.split(",") if p != ""]
        if len(parts) >= 2:
            d[parts[0]] = float(parts[1])
    return d

def part_valid(path, seg_dur):
    if not os.path.exists(path):
        return False
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=sample_aspect_ratio,duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip().startswith("1:1,"):
        return False
    parts = [p for p in r.stdout.strip().split(",") if p != ""]
    dur = float(parts[1])
    return abs(dur - 2 * seg_dur) < 1.0

def seg_chain(i, img, dur, motion):
    ia = ["-i", os.path.join(C, img)]
    vf = f"{COVER},{zoompan(motion, int(round(dur*FPS)))}"
    fc = f"[{i}:v]{vf},setpts=PTS-STARTPTS,fps={FPS}[v{i}]"
    return ia, fc

def build_part(slug, part, imgs, motions, seg_dur):
    out = os.path.join(D, f"{slug}-{part}.mp4")
    if part_valid(out, seg_dur):
        print(f"SKIP existing valid {out}", flush=True)
        return out
    if os.path.exists(out):
        print(f"hapus part tidak valid: {out}", flush=True)
        os.remove(out)
    args = [FFQ, "-y"]
    chains = []
    for i, (img, mo) in enumerate(zip(imgs, motions)):
        ia, fc = seg_chain(i, img, seg_dur, mo)
        args += ia
        chains.append(fc)
    chains.append("[v0][v1]concat=n=2:v=1:a=0[vv]")
    args += ["-filter_complex", ";".join(chains), "-map", "[vv]",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
             "-r", str(FPS), "-an", out]
    run(args, f"{slug} {part}")
    return out

SHORTS = [
    {"slug": "spotted-lake", "vo": "vo-spotted-lake.mp3", "vo_dur": 28.92,
     "final": "strange-tales-2026-10-20-spotted-lake.mp4",
     "imgs": ["spotted-osoyoos.jpg", "spotted-flickr1.jpg",
              "spotted-flickr2.jpg", "spotted-okanagan.jpg"],
     "naskah": ("In the summer, a lake in Canada turns into something unreal. Spotted Lake. "
                "As the water evaporates, hundreds of colorful mineral pools appear. Yellow. "
                "Green. Blue. Each spot is packed with minerals like magnesium and calcium. "
                "For centuries, the Okanagan people have called this place sacred, using the "
                "mud to heal wounds. Scientists say the colors come from different mineral "
                "concentrations. But no two summers look the same. The lake paints a brand "
                "new pattern every year. Hit subscribe for more strange tales.")},
    {"slug": "salar-uyuni", "vo": "vo-salar-uyuni.mp3", "vo_dur": 33.672,
     "final": "strange-tales-2026-10-20-salar-uyuni.mp4",
     "imgs": ["salar-reflection.jpg", "salar-dd1618.jpg",
              "salar-dd1012.jpg", "salar-sunset.jpg"],
     "naskah": ("In Bolivia lies the largest mirror on planet Earth. Salar de Uyuni. "
                "Ten thousand square kilometers of pure white salt. It was once a giant "
                "prehistoric lake. When the water dried up, it left behind a crust of salt, "
                "perfectly flat. Then the rain comes. A thin layer of water covers the desert "
                "of salt. And suddenly, the sky reflects below your feet. You cannot tell "
                "where the ground ends and the heavens begin. People come here to walk on "
                "the clouds. Hit subscribe for more strange tales.")},
    {"slug": "waitomo-glowworms", "vo": "vo-waitomo-glowworms.mp3", "vo_dur": 26.40,
     "final": "strange-tales-2026-10-20-waitomo-glowworms.mp4",
     "imgs": ["waitomo-green.jpg", "waitomo-glowworms.jpg",
              "waitomo-ruakuri1.jpg", "waitomo-ruakuri2.jpg"],
     "naskah": ("Deep under New Zealand, there is a cave that glows like the night sky. "
                "But these are not stars. They are alive. Thousands of glowworms hang from "
                "the ceiling, each one shining a tiny blue green light to lure insects into "
                "sticky threads. The darker the cave, the brighter they shine. Thirty million "
                "years in the making, this underground galaxy was sacred to the Maori people. "
                "Scientists still study how these tiny creatures make light without heat. "
                "A starry sky, hidden under the earth. Hit subscribe for more strange tales.")},
]
MOTIONS = ["zin", "pan", "zout", "zin"]

for t in glob.glob(os.path.join(D, "*.tmp.mp4")):
    os.remove(t)
    print(f"hapus sisa gagal: {os.path.basename(t)}", flush=True)

for sh in SHORTS:
    final = os.path.join(D, sh["final"])
    if os.path.exists(final) and os.path.getsize(final) > 100000:
        ds = durations(final)
        if abs(ds.get("video", 0) - sh["vo_dur"]) < 5:
            print(f"SKIP final existing {sh['final']}", flush=True)
            continue
    seg_dur = sh["vo_dur"] / 4
    a = build_part(sh["slug"], "partA", sh["imgs"][:2], MOTIONS[:2], seg_dur)
    b = build_part(sh["slug"], "partB", sh["imgs"][2:], MOTIONS[2:], seg_dur)
    caps = chunk_captions(sh["naskah"], sh["vo_dur"])
    print(f"caption {sh['slug']}: {len(caps)} chunks, contoh: {caps[0][0]!r} {caps[0][1]:.2f}-{caps[0][2]:.2f}",
          flush=True)
    vf = "[0:v][1:v]concat=n=2:v=1:a=0[vcat]"
    vchain = "[vcat]"
    for cap, t0, t1 in caps:
        vchain += drawtext(cap, t0, t1) + ","
    vchain += GRAIN + "[vv]"
    tmp = final + ".tmp.mp4"
    run([FFQ, "-y", "-i", a, "-i", b, "-i", os.path.join(D, sh["vo"]),
         "-filter_complex", vf + ";" + vchain,
         "-map", "[vv]", "-map", "2:a",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
         "-c:a", "aac", "-b:a", "128k",
         "-shortest", "-movflags", "+faststart", tmp],
        f"{sh['slug']} mux")
    ds = durations(tmp)
    vdur, adur = ds.get("video", 0), ds.get("audio", 0)
    assert vdur > 0 and adur > 0, f"stream hilang {sh['slug']}: {ds}"
    assert abs(vdur - adur) < 5, f"V/A selisih >5s {sh['slug']}: {vdur:.2f}/{adur:.2f}"
    assert abs(vdur - sh["vo_dur"]) < 5, f"video jauh dari VO {sh['slug']}"
    assert abs(adur - sh["vo_dur"]) < 5, f"audio jauh dari VO {sh['slug']}"
    assert 25 <= vdur <= 40, f"durasi di luar 25-40s {sh['slug']}: {vdur:.2f}"
    assert os.path.getsize(tmp) > 1000000, f"file terlalu kecil {sh['slug']}"
    print(f"DURASI OK {sh['slug']}: video {vdur:.2f}s audio {adur:.2f}s (VO {sh['vo_dur']})", flush=True)
    shutil.move(tmp, final)

print("ALL DONE")
