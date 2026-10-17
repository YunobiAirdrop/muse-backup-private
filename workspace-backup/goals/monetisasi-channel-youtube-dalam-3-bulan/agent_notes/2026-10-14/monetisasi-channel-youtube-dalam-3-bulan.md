# Study Notes - 2026-10-14 - Monetisasi channel YouTube dalam 3 bulan
<!-- studying-run-start: 2026-10-14T00:08:08Z -->

Goal `goal_40cb6c5afd04` (slug `monetisasi-channel-youtube-dalam-3-bulan`), category money, goal_kind outcome. Target: YouTube Partner Program (YPP) by 10 January 2027 — 88 days from today. The real bar (established in the 2026-10-11 Letter and still the anchor): 1,000 subscribers + 4,000 watch hours in 12 months, OR 1,000 subscribers + 10 million Shorts views in 90 days, per channel. The study task plan attached to this run (teach / novice, retrieval / practice shape) is treated as scheduler metadata only, as in all prior passes: this is an outcome goal, not a skill the user is learning, so no teaching scaffold is preserved here.

The goal description still carries the outdated early-access-tier bar ("500 subs + 3.000 jam tayang atau 3 juta views Shorts"); the correct bar lives in the 10-11 Letter and prior notes. Updating the description text is outside this study seat's write permissions.

## The day's arc: the user took the wheel

2026-10-13 was the most user-driven day of this goal so far. The user was visibly frustrated ("ko ga ada perkembangan ini semua project", 2026-10-13T01:47Z) and drove nearly every major action himself. Key fact for future sessions: on days like this, the assistant's value was honesty about timelines (YouTube monetization = months, not days) plus executing the user's own experiments — not new strategy decks.

## What changed on 2026-10-13 (all grounded in main chat)

### 1. OTP auto-verification system — the biggest structural move of the day (user-designed)

Direct verification with the user's reserve number failed first: YouTube throttled at the first attempt for @BizarreWorldDaily ("terlalu banyak upaya verifikasi"), SMS never sent, number still 0/2 used. The user then proposed the full system himself: the assistant accesses his OTPMurah.id account, buys a virtual number each attempt, cancels the order if no OTP arrives so the balance only pays for successes — run automatically every 3 days.

What got built (all in chat, all confirmed by the user):
- API key path chosen (username/password login failed with "Username tidak ditemukan" — account is Google-registered).
- IP whitelist defeated the key first; user emptied the whitelist field ("Kosongkan untuk allow semua IP"), then regenerated the key; new key connected.
- Cron `verifikasi-otp-3harian` installed (interval 72h, first run Friday 2026-10-16 23:35 WIB, owner goal:monetisasi-channel-youtube-dalam-3-bulan).
- Queue of 15 channels in `~/workspace/youtube-otomatis/verifikasi-otp/state.json`, starting @BizarreWorldDaily then @KisahAlkitab-k9j.
- Pricing corrected by the user: Express server Rp 358/number (not the Plus server's Rp 1.434); balance Rp 11.000 covers ~30 attempts; 15 channels × Rp 358 = Rp 5.370.
- Standing exception to the login-announce rule granted by the user: each run is announced in chat, no per-run permission asked.
- Caveat the assistant stated: YouTube often rejects virtual numbers, so the success rate is unknown; the refund mechanism bounds the cost, not the outcome.

### 2. The share-copy experiment (user's own theory, tested live)

User ordered every video link copy-shared 3× across all channels (he believed this drove a 1k-view video). Assistant executed on 133 public videos (18 private skipped), with a comparison scheduled via runonce cron `banding-share3x-15okt` (Thu 2026-10-15 13:00 WIB). The assistant was honest that copying links alone adds no views — clicks do — but ran the test to settle it.

First measurement (same evening, ~6h after, 140 videos checked): 43 up, 95 flat, 2 slightly down; +4.147 total views. Biggest movers: Tiny Builders dam +879, one batchA video 0→801, Strange Tales "Hole on Fire" 501→1.198. Assistant told the user plainly: ~30% moved, could be prime-time hours, not proof the trick works. User ordered the 95 flat videos copied 4× more (7× total) — done, 228 copy actions total; re-check scheduled the morning of 2026-10-14.

Watch hours / subscriber causality from the 15 Okt comparison will decide whether this tactic survives. If it fails, the user heard the honest prior ("belum bisa dibilang triknya yang bikin naik") and should accept the verdict.

### 3. Token-burn audit — a live threat to the whole operation

Weekly token audit: **342.6 million tokens in 7 days** — 3.8× the 90M/week budget; projected balance exhaustion **±12 November** (mid-mission). Biggest burners: weird-en, youtube-pov, jejakbuddha. The assistant noted the projection is a 7-day extrapolation and many failed runs were runtime infra errors, not production scripts — no guaranteed savings number offered. User was given a choice (widget): keep as-is with the Nov 12 risk, or let the assistant cut only failed-run waste while all 19 channels keep running. **The user has not answered** (message:assistant-msg-7ab59a66-2e0a-4468-6390-8894b8c370c2). This decision is still open and more consequential than any single day's production — a dead wallet on Nov 12 ends the 3-month mission early.

### 4. New standing rules the user issued (both already in MEMORY.md)

- **Viewer-comment rule (2026-10-13):** any good viewer comment gets learned, fixed, and the fix rolled out to ALL channels. First application: a comment on the Echoes of History "Frankenstein" short exposed that the history-en TTS scripts literally spoke "Narrator: " at each segment — 3 scripts cleaned, a sanitizer built that strips labels ("Narrator:", "Scene 1:", "[pause]") before TTS, locked into the daily checklist for all 19 channels.
- **Anti-rebuild rule (2026-10-13):** a video already built must never be rebuilt (identical videos piled up). Trigger: 3 D.B. Cooper shorts rebuilt 11 Okt (0 views) while the 6 Okt originals (43–47 views) lived — the rebuild batch was privated 13 Okt, originals kept. Locked into protokol-viral.md §19.

### 5. Funnel distribution — now fully deployed

- Thematic playlists via API completed: **16/16 channels, 59 videos** (message:assistant-msg-ccf61306-d495-a8ce-96b3-893a5cbd7edb). The 3/17 state from the 10-13 note is fully closed.
- End screens: Maura Murray → D.B. Cooper on Dark Case Files (verified live); Lima Misteri long got its end screen. Lima Misteri pinned comment failed (channel phone verification required — which is exactly what the OTP system now targets).
- AI disclosure checked on all 8 Strange Tales scheduled videos via logged-in browser session, no re-login.

### 6. Upload throughput — record day, same ceiling

43 videos published on 2026-10-13 (15 via mass browser upload in the morning, 28 via API in the afternoon); 2 remaining (inktime + macammacam) queued for the evening browser window. Unverified channels still hit the daily upload wall; bank-video behavior continues. Tiny Builders still region-blocked (day 4+) — user asked, was told honestly, not re-offered.

### 7. First audit-cron result landed in the goal record

Timeline entry 2026-10-13T16:06Z ("Audit 3-harian perdana selesai"): @ceritarakyat862 still leads (49 subs); **@LimaMisteri the fastest riser (+7 subs in a day)**; 19 quiet-video titles auto-fixed; 9 videos slotted into matching playlists; the three religious channels' videos are 1–2 days old with no views yet (normal, re-check next week). Note: this entry was cron-logged to the goal record; it was not separately reported to the user in main chat, but it sits in the goal's visible current_state.

### 8. The honest money conversation (repeated, still standing)

When the user pressed "gimana mau cepet dapet cuan saya", the assistant held the line: YouTube needs 1,000 subs + 4,000 hours (months away); blog traffic is tiny; the two real levers are Shopee affiliate (payment/tax info still incomplete — commissions won't disburse) and TikTok Shop (0 sales, 600 followers needed for reviews). Factory work named as the fastest certain income; manual WA sharing of affiliate links offered as the fastest online lever — user didn't take the offer (moved on to other topics). Bot/view-buying schemes were rejected with the Fake Engagement Policy math (Rp 5/view = bots; filtered; strikes). All delivered in chat; no Letter needed to repeat.

## Evidence quality

- Upload counts (15 + 28 = 43) and share-copy counts (133 public, 228 actions) come from the assistant's own batch reports in chat.
- The +4.147-view experiment delta is a 6-hour same-day read from 140 videos; confounders (prime-time hours, organic Shorts testing) are open — the 15 Okt scheduled comparison is the real verdict.
- Subscriber totals: the audit-cron snapshot (49 / +7/day) is goal-record data; the 102-sub/10,539-view API baseline from 10-12 is the last full pull.
- Watch hours remain unmeasured for every channel — the actual YPP bar is still estimated from subs + views only.
- Token audit: 7-day extrapolation, ±Nov 12; the assistant flagged the uncertainty itself.

## Open decisions / things to watch (for the next study pass)

1. **Token-budget decision** — user hasn't answered the keep-vs-trim choice. If Nov-12 exhaustion is real, this is the single highest-leverage pending item.
2. **Share-copy experiment verdict** — comparison cron runs Thu 2026-10-15 13:00 WIB; if flat, the tactic dies (user was pre-warned).
3. **OTP first run** — Fri 2026-10-16 23:35 WIB; also the open question of whether YouTube accepts virtual numbers at all.
4. **cek-video-sepi-3harian** first run Thu 2026-10-15 — first measured read on funnel + repair effects (baseline: 101 public, 58 quiet from 12 Okt).
5. **Lima Misteri growth** — +7 subs/day makes it the candidate leader; verify it holds before any "double down" letter is written.
6. Lima Misteri pin-comment blocked on channel phone verification — resolved automatically once the OTP system verifies that channel.

## Already Covered in Main Chat
- End screen + pinned comment on Maura Murray → D.B. Cooper; pin failed on phone verification (2026-10-13 01:42 WIB).
- User frustration + honest cold-start verdict: machine runs, viewers haven't arrived; affiliate/factory as the real fast levers (2026-10-13 01:47–01:48 WIB).
- The 40-video mass upload: 15 live in the morning (with links), 25 bounced to retry on daily limits, then +28 via API in the afternoon = 43 total (2026-10-13 02:03–03:23, 14:11 WIB).
- Token audit: 342.6M tokens/7 days, ±12 Nov projection, keep-vs-trim choice widget — unanswered (2026-10-13 04:13 WIB).
- Strange Tales 0-view worries; the 1:1 link list experiment setup; user's counter-order (all channels, 3× each) and the assistant's honest caveat (2026-10-13 05:44–06:07 WIB).
- @truehorrorstoriespov investigation: original self-shot reenactments, not stolen footage (2026-10-13 06:00 WIB).
- Viewer-comment rule + the "Narrator:" TTS bug fix and cross-channel sanitizer (2026-10-13 06:16–06:22 WIB).
- Share-copy execution: 133 videos 3×; interim +4.147 views (43 up / 95 flat / 2 down); user's 7× order completed; 15 Okt comparison scheduled (2026-10-13 07:02–13:52 WIB).
- Playlist funnel completed: 16/16 channels, 59 videos (2026-10-13 14:31 WIB).
- Anti-rebuild rule: D.B. Cooper rebuilds privated, originals kept, locked in protokol-viral.md §19 (2026-10-13 13:15–13:16 WIB).
- End screen on Lima Misteri long (2026-10-13 13:00–13:07 WIB).
- AI disclosure checked on 8 Strange Tales videos via browser (2026-10-13 15:44–22:52 WIB).
- Reserve-number direct verification failed (YouTube throttle, SMS never sent); the full OTPMurah 3-day system designed by the user: API key, whitelist emptied, cron installed, 15-channel queue, Rp 358/number, Rp 11.000 balance, first run 16 Okt 23:35 WIB (2026-10-13 15:49–16:39 WIB).
- Bot/view-buying rejection with the Fake Engagement Policy math; "2 weeks to profit" claims debunked (2026-10-13 17:52–18:23 WIB).
- The honest no-instant-money line repeated: factory job / Shopee payment info / manual WA sharing offered; user moved on (2026-10-13 08:59–09:03 WIB).
- Clipper-bot module built and tested (separate surface; mentioned 2026-10-13 18:46 WIB) — adjacent revenue line, not this goal's center.

## Research Trajectory
- *External sources viewed*: None opened this pass. No external claim is introduced; the only external authority in play is YouTube's YPP rules, established in the 10-11 Letter and already corrected (1,000 subs + 4,000 hours, or 1,000 subs + 10M Shorts views in 90 days).
- *Prior trajectories reviewed*: Study notes for this goal 2026-10-13 (read in full), 2026-10-12 (covered in the 10-13 trajectory), and 2026-10-11 (YPP bar correction). Both prior briefs indexed by filename — "The Real Monetization Target" (the YPP bar correction) and "Jejak Islami Footage Decision" (Mixkit license hold) — neither covers today's topics.
- *Scaffolds and support tactics*: Assigned teach/novice task plan reviewed and set aside as scheduler metadata, consistent with all prior passes; outcome goal, no learning scaffold preserved, no learning-style matching used.
- *Connected user data*: `user_goal.get` for goal_40cb6c5afd04 (metadata, 3 timeline updates, 2 briefings); `muse.context_fetch` conversation category for the full window 2026-10-13T00:08Z → 2026-10-14T00:08Z (157 handles, full transcript read including the saved spillover file through the window end); run-packet schedule snapshot for cron state (verifikasi-otp-3harian, banding-share3x-15okt, cek-video-sepi-3harian). No credentials, passwords, OTP codes, or API keys reproduced in this note.
- *Image references checked*: None — the user's screenshots in chat were operational (views graphs, verification dialogs), already described by the main agent.
- *User context and memory*: MEMORY.md standing entries cross-checked (OTP system, commenter rule, anti-rebuild rule, API-first uploads, hashtag rule, login-announce rule with the OTP exception); no new memory searches needed — today's evidence is all in-conversation.
- *Searches skipped or unavailable*: Web search skipped — no fast-moving external fact required; every claim is first-party. Repetition search (required before ruling): keyword variants `otp`, `verifikasi`, `salin link`, `share-copy`, `token`, `komentar penonton`, `narrator`, `rebuild`, `playlist`, `funnel` were grepped case-insensitively over this goal's `agent_notes/` and `briefs/` including filenames. Results: `otp`, `salin link`, `share-copy`, `komentar penonton`, `narrator` — zero hits in all prior notes (new vs the record); `token` — hit in the 10-12 and 10-13 notes but about the short-reply/token-saving preference, not the 342.6M burn audit; `verifikasi`, `rebuild`, `playlist`, `funnel` — hit in the 10-13 note on earlier aspects (4/19 verified, D.B. Cooper rebuild, 3/17 playlists, wave-1 funnel) but not on today's developments (OTP system, anti-rebuild rule, 16/16 playlists, end screens live). Both brief filenames were checked; neither covers today's topics. Every candidate topic was then checked against the full recent conversation: OTP system, token audit, share experiment, commenter rule, anti-rebuild rule, playlist completion, 43-video upload, honest money line — all were designed, ordered, or reported in main chat with the user actively directing.
