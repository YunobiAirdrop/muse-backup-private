#!/bin/bash
# Finisher: tunggu assembly_20261013.py selesai -> verifikasi output -> upload API -> bookkeeping.
# Dijalankan background oleh run horor-harian 2026-10-14; idempoten & aman diulang.
BASE=/home/hatch/workspace/horor-otomatis
S3=$BASE/shorts/2026-10-13-s3.mp4
VYT=$BASE/video/2026-10-13-youtube.mp4
LOG=$BASE/finisher-2026-10-14.log
VENV=/home/hatch/workspace/youtube-otomatis/yt-growth/venv/bin/python
t(){ date '+%H:%M:%S'; }

echo "[$(t)] finisher mulai, menunggu s3.mp4" >> $LOG
for i in $(seq 1 150); do
  [ -f "$S3" ] && break
  sleep 120
done
if [ ! -f "$S3" ]; then echo "[$(t)] GAGAL: s3.mp4 tak muncul 5 jam" >> $LOG; exit 1; fi
echo "[$(t)] s3.mp4 ada" >> $LOG

# verifikasi durasi video final ~703 dtk
DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VYT" 2>/dev/null | cut -d. -f1)
echo "[$(t)] durasi VYT=${DUR}s" >> $LOG
if [ -z "$DUR" ] || [ "$DUR" -lt 690 ] || [ "$DUR" -gt 716 ]; then
  echo "[$(t)] GAGAL: durasi video final abnormal ($DUR)" >> $LOG; exit 2
fi
# verifikasi 3 shorts ~45 dtk
for n in s1 s2 s3; do
  SD=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$BASE/shorts/2026-10-13-$n.mp4" 2>/dev/null | cut -d. -f1)
  [ "$SD" -ge 40 ] && [ "$SD" -le 50 ] || { echo "[$(t)] GAGAL: shorts $n durasi $SD" >> $LOG; exit 3; }
done
echo "[$(t)] verifikasi OK, upload API..." >> $LOG

$VENV $BASE/upload_api_20261013.py >> $LOG 2>&1
RC=$?
echo "[$(t)] upload rc=$RC" >> $LOG
if [ $RC -eq 0 ] && [ -f $BASE/upload-hasil-2026-10-13.json ]; then
  echo "long:2026-10-13" > $BASE/upload-terakhir.txt
  echo "[$(t)] upload-terakhir.txt -> long:2026-10-13" >> $LOG
  VID=$(python3 -c "import json;print(json.load(open('$BASE/upload-hasil-2026-10-13.json'))['url'])")
  echo "[$(t)] SELESAI: $VID" >> $LOG
  exit 0
fi
echo "[$(t)] upload GAGAL rc=$RC (lihat log)" >> $LOG
exit 4
