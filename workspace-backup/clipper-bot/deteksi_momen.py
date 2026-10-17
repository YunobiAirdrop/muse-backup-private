#!/usr/bin/env python3
"""
deteksi_momen.py — Transkripsi video panjang + deteksi momen viral.

Alur:
  1. Ekstrak audio video -> wav 16kHz mono (via ffmpeg-queue.sh).
  2. Transkripsi dengan faster-whisper (model tiny, gratis, offline, CPU).
  3. Skor tiap jendela waktu untuk potensi viral (kata kunci Bahasa Indonesia).
  4. Simpan data/transkrip.json dan data/candidates.json.

Pemakaian:
  venv/bin/python deteksi_momen.py --brief brief.yaml [--top 3]
  venv/bin/python deteksi_momen.py --brief brief.yaml --transkrip data/transkrip.json  # skor ulang tanpa transkripsi
"""
import os
# Sanitasi no_proxy: httpx2 (dipakai huggingface_hub saat unduh model) crash
# pada entri IPv6 bracket seperti [::1]. Aman karena huggingface.co tak ada di no_proxy.
_np = os.environ.get("no_proxy", "") + "," + os.environ.get("NO_PROXY", "")
if "[" in _np:
    os.environ["no_proxy"] = "localhost,127.0.0.1"
    os.environ["NO_PROXY"] = "localhost,127.0.0.1"

import argparse
import json
import re
import subprocess
import sys

import yaml

BASE = os.path.dirname(os.path.abspath(__file__))
FFMPEG_Q = os.path.expanduser("~/workspace/youtube-otomatis/ffmpeg-queue.sh")
DATA = os.path.join(BASE, "data")

# ----------------------------------------------------------------------------
# Kamus skoring viral (Bahasa Indonesia).
# Format: kategori -> (daftar frasa, bobot per kemunculan, label alasan)
# ----------------------------------------------------------------------------
KATEGORI = [
    ("opini_tegas",
     ["menurut saya", "faktanya", "sebenarnya", "sejujurnya", "jujur aja",
      "sudah jelas", "pasti", "dijamin", "tahu nggak sih"], 3,
     "opini tegas"),
    ("emosi",
     ["gila", "parah", "kaget", "nggak nyangka", "gak nyangka", "tidak nyangka",
      "marah", "kesal", "kesel", "nangis", "menangis", "takut",
      "merinding", "syok", "wow"], 3,
     "emosi kuat"),
    ("uang",
     ["duit", "uang", "rupiah", "juta", "miliar", "milyar", "gaji", "cuan",
      "bayar", "dibayar", "mahal", "murah", "gratis", "untung", "rugi",
      "kaya", "miskin", "modal"], 4,
     "bahas uang/duit"),
    ("kontroversi",
     ["bohong", "bohongin", "mitos", "salah besar", "jangan percaya",
      "penipuan", "menipu", "hoax", "hoaks", "bodoh", "pembodohan",
      "dilarang", "dilarang keras"], 4,
     "kontroversi/bantahan"),
    ("klaim_mengejutkan",
     ["ternyata", "rahasia", "tidak ada yang tahu", "nggak ada yang tahu",
      "gak ada yang tahu", "pertama kali", "satu-satunya",
      "tidak pernah ada", "belum pernah"], 4,
     "klaim mengejutkan"),
    ("nyentil",
     ["dengerin", "dengarkan", "catat", "ingat baik-baik", "tahu nggak",
      "tau nggak", "percaya nggak", "percaya atau tidak",
      "buat kamu", "untuk kalian"], 2,
     "kalimat nyentil penonton"),
]

BONUS_ANGKA = 2      # ada angka konkret -> klaim terasa nyata
BONUS_TANYA = 1      # kalimat tanya -> rasa penasaran


def load_brief(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ekstrak_audio(video, wav_out):
    os.makedirs(os.path.dirname(wav_out), exist_ok=True)
    cmd = [FFMPEG_Q, "-y", "-i", video, "-vn",
           "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav_out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("GAGAL ekstrak audio:", r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)


def baca_wav_16k_mono(path):
    """Baca wav PCM 16kHz mono -> numpy float32. Hindari bug av.open()
    (kwarg metadata_errors) pada build PyAV di VM ini."""
    import wave
    import numpy as np
    with wave.open(path, "rb") as w:
        nch, sw, fr = w.getnchannels(), w.getsampwidth(), w.getframerate()
        if not (nch == 1 and sw == 2 and fr == 16000):
            raise ValueError(f"Format wav tak terduga: {nch}ch/{sw * 8}bit/{fr}Hz")
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def transkripsi(wav_path, bahasa):
    from faster_whisper import WhisperModel
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    audio = baca_wav_16k_mono(wav_path)
    segments, _info = model.transcribe(
        audio, language=bahasa, word_timestamps=True,
        vad_filter=True, vad_parameters={"min_silence_duration_ms": 500},
    )
    kata = []  # [{m: mulai, s: selesai, t: teks}]
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            t = w.word.strip()
            if t:
                kata.append({"m": round(w.start, 2), "s": round(w.end, 2), "t": t})
    return kata


def simpan_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def skor_kata(kata):
    """Beri skor dasar per kata dari kemunculan frasa kategori."""
    n = len(kata)
    skor = [0] * n
    bukti = [[] for _ in range(n)]  # label kategori per kata
    teks_full = " ".join(k["t"] for k in kata).lower()
    # peta posisi karakter -> indeks kata (untuk frasa multi-kata)
    pos2idx = []
    p = 0
    for i, k in enumerate(kata):
        w = k["t"].lower()
        start = teks_full.find(w, p)
        if start == -1:
            start = p
        pos2idx.append((start, start + len(w)))
        p = start + len(w)
    for _kid, frasa_list, bobot, label in KATEGORI:
        for frasa in frasa_list:
            for m in re.finditer(re.escape(frasa), teks_full):
                s0, s1 = m.start(), m.end()
                kena = [i for i, (a, b) in enumerate(pos2idx) if a < s1 and b > s0]
                for i in kena:
                    skor[i] += bobot
                    if label not in bukti[i]:
                        bukti[i].append(label)
    return skor, bukti


def cari_kandidat(kata, skor, bukti, dmin, dmax, top_n):
    n = len(kata)
    if n == 0:
        return []
    jendela = []
    langkah = max(1, n // 400)  # batasi jumlah jendela utk video panjang
    ukuran = sorted({dmin, (dmin + dmax) / 2, dmax})
    for i in range(0, n, langkah):
        t0 = kata[i]["m"]
        for dur in ukuran:
            t1 = t0 + dur
            # kumpulkan kata dalam [t0, t1]
            idx = [j for j in range(i, n)
                   if kata[j]["m"] < t1 and kata[j]["s"] > t0]
            if not idx:
                continue
            mulai = kata[idx[0]]["m"]
            selesai = kata[idx[-1]]["s"]
            d = selesai - mulai
            if d < dmin * 0.8 or d > dmax * 1.2:
                continue
            s = sum(skor[j] for j in idx)
            teks = " ".join(kata[j]["t"] for j in idx)
            alasan = {}
            for j in idx:
                for lab in bukti[j]:
                    alasan[lab] = alasan.get(lab, 0) + 1
            # bonus
            if re.search(r"\d", teks):
                s += BONUS_ANGKA
                alasan["angka konkret"] = alasan.get("angka konkret", 0) + 1
            if "?" in teks:
                s += BONUS_TANYA
                alasan["kalimat tanya"] = alasan.get("kalimat tanya", 0) + 1
            if s <= 0:
                continue
            jendela.append({
                "mulai": round(mulai, 2), "selesai": round(selesai, 2),
                "durasi": round(d, 2), "skor": s, "teks": teks,
                "kata": [{"m": kata[j]["m"], "s": kata[j]["s"], "t": kata[j]["t"],
                          "ss": skor[j]} for j in idx],
                "alasan": [f"{lab} (x{c})" for lab, c in
                           sorted(alasan.items(), key=lambda x: -x[1])],
            })
    # pilih top-N tanpa overlap (greedy)
    jendela.sort(key=lambda x: -x["skor"])
    terpilih = []
    for j in jendela:
        if all(j["selesai"] <= t["mulai"] or j["mulai"] >= t["selesai"]
               for t in terpilih):
            terpilih.append(j)
        if len(terpilih) >= top_n:
            break
    terpilih.sort(key=lambda x: x["mulai"])
    for i, t in enumerate(terpilih, 1):
        t["id"] = i
    return terpilih


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", default=os.path.join(BASE, "brief.yaml"))
    ap.add_argument("--transkrip", default=None,
                    help="pakai transkrip JSON yang sudah ada (lewati transkripsi)")
    ap.add_argument("--top", type=int, default=None)
    args = ap.parse_args()

    brief = load_brief(args.brief)
    top_n = args.top or int(brief.get("jumlah_klip", 3))
    dmin = float(brief.get("durasi_klip_min", 20))
    dmax = float(brief.get("durasi_klip_max", 60))
    bahasa = brief.get("bahasa", "id")

    wav = os.path.join(DATA, "audio-16k.wav")
    tr_path = os.path.join(DATA, "transkrip.json")

    if args.transkrip:
        print(f"[1/3] Pakai transkrip: {args.transkrip}")
        with open(args.transkrip, encoding="utf-8") as f:
            kata = json.load(f)
    else:
        video = args_video(brief)
        print(f"[1/3] Ekstrak audio: {video}")
        ekstrak_audio(video, wav)
        print("[2/3] Transkripsi (faster-whisper tiny, CPU)...")
        kata = transkripsi(wav, bahasa)
        simpan_json(tr_path, kata)
        print(f"      {len(kata)} kata -> {tr_path}")

    print("[3/3] Skoring momen viral...")
    skor, bukti = skor_kata(kata)
    kandidat = cari_kandidat(kata, skor, bukti, dmin, dmax, top_n)
    cand_path = os.path.join(DATA, "candidates.json")
    simpan_json(cand_path, kandidat)
    print(f"      {len(kandidat)} kandidat -> {cand_path}")
    for k in kandidat:
        print(f"      #{k['id']} {k['mulai']:.0f}-{k['selesai']:.0f}d "
              f"skor={k['skor']} | {'; '.join(k['alasan'][:3])}")


def args_video(brief):
    v = brief.get("sumber_video", "")
    if not os.path.isabs(v):
        v = os.path.join(BASE, v)
    if not os.path.exists(v):
        print(f"ERROR: sumber_video tidak ditemukan: {v}", file=sys.stderr)
        sys.exit(1)
    return v


if __name__ == "__main__":
    main()
