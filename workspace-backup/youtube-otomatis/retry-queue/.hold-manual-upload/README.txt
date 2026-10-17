HOLD — cegah duplikat upload video perdana Macam Macam (2026-10-10 ~18:30 UTC)

File macammacam-2026-10-10-truk-part1.json dipindah ke sini (dari retry-queue/)
karena DUA jalur upload aktif untuk video yang sama:
  1. User pegang paket upload-ready untuk upload MANUAL (disetujui "nah udah oke" 2026-10-10 ~11:20 WIB)
  2. Antrean retry watchdog (eligible 2026-10-11T01:11Z, run 2026-10-11T13:00Z)
Browser check 2026-10-10T18:27Z: channel @MacamMacamID BELUM ada konten -> video belum terbit.

CARA MELEPAS HOLD (pilih satu):
- User konfirmasi SUDAH upload manual -> pindahkan JSON ke retry-queue/done/
- User konfirmasi BELUM upload / tidak menjawab -> pindahkan JSON kembali ke retry-queue/
  (watchdog akan mencoba upload besok 20:00 WIB seperti biasa)
Watchdog hanya membaca retry-queue/*.json, jadi file di sini aman dari proses otomatis.

[2026-10-11 ~13:35 WIB — HOLD SUPERSEDED, JANGAN dilepas]
User konfirmasi 2026-10-11: upload manual GAGAL (limit akun baru), salinan HP sudah dihapus.
Entri retry aktif: retry-queue/macammacam-2026-10-10-perdana.json (gagal_pada diperbaiki ke
2026-10-10T02:12:07+00:00; video master truk-part1.mp4 utuh 16,4 MB) — watchdog 20:00 WIB
akan mengerjakannya. File hold di folder ini SUDAH TIDAK BERLAKU; JANGAN pindahkan kembali
ke retry-queue/ (akan menyebabkan duplikat upload). Hapus file ini setelah upload perdana sukses.
