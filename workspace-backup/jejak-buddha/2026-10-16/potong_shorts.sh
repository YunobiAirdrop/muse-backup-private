#!/bin/bash
# Potong 3 shorts vertikal 9:16 dari long Jejak Buddha 2026-10-15 ("Pertapaan dan Jalan Tengah")
# Timeline video = beat0(0-120.3) beat1(120.3-182.3) beat2(182.3-245.1) beat3(245.1-304.8)
#                  bumper(~9.3s) beat4(314.0-387.8) beat5(387.8-449.1) beat6(449.1-510.7) beat7(510.7-569.1)
# CTA "Subscribe Jejak Buddha" overlay 3 detik terakhir (aturan wajib user, shorts).
set -e
SRC=/home/hatch/workspace/jejak-buddha/2026-10-15/jejak-buddha-2026-10-15-upload.mp4
D=/home/hatch/workspace/jejak-buddha/2026-10-16
FQ=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
FONT=/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf
mkdir -p "$D"
cut() { # name start
  "$FQ" -y -i "$SRC" -ss "$2" -t 58 \
    -vf "crop=405:720:437:0,scale=1080:1920,drawtext=fontfile=${FONT}:text='Subscribe Jejak Buddha':fontsize=64:fontcolor=white:borderw=4:bordercolor=black@0.85:x=(w-text_w)/2:y=h-260:box=1:boxcolor=black@0.45:boxborderw=24:enable='gte(t,55)',format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k -movflags +faststart "$D/$1.mp4"
  ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$D/$1.mp4"
}
cut short1-enam-tahun 0
cut short2-senar-kecapi 387.84
cut short3-ambang-kematian 245.06
echo "SELESAI"
