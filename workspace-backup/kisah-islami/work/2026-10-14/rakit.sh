#!/bin/bash
# Rakit LONG Jejak Islami 2026-10-14 — Ashabul Kahfi (QS Al-Kahfi 18:9-26)
# Klip: 4 baru (clips/n02,n04,n05,n06) + 12 bank terverifikasi (work/2026-10-11/pexels/uNN)
# Narasi: 486.456 dtk. 22 slot x 23 dtk = 506 dtk.
set -e
W=/home/hatch/workspace/kisah-islami/work/2026-10-14
WB=/home/hatch/workspace/kisah-islami/work/2026-10-11/pexels
FF=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
cd "$W"
mkdir -p segs

FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
VF="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,eq=contrast=1.05:saturation=0.95,noise=alls=7:allf=t,format=yuv420p"

build() { # slot src dur [ssoffset]
  local slot="$1" src="$2" dur="$3" sso="${4:-0}"
  if [ -s "$W/segs/p$slot.mp4" ]; then echo "SKIP p$slot"; return; fi
  if [ "$sso" != "0" ]; then
    $FF -hide_banner -loglevel error -ss "$sso" -i "$src" -t "$dur" -vf "$VF" \
      -c:v libx264 -preset veryfast -crf 20 -an -y "$W/segs/p$slot.mp4"
  else
    $FF -hide_banner -loglevel error -stream_loop -1 -i "$src" -t "$dur" -vf "$VF" \
      -c:v libx264 -preset veryfast -crf 20 -an -y "$W/segs/p$slot.mp4"
  fi
  echo "OK p$slot ($dur s)"
}

C=$W/clips
build 01 $C/n02.mp4 23
build 02 $WB/u05.mp4 23
build 03 $C/n04.mp4 23
build 04 $C/n04.mp4 23
build 05 $WB/u03.mp4 23
build 06 $C/n06.mp4 23 18
build 07 $WB/u07.mp4 23
build 08 $C/n02.mp4 23
build 09 $C/n05.mp4 23
build 10 $WB/u09.mp4 23
build 11 $WB/u04.mp4 23
build 12 $WB/u12.mp4 23
build 13 $WB/u13.mp4 23
build 14 $WB/u08.mp4 23
build 15 $WB/u10.mp4 23
build 16 $WB/u17.mp4 23
build 17 $WB/u05.mp4 23
build 18 $WB/u03.mp4 23
build 19 $C/n05.mp4 23
build 20 $WB/u19.mp4 23
build 21 $WB/u20.mp4 23
build 22 $WB/u04.mp4 23
echo "--- semua segmen selesai ---"

rm -f "$W/concat.txt"
for n in $(seq -w 1 22); do
  echo "file '$W/segs/p$n.mp4'" >> "$W/concat.txt"
done
$FF -hide_banner -loglevel error -f concat -safe 0 -i "$W/concat.txt" -c copy -y "$W/dasar.mp4"
echo "--- concat selesai ---"

DUR_DASAR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/dasar.mp4")
DUR_NAR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/audio/narration-full.mp3")
echo "durasi dasar=$DUR_DASAR narasi=$DUR_NAR"
python3 - "$DUR_DASAR" "$DUR_NAR" <<'EOF'
import sys
d, n = float(sys.argv[1]), float(sys.argv[2])
assert d >= n - 2, f"dasar ({d}) lebih pendek dari narasi ({n}) — STOP"
print("durasi dasar OK")
EOF

DT1="drawtext=fontfile=$FONT:text='TIDUR 309 TAHUN, LALU BANGUN':fontsize=64:fontcolor=#FFD700:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=120:enable='between(t,0,5)'"
DT2="drawtext=fontfile=$FONT:text='KOTA AFSUS DI BAWAH RAJA DAKYANUS':fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-150:enable='between(t,67,72)'"
DT3="drawtext=fontfile=$FONT:text='DOA PARA PEMUDA \\: QS AL-KAHFI 10':fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-150:enable='between(t,183,188)'"
DT4="drawtext=fontfile=$FONT:text='309 TAHUN DALAM GUA \\: QS AL-KAHFI 25':fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-150:enable='between(t,222,227)'"
DT5="drawtext=fontfile=$FONT:text='SUBSCRIBE!':fontsize=72:fontcolor=#FFD700:borderw=4:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-220:enable='between(t,284,287)'"
DT6="drawtext=fontfile=$FONT:text='SEHARI ATAU SETENGAH HARI? \\: QS AL-KAHFI 19':fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-150:enable='between(t,294,299)'"
DT7="drawtext=fontfile=$FONT:text='RUMAH IBADAH DI ATAS GUA \\: QS AL-KAHFI 21':fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h-150:enable='between(t,364,369)'"

TMP="$W/jejak-islami-2026-10-14-long-TMP.mp4"
FINAL="$W/jejak-islami-2026-10-14-long.mp4"
$FF -hide_banner -loglevel error -i "$W/dasar.mp4" -i "$W/audio/narration-full.mp3" \
  -vf "$DT1,$DT2,$DT3,$DT4,$DT5,$DT6,$DT7" -map 0:v -map 1:a \
  -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k -movflags +faststart -shortest \
  -y "$TMP"
echo "--- mux selesai ---"

DUR_OUT=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP")
python3 - "$DUR_OUT" "$DUR_NAR" <<'EOF'
import sys
d, n = float(sys.argv[1]), float(sys.argv[2])
assert abs(d - n) < 5, f"durasi final ({d}) != narasi ({n}) — JANGAN TIMPA, simpan TMP untuk diagnosa"
print(f"durasi final OK: {d}s")
EOF
mv "$TMP" "$FINAL"
echo "FINAL: $FINAL"

$FF -hide_banner -loglevel error -ss 40 -i "$C/n05.mp4" -frames:v 1 \
  -vf "scale=1280:720,drawtext=fontfile=$FONT:text='TUJUH PEMUDA BANGUN':fontsize=92:fontcolor=#FFD700:borderw=5:bordercolor=black@0.9:shadowcolor=black@0.8:shadowx=4:shadowy=4:x=(w-text_w)/2:y=80" \
  -y "$W/thumbnail.jpg"
echo "--- thumbnail selesai ---"
ls -la "$FINAL" "$W/thumbnail.jpg"
echo "SELESAI"
