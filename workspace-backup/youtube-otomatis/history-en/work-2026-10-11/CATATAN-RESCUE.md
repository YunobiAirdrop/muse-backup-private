CATATAN (worker rescue history-en, 2026-10-12 ~13:05 UTC):
- rakit_singlepass_2026-10-11.py (72 input ffmpeg) TERBUKTI DEADLOCK: 2x kejadian sama (CPU berhenti ~0:13-0:19, output berhenti di 3,1MB, 149 thread futex-wait). JANGAN dijalankan lagi.
- Jalur yang DIPAKAI: rakit_3step_2026-10-11.py (langkah B video silent dari imglist work-2026-10-11/imglist.txt) + audio gabungan dari build_chunks.py (chunk concat-filter, hasil gabungan-final-2026-10-11.mp3). Mux final manual setelah B selesai.
- Rerun single-pass 12:26 UTC dihentikan worker ini karena deadlock yang sama dan menahan 1 slot ffmpeg.
