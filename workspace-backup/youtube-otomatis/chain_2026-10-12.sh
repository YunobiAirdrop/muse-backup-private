#!/bin/bash
# Rantai penyelesaian POV 2026-10-12: merge polos -> audio final (atempo+bumper) -> rakit -> overlay -> web.
cd /home/hatch/workspace/youtube-otomatis || exit 1
while [ ! -s audio/durasi-beat-2026-10-12.json ] || [ ! -s audio/gabungan-2026-10-12.mp3 ]; do
  if ! pgrep -f "merge_audio_pov_2026-10-12" > /dev/null; then
    python3 merge_audio_pov_2026-10-12.py >> /tmp/merge3-2026-10-12.log 2>&1
  fi
  sleep 20
done
echo "MERGE OK $(date)"
if [ ! -s audio/gabungan-2026-10-12-fast.mp3 ]; then
  cp audio/durasi-beat-2026-10-12.json audio/durasi-beat-2026-10-12-orig.json
  python3 build_fast_audio.py
  echo "FAST rc=$? $(date)"
fi
python3 rakit_light.py gambar/2026-10-12 audio/gabungan-2026-10-12-fast.mp3 video/2026-10-12.mp4 audio/durasi-beat-2026-10-12.json
echo "RAKIT rc=$? $(date)"
python3 overlay_pov_2026-10-12.py video/2026-10-12.mp4 audio/durasi-beat-2026-10-12.json video/2026-10-12-final.mp4
echo "OVERLAY rc=$? $(date)"
./ffmpeg-queue.sh -y -i video/2026-10-12-final.mp4 -c:v libx264 -preset veryfast -crf 28 -c:a aac -b:a 128k -movflags +faststart video/2026-10-12-web.mp4
echo "WEB rc=$? $(date)"
ls -la video/2026-10-12*.mp4
echo "CHAIN SELESAI"
