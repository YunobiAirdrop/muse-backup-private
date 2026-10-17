# TEKNIK — Demo Keyframe "Belajar Warna bersama Bimo & Alat Berat"
File final: demo-keyframe-2026-10-12.mp4 — 720x1280, 30fps, 44,9 detik, H.264 + AAC.
Semua render dijalankan lewat ~/workspace/youtube-otomatis/ffmpeg-queue.sh.

## Layer per adegan
1. **Background panorama** (bg.webp 2352x1008) di-scale ke 2987x1280, lalu crop jendela 720x1280.
2. **Kendaraan transparan**: bus/excavator/truck/bulldozer di-chromakey dari background magenta polos (colorkey 0xFE1991:0.22:0.05) menjadi PNG RGBA ukuran kanvas asli 1920x1280 (truck di-hflip agar menghadap kanan).
3. **Layer roda terpisah** (khusus bus & truk): crop lingkaran dari PNG keyed + mask alpha lingkaran penuh (geq), di-overlay tepat di atas roda bawaan gambar.
4. **Layer lubang jalan & tambalan**: elips pipih hasil geq (300x90), tambalan = versi abu muda; di S4 lubang fade-out dan tambalan fade-in.
5. **Teks drawtext** (DejaVuSans-Bold + border hitam): judul, kartu warna HIJAU/KUNING/MERAH/BIRU, dan teks akhir.

## Keyframe yang BENAR-BENAR terpakai
- **Background scroll: YA** — di S0 crop x bergerak `min(2150, 6*n)` (panorama bergeser selama Bimo "berjalan"); adegan lain memakai crop statis pada posisi panorama berbeda-beda.
- **Roda berputar: YA** — layer roda bus & truk diputar `rotate=a='-4*t'` (bus: berhenti di t=1,9 pada adegan hook; truk: berhenti di t=1,8), mengikuti fase masuk kendaraan lalu berhenti bersama kendaraannya.
- **Geser masuk (slide-in)**: hampir semua kendaraan masuk dengan kurva `exp(-k*t)` dari luar layar (deselerasi halus), bukan linear.
- **Mantul halus**: osilasi y sinusoidal kecil pada badan kendaraan (bus 5px @13,8 rad/s; truk 4px; finale 3px beda fase per kendaraan).
- **Getar kerja**: excavator bergetar (sin 20 rad/s + 8,8 rad/s) pada fase "menggali" t=1,2–4,2.
- **Jeda/goyang tambalan**: truk bergoyang sekali (osilasi teredam exp) setelah t=2,3, menyimulasikan menuang pasir.
- **Fade**: lubang memudar keluar & tambalan memudar masuk di adegan bulldozer; bulldozer sendiri meluncur linear melintasi lubang.

## Audio
- Lagu tema (chant TTS ritmis, lirik orisinal "Lagu Bimo"): 4 baris pada detik ±0,3–11,3 (adegan pembuka S0); reprise 1 baris pada detik ±36,4–39,1; salam pamit ±39,3; CTA subscribe ±41,9 (file cta.mp3 berhenti tepat di 44,8).
- Narasi per bagian menyusul sesudah lagu: hook 11,2 • excavator 16,4 • truk 21,1 • bulldozer 25,6 • hore/penutup 30,6.
- Musik latar (musik.wav, loop) di bawah suara: volume 0,30 saat lagu, 0,13 saat narasi, 0,26 di finale; semua campuran dibatasi alimiter 0,95.

## Kekurangan (jujur)
1. **Judul pembuka kepotong**: teks "BIMO & ALAT BERAT" fontsize 70 lebih lebar dari 720px — huruf pertama & terakhir terpotong tepi layar (terlihat jelas di frame t=3).
2. **Lubang tertutup truk**: di adegan truk, elips lubang ter-overlay di bawah badan truk sehingga terbaca seperti bayangan, bukan lubang di depan kendaraan.
3. **Artefak layer roda**: ada sliver hijau kecil di dekat roda depan bus dan fringe tipis kemerahan di tepi ban truk — sisa tepi chromakey pada crop roda.
4. **Excavator pasif**: lengan & bucket tidak dipisah layer, jadi tidak benar-benar "menggali" — gerakannya hanya getar/bobbing badan utuh. Roda rantai excavator & bulldozer tidak berputar (sesuai gambar aslinya memang beroda rantai).
5. **Lagu tema = chant**, bukan nyanyian melodis: TTS dibawakan ritmis mengikuti beat; terdengar seperti rap anak sederhana.
6. **Waktu produksi lama karena antrean**: prep aset ±35 menit, render 6 adegan + mix ±39 menit, ekstraksi frame verifikasi ±43 menit — hampir seluruhnya menunggu slot ffmpeg-queue yang dipakai bersama 19 channel, bukan waktu komputasi.
