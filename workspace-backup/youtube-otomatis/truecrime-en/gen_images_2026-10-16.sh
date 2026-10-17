#!/bin/bash
# gen_images_2026-10-16.sh <start1based> <end1based> [thumb]
BASE=/home/hatch/workspace/youtube-otomatis/truecrime-en
GDIR=$BASE/gambar/2026-10-16
FFQ=/home/hatch/workspace/youtube-otomatis/ffmpeg-queue.sh
mkdir -p "$GDIR"
MG=/opt/hatch/bin/media-generation

gen_one() { # $1=prompt $2=outfile
  local prompt="$1" out="$2"
  [ -s "$out" ] && { echo "SKIP $out"; return 0; }
  for att in 1 2 3; do
    cj=$(python3 -c "import json,sys; print(json.dumps([{'text': sys.argv[1]}]))" "landscape 16:9 image. $prompt")
    resp=$($MG --media-subagent-output-type image --conversation-json "$cj" 2>/dev/null)
    webp=$(echo "$resp" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('media_paths',[None])[0] or '')" 2>/dev/null)
    if [ -n "$webp" ] && [ -f "$webp" ]; then
      # Konversi still-image via PIL (bukan ffmpeg-queue): webp->jpg 2 detik,
      # tidak butuh slot render video (aturan ffmpeg-queue untuk cegah OOM render).
      if python3 -c "
from PIL import Image
im = Image.open('$webp').convert('RGB')
im.save('$out', 'JPEG', quality=90)
" 2>/dev/null && [ -s "$out" ]; then
        echo "OK $out"; return 0
      fi
    fi
    sleep 8
  done
  echo "FAIL $out"
  return 1
}

if [ "$3" = "thumb" ]; then
  gen_one "YouTube thumbnail: masked man wearing a rubber TV-host mask and dark sunglasses on a flickering CRT television full of static, rippling corrugated metal background, bold big red-yellow text '90 SECONDS OF TERROR', high contrast, dramatic, dark noir style, 16:9" "$BASE/thumbnail-2026-10-16.jpg"
  exit 0
fi

for i in $(seq "$1" "$2"); do
  bid=$(printf "beat-%03d" "$i")
  prompt=$(python3 -c "import json; print(json.load(open('$BASE/script/beats-2026-10-16.json'))[$i-1]['image'])")
  gen_one "$prompt" "$GDIR/$bid.jpg"
done
echo "WORKER $1-$2 DONE"
