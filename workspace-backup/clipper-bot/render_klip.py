#!/usr/bin/env python3
"""
render_klip.py — Potong kandidat momen viral jadi klip vertikal siap posting.

Untuk tiap kandidat (data/candidates.json):
  - potong segmen dari video sumber (via ffmpeg-queue.sh — WAJIB, bukan ffmpeg langsung)
  - ubah ke vertikal 1080x1920 (scale-fill + center crop)
  - bakar subtitle dari transkrip kata (filter subtitles/libass)
  - badge HOOK teks di 3 detik pertama (drawtext)
  - overlay CTA di 5 detik terakhir (drawtext)
  - hasil: clips/klip-01.mp4, klip-02.mp4, ...

Aturan teks drawtext (AGENTS.md): TANPA karakter '%' (diganti PERSEN),
TANPA apostrof (') bila digabung enable='between(...)'.

Pemakaian:
  venv/bin/python render_klip.py --brief brief.yaml
"""
import argparse
import json
import os
import re
import subprocess
import sys

import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
FFMPEG_Q = os.path.expanduser("~/workspace/youtube-otomatis/ffmpeg-queue.sh")
DATA = os.path.join(BASE, "data")
CLIPS = os.path.join(BASE, "clips")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def sanitasi_drawtext(teks):
    """Amankan teks untuk drawtext: tanpa ' dan %, escape : dan backslash."""
    t = teks.replace("\\", "\\\\")
    t = t.replace("%", "PERSEN")
    t = t.replace("'", "")          # apostrof dilarang (filtergraph rusak)
    t = t.replace('"', "")
    t = t.replace(":", "\\:")
    t = t.replace("\n", " ")
    return t.strip()


def escape_sub_path(path):
    return (path.replace("\\", "\\\\").replace(":", "\\:")
                .replace("'", "\\'").replace("[", "\\[").replace("]", "\\]"))


def frasa_hook_terbaik(kandidat, maks_kata):
    """Pilih rangkaian kata berurutan dengan skor viral tertinggi untuk badge hook.

    Batas: anggaran ~52 karakter (2 baris) dan maks_kata+2 kata. Bonus untuk
    rangkaian yang berakhir di akhir kalimat (. ! ?). Tepi rangkaian
    dirapikan: token tanpa skor / murni tanda baca di ujung dibuang
    (mencegah artefak seperti "-SOREI." atau frasa terpotong).
    """
    kata = kandidat.get("kata", [])
    teks_awal = " ".join(kandidat.get("teks", "").split()[:maks_kata])
    if not kata:
        return teks_awal
    budget = 52
    n = len(kata)
    best, best_s = (0, 1), -1.0
    for i in range(n):
        s, chars = 0, 0
        for j in range(i, n):
            if (j - i + 1) > maks_kata + 2:
                break
            w = kata[j]["t"]
            add = len(w) + (1 if j > i else 0)
            if chars + add > budget:
                break
            chars += add
            s += kata[j].get("ss", 0)
            tot = s + (1.5 if w[-1:] in ".!?" else 0)
            if tot > best_s:
                best_s, best = tot, (i, j + 1)
    i, j = best
    while i < j and (kata[i].get("ss", 0) <= 0
                     or re.fullmatch(r"\W+", kata[i]["t"])):
        i += 1
    while j > i and re.fullmatch(r"\W+", kata[j - 1]["t"]):
        j -= 1
    hasil = " ".join(k["t"] for k in kata[i:j])
    return hasil if hasil else teks_awal


def tulis_hook_dua_baris(hook, path):
    """Bagi hook jadi 2 baris seimbang (drawtext satu baris bisa overflow)."""
    kata = hook.split()
    if len(kata) <= 4:
        baris = [" ".join(kata)]
    else:
        tengah = (len(kata) + 1) // 2
        baris = [" ".join(kata[:tengah]), " ".join(kata[tengah:])]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(baris))
    return len(baris)


def fmt_srt(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def tulis_srt(kata, mulai_abs, path):
    """Kelompokkan kata jadi cue SRT (maks ~34 karakter / 2,4 detik)."""
    cues = []
    cur, cur_t0, cur_t1 = [], None, None
    for w in kata:
        t0 = max(0.0, w["m"] - mulai_abs)
        t1 = max(0.0, w["s"] - mulai_abs)
        teks = (cur and " ".join(cur) + " " or "") + w["t"]
        if cur and (len(teks) > 34 or (t1 - cur_t0) > 2.4):
            cues.append((cur_t0, cur_t1, " ".join(cur)))
            cur, cur_t0 = [], None
        if cur_t0 is None:
            cur_t0 = t0
        cur.append(w["t"])
        cur_t1 = t1
    if cur:
        cues.append((cur_t0, cur_t1, " ".join(cur)))
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, teks) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt_srt(a)} --> {fmt_srt(b)}\n{teks}\n\n")
    return len(cues)


def render_satu(kandidat, brief, sumber):
    kid = kandidat["id"]
    mulai = kandidat["mulai"]
    selesai = kandidat["selesai"]
    durasi = kandidat["selesai"] - kandidat["mulai"]
    out = os.path.join(CLIPS, f"klip-{kid:02d}.mp4")
    srt = os.path.join(DATA, f"subs-klip-{kid:02d}.srt")
    n_cue = tulis_srt(kandidat.get("kata", []), mulai, srt)

    # Hook: frasa viral terbaik (<= maks_kata kata), huruf kapital, 2 baris via textfile
    maks_kata = int(brief.get("hook", {}).get("maks_kata", 8))
    hook = sanitasi_drawtext(frasa_hook_terbaik(kandidat, maks_kata).upper())
    hook_file = os.path.join(DATA, f"hook-klip-{kid:02d}.txt")
    n_baris = tulis_hook_dua_baris(hook, hook_file)

    # CTA
    cta_cfg = brief.get("cta", {})
    cta = sanitasi_drawtext(str(cta_cfg.get("teks", "")))
    cta_dur = float(cta_cfg.get("overlay_durasi_detik", 5))
    badge_dur = float(brief.get("hook", {}).get("badge_durasi_detik", 3))
    t_cta0 = max(0.0, durasi - cta_dur)

    # CATATAN: jangan pakai warna format &H (mis. PrimaryColour=&H00FFFFFF) di
    # force_style — di ffmpeg 8.1.2 VM ini itu membuat subtitle TIDAK ter-render
    # sama sekali (terbukti via biseksi). Default libass sudah putih + outline hitam.
    # MarginV dalam koordinat play-res SRT (384x288), BUKAN piksel video:
    # 45 ≈ 300px dari bawah pada video 1080x1920. Nilai 320 melempar subtitle
    # keluar layar (margin > tinggi play-res).
    style_sub = ("FontName=DejaVu Sans,FontSize=22,"
                 "BorderStyle=1,Outline=2,Alignment=2,MarginV=45")
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"subtitles='{escape_sub_path(srt)}':force_style='{style_sub}',"
        f"drawtext=fontfile={FONT}:textfile='{escape_sub_path(hook_file)}':"
        f"fontsize=58:fontcolor=white:"
        f"borderw=3:bordercolor=black:box=1:boxcolor=black@0.55:boxborderw=24:"
        f"x=(w-text_w)/2:y=200:enable='between(t,0,{badge_dur})',"
        f"drawtext=fontfile={FONT}:text='{cta}':fontsize=54:fontcolor=yellow:"
        f"borderw=3:bordercolor=black:box=1:boxcolor=black@0.55:boxborderw=24:"
        f"x=(w-text_w)/2:y=h-360:enable='between(t,{t_cta0:.1f},{durasi:.1f})'"
    )
    cmd = [FFMPEG_Q, "-y",
           "-ss", str(mulai), "-to", str(selesai), "-i", sumber,
           "-vf", vf,
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k",
           "-movflags", "+faststart",
           "-avoid_negative_ts", "make_zero",
           out]
    print(f"  [klip-{kid:02d}] {mulai:.0f}-{selesai:.0f}d ({durasi:.0f}d) "
          f"+ {n_cue} cue subtitle ...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  GAGAL render klip-{kid:02d}:", r.stderr[-1500:], file=sys.stderr)
        return None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default=os.path.join(BASE, "brief.yaml"))
    ap.add_argument("--candidates", default=os.path.join(DATA, "candidates.json"))
    args = ap.parse_args()

    with open(args.brief, encoding="utf-8") as f:
        brief = yaml.safe_load(f)
    with open(args.candidates, encoding="utf-8") as f:
        kandidat = json.load(f)
    if not kandidat:
        print("ERROR: candidates.json kosong — jalankan deteksi_momen.py dulu.",
              file=sys.stderr)
        sys.exit(1)

    sumber = brief.get("sumber_video", "")
    if not os.path.isabs(sumber):
        sumber = os.path.join(BASE, sumber)
    os.makedirs(CLIPS, exist_ok=True)

    jumlah = int(brief.get("jumlah_klip", len(kandidat)))
    hasil = []
    for k in sorted(kandidat, key=lambda x: -x["skor"])[:jumlah]:
        out = render_satu(k, brief, sumber)
        if out:
            hasil.append((k, out))
    print(f"Selesai: {len(hasil)} klip di {CLIPS}/")


if __name__ == "__main__":
    main()
