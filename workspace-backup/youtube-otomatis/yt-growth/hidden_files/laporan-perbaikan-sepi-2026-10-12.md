# Laporan Perbaikan Metadata Video Sepi — 2026-10-12 (malam)

Perintah user: scan 1:1 semua channel, perbaiki video sepi sampai peluang ramenya naik. Sumber daftar: `sepi-2026-10-12.json`. Eksekusi via YouTube Data API (yt_put), aturan protokol-viral.md bag. 3/14/17 + packaging-formulas.md.

## Ringkasan total

- Video dalam daftar yang diproses: **132** (17 channel) — di luar pengecualian.
- **Diperbaiki: 128 video.** Verifikasi read-back 2 video acak per channel: **17/17 channel cocok**.
- **Tidak diubah: 4 video** (metadata sudah lulus audit, lihat bagian bawah).
- Duplikat 0-view di-private: **2 video** (@TalesOfDreadTV).
- Dikecualikan sesuai instruksi: bGBGROVZfZY (@MacamMacamID) — tidak disentuh sama sekali.
- Audit ulang pasca-perbaikan (sampel): horor nadty2jGMfY 100/100, mystery-en FZZpx8dT-Xc 95/100, jejakislami 8LdS1kmxEjg 95/100, lima-misteri K8QaZZXVN2Q 90/100.

Cacat yang paling banyak ditemukan (hampir semua Shorts): hashtag penutup **#foryou hilang** (ekor judul berhenti di hashtag niche), kolom **tags tipis/kosong** (0–60 karakter), dan deskripsi Shorts tanpa link ke video long pasangannya / deskripsi long tanpa hashtag #foryou. Hook judul sendiri umumnya sudah kuat — dipertahankan, hanya 2 judul yang inti hook-nya ditulis ulang (mind-en eHDUZyD8oKw, space-en I-fJeXXkgn8) sesuai pola pemenang bag. 18.

## Per channel

### @AncientEmpiresTV (empires-en) — 11/11 video diperbaiki; verifikasi 2/2 cocok
- Judul: `They Predicted Eclipses but Missed the Drought #shorts #history #archaeology`
  → `They Predicted Eclipses but Missed the Drought #shorts #history #archaeology #foryou`
- Judul: `60 Maya Cities Died in One Lifetime 😱 #shorts #history #archaeology`
  → `60 Maya Cities Died in One Lifetime 😱 #shorts #history #archaeology #foryou`
- Jenis perubahan: judul ×9, deskripsi ×8, tags ×9

### @EchoesOfThePast-e9m (history-en) — 3/3 video diperbaiki; verifikasi 2/2 cocok
- Judul: `The Greatest City on Earth Vanished in 93 Days #shorts #history #documentary`
  → `The Greatest City on Earth Vanished in 93 Days #shorts #history #documentary #foryou`
- Jenis perubahan: judul ×1, deskripsi ×3, tags ×1

### @KisahPOV (horor) — 20/20 video diperbaiki; verifikasi 2/2 cocok
- Judul: `Dia Ikut Pulang! Tiap Difoto Makin Dekat | Kutukan Candi Terlarang #shorts #horor #ceritahoror`
  → `Dia Ikut Pulang! Tiap Difoto Makin Dekat | Kutukan Candi Terlarang #shorts #horor #foryou`
- Judul: `3 Hari Setelah Motret, Kakeknya Meninggal! | Kutukan Candi Terlarang #shorts #horor #ceritahoror`
  → `3 Hari Setelah Motret, Kakeknya Meninggal! | Kutukan Candi Terlarang #shorts #horor #foryou`
- Jenis perubahan: deskripsi ×14, tags ×18, judul ×12

### @TalesOfDreadTV (horror-en) — 4/4 video diperbaiki; verifikasi 2/2 cocok
- Judul: `He Wouldn't Open the Doors #shorts #horror #scarystories`
  → `He Wouldn't Open the Doors #shorts #horror #scarystories #foryou`
- Judul: `She Had NO Reflection #shorts #horror #scarystories`
  → `She Had NO Reflection #shorts #horror #scarystories #foryou`
- Jenis perubahan: judul ×3, tags ×4, deskripsi ×1
- Duplikat di-private: jhDzosY_vj8 + 7mkgmONd89o (lihat bagian duplikat).

### @JejakBuddha (jejakbuddha) — 4/4 video diperbaiki; verifikasi 2/2 cocok
- Jenis perubahan: deskripsi ×4

### @JejakIslami-h3d (jejakislami) — 6/6 video diperbaiki; verifikasi 2/2 cocok
- Judul: `Mimpi Sebelas Bintang Jadi Kenyataan #shorts #islami #kisahnabi`
  → `Mimpi Sebelas Bintang Jadi Kenyataan #shorts #islami #kisahnabi #foryou`
- Judul: `Difitnah Lalu Dipenjara Tanpa Bersalah #shorts #islami #kisahnabi`
  → `Difitnah Lalu Dipenjara Tanpa Bersalah #shorts #islami #kisahnabi #foryou`
- Jenis perubahan: deskripsi ×6, judul ×3, tags ×3
- Catatan: w6iwcZqpV1E (versi lama Musa, tertahan private) hanya ditambah hashtag deskripsi; status private-nya TIDAK diubah — tetap tidak tayang, sesuai keputusan sebelumnya.

### @KisahAlkitab-k9j (kisahalkitab) — 3/3 video diperbaiki; verifikasi 2/2 cocok
- Judul: `"Allah Mereka-rekakannya untuk Kebaikan" — Kisah Yusuf #shorts #alkitab #rohani`
  → `"Allah Mereka-rekakannya untuk Kebaikan" — Kisah Yusuf #shorts #alkitab #rohani #foryou`
- Judul: `Pagi Masih Tahanan, Sore Jadi Penguasa Mesir — Kisah Yusuf #shorts #alkitab #rohani`
  → `Pagi Masih Tahanan, Sore Jadi Penguasa Mesir — Kisah Yusuf #shorts #alkitab #rohani #foryou`
- Jenis perubahan: judul ×3, deskripsi ×3, tags ×3

### @KisahDharma (kisahdharma) — 3/3 video diperbaiki; verifikasi 2/2 cocok
- Jenis perubahan: deskripsi ×3, tags ×3

### @LimaMisteri (lima-misteri) — 10/10 video diperbaiki; verifikasi 2/2 cocok
- Judul: `Difoto Desanya Ada, Hasilnya Cuma Hutan Kosong | Lima Misteri #shorts #misteri #penampakan`
  → `Difoto Desanya Ada, Hasilnya Cuma Hutan Kosong | Lima Misteri #shorts #misteri #penampakan #foryou`
- Judul: `Terekam Dasbor Tapi Tak Ada di Spion, Sosok Tol Misterius| Lima Misteri #shorts #misteri #penampakan`
  → `Terekam Dasbor Tapi Tak Ada di Spion, Sosok Tol Misterius| Lima Misteri #shorts #misteri #foryou`
- Jenis perubahan: deskripsi ×10, tags ×8, judul ×5

### @TheDarkMindFiles-s6i (mind-en) — 6/6 video diperbaiki; verifikasi 2/2 cocok
- Judul: `The Free Gift That Is Not Free #shorts #psychology #mindset`
  → `That 'Free' Gift Is a Trap to Control You #shorts #psychology #mindset #foryou`
- Judul: `Gaslighting: How They Destroy Your Reality #shorts #psychology #mindset`
  → `Gaslighting: How They Destroy Your Reality #shorts #psychology #mindset #foryou`
- Jenis perubahan: judul ×4, deskripsi ×6, tags ×4

### @MysteryShadowsTV (mystery-en) — 4/4 video diperbaiki; verifikasi 2/2 cocok
- Judul: `Her Tongue Was Missing. Their Clothes Were Radioactive.`
  → `Her Tongue Was Missing. Their Clothes Were Radioactive. #shorts #mystery #unsolved #foryou`
- Judul: `Glowing Orbs Were Seen Over the Mountain That Night`
  → `Glowing Orbs Were Seen Over the Mountain That Night #shorts #mystery #unsolved #foryou`
- Jenis perubahan: judul ×3, deskripsi ×4, tags ×3

### @CosmosUnknownTV (space-en) — 6/7 video diperbaiki; verifikasi 2/2 cocok
- Judul: `330 MILLION Light-Years of NOTHING Exists?! 😱 #shorts #space #universe`
  → `The Boötes Void: 330 Million Light-Years of NOTHING #shorts #space #universe #foryou`
- Judul: `Could Life Survive With NO Sunlight? 👽 #shorts #space #universe`
  → `Could Life Survive With NO Sunlight? 👽 #shorts #space #universe #foryou`
- Jenis perubahan: judul ×4, deskripsi ×6, tags ×5

### @StrangeTales-g6n (strangetales) — 10/10 video diperbaiki; verifikasi 2/2 cocok
- Judul: `This Hole Has Been on Fire for 50 Years — HOW?! #shorts #weirdfacts #strangetales`
  → `This Hole Has Been on Fire for 50 Years — HOW?! #shorts #weirdfacts #strangetales #foryou`
- Judul: `Scientists Heard SOMETHING Huge in the Ocean — What Was It?! #shorts #mystery #strangetales`
  → `Scientists Heard SOMETHING Huge in the Ocean — What Was It?! #shorts #mystery #strangetales #foryou`
- Jenis perubahan: deskripsi ×6, tags ×10, judul ×9

### @tinybuilders-d5z (tinybuilders) — 7/7 video diperbaiki; verifikasi 2/2 cocok
- Judul: `They Built a Tiny DAM That Actually Works! #shorts #miniature #diy`
  → `They Built a Tiny DAM That Actually Works! #shorts #miniature #diy #foryou`
- Judul: `This Bamboo Pump Moves REAL Water! #shorts #miniature #diy`
  → `This Bamboo Pump Moves REAL Water! #shorts #miniature #diy #foryou`
- Jenis perubahan: judul ×6, deskripsi ×7, tags ×7

### @TrueCaseFilesTV (truecrime-en) — 11/12 video diperbaiki; verifikasi 2/2 cocok
- Judul: `Cooper Vanished Mid-Air. The FBI Never Solved It #shorts #truecrime #mystery`
  → `Cooper Vanished Mid-Air. The FBI Never Solved It #shorts #truecrime #mystery #foryou`
- Judul: `The $5,800 That Reopened America's Greatest Mystery #shorts #truecrime #mystery`
  → `The $5,800 That Reopened America's Greatest Mystery #shorts #truecrime #mystery #foryou`
- Jenis perubahan: judul ×9, deskripsi ×8, tags ×11

### @BizarreWorldDaily (weird-en) — 1/2 video diperbaiki; verifikasi 1/1 cocok
- Jenis perubahan: deskripsi ×1, tags ×1

### @ceritarakyat862 (youtube-pov) — 19/20 video diperbaiki; verifikasi 2/2 cocok
- Judul: `Diserang Saat Fajar! Thorvald Gugur di Vinland | POV Pelaut Viking #shorts #pov #sejarah`
  → `Diserang Saat Fajar! Thorvald Gugur di Vinland | POV Pelaut Viking #shorts #pov #sejarah #foryou`
- Judul: `Perahu-Perahu Asing Mendekat... Mereka Bukan Kawan! | POV Pelaut Viking #shorts #pov #sejarah`
  → `Perahu-Perahu Asing Mendekat... Mereka Bukan Kawan! | POV Pelaut Viking #shorts #pov #foryou`
- Jenis perubahan: deskripsi ×13, tags ×14, judul ×12

## Duplikat @TalesOfDreadTV — sudah di-private

- `jhDzosY_vj8` "She Had NO Reflection 😱" (0 views) → **private** (terverifikasi read-back). Kembarannya LYjw4nTlwUE (6 views) tetap publik dan metadatanya ikut diperbaiki.
- `7mkgmONd89o` "I Was Dead for 52 Years..." (0 views) → **private** (terverifikasi read-back). Kembarannya u-GqEcijwIk (34 views) tetap publik dan metadatanya ikut diperbaiki.
Tidak ada video yang dihapus.

## InkTime (@InkTime-d3t) — temuan read-only

Resolve ulang dari handle memakai token lima-misteri BERHASIL: channel ID asli **UCoZl5OaqjXSVkE4S96RY8_g** — sama persis dengan yang dipakai scan (playlist uploads UUoZl5OaqjXSVkE4S96RY8_g). Error 404 scan BUKAN karena ID salah: statistik resmi channel menunjukkan **0 subscriber dan 0 video** — channel-nya benar-benar kosong, sehingga playlist uploads-nya tidak ada (itu yang membalas 404). Kesimpulan: **tidak ada video sepi di InkTime karena belum ada video apa pun di channel itu.** Tidak ada penulisan apa pun (memang tidak ada token InkTime).

## Video yang TIDAK diubah (metadata sudah bagus)

- @CosmosUnknownTV `5ijR6apbCps` — "Fast Radio Bursts: Millisecond Screams From Deep Space" (skor audit awal 95/100). Judul/deskripsi/tags sudah memenuhi aturan (hashtag #foryou ada, CTA ada, tags cukup) — mengubahnya lagi tidak menambah peluang dan berisiko merusak yang sudah benar.
- @TrueCaseFilesTV `E4OjHTPQbeU` — "Maura Murray Vanished 19 Minutes After Her Crash" (skor audit awal 95/100). Judul/deskripsi/tags sudah memenuhi aturan (hashtag #foryou ada, CTA ada, tags cukup) — mengubahnya lagi tidak menambah peluang dan berisiko merusak yang sudah benar.
- @BizarreWorldDaily `5hHQlZvoYqk` — "7 Places on Earth That Look Completely FAKE" (skor audit awal 100/100). Judul/deskripsi/tags sudah memenuhi aturan (hashtag #foryou ada, CTA ada, tags cukup) — mengubahnya lagi tidak menambah peluang dan berisiko merusak yang sudah benar.
- @ceritarakyat862 `zafVpCmFduk` — "10.000 Prajurit Kepung Batavia... Aku di Barisan Paling Depan! | POV Prajurit Mataram 1628" (skor audit awal 90/100). Judul/deskripsi/tags sudah memenuhi aturan (hashtag #foryou ada, CTA ada, tags cukup) — mengubahnya lagi tidak menambah peluang dan berisiko merusak yang sudah benar.

## Catatan kejujuran — cacat metadata vs faktor algoritma

- **Yang benar-benar cacat dan sudah diperbaiki:** ekor hashtag Shorts tanpa #foryou (mayoritas daftar), tags kosong/tipis (mis. lima-misteri K8QaZZXVN2Q tags kosong total, mind-en eHDUZyD8oKw tags kosong), deskripsi Shorts tanpa link ke long pasangannya (sekarang 60+ Shorts membawa link youtu.be ke long-nya), deskripsi long tanpa #foryou/CTA.
- **Yang metadatanya sudah lumayan tapi tetap sepi:** 25 dari 132 video skor audit awalnya ≥85 — perubahan pada mereka hanya penyempurnaan kecil. Kesepian kelompok ini (dan video long di channel ber-subscriber 0–20 pada umumnya) terutama faktor **umur channel & belum adanya seed audience**, bukan metadata.
- **Batas perbaikan ini:** mengganti metadata TIDAK menjamin video lama hidup lagi. Shorts yang sudah melewati jendela distribusi awal jarang bangkit hanya karena judul diganti; peluang terbesar justru pada video yang masih private/terjadwal (metadata barunya berlaku sejak tayang pertama) dan pada sinyal search/suggested jangka panjang dari tags + deskripsi yang sekarang lengkap. Perkembangan views-nya perlu dicek lagi 3–7 hari ke depan sebelum menyimpulkan berhasil/gagal.
- Privasi, jadwal, audience, dan setelan komentar semua video TIDAK diubah (satu-satunya pengecualian: 2 duplikat di atas, sesuai instruksi). Link afiliasi/atribusi di deskripsi dipertahankan utuh — perubahan deskripsi bersifat menambah (append), tidak pernah menghapus baris yang sudah ada.
- File pendukung: `hidden_files/perbaikan-sepi-plan.json` (rencana + skor audit awal per video), `hidden_files/perbaikan-sepi-hasil.json` (hasil + verifikasi), skrip `hidden_files/fix_sepi.py`.