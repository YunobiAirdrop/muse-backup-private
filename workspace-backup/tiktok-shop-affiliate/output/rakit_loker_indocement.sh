#!/bin/bash
# Rakit video loker TikTok Indocement MT: gambar + zoompan + teks overlay + VO + film grain, vertical 9:16
set -e
OUT=~/workspace/tiktok-shop-affiliate/output
IMG="$OUT/media-generation-loker-indocement-20261012-0-b7f683a5-6f50-4693-8368-6811999a09ba.webp"
VO="$OUT/loker-indocement-20261012-vo2.mp3"
VOF="$OUT/loker-indocement-20261012-vo-fast.mp3"
FINAL="$OUT/loker-lowongan-kerja-management-trainee-indocement-2026-20261012.mp4"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

~/workspace/youtube-otomatis/ffmpeg-queue.sh -y -v error -i "$VO" -filter:a "atempo=1.15" "$VOF"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VOF")
echo "VO duration: $DUR"
T2=$(python3 -c "print(round($DUR*0.14,2))")
T3=$(python3 -c "print(round($DUR*0.34,2))")
T4=$(python3 -c "print(round($DUR*0.62,2))")
T_SCAM2=$(python3 -c "print(round($DUR-3,2))")
T_LINK=$(python3 -c "print(round($DUR-3,2))")

~/workspace/youtube-otomatis/ffmpeg-queue.sh -y -v error \
 -loop 1 -framerate 30 -i "$IMG" -i "$VOF" \
 -filter_complex "\
[0:v]scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,\
zoompan=z='min(zoom+0.0012\,1.25)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,\
noise=alls=8:allf=t,\
drawtext=fontfile=$FONT:text='MANAGEMENT TRAINEE':fontsize=76:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=420:enable='between(t\,0\,$T2)',\
drawtext=fontfile=$FONT:text='INDOCEMENT DIBUKA!':fontsize=80:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=540:enable='between(t\,0\,$T2)',\
drawtext=fontfile=$FONT:text='LOKER INDOCEMENT 2026':fontsize=70:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=460:enable='between(t\,$T2\,$T3)',\
drawtext=fontfile=$FONT:text='FRESH GRADUATE BISA DAFTAR':fontsize=52:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=580:enable='between(t\,$T2\,$T3)',\
drawtext=fontfile=$FONT:text='SYARAT\\: LULUSAN S1':fontsize=60:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=460:enable='between(t\,$T3\,$T4)',\
drawtext=fontfile=$FONT:text='INGGRIS JADI NILAI PLUS':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=570:enable='between(t\,$T3\,$T4)',\
drawtext=fontfile=$FONT:text='WASPADA PENIPUAN!':fontsize=80:fontcolor=red:borderw=4:bordercolor=white:x=(w-text_w)/2:y=460:enable='between(t\,$T4\,$T_SCAM2)',\
drawtext=fontfile=$FONT:text='RESMI TIDAK MINTA UANG':fontsize=50:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=580:enable='between(t\,$T4\,$T_SCAM2)',\
drawtext=fontfile=$FONT:text='LINK DI BIO':fontsize=120:fontcolor=yellow:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-60:enable='gte(t\,$T_LINK)',\
drawtext=fontfile=$FONT:text='KOMEN DOMISILI KAMU!':fontsize=56:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+90:enable='gte(t\,$T_LINK)'[v]" \
 -map "[v]" -map 1:a -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k \
 -t "$DUR" -movflags +faststart -shortest "$FINAL"
echo "FINAL: $FINAL"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$FINAL"
