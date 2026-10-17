#!/bin/bash
# Rakit video loker TikTok: gambar + zoompan + teks overlay + VO + film grain, vertical 9:16
set -e
OUT=~/workspace/tiktok-shop-affiliate/output
IMG="$OUT/media-generation-loker-p2mi-20261011-0-1dbaac86-b85e-430d-9603-5d167b7fe9df.webp"
VO="$OUT/loker-p2mi-20261011-vo.mp3"
VOF="$OUT/loker-p2mi-20261011-vo-fast.mp3"
FINAL="$OUT/loker-lowongan-kerja-luar-negeri-p2mi-2026-20261011.mp4"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf

# Percepat VO 10% supaya muat 25-40 detik
~/workspace/youtube-otomatis/ffmpeg-queue.sh -y -v error -i "$VO" -filter:a "atempo=1.10" "$VOF"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VOF")
echo "VO duration: $DUR"
FRAMES=$(python3 -c "print(int($DUR*30))")
END=$(python3 -c "print(round($DUR,2))")
T_LINK=$(python3 -c "print(round($DUR-3,2))")
T_SCAM1=$(python3 -c "print(round($DUR-14.5,2))")
T_SCAM2=$(python3 -c "print(round($DUR-9.5,2))")

~/workspace/youtube-otomatis/ffmpeg-queue.sh -y -v error \
 -loop 1 -framerate 30 -i "$IMG" -i "$VOF" \
 -filter_complex "\
[0:v]scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,\
zoompan=z='min(zoom+0.0012\,1.25)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,\
noise=alls=8:allf=t,\
drawtext=fontfile=$FONT:text='73 PERSEN POSISI':fontsize=80:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=460:enable='between(t\,0\,4.5)',\
drawtext=fontfile=$FONT:text='MASIH KOSONG!':fontsize=80:fontcolor=yellow:borderw=4:bordercolor=black:x=(w-text_w)/2:y=580:enable='between(t\,0\,4.5)',\
drawtext=fontfile=$FONT:text='KERJA LUAR NEGERI 2026':fontsize=78:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=520:enable='between(t\,4.5\,11)',\
drawtext=fontfile=$FONT:text='RESMI KEMENTERIAN P2MI':fontsize=52:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=640:enable='between(t\,4.5\,11)',\
drawtext=fontfile=$FONT:text='SYARAT\: SMA ATAU SEDERAJAT':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=520:enable='between(t\,11\,17.5)',\
drawtext=fontfile=$FONT:text='BISA BAHASA ASING':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=620:enable='between(t\,11\,17.5)',\
drawtext=fontfile=$FONT:text='WASPADA PENIPUAN!':fontsize=80:fontcolor=red:borderw=4:bordercolor=white:x=(w-text_w)/2:y=500:enable='between(t\,$T_SCAM1\,$T_SCAM2)',\
drawtext=fontfile=$FONT:text='JALUR RESMI TIDAK MINTA UANG':fontsize=48:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=620:enable='between(t\,$T_SCAM1\,$T_SCAM2)',\
drawtext=fontfile=$FONT:text='LINK DI BIO':fontsize=120:fontcolor=yellow:borderw=5:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2-60:enable='gte(t\,$T_LINK)',\
drawtext=fontfile=$FONT:text='KOMEN DOMISILI KAMU!':fontsize=56:fontcolor=white:borderw=3:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2+90:enable='gte(t\,$T_LINK)'[v]" \
 -map "[v]" -map 1:a -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k \
 -t "$DUR" -movflags +faststart -shortest "$FINAL"
echo "FINAL: $FINAL"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$FINAL"
