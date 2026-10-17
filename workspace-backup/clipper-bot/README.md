# Clipper-Bot

Pipeline otomatis untuk campaign clipper (contoh: Clippo.id):
**video panjang resmi campaign → deteksi momen viral → klip vertikal siap posting.**

Semua pemanggilan ffmpeg lewat `~/workspace/youtube-otomatis/ffmpeg-queue.sh`
(semaphore, maks 2 render bareng — aturan AGENTS.md). Tooling 100% gratis.

## Struktur

```
clipper-bot/
├── brief.yaml          # config campaign (contoh) — salin per campaign baru
├── deteksi_momen.py    # transkripsi (faster-whisper tiny) + skoring viral
├── render_klip.py      # potong + render vertikal 1080x1920 (hook/subs/CTA)
├── siapkan_posting.py  # captions.txt + manifest.json
├── venv/               # Python env (faster-whisper, pyyaml)
├── data/               # audio-16k.wav, transkrip.json, candidates.json
├── clips/              # hasil klip MP4 vertikal
└── sampel/             # video sumber untuk uji coba
```

## Cara pakai

```bash
cd ~/workspace/clipper-bot

# 0. (sekali saja) siapkan environment — SUDAH jadi di VM ini
python3 -m venv venv && venv/bin/pip install faster-whisper pyyaml

# 1. Isi brief campaign: salin & edit
cp brief.yaml brief-nutriflakes.yaml
#    → ganti campaign, sumber_video, hashtag_wajib, cta, dst.

# 2. Deteksi momen viral (transkripsi + skoring)
venv/bin/python deteksi_momen.py --brief brief-nutriflakes.yaml
#    hasil: data/transkrip.json, data/candidates.json

# 3. Render klip vertikal (1080x1920, hook 3 dtk + subtitle + CTA 5 dtk)
venv/bin/python render_klip.py --brief brief-nutriflakes.yaml
#    hasil: clips/klip-01.mp4, ...

# 4. Siapkan caption + manifest posting
venv/bin/python siapkan_posting.py --brief brief-nutriflakes.yaml
#    hasil: captions.txt, manifest.json
```

Opsi tambahan `deteksi_momen.py`:
- `--top 5` — ambil 5 kandidat teratas (default: `jumlah_klip` di brief)
- `--transkrip data/transkrip.json` — skor ulang tanpa transkripsi ulang

## Cara kerja skoring viral

Tiap jendela waktu (20–60 detik, sesuai brief) diskoring dari kata kunci
Bahasa Indonesia:

| Kategori | Contoh kata | Bobot |
|---|---|---|
| Opini tegas | faktanya, jujur aja, pasti | 3 |
| Emosi | gila, parah, kaget, merinding | 3 |
| Uang/duit | duit, cuan, juta, gratis | 4 |
| Kontroversi | bohong, mitos, jangan percaya | 4 |
| Klaim mengejutkan | ternyata, rahasia | 4 |
| Nyentil | dengerin, tahu nggak | 2 |

Bonus: angka konkret (+2), kalimat tanya (+1). Kandidat teratas dipilih
tanpa overlap waktu (greedy).

## Catatan

- Video sumber HARUS materi resmi campaign (dari dashboard/grup campaign).
  Klip dari video orang tanpa izin = pelanggaran hak cipta.
- Views/like hasil beli/bot melanggar kebijakan platform — views harus organik.
- Unduh model whisper pertama kali butuh internet; skrip otomatis
  membersihkan variabel `no_proxy` yang merusak downloader.
