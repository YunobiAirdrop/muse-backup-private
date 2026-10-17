#!/bin/bash
# Burn 4 text overlay ke video final weird-en
# Usage: overlay_weird.sh <input_mp4> <output_mp4>
set -e
IN="$1"; OUT="$2"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
printf "SURVIVED OUTER SPACE" > /tmp/ov1.txt
printf "BIOLOGICALLY IMMORTAL" > /tmp/ov2.txt
printf "50 MPH PUNCH" > /tmp/ov3.txt
printf "HOTTER THAN THE SUN" > /tmp/ov4.txt
DT="drawtext=fontfile=$FONT:textfile=/tmp/ov1.txt:fontsize=64:fontcolor=white:borderw=3:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=h*0.78:enable='between(t,10.05,12.25)'"
DT="$DT,drawtext=fontfile=$FONT:textfile=/tmp/ov2.txt:fontsize=64:fontcolor=white:borderw=3:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=h*0.78:enable='between(t,150.44,152.64)'"
DT="$DT,drawtext=fontfile=$FONT:textfile=/tmp/ov3.txt:fontsize=64:fontcolor=white:borderw=3:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=h*0.78:enable='between(t,210.72,212.92)'"
DT="$DT,drawtext=fontfile=$FONT:textfile=/tmp/ov4.txt:fontsize=64:fontcolor=white:borderw=3:bordercolor=black:box=1:boxcolor=black@0.6:boxborderw=20:x=(w-text_w)/2:y=h*0.78:enable='between(t,433.05,435.25)'"
/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh -y -i "$IN" -vf "$DT" -c:v libx264 -preset veryfast -crf 20 -c:a copy -movflags +faststart "$OUT"
echo "OK: $OUT"
