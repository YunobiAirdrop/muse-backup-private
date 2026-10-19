#!/bin/bash
# Potong 3 shorts vertikal 9:16 dari long Jejak Buddha 2026-10-18 ("Pencerahan di bawah pohon Bodhi")
# Timeline (dari rakit.py 2026-10-18):
#   beat0 0-59.81 (cold open serangan Mara)
#   beat2 98.14-152.67 (Mara + bhumisparsha)
#   beat3 152.67-201.51 (tiga jaga malam)
# CTA "Subscribe Jejak Buddha" overlay 3 detik terakhir (aturan wajib user, shorts).
set -e
SRC=/home/hatch/workspace/jejak-buddha/2026-10-18/jejak-buddha-2026-10-18-upload.mp4
D=/home/hatch/workspace/jejak-buddha/2026-10-19
FQ=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
FONT=/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf
mkdir -p "$D"
cut() { # name start dur cta_at
  echo "CUT $1 @ $2 dur $3" >&2
  "$FQ" -y -i "$SRC" -ss "$2" -t "$3" \
    -vf "crop=405:720:437:0,scale=1080:1920,drawtext=fontfile=${FONT}:text='Subscribe Jejak Buddha':fontsize=64:fontcolor=white:borderw=4:bordercolor=black@0.85:x=(w-text_w)/2:y=h-260:box=1:boxcolor=black@0.45:boxborderw=24:enable='gte(t,$4)',format=yuv420p" \
    -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k -movflags +faststart "$D/$1.mp4"
  ffprobe -v error -show_entries stream=width,height -show_entries format=duration -of default=noprint_wrappers=1 "$D/$1.mp4" | grep -E "width|height|duration"
}
cut short1-serangan-mara 0 59.8 56.8
cut short2-bhumisparsha 98.14 54.5 51.5
cut short3-tiga-jaga 152.67 48.8 45.8
echo "SELESAI"
