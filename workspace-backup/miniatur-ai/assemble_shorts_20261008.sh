#!/bin/bash
# Rakit 3 shorts Tiny Builders 2026-10-08: loop seamless + film grain + SFX asli
# WAJIB: pakai ffmpeg-queue.sh (limit konkuren, anti-OOM)
set -e
D=~/workspace/miniatur-ai
SFX=$D/sfx-real
IN=$D/shorts-2026-10-08
OUT=$D/shorts-2026-10-08/final
FF=~/workspace/youtube-otomatis/ffmpeg-queue.sh
mkdir -p "$OUT"

C1=$(ls $IN/media-generation-tiny-builders-short1-2026-10-0-0-*.mp4)
C2=$(ls $IN/media-generation-tiny-builders-short2-2026-10-0-0-*.mp4)
C3=$(ls $IN/media-generation-tiny-builders-short3-2026-10-0-0-*.mp4)

# Short 1: sumur bata (40s = 4x loop)
$FF -y -stream_loop 3 -i "$C1" -i $SFX/brick-place-1.mp3 -i $SFX/brick-place-2.mp3 -i $SFX/brick-place-3.mp3 -i $SFX/water-splash-1.mp3 \
 -filter_complex "[0:v]noise=alls=8:allf=t[v];[1:a]adelay=4000|4000[a1];[2:a]adelay=9000|9000[a2];[3:a]adelay=13000|13000[a3];[4:a]adelay=33500|33500,volume=0.9[a4];[a1][a2][a3][a4]amix=inputs=4:normalize=0[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -c:a aac -t 40 "$OUT/tb-short1-2026-10-08.mp4"

# Short 2: pompa bambu (50s = 5x loop), trickle bed + gush
$FF -y -stream_loop 4 -i "$C2" -i $SFX/water-trickle.mp3 -i $SFX/water-gush.mp3 \
 -filter_complex "[0:v]noise=alls=8:allf=t[v];[1:a]atrim=0:50,volume=0.12[bed];[2:a]atrim=0:12,adelay=24000|24000,volume=0.9[g];[bed][g]amix=inputs=2:normalize=0[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -c:a aac -t 50 "$OUT/tb-short2-2026-10-08.mp4"

# Short 3: bendungan mini (30s = 3x loop)
$FF -y -stream_loop 2 -i "$C3" -i $SFX/shovel-dig-1.mp3 -i $SFX/shovel-dig-2.mp3 -i $SFX/water-gush.mp3 \
 -filter_complex "[0:v]noise=alls=8:allf=t[v];[1:a]atrim=0:10,adelay=3000|3000[d1];[2:a]adelay=8000|8000,volume=0.8[d2];[3:a]atrim=0:10,adelay=18000|18000,volume=0.9[g];[d1][d2][g]amix=inputs=3:normalize=0[a]" \
 -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -c:a aac -t 30 "$OUT/tb-short3-2026-10-08.mp4"

echo OK
