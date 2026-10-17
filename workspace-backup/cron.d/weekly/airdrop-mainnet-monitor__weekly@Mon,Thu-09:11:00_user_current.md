---
id: airdrop-mainnet-monitor
title: Monitor mainnet airdrop testnet
enabled: true
mode: task
schedule:
  kind: weekly
  timezone: '@user.current'
  time: 09:11:00
  dow: [Mon, Thu]
delivery:
  - chat_id: cff15a74-710d-4347-9f43-b63e9629bb90
metadata:
  tags: [cron:flexible-time]
  originating_chat_context_json: '{"chat_id":"cff15a74-710d-4347-9f43-b63e9629bb90","origin_provider":"main","chat_kind":"direct","event_kind":"message","require_mention":false,"device_id":"a132f74a55562927"}'
  presentation_locale: id-ID
---
Monitor 7 testnet airdrop projects for mainnet launch announcements. Projects: GTE (MegaETH), Neptune Protocol, Variational, Plaza Finance, Zenchain, Sahara AI, Multipli.fi.

Steps:
1. Search for recent news about each project (use browser.search with news vertical, queries like "GTE mainnet launch", "Neptune Protocol mainnet", etc.)
2. Check if any project has announced a mainnet date, TGE (token generation event), or snapshot
3. If YES for any project: report to user in Indonesian with project name, mainnet date, and what they need to do (e.g., "mainnet 15 Nov, pastikan wallet eligible")
4. If NO new announcements: stay silent (do not spam)

Only alert when there's genuinely new mainnet/TGE/snapshot news. Check official sources (project Twitter/X, docs, blog).
