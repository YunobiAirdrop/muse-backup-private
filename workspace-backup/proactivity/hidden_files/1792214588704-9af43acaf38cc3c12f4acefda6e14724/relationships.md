## [source:43] /home/hatch/memory/people/jub0t.md

Updated by relationships at 2026-10-17T03:09:39.607752Z

Original: /home/hatch/memory/people/jub0t.md

# Jareer (jub0t)

## Facts
- Handle GitHub "jub0t"; nama "Jareer" tercatat sebagai nama pembuat asli di kode aplikasi Concat (memory://md:memory/2026-10-15.md:1075).
- Pembuat aplikasi open-source "Concat" (repo github.com/jub0t/concat, lisensi AGPL-3.0) yang di-fork user menjadi "Yunobi Cipcat" (message:d3bfdc2f-da75-8795-ad8e-ffd3bc58c947; memory://md:memory/2026-10-15.md:1029).
- User menyebutnya sebagai temannya: "pemilik aslinya juga temen saya" (message:1b4da532-f871-8e9a-b962-ce792b8e617c).

## History
- 2026-10-15: user meminta asisten menyalin repo jub0t/concat, mengganti namanya menjadi "Yunobi Cipcat", dan memasukkannya ke GitHub miliknya (YunobiAirdrop/yunobi-cipcat). User menyatakan sudah meminta izin darinya untuk mengganti seluruh nama dan atribusi ke atas namanya, termasuk menghapus nama pembuat asli (message:8c897899-17a6-8b6e-871e-13b050e03f61; memory://md:memory/2026-10-15.md:1059).
- 2026-10-16: user meminta asisten membuat APK Android dari repo Yunobi Cipcat ("oiya cara membuat apk dari repo yang kita buat gimna"; message:f8499ad3-40d6-8e48-b9c2-6158b41c637f). User mengklarifikasi yang dimaksud adalah repo Yunobi Cipcat, bukan dashboard PWA ("bukan yang itu, yang satu lagi yang yunobi cipcat"; message:22eaf9a1-94a9-8d93-9c43-dcf68211251d). Asisten memulai setup toolchain Rust + Android SDK + Java di background (estimasi 15–20 menit); saat jendela berakhir SDK masih diunduh (±1,5 GB, NDK paling besar) dan build belum selesai (message:assistant-msg-6ce291f5-ae48-424c-bd64-1bda5ebf79d3; message:assistant-msg-d96e4846-c80e-48d4-966e-499fc4773543).
- 2026-10-16 pagi: user menanyakan hasil build APK-nya ("mana hasil build apk nya?"; message:10f45144-46aa-8c8c-9c18-e53877687a16). Per 2026-10-17 pagi build masih belum selesai — build-tools Android SDK terhapus saat restart dan sedang diunduh ulang sebelum build dimulai (message:assistant-msg-75a75a3c-e2d0-4470-bc07-e6b2b2926d6e).
- 2026-10-17: user memerintahkan menghentikan build APK Yunobi Cipcat dan menghapus semua yang diunduh ("hentikan build apknya dan hapus semua yang di download tadi"; message:e47fd2b7-1782-8d89-a541-78d90fe3485b); asisten menghentikan build dan menghapus Android SDK, NDK, JDK, dan Rust (message:assistant-msg-eb0c78cd-22ca-458c-86f0-3cd4bbc6b4f6). Karena build lokal sempat macet, asisten mengunduh APK resmi Concat 0.2.7 (69 MB, SHA256 terverifikasi) sebagai cadangan — versi asli dari Jareer, bukan fork Yunobi Cipcat (message:assistant-msg-b771fe2a-c617-4e31-b419-af233bdf7c36; message:assistant-msg-16e90250-a700-4571-bddd-b67f042d1714). User bertanya apakah APK bisa dipasang di server untuk edit video semua channel (message:6fa15405-a59f-4c05-a4fc-7f107890744b); dijawab tidak bisa dan tidak perlu — server tanpa KVM/virtualisasi dengan RAM sisa ~1 GB, dan pipeline editing sudah berjalan dengan ffmpeg (message:assistant-msg-318ea45f-64bc-47b3-be41-bed8847dbb18). User memutuskan proyek tidak dilanjutkan dan fokus ke yang sudah jalan ("jangan di lanjut, pokus ke project kita aja yang udah jalan"; message:51189a7b-1a9c-8646-a67c-bbf27ae42a31).

## The relationship
- Menurut ucapan user sendiri, Jareer adalah temannya ("temen saya").
- Satu-satunya interaksi yang tercatat adalah klaim user bahwa Jareer memberi izin penuh untuk me-rebrand Concat menjadi Yunobi Cipcat; klaim izin tersebut belum terverifikasi secara independen dan dicatat sebagai pernyataan user, bukan fakta terkonfirmasi.
- Tidak ada riwayat pertemuan, kontak langsung, atau kolaborasi lain di memori.

## In common
- Keduanya berkecimpung di aplikasi desktop open-source — Jareer sebagai pembuat Concat, user sebagai penerus fork Yunobi Cipcat.

## Open threads
- [x] Hasil build APK Yunobi Cipcat — DIBATALKAN user 2026-10-17: user memerintahkan hentikan build dan hapus semua toolchain yang diunduh, lalu memutuskan "jangan di lanjut, pokus ke project kita aja yang udah jalan" (message:e47fd2b7-1782-8d89-a541-78d90fe3485b; message:51189a7b-1a9c-8646-a67c-bbf27ae42a31).

## Strengthening


