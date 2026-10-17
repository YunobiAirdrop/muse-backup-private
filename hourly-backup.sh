#!/bin/bash
# Backup workspace per jam ke repo private YunobiAirdrop/muse-backup-private
# Hanya commit kalau ada perubahan. File sensitif & file besar di-skip.
set -e

REPO_DIR=~/workspace/muse-backup-private
STAGE="$REPO_DIR/workspace-backup"
LOG=~/workspace/goals/dashboard-monitor-project/hidden_files/backup-perjam.log
GH_TOKEN_FILE=~/.hermes/github-dashboard-token

log() { echo "$(date '+%Y-%m-%d %H:%M') $1" >> "$LOG"; }

[ -f "$GH_TOKEN_FILE" ] || { log "SKIP: token github tidak ada"; exit 0; }
export GH_TOKEN=$(cat "$GH_TOKEN_FILE")

cd "$REPO_DIR"
# Auth via token untuk pull & push, kembalikan ke URL polos setelahnya
git remote set-url origin "https://x-access-token:${GH_TOKEN}@github.com/YunobiAirdrop/muse-backup-private.git"
git pull --quiet origin main 2>/dev/null || true

mkdir -p "$STAGE"
# --delete-excluded: file yang di-exclude juga DIHAPUS dari stage (tanpa ini,
# file besar yang dulu lolos filter menumpuk selamanya di stage).
rsync -a --delete-excluded \
  --exclude='muse-backup-private/' \
  --exclude='_home/' \
  --exclude='.git/' \
  --exclude='__pycache__/' \
  --exclude='node_modules/' \
  --exclude='venv/' --exclude='.venv*/' \
  --exclude='.hatch-browser/' \
  --exclude='*.mp4' --exclude='*.mp4.*' --exclude='*.mkv' --exclude='*.mov' --exclude='*.avi' \
  --exclude='*.webm' --exclude='*.ogv' --exclude='*.ogg' --exclude='*.opus' \
  --exclude='*.mp3' --exclude='*.wav' --exclude='*.m4a' --exclude='*.aac' --exclude='*.flac' \
  --exclude='*.png' --exclude='*.jpg' --exclude='*.jpeg' --exclude='*.webp' --exclude='*.gif' \
  --exclude='*.bmp' --exclude='*.tiff' --exclude='*.tif' --exclude='*.psd' \
  --exclude='*.apk' --exclude='*.ipa' \
  --exclude='*.so' --exclude='*.so.*' --exclude='*.whl' \
  --exclude='*.zip' --exclude='*.tar' --exclude='*.tar.gz' --exclude='*.tgz' --exclude='*.7z' --exclude='*.rar' \
  --exclude='*.iso' --exclude='*.dmg' --exclude='*.img' \
  --exclude='*.orig' --exclude='*.rej' \
  --exclude='.env' --exclude='*.env' \
  --exclude='*secret*' --exclude='*token*' --exclude='*credential*' \
  --exclude='*.pem' --exclude='*.key' \
  --exclude='.gnupg/' --exclude='.ssh/' \
  --max-size=25M \
  ~/workspace/ "$STAGE/" 2>/dev/null || true
# --max-size=25M = jaring pengaman: file APAPUN di atas 25MB tidak ikut,
# supaya pack push tidak membengkak lagi (kasus 2026-10-17: pack 2,56GB
# dari .webm/.ogv footage + venv binaries + *.orig + *.apk yang lolos
# filter ekstensi, push gagal 5x).

# File penting di home (bukan workspace)
mkdir -p "$STAGE/_home"
for f in MEMORY.md USER.md AGENTS.md SOUL.md IDENTITY.md; do
  [ -f ~/"$f" ] && cp ~/"$f" "$STAGE/_home/" 2>/dev/null || true
done

git add -A
if git diff --cached --quiet; then
  log "OK: tidak ada perubahan baru di working tree"
else
  CHANGED=$(git diff --cached --stat | tail -1)
  git -c user.name="YunobiAirdrop" -c user.email="khususstokyunobi@gmail.com" \
    commit -qm "auto-backup: $CHANGED"
  log "commit $(git rev-parse --short HEAD) — $CHANGED"
fi

# Push kalau ada commit lokal yang belum sampai ke GitHub — termasuk sisa
# antrean dari run sebelumnya (kasus 2026-10-17: commit 0a1d2984 tertunda
# karena push gagal, run berikutnya skip push kalau tidak ada perubahan baru).
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 1)
if [ "$AHEAD" = "0" ]; then
  log "OK: sudah sinkron dengan GitHub, tidak perlu push"
  git remote set-url origin "https://github.com/YunobiAirdrop/muse-backup-private.git"
  exit 0
fi

set -o pipefail
if git push --quiet origin main 2>&1 | tail -2; then
  log "OK: push $(git rev-parse --short HEAD) — $AHEAD commit terkirim"
else
  log "GAGAL: push exit $? — $AHEAD commit tertunda di lokal"
fi
set +o pipefail
git remote set-url origin "https://github.com/YunobiAirdrop/muse-backup-private.git"
