# Horor Otomatis — Channel Cerita Horor Harian

Pipeline produksi video cerita horor otomatis, mirip `~/workspace/youtube-otomatis/`
tapi untuk konten horor Indonesia. Target channel: **"Kisah POV" (@KisahPOV)**.

## Struktur
```
horor-otomatis/
├── script/            # naskah per hari: script/YYYY-MM-DD.txt (~1000-1200 kata, per beat)
├── audio/             # voiceover: audio/YYYY-MM-DD.mp3 + test-voice.mp3
├── gambar/           # ilustrasi per hari: gambar/YYYY-MM-DD/*.webp (70-80 gambar)
├── video/            # video final: video/YYYY-MM-DD.mp4
├── shorts/           # 3 shorts per hari
├── thumbnail-*.jpg   # thumbnail per hari
├── bikin_thumbnail.py # thumbnail gaya horor (teks merah darah, ≤4 kata)
├── rakit_video.py    # rakit gambar + audio (Ken Burns + grain + vignette)
├── pool-cerita.md    # 45 tema: hantu lokal, urban legend, misteri, legenda
├── riwayat-cerita.json # anti-ulang 60 hari
└── CRON-SETUP.md     # definisi cron horor-harian (didaftarkan parent agent)
```

## Format (dikunci 2026-10-04)
- 9-10 menit, ~1000-1200 kata Bahasa Indonesia, POV mencekam
- 70-80 gambar ilustrasi 2D storybook GELAP (bukan photorealistic)
- Pacing 6-7 detik/gambar, 1 gambar per 1-2 kalimat (beat), hard cut
- Voice: `tts --language id --voice avocado_v2:magnus`
- Thumbnail: gelap + teks merah ≤4 kata
- Hashtag: #horor #ceritahoror #misteri + 2 spesifik
- Afiliasi: 1-2 produk dari share_promo.py (rotasi 7 hari)

## Aturan penting
- Upload HANYA ke @KisahPOV — CEK channel aktif SEBELUM upload!
- Upload butuh approval user
- Jangan janji garansi FYP/views
- Semua tool gratis
