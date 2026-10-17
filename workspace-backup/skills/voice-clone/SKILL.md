# Voice Clone (gratis, via HuggingFace)

Generate voiceover dengan suara hasil cloning — gratis, tanpa daftar akun,
tanpa GPU lokal. Memakai XTTS-v2 yang jalan di GPU gratis HuggingFace
(ZeroGPU) lewat Gradio API, dengan fallback otomatis antar Space.

## Pakai

```bash
# Suara default = suara asli owner (Yunobi)
/home/hatch/workspace/skills/voice-clone/clone_voice.py \
  --text "Halo, saya Yunobi. Selamat datang di Kisah Horor." \
  --out bumper-horor.wav

# Sampel suara lain (file lokal atau URL)
/home/hatch/workspace/skills/voice-clone/clone_voice.py \
  --text "Hi, I'm Yunobi." --ref /path/suara.wav --lang English --out en.wav
```

Argumen:
- `--text` (wajib): teks yang diucapkan
- `--out` (wajib): file output .wav
- `--ref`: path lokal atau URL sampel suara (default: suara owner di
  `~/workspace/youtube-otomatis/dola-intro/suara-bersih-test.mp3`)
- `--lang`: bahasa (default `English`; catatan: `English` terbukti
  menghasilkan ucapan Indonesia yang benar untuk teks Indonesia)

## Batasan (jujur)

- Cocok untuk klip PENDEK (bumper, stinger, kalimat). BUKAN untuk narasi
  panjang harian — GPU gratis ada kuota dan Space bisa antre/mati.
- Kualitas clone tergantung sampel: sampel 4,5 detik (bawaan) = mirip tapi
  tidak sempurna; sampel 10-15 detik yang jelas = jauh lebih baik.
- Sampel suara adalah data biometrik: jangan sebar URL publiknya.
- Space yang terverifikasi saat ini: `hasanbasbunar/voice-cloning-xtts-v2`
  (2026-10-11). Daftar cadangan ada di `SPACES` dalam `clone_voice.py` —
  tambah Space baru ke list setelah verifikasi manual.

## Pelajaran teknis (jangan diulang)

1. `no_proxy`/`NO_PROXY` bawaan runtime mengandung `[::1]` yang merusak
   parsing URL di httpx lama — skrip menghapus keduanya saat start.
2. Space HARUS menerima upload WAV 24kHz mono via `/gradio_api/upload`
   lalu `file_url`-nya sebagai `reference_audio_url`. MP3 langsung
   DITOLAK (ffmpeg decoding failed); URL Drive langsung juga gagal di-decode
   di sisi server — selalu download dulu lalu upload.
3. `example_audio_name` WAJIB `None` bila memakai `reference_audio_url`
   (kalau tidak: "provide either ... but not both").
4. Butuh venv `/home/hatch/workspace/.venv-stt` (gradio_client) + ffmpeg.

## Riwayat

- 2026-10-11: 19/19 bumper channel YouTube digenerate dengan tool ini
  (`~/workspace/youtube-otomatis/voice-clone-test/bumper-*.wav`).
