#!/bin/bash
# Batch5 audit pipeline: download full video, frames per 10s, contact sheets, keyframes, subs, audio analysis
set -u
D=~/workspace/youtube-otomatis/hidden_files/audit-2026-10-20/batch5
cd "$D"
YTDLP=~/.local/bin/yt-dlp

download_one() {
  local slug="$1" vid="$2"
  local out="${slug}__${vid}.mp4"
  [ -f "$out" ] && { echo "SKIP exists $out"; return 0; }
  local ok=0
  for attempt in 1 2; do
    if $YTDLP -q --no-warnings --extractor-args "youtube:player_client=android" --no-playlist \
        -f "b[height<=480]/b" --merge-output-format mp4 \
        -o "${slug}__${vid}.mp4" "https://www.youtube.com/watch?v=${vid}" 2>>dl_errors.log; then
      ok=1; break
    fi
    echo "retry $vid attempt $attempt" >> dl_errors.log
    sleep 5
  done
  if [ $ok -eq 0 ]; then
    echo "GAGAL_DOWNLOAD: $slug $vid" >> dl_errors.log
    echo "$vid" >> gagal_download.txt
  fi
}

frames_one() {
  local slug="$1" vid="$2"
  local f="${slug}__${vid}.mp4"
  [ -f "$f" ] || { echo "no file $f"; return 1; }
  mkdir -p "fr_${vid}"
  if [ ! -f "fr_${vid}/f0001.jpg" ]; then
    ffmpeg -y -v error -i "$f" -vf "fps=1/10,scale=320:-1" "fr_${vid}/f%04d.jpg" 2>>dl_errors.log
  fi
  python3 - "$vid" <<'EOF'
import glob, os, sys
from PIL import Image
vid = sys.argv[1]
files = sorted(glob.glob(f"fr_{vid}/f*.jpg"))
if not files:
    print(f"no frames {vid}"); sys.exit(0)
w,h = Image.open(files[0]).size
cols, rows = 4, 3
per = cols*rows
for si in range((len(files)+per-1)//per):
    sheet = Image.new("RGB",(w*cols,h*rows),(0,0,0))
    batch = files[si*per:(si+1)*per]
    for i,p in enumerate(batch):
        im = Image.open(p)
        sheet.paste(im,((i%cols)*w,(i//cols)*h))
    sheet.save(f"sheet_{vid}_{si:02d}.jpg", quality=80)
print(f"sheets {vid}: {(len(files)+per-1)//per} from {len(files)} frames")
EOF
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f" 2>/dev/null | cut -d. -f1)
  mid=$((dur/2)); end=$((dur-3))
  ffmpeg -y -v error -ss 1 -i "$f" -frames:v 1 "key_${vid}_awal.jpg" 2>/dev/null
  ffmpeg -y -v error -ss "$mid" -i "$f" -frames:v 1 "key_${vid}_tengah.jpg" 2>/dev/null
  ffmpeg -y -v error -ss "$end" -i "$f" -frames:v 1 "key_${vid}_akhir.jpg" 2>/dev/null
}

subs_one() {
  local slug="$1" vid="$2"
  local base="${slug}__${vid}"
  ls "${base}".*.vtt >/dev/null 2>&1 && return 0
  $YTDLP -q --no-warnings --extractor-args "youtube:player_client=android" \
    --write-auto-subs --write-subs --sub-langs "en,id" --sub-format vtt --skip-download \
    -o "${base}.%(ext)s" "https://www.youtube.com/watch?v=${vid}" 2>>dl_errors.log || true
}

audio_one() {
  local slug="$1" vid="$2"
  local f="${slug}__${vid}.mp4"
  [ -f "$f" ] || return 1
  ffmpeg -y -v info -i "$f" -af "volumedetect,silencedetect=noise=-35dB:d=2" -vn -f null - 2>&1 \
    | grep -E "max_volume|mean_volume|silence_start|silence_end" > "audio_${vid}.txt" || true
  ffprobe -v error -show_entries stream=codec_type,sample_rate -of csv "$f" > "astream_${vid}.txt" 2>/dev/null || true
}

thumb_one() {
  local vid="$1"
  [ -f "th_${vid}.jpg" ] || curl -sL "https://i.ytimg.com/vi/${vid}/hqdefault.jpg" -o "th_${vid}.jpg"
}

process() {
  local slug="$1"; shift
  for vid in "$@"; do
    download_one "$slug" "$vid"
    if [ -f "${slug}__${vid}.mp4" ]; then
      frames_one "$slug" "$vid" &
      subs_one "$slug" "$vid" &
      audio_one "$slug" "$vid" &
      thumb_one "$vid" &
      wait
    fi
  done
}

process youtube-pov YQgVMynmH0Q U6w2jXqHL4c BpCUCwRT8Yc 9zcuRu6WvAo 8CO2EXHPlCE
process tinybuilders Xbdku0L_4Xw GKvuJopBwcY uiTYVHzYzjU SbN_Xgr2jq8
process fakta-bola-dunia IO_NRJ6FJc0
process strangetales Xtm4fZG-LOQ NDz4xGbf8zQ dAYGIAGxjyw -SDS41ICvi4 K0R-iFkBhUo
echo "DONE batch5 pipeline"
