#!/bin/bash
# Assemble sisa video horor 2026-10-10 lalu tulis retry-queue (ANTI-MOGOK).
# Dijalankan background; selesai otomatis tanpa intervensi.
cd /home/hatch/workspace/horor-otomatis
echo "[$(date)] mulai assembly" >> video/_tmp_segs_20261010/wrapper.log
python3 assembly_20261010.py >> video/_tmp_segs_20261010/wrapper.log 2>&1
RC=$?
echo "[$(date)] assembly rc=$RC" >> video/_tmp_segs_20261010/wrapper.log
if [ $RC -eq 0 ] && [ -f video/2026-10-10-youtube.mp4 ]; then
  DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video/2026-10-10-youtube.mp4)
  echo "[$(date)] video OK durasi=${DUR}s" >> video/_tmp_segs_20261010/wrapper.log
  # Tulis retry-queue JSON untuk watchdog
  cat > /home/hatch/workspace/youtube-otomatis/retry-queue/"Kisah Horor-2026-10-11.json" <<EOF
{"channel":"Kisah Horor","video_path":"/home/hatch/workspace/horor-otomatis/video/2026-10-10-youtube.mp4","instruksi_path":"/home/hatch/workspace/horor-otomatis/upload-instruksi-2026-10-11.md","slot_target":"2026-10-12 19:00 WIB","gagal_pada":"$(date -u +%Y-%m-%dT%H:%M:%S+07:00)","sebab":"Assembly selesai lewat jendela upload 20:00-22:00 WIB (kontensi slot render 19 channel); video siap, menunggu giliran watchdog."}
EOF
  echo "[$(date)] retry-queue ditulis" >> video/_tmp_segs_20261010/wrapper.log
  # Status untuk run horor-harian besok (2026-10-12):
  cat > PENDING-UPLOAD-2026-10-11.txt <<EOF
STATUS: Video LONG 2026-10-10 ("Suster Ngesot di Rumah Sakit Tua") selesai dirakit
$(date) tetapi LEWAT jendela upload 20:00-22:00 WIB (kontensi slot render 19 channel
+ 1x OOM kill + bug frame-multiplication pada batch worker yang sudah diperbaiki).
Masuk retry-queue; watchdog mengerjakan 2026-10-12 20:00 WIB, tayang 2026-10-13 19:00 WIB.
INSTRUKSI UNTUK RUN 2026-10-12: JANGAN produksi konten baru. JANGAN upload shorts
(dari video yang belum tayang). Cukup pastikan video ter-upload via watchdog.
Pola normal (shorts dari video 2026-10-10) dilanjutkan 2026-10-13.
EOF
else
  echo "[$(date)] GAGAL rc=$RC" >> video/_tmp_segs_20261010/wrapper.log
fi
