# Hourly GitHub backup

Goal ID: goal_b7fdba2cc444
Goal slug: hourly-github-backup

## Description
Automatic hourly backups of the workspace to GitHub, set up because Yunobi feared the VM could be reset. A public fork holds only the tooling (no secrets), while a private repo keeps the backup tooling plus an AES-256 encrypted secrets bundle and restore.sh so all keys return automatically on a fresh VM without re-entering API keys.
