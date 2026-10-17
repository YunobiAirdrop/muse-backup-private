# Comment Intel Playbook — YouTube (adaptasi dari youtube-marketing-skills/comment-intel)

Tujuan: setiap komentar penonton adalah riset gratis. Selain dibalas, komentar DITAMBANG untuk:
ide video, pertanyaan yang berulang (FAQ), dan bahasa alami penonton (emas keyword).

Aturan user yang didukung: "komentar penonton berisi masukan bagus → pelajari, perbaiki,
terapkan ke semua channel."

## Yang dicari di komentar

1. **Permintaan topik** — "bikin dong tentang...", "coba bahas...", "next... please"
   → IDE VIDEO langsung. Catat topik + channel + frekuensi.
2. **Pertanyaan berulang** — pertanyaan yang sama muncul 3x+ (antar video/channel)
   → kandidat video FAQ / Shorts jawab pertanyaan.
3. **Bahasa alami penonton (keyword gold)** — kata/frasa yang mereka pakai sendiri
   → pakai di judul & deskripsi video berikutnya (bahasa mereka = bahasa pencarian mereka).
4. **Koreksi/masukan** — "suaranya kekecilan", "gambarnya kurang jelas", "kepanjangan"
   → PERBAIKAN produksi, terapkan ke semua channel (aturan user).
5. **Sentimen** — apa yang bikin mereka senang ("merinding", "bikin nagih") vs bingung
   → gandakan yang disukai, perbaiki yang membingungkan.

## Cara kerja (tiap run balas-komentar malam)

Saat membaca komentar baru tiap channel, selain membalas:
- Tandai komentar yang masuk 5 kategori di atas.
- Tulis temuan ke `~/workspace/youtube-otomatis/comment-intel.json` (append):
  `{"tanggal": "YYYY-MM-DD", "channel": "...", "kategori": "ide-video|faq|keyword|koreksi|sentimen", "kutipan": "...", "aksi": "..."}`
- Di laporan run: bagian "INTEL KOMENTAR" — maksimal 5 temuan terbaik + aksi yang diambil
  (mis. "3 penonton minta bahas X → masuk antrean topik Lima Misteri").

## Batasan

- Jangan mengarang komentar — hanya yang benar-benar tertulis.
- 1 ide video dari komentar WAJIB melewati filter anti-rebuild (cek riwayat topik channel dulu).
- Koreksi produksi yang ditemukan di 1 channel → cek apakah masalahnya ada di channel lain juga.
