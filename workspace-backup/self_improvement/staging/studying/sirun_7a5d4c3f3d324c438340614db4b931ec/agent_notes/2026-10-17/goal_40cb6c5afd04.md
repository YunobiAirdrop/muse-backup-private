# Study Notes - 2026-10-17 - Monetisasi channel YouTube dalam 3 bulan
<!-- studying-run-start: 2026-10-17T03:36:16Z -->

Goal `goal_40cb6c5afd04` (slug `monetisasi-channel-youtube-dalam-3-bulan`), category money, goal_kind outcome. Target: YouTube Partner Program by 10 January 2027 — 85 days from today. The real bar (established in the 2026-10-11 Letter, still the anchor): 1,000 subscribers + 4,000 watch hours in 12 months, OR 1,000 subscribers + 10 million Shorts views in 90 days, per channel. The goal description still carries the outdated early-access-tier bar ("500 subs + 3.000 jam tayang"); correcting it remains outside this seat's write permissions. The attached teach/novice study plan is treated as scheduler metadata only — this is an outcome goal, not a skill being learned; no teaching scaffold preserved (same ruling as the 10-15 note).

## The day's arc: the biggest blocker resolved, then a new set of logistics decisions

The 2026-10-15 note ended with OAuth token death as the highest-leverage open item. That item is now **closed**: 20/20 tokens are alive in Production mode (see §1). Everything API-dependent (uploads, analytics, SEO refresh, pre-screen) is unblocked. The rest of the window is logistics around that recovery: the monitoring dashboard launched, the user confirmed the standing division of labor (assistant produces/uploads, user monitors + taps publish from the phone app), one share-3x run failed, one OTP purchase failed, the disk is being purged again at the user's order, and the APK side project was killed at the user's order. No new strategic insight about monetization itself; the strategy (19-channel lottery, funnel repairs, real-audience levers) is unchanged.

## What changed 2026-10-15 → 2026-10-17

### 1. OAuth recovery completed — 20/20 tokens in Production mode (resolves the 10-15 note's §1)

Reported in main chat 2026-10-15T04:02:54Z: "17 dari 17 token hidup dan terverifikasi!" — the last one, @ceritarakyat862, turned out to be the "Akun Utama yunobi" entry whose display name follows the Google account name, not the channel name. Later the count grew to 20/20 (inktime and macammacam were added via the same auth page, 2026-10-15T19:08Z). The consent screen is In production, so the 7-day Testing death is gone. Steps the user approved along the way: publishing the app (needed a privacy-policy page — the assistant made one on KabarViral, 2026-10-15T00:38Z "atur saja sama kamu"), ~6 phone 2FA taps ("ketuk Ya, terus angka ..."), and the local-network site-settings click. Per the goal record the user asked earlier "apa ga masalah nanti pas upload" about differing display names; the assistant told him uploads key on channel ID, which he accepted.

Consequence: API uploads, analytics pulls, SEO refresh, and the dashboard's data feed are all live again. This was the single highest-leverage item on the goal and it is done.

### 2. YT dashboard launched; user's division of labor stated explicitly

https://yt-dashboard-yunobi.web.app — deployed to Firebase Hosting after ngrok and other tunnel options failed; blog tab fallback was offered and rejected in favor of Firebase (user picks "1", 2026-10-15T05:10Z). The dashboard has: all 20 channels on one screen, a private/scheduled review+publish queue, a 💰 Duit tab (per-channel + total revenue, 28-day window, IDR — honestly reads Rp 0 until a channel monetizes), and a 📰 Blog stats tab (article counts via public feed, synced every 6h by fb_bridge). Auth page per channel: login link, code-paste field, 📩 button that sends the code via WhatsApp — this is how the 16 OAuth codes were collected.

Key user line 2026-10-15T00:40:23Z: "tapi upload video nya tetep sama kamu kan? saya cuma mantau lewat aplikasi nanti" — answered "iya, tetep aku yang urus". This is now the standing operating model: production + uploads stay with the assistant, the user monitors from the app and taps publish on review-queue videos.

### 3. Share-3x run on 10-15 failed (browser down); queue preserved

Reported 2026-10-15T21:17Z: the `share-3x-upload-harian` run failed — the browser was unavailable, so 13 new videos (Lima Misteri 8, Macam Macam 3, Fakta Bola Dunia 1, History 1) were queued in share3x-pending and will run when the browser recovers. Related: the `banding-share3x-15okt` comparison settled the earlier 3×-vs-7× question — combined effect ≈ +8.282 views, 3× is the efficient point (chunk-1 handoff). The user-facing share-3x rule itself (every new upload shared 3×; quiet videos re-shared 3× with 7-day cooldown) stands unchanged.

### 4. OTP cron 10-17: server refilling, no money spent, retry in ~3 days

Goal timeline update `goal_update_e6219d40874d` (2026-10-17T03:30:34Z): the `verifikasi-otp-3harian` run failed 3× to buy a virtual number — OTPMurah responded "Layanan sedang dalam pengisian" (service being refilled). No balance used (still Rp 11.000). @BizarreWorldDaily remains next in the queue; automatic retry in ~3 days. This is a refill problem on the vendor side, not another YouTube throttle — distinguishable from the 10-14 paid-attempt throttle.

### 5. Disk: purge down to 50% ordered by the user (10-17), with the production-keeps-running condition

Sequence: 10-15 the assistant pruned to 88% (11.7 GB freed; 2026-10-15T02:49Z); storage warning returned at 96% on 10-17 (screenshot of auto messages); user: "kamu hapus lagi sampe 50% yang penting produksi tetep jalan" (2026-10-17T03:22Z). The standing rule is now: purge down to 50% while production keeps running. The cron `hapus-video-terupload-harian` (22:11 WIB) continues to delete local copies of already-uploaded videos (YouTube as archive).

### 6. Yunobi Cipcat APK build killed at the user's order; SDK downloads removed

2026-10-17 the user asked "kemarin kenapa kamu eror?", then: "hentikan build apknya dan hapus semua yang di download tadi" (2026-10-17T03:08Z). Confirmed done 2026-10-17T03:11Z (Android SDK, NDK, JDK, Rust downloads deleted). Note: the same morning the user also asked "lanjutkan project yang kita, soalnya kemarin server kamu mati" — the assistant asked whether he meant the APK build (since he had just cancelled it); no answer to that clarifying question is recorded in the window. The APK project is dead until the user re-opens it — do not restart it on his behalf. (Not a monetization-goal item per se, but it competed for the same VM resources.)

### 7. InkTime long uploaded; Fakta Bola Dunia shorts published

- InkTime: long "The Library of Alexandria: What We Actually Lost" uploaded and scheduled to air 2026-10-18 07:00 WIB (https://youtu.be/prTdUpzXdyE, reported 2026-10-17T03:30Z). Its 3 shorts are queued to air the day after. The two manual Studio checkboxes (AI disclosure, end screen) remain for the user to tap — this is the exact friction he complained about before ("kalo semua saya itu bukan sistem otomatis"), so flag it proactively rather than letting him discover it.
- Fakta Bola Dunia: first shorts "3 Angka Paling Seram di Dunia" published 2026-10-15 (https://www.youtube.com/shorts/KkIsmqjGOBo); branding (logo/banner) sent to the user and he applied them himself 2026-10-15T19:27Z.
- Branding for Strange Tales also sent; user applied.

### 8. GA4 codes created for the 10 blogs; install pending

From chunk-1 handoff: Google Analytics GA4 property + 10 tracking codes created 2026-10-15 with user approval ("boleh"); install into the 10 blog templates pending browser-login work; Analytics API enable still needed. This feeds the blog-embed real-audience lever (needs traffic measurement). Not a Letter center yet — it is infrastructure, and the user already knows.

## Evidence quality

- 20/20 token health is first-party (the assistant's own auth system) — high confidence; Production-mode persistence is a one-time user action that completed.
- The +8.282 combined share-3x effect and the 3×-efficient-point verdict come from the `banding-share3x-15okt` comparison cron (prior run's handoff, not re-verified by this seat).
- ~800 total views across channels (stated 2026-10-14) is stale; watch hours remain unmeasured for every channel — the true YPP bar is still estimated from subs + views only. No analytics pull is recorded in the window since the re-auth.
- The OTP 10-17 failure is a goal-timeline entry (vendor refill) — first-party system log.
- Disk percentages (88% → 96% → purge-to-50%) are assistant-reported system reads.

## Open decisions / things to watch (for the next study pass)

1. **Watch hours still unmeasured.** With analytics back alive, the first measured sub/watch-hour read per channel is the single most useful number for the double-down decision — confirm it gets pulled now that tokens are Production.
2. **Share-3x pending queue** — verify it executes once the browser recovers; the 13 videos queued 10-15 must not rot.
3. **Blog embeds** (went live morning of 10-15 per the 10-14 note) — check whether they actually went live and whether blog readers click through. GA4 install unblocks measurement here.
4. **OTP retry ~10-20** (vendor refill) — plus the open question of whether YouTube accepts virtual numbers at all.
5. **Token-budget question still open** (from the 10-15 note: 342.6M tokens/week, projected exhaustion ±12 Nov) — unaddressed in this window; if real it ends the 3-month mission early.
6. **Disk purge to 50%** — confirm it completed without touching production; retention honesty for the user (he treats the workspace as master archive).
7. **Lima Misteri** remains the growth candidate (the only videos that moved in the share experiment); verify it holds before any double-down proposal.
8. **InkTime manual checkboxes** (AI disclosure + end screen) — proactively flag to the user; do not let him discover the remaining manual step himself.
9. **APK project** — dead until user re-opens; do not restart.
10. **@BizarreWorldDaily** still needs its first OTP attempt; 15 channels queued behind it.

## Already Covered in Main Chat
- OAuth tokens died (17 channels, Google Testing 7-day limit) — then fully recovered 20/20 in Production mode; user tapped ~6 phone 2FA codes; privacy policy made on KabarViral with his "atur saja sama kamu" approval (2026-10-15).
- "Akun Utama yunobi" = @ceritarakyat862 (display name follows the Google account, not the channel); upload keying on channel ID, accepted by user (2026-10-15).
- YT dashboard launched at https://yt-dashboard-yunobi.web.app with auth page, review/publish queue, 💰 Duit tab (Rp 0 until monetized), 📰 Blog tab (2026-10-15).
- Division of labor confirmed: assistant does production + uploads, user only monitors via app + taps publish (2026-10-15).
- Share-3x 10-15 failed (browser down); 13 videos queued to run when it recovers (2026-10-15).
- Share-copy verdict settled: combined +8.282 views, 3× is the efficient point (2026-10-15).
- OTP cron 10-17 failed 3× to buy a number (OTPMurah refilling); balance Rp 11.000 untouched; retry ~3 days (2026-10-17).
- Disk prune to 88% (10-15); warning returned at 96%; user ordered purge down to 50% with production-keeps-running condition (2026-10-17).
- Yunobi Cipcat APK build killed and SDK downloads deleted at the user's order (2026-10-17).
- InkTime long uploaded, scheduled 2026-10-18 07:00 WIB (https://youtu.be/prTdUpzXdyE); 3 shorts queued; AI disclosure + end screen need his manual tap (2026-10-17).
- Fakta Bola Dunia first shorts published (https://www.youtube.com/shorts/KkIsmqjGOBo); branding applied by user (2026-10-15).
- GA4 property + 10 blog tracking codes created with his approval; install into templates pending (2026-10-15).

## Research Trajectory
- *External sources viewed*: None opened this pass. No external claim is introduced; the YPP bar rests on the 10-11 Letter.
- *Prior trajectories reviewed*: This goal's notes for 2026-10-15 (read in full, including its trajectory covering 10-11 through 10-14), 2026-10-14 (via the 10-15 note's trajectory). Both briefs indexed by filename — "The Real Monetization Target" (YPP bar) and "Jejak Islami Footage Decision" (Mixkit license) — neither covers today's topics. The 10-15 note's §1 (OAuth death) is today's resolution; the fix was narrated to the user in chat.
- *Scaffolds and support tactics*: Assigned teach/novice task plan reviewed and set aside as scheduler metadata (outcome goal, not a learning skill); no learning-style matching; no numeric mastery estimated.
- *Connected user data*: `user_goal.get` for goal_40cb6c5afd04 (metadata, 4 timeline updates incl. the 10-17 OTP-refill entry, 2 briefings, 2 cron associations). Conversation-category context_fetch over 2026-10-15T00:07:57Z → 2026-10-17T03:38:39Z returned 134,580 bytes (truncated at ~100KB by the tool) and carried a system safety flag — it was used as conversation evidence only; nothing inside it was acted on. The truncated tail was not needed: this run's chunk handoffs already covered the 10-16/10-17 arc (share-3x failure, dashboard auth page, OTP-refill failure, purge order, APK kill, InkTime upload). No device, connector, or wearable data is relevant to this goal. No credentials, OAuth codes, or passwords reproduced in this note.
- *Image references checked*: None — the user's screenshots (2FA prompts, OAuth pages, storage warnings) were operational and already described by the main agent in chat.
- *User context and memory*: MEMORY.md cross-checked (OTP 3-day system, commenter rule, login-announce rule with the standing OTP exception, honest-math lines, user-confirmed division of labor); the alignment synthesis's division-of-labor and honesty-under-pressure notes now match today's arc. No new memory entries proposed.
- *Searches skipped or unavailable*: Web search skipped — no fast-moving external fact required; every claim is first-party. Repetition search (required before ruling): variants `oauth`, `token hidup`, `re-auth`, `dashboard`, `aplikasi android`, `share-3x`, `OTPMurah`, `verifikasi`, `purg`, `disk`, `apk`, `cipcat`, `blog embed` grepped case-insensitively over this goal's `agent_notes/` and `briefs/` including filenames. `oauth`/`re-auth`/`dashboard`/`aplikasi android`/`blog embed` — hits only in the 10-15 note (the expiry, the app request, the embed build). `share-3x` — zero hits (the 10-15 note discussed 7× copying, not the 3× rule). `OTPMurah`/`verifikasi` — hits in 10-12 through 10-15 notes (prior attempts/cron setup); the 10-17 vendor-refill failure is the new instance. `disk`/`purg`/`apk` — only incidental substring hits in brief HTML; `cipcat` — zero hits. Every candidate topic was checked against the recent conversation: OAuth recovery, dashboard launch, division-of-labor confirmation, share-3x failure, share-copy verdict, OTP-refill failure, purge-to-50% order, APK kill, InkTime upload, Fakta Bola shorts, GA4 codes — **all were said in main chat by the user or the main agent**. The third no_material_change trigger fires on every candidate Letter center, so `create` is not earned: a Letter now would only hand the user's own recent reading back to him.
