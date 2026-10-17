#!/bin/bash
# Generate 88 gambar storybook via media-generation CLI, paralel.
# Usage: gen_images_2026-10-14.sh [start] [end]
cd /home/hatch/workspace/youtube-otomatis || exit 1
GDIR="gambar/2026-10-14"
TMP="_tmp_img/gen14"
mkdir -p "$GDIR" "$TMP"
START=${1:-1}; END=${2:-88}
export GDIR TMP START END
gen_one() {
  local i=$1
  local out="$GDIR/beat-$(printf '%03d' $i).webp"
  [ -s "$out" ] && { echo "skip $i"; return 0; }
  local prompt
  prompt=$(sed -n "${i}p" _tmp_img/prompts.txt)
  local cj
  cj=$(python3 -c "import json,sys; print(json.dumps([{'text': open('/dev/stdin').read()}]))" <<< "$prompt")
  local d="$TMP/b$(printf '%03d' $i)"
  mkdir -p "$d"
  for attempt in 1 2 3; do
    if timeout 240 /opt/hatch/bin/media-generation --media-subagent-output-type image \
        --conversation-json "$cj" --orientation landscape --image-output-format webp \
        --output-dir "$d" > "$d/log.txt" 2>&1; then
      local f
      f=$(ls "$d"/*.webp 2>/dev/null | head -1)
      if [ -s "$f" ]; then cp "$f" "$out"; echo "ok $i"; return 0; fi
    fi
    echo "retry $i (a$attempt): $(tail -c 200 "$d/log.txt")"
    sleep 5
  done
  echo "GAGAL $i"
  return 1
}
export -f gen_one
seq $START $END | xargs -P 6 -I{} bash -c 'gen_one {}' 2>&1 | tee "$TMP/progress.log"
echo "SELESAI: $(ls $GDIR/*.webp 2>/dev/null | wc -l)/88"
