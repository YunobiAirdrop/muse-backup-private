# Fallback seed comments — night run 2026-10-17 (21:11 WIB)

DIRECTIVE FOR balas-komentar-youtube-malam RUN (2026-10-17 21:11 WIB):

- commentThreads.insert via YouTube API returned 403 "insufficient permissions" on
  ALL 7 seed attempts, BOTH Google accounts (khususstokyunobi + stokakunwebyunobi),
  2026-10-17 ~03:22 UTC. Seeds worked fine 15 Oct. Read APIs still work; other
  write APIs worked same day (52 metadata fixes, horror-en upload). Diagnosis:
  YouTube-side anti-spam restriction on comment posting for these clients,
  NOT an auth/scope problem (youtube.force-ssl scope present in auth.py).
- Do NOT retry the API seeding path tonight. Repeated attempts risk tightening
  the restriction. Post discussion comments via YouTube Studio browser only
  (cron step 4: post as channel, then pin).
- The 7 seed texts + video links are in komentar-seeds-2026-10-17-malam.json
  (same dir). Regenerate fresh seeds if the run prefers; otherwise use these
  as the fallback payload.
- Leave a line in the run report noting the 403 is being monitored.
