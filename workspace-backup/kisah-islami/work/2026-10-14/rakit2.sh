#!/bin/bash
# Rakit LONG Jejak Islami 2026-10-15 — Ashabul Kahfi (QS Al-Kahfi 18:9-26)
# Melanjutkan run 2026-10-14 yang macet di assembly (narasi + klip sudah siap).
# Klip: 1 baru terverifikasi (c01 gua, CC BY) + 13 bank Commons terverifikasi (uNN).
# n04 DITOLAK (turis berpakaian tidak sopan); n01/n02/n05/n06 DITOLAK (lisensi tak terlacak).
# Narasi: 486.456 dtk. 22 slot x 23 dtk = 506 dtk -> final di-shortest ke narasi.
set -e
W=/home/hatch/workspace/kisah-islami/work/2026-10-14
WB=/home/hatch/workspace/kisah-islami/work/2026-10-11/pexels
FF=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
cd "$W"
mkdir -p segs

FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
VF="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,eq=contrast=1.05:saturation=0.95,noise=alls=7:allf=t,format=yuv420p"

build() { # slot src dur [ssoffset]
  # Loop TERBATAS (bukan -1): -stream_loop tak terbatas pernah bikin ffmpeg hang ~30 mnt
  # setelah output selesai (kasus p12, 2026-10-15). Loop hanya bila sumber < durasi target.
  local slot="$1" src="$2" dur="$3" sso="${4:-0}"
  if [ -s "$W/segs/p$slot.mp4" ]; then echo "SKIP p$slot"; return; fi
  if [ "$sso" != "0" ]; then
    $FF -hide_banner -loglevel error -ss "$sso" -i "$src" -t "$dur" -vf "$VF" \
      -c:v libx264 -preset veryfast -crf 20 -an -y "$W/segs/p$slot.mp4"
  else
    local srcdur loopopt=""
    srcdur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$src" 2>/dev/null || echo "$dur")
    local loops=$(python3 -c "import math; sd=max(float('$srcdur'),0.1); print(max(0, math.ceil($dur/sd)-1))" 2>/dev/null || echo 0)
    [ "$loops" -gt 0 ] && loopopt="-stream_loop $loops"
    $FF -hide_banner -loglevel error $loopopt -i "$src" -t "$dur" -vf "$VF" \
      -c:v libx264 -preset veryfast -crf 20 -an -y "$W/segs/p$slot.mp4"
  fi
  echo "OK p$slot ($dur s)"
}

C=$W/clips
build 01 $C/c01.webm 23 5
build 02 $WB/u13.mp4 23
build 03 $WB/u03.mp4 23
build 04 $WB/u10.mp4 23
build 05 $WB/u07.mp4 23
build 06 $WB/u08.mp4 23
build 07 $C/c01.webm 23 28
build 08 $WB/u17.mp4 23
build 09 $WB/u12.mp4 23

echo "--- concat (11 segmen x2, urutan beda — anti-macet: klip boleh dipakai 2x) ---"
: > concat-list2.txt
for f in p01 p02 p03 p04 p05 p06 p07 p08 p09 p12 p13 p08 p05 p02 p13 p09 p06 p03 p12 p07 p04 p01; do
  echo "file '$W/segs/$f.mp4'" >> concat-list2.txt
done
$FF -hide_banner -loglevel error -f concat -safe 0 -i concat-list2.txt -c copy -y vconcat2.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 vconcat2.mp4

echo "--- final: overlay teks + narasi ---"
DT1="drawtext=fontfile=$FONT:text='ASHABUL KAHFI':fontsize=76:fontcolor=white:borderw=3:bordercolor=black@0.9:shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=(h-text_h)/2-40:enable='between(t,3,11)'"
DT1B="drawtext=fontfile=$FONT:text='Tujuh Pemuda Penghuni Gua':fontsize=44:fontcolor=#FFD700:borderw=2:bordercolor=black@0.9:x=(w-text_w)/2:y=(h-text_h)/2+60:enable='between(t,3,11)'"
DT2="drawtext=fontfile=$FONT:text='QITHMIR - Anjing yang Setia':fontsize=50:fontcolor=white:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=h-140:enable='between(t,170,178)'"
DT3="drawtext=fontfile=$FONT:text='TERTIDUR 309 TAHUN':fontsize=64:fontcolor=#FFD700:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,218,227)'"
DT4="drawtext=fontfile=$FONT:text='IMAN TIDAK MENGENAL USIA':fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=h-140:enable='between(t,380,388)'"
DT5="drawtext=fontfile=$FONT:text='QS AL-KAHFI 18\:9-26':fontsize=50:fontcolor=white:borderw=3:bordercolor=black@0.9:x=(w-text_w)/2:y=h-140:enable='between(t,448,456)'"
CTA1="drawtext=fontfile=$FONT:text='SUBSCRIBE UNTUK KISAH HIKMAH LAINNYA':fontsize=44:fontcolor=white:borderw=2:bordercolor=black@0.9:x=(w-text_w)/2:y=90:enable='between(t,243,249)'"
CTA2="drawtext=fontfile=$FONT:text='SUBSCRIBE - SAMPAI JUMPA DI KISAH BERIKUTNYA':fontsize=40:fontcolor=white:borderw=2:bordercolor=black@0.9:x=(w-text_w)/2:y=90:enable='between(t,480,486)'"

$FF -hide_banner -loglevel error -i vconcat2.mp4 -i audio/narration-full.mp3 \
  -vf "$DT1,$DT1B,$DT2,$DT3,$DT4,$DT5,$CTA1,$CTA2" \
  -af "afade=t=out:st=481:d=5" \
  -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 128k -shortest \
  -y jejak-islami-2026-10-15-long-TEMP.mp4

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 jejak-islami-2026-10-15-long-TEMP.mp4)
echo "durasi final: $DUR (narasi 486.456)"
python3 -c "
d=float('$DUR'); assert abs(d-486.456)<5, f'durasi menyimpang: {d}'
print('DURASI OK')
"
mv jejak-islami-2026-10-15-long-TEMP.mp4 jejak-islami-2026-10-15-long.mp4
echo "--- FINAL OK: jejak-islami-2026-10-15-long.mp4 ---"

echo "--- thumbnail ---"
$FF -hide_banner -loglevel error -y -ss 30 -i $C/c01.webm -frames:v 1 \
  -vf "scale=1280:720,drawtext=fontfile=$FONT:text='TIDUR 309 TAHUN':fontsize=110:fontcolor=#FFD700:borderw=6:bordercolor=black@0.9:shadowcolor=black@0.8:shadowx=5:shadowy=5:x=(w-text_w)/2:y=90" \
  thumbnail-2026-10-15.jpg
echo "--- thumbnail OK ---"
