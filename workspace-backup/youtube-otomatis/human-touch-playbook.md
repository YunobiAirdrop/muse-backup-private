# HUMAN TOUCH PLAYBOOK — Lolos Review Monetisasi YouTube

Dasar: kebijakan "inauthentic content" YouTube (15 Juli 2025, klarifikasi 2026).
YouTube TIDAK melarang channel AI — yang ditolak = channel yang kelihatan
mass-produced/template tanpa jejak keputusan manusia. Reviewer menilai
channel secara keseluruhan: "kelihatan nggak, apa yang diputuskan manusia
di video ini?" Riset komunitas kreator 2026-10-10 (arsip: research_notes/
ai-channels-pass-monetization-review-20261010-1633/).

Berlaku untuk 19 channel mulai produksi 2026-10-11. Melengkapi (bukan
mengganti) aturan anti-AI-look di AGENTS.md.

## 7 JURUS WAJIB

### 1. Naskah opini-first (jurus #1 komunitas)
Setiap naskah WAJIB mengandung:
- Segmen ANALISIS/OPINI eksplisit: "menurut saya...", "yang menarik dari sini...",
  verdict/kesimpulan personal di akhir. Bukan sekadar membacakan fakta.
- 1 ANEKDOT personal per video long ("saya pernah baca...", "waktu kecil saya..."),
  ditulis sebagai persona host (lihat daftar di bawah).
- AI boleh bikin draft, tapi naskah final = rewrite total dengan suara persona.
  Fakta dicek ulang (fact-check = bagian yang dinilai reviewer).

### 2. Host persona tetap per channel
Tiap channel punya PEMBAWA ACARA fiktif yang konsisten: nama, gaya bicara,
catchphrase. Naskah ditulis orang-pertama sebagai dia. Channel jadi terasa
"ada orangnya", bukan robot baca teks.

| Channel | Persona | Gaya |
|---|---|---|
| @AncientEmpiresTV | Prof. Adrian, arkeolog | Antusias, "bayangkan..." |
| @EchoesOfThePast-e9m | Sang Pencerita Waktu | Misterius, puitis ringan |
| @KisahPOV | Bang Rano, pendongeng kampung | Santai, "ngeri nggak tuh?" |
| @TalesOfDreadTV | The Night Narrator | Pelan, mencekam |
| @JejakBuddha | Bhante terse senyum | Tenang, penuh hikmah |
| @JejakIslami-h3d | Ustadz Salman | Hangat, "masya Allah..." |
| @KisahAlkitab-k9j | Pak Daniel, pengajar | Bersahaja, "pelajarannya..." |
| @KisahDharma | Resi Dharma | Bijak, perumpamaan |
| @LimaMisteri | Reza Penasaran | "Saya" yang kepo, ajak mikir |
| @TheDarkMindFiles-s6i | Dr. Mind (pop-psych) | Fakta psikologi, TANPA nasihat kesehatan mental |
| @MysteryShadowsTV | Detektif Mara | Investigatif, "buktinya..." |
| @CosmosUnknownTV | Kapten Nova | Takjub, "luar biasa..." |
| @StrangeTales-g6n | Si Aneh | Cepat, kaget, khas Shorts |
| @tinybuilders-d5z | Kang Udin, tukang miniatur | Ceria, "lihat nih..." |
| @TrueCaseFilesTV | Jurnalis Case | Dokumenter, kronologis ketat |
| @BizarreWorldDaily | Bo, si takjub | "Serius ini nyata?!" |
| @ceritarakyat862 | Mbah Dongeng | Hangat, "pada zaman dahulu..." |
| @InkTime-d3t | Pak Guru Ink | Explainer whiteboard, "gampangnya..." |
| @MacamMacamID | Bang Macam | Serba-tahu santai |

### 3. Variasi format — bunuh template tunggal
Tiap channel WAJIB punya 3 format yang DIROTASI (bukan 1 template diulang):
contoh LimaMisteri: (a) countdown 5, (b) deep-dive 1 kasus, (c) "teori saya"
opini. Format boleh konsisten (intro/outro sama = diizinkan), ISI yang
harus beda tiap video. Larangan: 3 video beruntun dengan struktur identik.

### 4. Read-aloud test
Sebelum render: baca naskah keras-keras (simulasi). Kalau terdengar seperti
robot baca Wikipedia → tulis ulang. Kalimat pendek, kontraksi natural,
jeda tertulis (tanda baca = jeda napas). Berlaku untuk voice Mudiwa maupun EN.

### 5. Riset sebagai produk
Sumber disebut eksplisit di naskah/deskripsi: "menurut catatan...", "dilansir
dari...". Untuk true crime: kronologi + peta/timeline. Untuk sejarah:
periode + tokoh spesifik. Reviewer menghargai jejak riset manusia.

### 6. Visual scene-by-scene beda
Lanjutan aturan AGENTS.md: tiap scene visual BERBEDA (angle/komposisi/warna).
QC: tonton tanpa suara — kalau 3 shot beruntun kelihatan sama = gagal,
bikin ulang. Dilarang pakai library template gerak yang sama antar channel.

### 7. Pre-application audit + appeal asset
Sebelum tiap channel didaftarkan monetisasi:
- Unlist/hapus video low-effort / template mentah dari backlog.
- Lengkapi About/deskripsi channel (identitas persona jelas).
- SIMPAN file proyek: naskah final, log produksi, prompt visual. Ini bukti
  banding (appeal video <5 menit nunjukkin proses produksi) kalau ditolak.

## CATATAN RISIKO KHUSUS
- Shorts-only (Strange Tales dkk): jalur 10M views/90 hari approval-nya
  dilaporkan lebih ketat dari jalur long-form 2026. Shorts tetap jalan
  (dukung discoverability), tapi tiap channel shorts WAJIB punya rencana
  long-form pendamping untuk jalur 1K subs + 4K jam tayang.
- @TheDarkMindFiles-s6i: JANGAN jadi persona pemberi nasihat kesehatan
  mental/finansial — kategori AI persona topik sensitif = ineligible 2026.
  Tetap di fakta & keingintahuan psikologi populer.
- AI disclosure tetap dicentang tiap upload (tidak mengurangi reach).

## BUMPER SUARA OWNER (audio-only, tanpa avatar)
- **Keputusan user 2026-10-11: bumper HANYA suara, tanpa klip avatar Dola.**
  (User tidak perlu membuat 18 klip Dola sisa.) Alasan: avatar AI justru
  berisiko terlihat "AI-produced"; suara asli owner = sinyal manusia yang
  lebih kuat untuk review monetisasi.
- File: `youtube-otomatis/voice-clone-test/bumper-*.wav` (19 file, 9 Inggris
  + 10 Indonesia, hasil clone suara asli owner via XTTS-v2; disetujui user
  2026-10-11). Dibuat ulang kapan saja via toolkit `~/workspace/skills/voice-clone/`.
- **PENEMPATAN: JANGAN di detik 0** — kebanyakan penonton tidak suka intro
  di depan. Selipkan di TENGAH video pada jeda chapter/scene yang natural
  (sekitar 30-50% durasi, tepat di potongan scene): duck audio latar,
  putar voiceover bumper, tampilkan overlay teks nama channel (lower-third,
  2-3 detik). Untuk Shorts: versi 2 detik ("Halo, saya Yunobi!" /
  "Hi, I'm Yunobi!") diselipkan di tengah pada potongan visual — bukan di
  awal dan bukan di seam loop (seamless loop wajib utuh).
- (Arsip: rencana awal bumper video avatar Dola DIBATALKAN 2026-10-11.
  Satu file lama `empires-en/intro-bumper.mp4` sudah tidak dipakai.)
