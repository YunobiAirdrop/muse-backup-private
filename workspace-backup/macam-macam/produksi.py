#!/usr/bin/env python3
"""Produksi video 'Macam-macam Jenis X' untuk channel Macam Macam (@MacamMacamID).
Format: Shorts 1080x1920, foto real Pexels (gaya kartun tempel: cutout + background
kartun) + label nama + sulih suara + musik latar ceria + CTA full.

Alur: python3 produksi.py <slug-tema>  (baca tema/<slug>.json)
  1. Ambil foto per item via Pexels API (PEXELS_API_KEY di ~/.hermes/pexels.env)
  2. Cutout background (rembg u2netp) + tempel ke background kartun (gaya stiker)
  3. TTS per segmen (Mudiwa, bahasa Indonesia)
  4. Rakit: hook + 8 item + CTA akhir, teks overlay nama + CTA subscribe
  5. Musik latar ceria (synth, volume rendah) di-mix di bawah narasi
  6. Output: output/<slug>-part<N>.mp4 + metadata JSON (judul, deskripsi, hashtag)

CTA full: teks overlay subscribe di hook & tiap item + sulih suara CTA di tengah & akhir.
"""
import json, os, subprocess, sys, time, urllib.request, urllib.parse
from pathlib import Path
import numpy as np

BASE = Path.home() / "workspace" / "macam-macam"
TEMA_DIR = BASE / "tema"
OUT_DIR = BASE / "output"
FFMPEG_Q = "/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh"
TTS_BIN = "/opt/hatch/bin/tts"

# ==== PRESET GERAK KEYFRAME (permintaan user 2026-10-12: "gambar kendaraan
# pake frame key biar gerak") ====
# Segmen item dirender dari 2 layer (background kartun + stiker cutout) dan
# kendaraan dianimasikan pakai ekspresi waktu ffmpeg. Semua tema otomatis
# memakai preset yang sama — ubah gerak cukup di blok ini.
KF_SLIDE_DUR = 0.8      # durasi meluncur masuk dari luar layar (detik)
KF_SLIDE_GAP = 60       # jarak awal stiker di luar tepi layar (px)
KF_OVERSHOOT = 1.70158  # konstanta easeOutBack: overshoot halus lalu settle
KF_BOUNCE_AMP = 6       # amplitudo mantul vertikal (px) — kesan suspensi jalan
KF_BOUNCE_FREQ = 2.2    # frekuensi mantul (Hz)
KF_ROT_AMP = 0.012      # amplitudo goyangan rotasi (rad, ±0,7 derajat)
KF_ROT_FREQ = 0.9       # frekuensi goyangan rotasi (Hz)
KF_BG_PAN = 80          # total geser background per segmen (px, lawan arah luncur)
KF_PAD_SIDE = 65        # padding transparan tiap sisi stiker agar rotasi tak motong tepi
KF_CY_FRAC = 0.37       # titik tengah vertikal stiker (samakan tempel.py)

def pexels_key():
    p = Path.home() / ".hermes" / "pexels.env"
    if p.exists():
        for line in p.read_text().splitlines():
            if line.startswith("PEXELS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    return os.environ.get("PEXELS_API_KEY", "")

def pexels_foto(query, per_page=5):
    """Cari foto di Pexels, kembalikan URL ukuran besar + info fotografer."""
    key = pexels_key()
    if not key:
        raise RuntimeError("PEXELS_API_KEY belum diset (minta ke user di pexels.com/api)")
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": per_page, "orientation": "portrait"})
    req = urllib.request.Request(url, headers={"Authorization": key})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    hasil = []
    for ph in data.get("photos", []):
        src = ph.get("src", {})
        hasil.append({
            "url": src.get("large2x") or src.get("large"),
            "fotografer": ph.get("photographer", ""),
            "pexels_url": ph.get("url", ""),
        })
    return hasil

def unduh(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest

def tts(teks, out):
    r = subprocess.run([TTS_BIN, "speak", "--language", "id",
                        "--voice", "avocado_v2:mudiwa", "--speed", "100",
                        "--output", str(out), "--text-stdin"],
                       input=teks.encode(), capture_output=True, timeout=300)
    if r.returncode != 0 or b'"ok":true' not in r.stdout:
        raise RuntimeError(f"TTS gagal: {r.stderr.decode()[:200]}")
    return out

def durasi_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def _teks_overlay_vf(teks_overlay):
    """Rantai drawtext: nama besar di bawah + CTA subscribe kecil di atas.
    Dipakai jalur keyframe maupun jalur diam agar tampilan teks identik."""
    # font otomatis mengecil untuk teks panjang biar tidak kepotong
    def fs_for(teks, base=72):
        # perkiraan kasar: tiap karakter ~0.55 * fontsize piksel
        while len(teks) * 0.55 * base > 1000 and base > 36:
            base -= 4
        return base
    teks = teks_overlay.replace("'", "").replace(":", "\\:")
    cta = "SUBSCRIBE YA!".replace(":", "\\:")
    fs_nama = fs_for(teks_overlay)
    return (f"drawtext=text='{teks}':fontcolor=white:fontsize={fs_nama}:borderw=4:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-380,"
            f"drawtext=text='{cta}':fontcolor=yellow:fontsize=40:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=120")

def buat_stiker_png(cutout_path, cache_path):
    """Stiker RGBA (cutout + outline putih gaya stiker) dari PNG hasil rembg,
    memakai resep tempel.buat_stiker persis. Hasil di-cache (work/<tema>/stiker/)."""
    cache_path = Path(cache_path)
    if cache_path.exists():
        return cache_path
    from PIL import Image
    import tempel
    cut = Image.open(cutout_path).convert("RGBA")
    stiker = tempel.buat_stiker(cut)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    stiker.save(cache_path)
    return cache_path

def _layer_untuk(img, tema):
    """Pasangan layer (background, cutout PNG) untuk sebuah gambar tempel item.
    Kembalikan (None, None) bila gambar bukan hasil tempel / layer tak lengkap
    (pemanggil lalu jatuh ke jalur gambar diam)."""
    img = Path(img)
    if img.parent.name != "tempel":
        return None, None
    cut = img.parent.parent / "cutout" / (img.stem + ".png")
    bg = tema.get("background")
    if not bg:
        import tempel
        bg = str(tempel.BG_DEFAULT)
    if cut.exists() and Path(bg).exists():
        return bg, cut
    return None, None

def segmen_video_keyframe(bg, stiker, dur, teks_overlay, out):
    """Segmen KEYFRAME dari 2 layer: background kartun + stiker kendaraan.

    - Background diskalakan 110% lalu crop-window-nya bergeser perlahan
      (KF_BG_PAN px selama segmen) berlawanan arah luncur kendaraan → kesan jalan.
    - Stiker MELUNCUR MASUK dari luar kiri ke posisi tengah (easeOutBack,
      KF_SLIDE_DUR detik: overshoot halus lalu settle), lalu terus MANTUL
      vertikal kecil (KF_BOUNCE_AMP px @ KF_BOUNCE_FREQ Hz, kesan suspensi)
      + goyangan rotasi ±KF_ROT_AMP rad.
    - Label nama + CTA statis di posisi aman (sama seperti jalur diam) agar
      tetap terbaca jelas.
    Semua render lewat ffmpeg-queue.sh seperti jalur lain.
    """
    tin = KF_SLIDE_DUR
    # easeOutBack: u = t/tin dijepit ke 1; v = u-1; f = 1 + (c+1)v^3 + c v^2
    u = f"if(gte(t,{tin}),1,t/{tin})"
    v = f"({u}-1)"
    ease = f"(1+{KF_OVERSHOOT + 1}*{v}*{v}*{v}+{KF_OVERSHOOT}*{v}*{v})"
    xt = "(main_w-overlay_w)/2"                    # posisi tampil (tengah)
    xs = f"(-overlay_w-{KF_SLIDE_GAP})"            # posisi awal (di luar kiri)
    x = f"if(lt(t,{tin}),{xs}+({xt}-{xs})*{ease},{xt})"
    # basis y: titik tengah stiker di KF_CY_FRAC tinggi frame, dijepit seperti tempel.py
    yraw = f"(main_h*{KF_CY_FRAC}-overlay_h/2)"
    ybase = (f"if(lt({yraw},140),140,"
             f"if(gt({yraw},main_h-420-overlay_h),main_h-420-overlay_h,{yraw}))")
    y = f"({ybase})+{KF_BOUNCE_AMP}*sin(2*PI*{KF_BOUNCE_FREQ}*t)"
    bgx = f"14+{KF_BG_PAN}*t/{dur:.3f}"            # background geser lawan arah luncur
    fc = (
        f"[0:v]scale=1188:2112:force_original_aspect_ratio=increase,crop=1188:2112,"
        f"crop=1080:1920:x='{bgx}':y=96[bg];"
        f"[1:v]format=rgba,pad=width=iw+{2 * KF_PAD_SIDE}:height=ih+{2 * KF_PAD_SIDE}"
        f":x={KF_PAD_SIDE}:y={KF_PAD_SIDE}:color=0x00000000,"
        f"rotate=a='{KF_ROT_AMP}*sin(2*PI*{KF_ROT_FREQ}*t)':ow=iw:oh=ih:c=none[stk];"
        f"[bg][stk]overlay=x='{x}':y='{y}'[comp];"
        f"[comp]eq=contrast=1.06:saturation=1.05,noise=alls=5:allf=t,"
        f"{_teks_overlay_vf(teks_overlay)}[vout]"
    )
    r = subprocess.run([FFMPEG_Q, "-y",
                        "-loop", "1", "-framerate", "30", "-i", str(bg),
                        "-loop", "1", "-framerate", "30", "-i", str(stiker),
                        "-filter_complex", fc, "-map", "[vout]",
                        "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", str(out)],
                       capture_output=True)
    if r.returncode != 0:
        print("  ffmpeg keyframe stderr:", r.stderr.decode()[-400:])
    return r.returncode == 0

def segmen_video(img, dur, teks_overlay, idx, out, bg=None, cutout=None):
    """Satu segmen 1080x1920: foto + teks nama besar.
    Bila layer (background + cutout) tersedia → jalur KEYFRAME (kendaraan
    bergerak); bila tidak / gagal → jalur diam Ken Burns seperti sebelumnya."""
    if bg is not None and cutout is not None:
        try:
            stiker = buat_stiker_png(
                cutout, Path(out).parent.parent / "stiker" / (Path(cutout).stem + ".png"))
            if segmen_video_keyframe(bg, stiker, dur, teks_overlay, out):
                return True
            print("  ! render keyframe gagal — fallback gambar diam")
        except Exception as e:
            print(f"  ! keyframe error: {e} — fallback gambar diam")
    frames = int(dur * 30)
    mode = idx % 3
    if mode == 0:
        zp = f"zoompan=z='min(zoom+0.0015,1.18)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
    elif mode == 1:
        zp = f"zoompan=z='min(zoom+0.0015,1.18)':d={frames}:x='(iw-iw/zoom)*on/{frames}':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
    else:
        zp = f"zoompan=z='max(1.18-0.0015*on,1.0)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30"
    # crop tengah 9:16 dulu, lalu kenburns
    vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{zp},"
          "eq=contrast=1.06:saturation=1.05,"
          "noise=alls=5:allf=t")
    # teks overlay: nama besar di bawah + CTA subscribe kecil di atas
    vf += "," + _teks_overlay_vf(teks_overlay)
    r = subprocess.run([FFMPEG_Q, "-y", "-loop", "1", "-i", str(img), "-vf", vf,
                        "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast",
                        "-pix_fmt", "yuv420p", "-r", "30", str(out)],
                       capture_output=True)
    return r.returncode == 0

def buat_musik_ceria(path, dur):
    """Musik latar ceria (synth): progresi C-G-Am-F + melodi playful. Volume rendah."""
    import wave
    SR = 44100
    def note(freq, dur, vol=0.5, kind='sine'):
        n = int(dur * SR)
        tt = np.arange(n) / SR
        w = np.sin(2*np.pi*freq*tt) if kind == 'sine' else 2*np.abs(2*((freq*tt) % 1) - 1) - 1
        env = np.minimum(1, tt/0.02) * np.exp(-tt/(dur*1.5))
        return (w * env * vol)[:n]
    N = {'C3':130.81,'D3':146.83,'E3':164.81,'F3':174.61,'G3':196.00,'A3':220.00,'B3':246.94,
         'C4':261.63,'D4':293.66,'E4':329.63,'F4':349.23,'G4':392.00,'A4':440.00,'B4':493.88,
         'C5':523.25,'D5':587.33,'E5':659.25,'F5':698.46,'G5':783.99,'A5':880.00,
         'C2':65.41,'G2':98.00,'A2':110.00,'F2':87.31}
    chords = [
        (['C3','E3','G3'], ['C4','E4','G4','A4','G4','E4']),
        (['G2','B3','D4'], ['D4','G4','B4','G4','D4','B3']),
        (['A2','C4','E4'], ['E4','A4','C5','A4','E4','C4']),
        (['F2','A3','C4'], ['F4','A4','C5','A4','F4','A4']),
    ]
    track = np.zeros(int(dur*SR))
    t, ci, beat = 0.0, 0, 0.333
    while t < dur - 2:
        cn, mel = chords[ci % 4]
        for c in cn:
            s = note(N[c], 1.8, vol=0.10, kind='tri')
            st = int(t*SR); track[st:st+len(s)] += s
        for m in mel:
            s = note(N[m], beat*0.95, vol=0.16) + note(N[m]*2, beat*0.95, vol=0.04)
            st = int(t*SR); track[st:st+len(s)] += s
            t += beat
        ci += 1
    track = track / (np.abs(track).max() + 1e-9) * 0.85
    f = int(2*SR)
    track[:f] *= np.linspace(0,1,f); track[-f:] *= np.linspace(1,0,f)
    with wave.open(str(path),'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track*32767).astype(np.int16).tobytes())

def main():
    slug = sys.argv[1]
    tema = json.load(open(TEMA_DIR / f"{slug}.json"))
    part = tema.get("part", 1)
    items = tema["items"]
    kerja = BASE / "work" / f"{slug}-part{part}"
    (kerja / "foto").mkdir(parents=True, exist_ok=True)
    (kerja / "audio").mkdir(parents=True, exist_ok=True)
    (kerja / "seg").mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1. Foto ---
    print("== Ambil foto Pexels ==")
    for i, it in enumerate(items):
        if it.get("foto_lokal") and Path(it["foto_lokal"]).exists():
            continue
        hasil = pexels_foto(it["pexels_query"])
        if not hasil:
            print(f"  ! tidak ada foto untuk: {it['pexels_query']}"); sys.exit(1)
        # pilih foto pertama yang landscape-nya cocok (skip yang sudah dipakai)
        foto = hasil[0]
        dest = kerja / "foto" / f"item{i:02d}.jpg"
        unduh(foto["url"], dest)
        it["foto_lokal"] = str(dest)
        it["kredit"] = f"{foto['fotografer']} / Pexels"
        print(f"  OK {it['nama']}")
        time.sleep(1)
    # simpan tema terupdate (dengan foto_lokal)
    json.dump(tema, open(TEMA_DIR / f"{slug}.json", "w"), indent=1, ensure_ascii=False)

    # --- 2. Naskah + TTS ---
    print("== TTS ==")
    segmen = []  # (teks_narasi, label_overlay, audio_path)
    # HOOK
    hook_teks = (f"Hayo, kamu tahu nggak macam-macam {tema['kategori']}? "
                 f"Jangan lupa subscribe dulu ya!")
    segmen.append((hook_teks, f"MACAM-MACAM {tema['kategori'].upper()}!", "hook"))
    for i, it in enumerate(items):
        nar = f"Ini {it['nama']}! {it['fakta']}"
        if i == 3:  # CTA tengah
            nar += " Eh, udah subscribe belum? Subscribe dulu gih!"
        segmen.append((nar, it["nama"].upper(), f"item{i:02d}"))
    # CTA AKHIR (seamless loop: kalimat terakhir = pertanyaan hook awal)
    cta_teks = (f"Nah, itu dia macam-macam {tema['kategori']} part {part}! "
                f"Jangan lupa subscribe, like, dan komen mau part {part+1} tentang apa! "
                f"Hayo, kamu tahu nggak macam-macam {tema['kategori']}?")
    segmen.append((cta_teks, "SUBSCRIBE BIAR NGGAK KETINGGALAN!", "cta"))

    for teks, label, key in segmen:
        ap = kerja / "audio" / f"{key}.mp3"
        if not ap.exists():
            tts(teks, ap)
            print(f"  OK {key}")

    # --- 3. Rakit segmen ---
    print("== Rakit video ==")
    seg_files = []
    for idx, (teks, label, key) in enumerate(segmen):
        ap = kerja / "audio" / f"{key}.mp3"
        d = durasi_audio(ap) + 0.4
        if key == "hook":
            img = Path(items[0]["foto_lokal"])  # hook pakai foto item pertama
        elif key == "cta":
            img = Path(items[-1]["foto_lokal"])
        else:
            img = Path(items[int(key[4:])]["foto_lokal"])
        sp = kerja / "seg" / f"s{idx:02d}.mp4"
        sap = kerja / "seg" / f"s{idx:02d}_a.mp4"
        if not (sp.exists() and durasi_audio(sp) >= d * 0.9):
            bgp, cutp = _layer_untuk(img, tema)
            assert segmen_video(img, d, label, idx, sp, bg=bgp, cutout=cutp), f"gagal segmen {key}"
        # mux audio narasi (lewati bila hasil mux sudah ada — hemat antrean ffmpeg)
        if not sap.exists():
            r = subprocess.run([FFMPEG_Q, "-y", "-i", str(sp), "-i", str(ap),
                                "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                                "-shortest", str(sap)], capture_output=True)
            assert r.returncode == 0, f"gagal mux {key}"
        seg_files.append(sap)
        print(f"  OK seg {key} ({d:.1f}s)")

    # concat
    lst = kerja / "list.txt"
    with open(lst, "w") as f:
        for s in seg_files:
            f.write(f"file '{s}'\n")
    final = OUT_DIR / f"{slug}-part{part}.mp4"
    subprocess.run([FFMPEG_Q, "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", "-movflags", "+faststart", str(final)],
                   capture_output=True, check=True)

    # --- 5. Musik latar ---
    print("== Musik latar ==")
    musik = kerja / "musik-latar.wav"
    dur_total = durasi_audio(final)
    if not musik.exists():
        buat_musik_ceria(musik, dur_total + 5)
        print(f"  OK musik ({dur_total:.0f}s)")
    final_m = OUT_DIR / f"{slug}-part{part}-tmp.mp4"
    subprocess.run([FFMPEG_Q, "-y", "-v", "error", "-i", str(final), "-i", str(musik),
                    "-filter_complex",
                    f"[1:a]volume=0.18,atrim=0:{dur_total:.1f},asetpts=PTS-STARTPTS[m];"
                    "[0:a][m]amix=inputs=2:duration=first:dropout_transition=0[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", str(final_m)],
                   check=True)
    final_m.replace(final)

    # --- 6. Metadata (aturan hashtag user 2026-10-18: 5 hashtag WAJIB =
    # #butifyourcloseyoureyesmeme + 3 hashtag trending bervolume terbesar dari
    # paket protokol-viral.md bag.14 + #foryou sebagai penutup)
    tag_set = "#butifyourcloseyoureyesmeme #shorts #viral #fyp #foryou"
    judul = f"Macam-macam Jenis {tema['judul']} (Part {part}) {tag_set}"
    kredit_teks = "\n".join(f"- {it['nama']}: {it.get('kredit','Pexels')}" for it in items)
    sumber = "Pexels" if any("/ Pexels" in it.get("kredit", "") for it in items) else "Wikimedia Commons"
    deskripsi = (
        f"Tahukah kamu macam-macam {tema['kategori']}? Yuk kenalan satu-satu!\n\n"
        f"Jangan lupa SUBSCRIBE biar nggak ketinggalan Part {part+1}! "
        f"Like kalau kamu suka, dan komen mau bahas apa lagi!\n\n"
        f"{tag_set}\n\n"
        f"Kredit foto:\n{kredit_teks}\n(Sumber: {sumber}, lisensi aman komersial)"
    )
    meta = {"judul": judul, "deskripsi": deskripsi,
            "file": str(final), "durasi_detik": durasi_audio(final)}
    json.dump(meta, open(OUT_DIR / f"{slug}-part{part}.json", "w"),
              indent=1, ensure_ascii=False)
    print(f"\nSELESAI: {final} ({meta['durasi_detik']:.0f} detik)")
    print(f"Judul: {judul}")

if __name__ == "__main__":
    main()
