# Study Notes - 2026-10-12 - Monetisasi channel YouTube dalam 3 bulan
<!-- studying-run-start: 2026-10-12T00:11:06Z -->

Goal `goal_40cb6c5afd04` (slug `monetisasi-channel-youtube-dalam-3-bulan`), category money, goal_kind outcome. Deadline in the goal record: 10 January 2027, for YouTube Partner Program (YPP) ad revenue. Yesterday's study (2026-10-11) and its Letter "The Real Monetization Target" already corrected the bar to 1,000 subscribers + 4,000 watch hours in 12 months, OR 1,000 subscribers + 10 million Shorts views in 90 days. This pass does not repeat that correction. It covers the first full production day under the user's all-19-channels decision (2026-10-11, Asia/Jakarta) and what that day revealed that was not in the prior note, not in the prior Letter, and in its two most important parts never told to the user in main chat.

The study task plan attached to this run (teach / novice, retrieval / practice / rubric shape) is treated as scheduler metadata only, as in the prior pass: this is an outcome goal, not a skill the user is learning, so no teaching scaffold is preserved here.

## What changed on 2026-10-11

### Verification: 2 of 19 -> 4 of 19, with a retry due today (Monday, 2026-10-12)

- On 2026-10-11 at 08:31-08:35 WIB, @StrangeTales-g6n and @LimaMisteri were phone-verified, bringing the verified total to 4 of 19 (@KisahPOV and @ceritarakyat862 were already verified). That first number is now at its 2-channels-per-year limit. This was done live with the user in main chat, codes supplied by the user; no number or code is recorded here.
- On 2026-10-11 at about 11:20 WIB, a second number for @BizarreWorldDaily and @KisahAlkitab-k9j (the two largest queues, 5 videos each; user approved that pair) was rejected by YouTube with a too-many-attempts throttle, because two verifications had succeeded about an hour earlier. The number is not burned; the agreed retry is today, 2026-10-12, or the night before. As of this run (2026-10-12 07:11 WIB) there is no record that the retry has happened yet.
- Constraint that now binds that retry: the rule the user laid down on 2026-10-11 at 20:13-20:38 WIB - announce before any login or account-settings change and wait for explicit permission (see the session incident below). A verification attempt is exactly that kind of touch, so the retry cannot be run silently.
- Verification did not behave as a simple on/off switch for upload limits on 2026-10-11, which corrects a simplification in earlier reporting:
  - Retry run 2026-10-11 13:55-14:45 WIB tried 11 queued videos across 5 channels and got 0 through; Studio showed the daily-limit message ("setelah verifikasi satu kali") on all of them.
  - Retry run 2026-10-11 about 15:55-17:07 WIB then got 5 of 5 through, including 3 @LimaMisteri Shorts scheduled that evening and the @MacamMacamID premiere.
  - @KisahAlkitab-k9j, not yet phone-verified, uploaded 3 Shorts on 2026-10-11 at about 17:26 WIB with no daily-limit hit at all (scheduled Monday, 2026-10-12 19:00 WIB).
  - Reading: the rolling ~24-hour window matters as much as verification status in the short term. Verification raises the ceiling; it does not clear a window that is already spent.

### First production day: real output, and a misleading "failed" surface

Scheduler status for 2026-10-11 shows many channel crons as `failed` (among them empires-en, history-en, horor, horror-en, inktime, jejakbuddha, jejakislami, kisahdharma, lima-misteri, macammacam, mind-en, mystery-en, space-en, strangetales, tinybuilders, truecrime-en, weird-en, youtube-pov). The dated log shows that label is not a production scoreboard: several of those same runs produced or uploaded successfully the same day, for example:

- @KisahAlkitab-k9j: 3 Shorts from the Yusuf long (Genesis 37-50) uploaded, scheduled 2026-10-12 19:00 WIB.
- @KisahPOV (Kisah Horor): long "Suster Ngesot Itu Nyuruh Aku Gantian Jaga Shift!" (12.1 min) uploaded via the YouTube Data API on 2026-10-11 at 21:30 WIB, scheduled 2026-10-12 19:00 WIB; its missing AI-disclosure check was fixed and verified on 2026-10-12 at about 02:30 WIB.
- @CosmosUnknownTV: Bootes Void long uploaded 2026-10-11 at 15:57 WIB, scheduled 2026-10-12 07:00 WIB.
- @MacamMacamID: first long produced (7 min 10 sec, "7 Hewan dengan Kemampuan Mustahil Ini Nyata!"), upload instruction set for scheduling on 2026-10-12 19:00 WIB.
- @JejakBuddha: a long uploaded the previous night was scheduled via API to Monday, 2026-10-12 19:00 WIB after the browser task failed to switch channels.

Do not quote the cron `failed` count to the user as "production failed." The useful Day-1 facts are the bottlenecks underneath it, next section.

### Production bottlenecks observed on 2026-10-11 (supporting evidence, not the Letter centre)

- Render contention is now a structural limit: all video scripts share `ffmpeg-queue.sh` with a maximum of 2 concurrent renders on an 8 GB / 2 CPU machine. On 2026-10-11 that produced stale-slot stalls (slots held by dead PIDs, cleared manually), at least one OOM SIGKILL during the Kisah Horor assembly (34 of 76 segments done, then stagnant), and repeated hangs in the InkTime multi-input concat job. Horor's long was eventually assembled late (21:15 WIB) and uploaded by API because the 196 MB file exceeded the browser upload path.
- Tiny Builders produced nothing on 2026-10-11: `media.generate_video` returned a region 403 for the second day in a row. Its 2026-10-10 queue entry stayed intact for the watchdog. This blocker was already known and accepted by the user, so it is not new material on its own.
- Token audit recorded on the evening of 2026-10-11 (covering the prior 7 days): about 67M tokens/week across the top 25 crons, with roughly 51M/week attributed to failed runs and duplication - including about 34M on videos that were produced but then hit the daily upload limit. That audit supports the same conclusion as the render evidence: production capacity is being spent faster than publishing capacity can absorb it. The user delegated optimisation on 2026-10-10/11 with the condition "asalkan upload lancar dan project saya menghasilkan" - that delegation is already covered in main chat / memory, so it is not re-presented as a finding here.

## The two findings that are new to the user

Both findings below were searched against the prior note, the prior Letter, and the 2026-10-11 main-chat conversation: neither appears in any of them. Both bear directly on whether channels can actually monetise, not just on whether videos upload.

### 1. Comments-off has relapsed on newest videos, despite the "all clean" audit

The user's hard rule from 2026-10-10 is that comments must be ON on every video on every channel, and an API audit that day was reported as leaving all channels clean. The comment runs on 2026-10-11 contradict "clean" as a durable state:

- Morning run, 2026-10-11 09:14 WIB (13 channels fetched via API): 0 new viewer comments anywhere. Seed discussion comments could not be posted on the newest videos of several channels because comments were disabled on those videos, including @StrangeTales-g6n and @ceritarakyat862; the setting was not changed by the run. One positive counter-example: the newest @AncientEmpiresTV video had comments active, after its two 2026-10-10 predecessors had them off.
- Evening run, 2026-10-11 21:19 WIB (13 channels): again 0 new viewer comments, and 4 newest videos returned 403 commentsDisabled - @ceritarakyat862, @EchoesOfThePast-e9m, @CosmosUnknownTV (the Bootes Void video uploaded that same afternoon), and @TheDarkMindFiles-s6i. The run log's own conclusion: this is a recurring pattern in the upload pipeline and needs checking.

Implication: whatever the upload pipeline defaults to is still publishing some newest videos with comments off, across both Indonesian and English channels, verified and unverified alike. That silently breaks the user's explicit rule, removes the comment surface the viral protocol depends on for engagement signals, and means the main agent's morning/evening comment work has nothing to work with on those videos. The next move is a pipeline-level fix (default / post-upload verification per video), not another one-off audit: the 2026-10-10 audit already proved one-off fixes do not hold for even 24 hours.

### 2. Jejak Islami's 2026-10-11 long uses non-commercial-licensed footage

The religious channels' established pattern is Pexels stock footage. For @JejakIslami's long on 2026-10-11 ("Nabi Musa AS - Laut Merah Terbelah", 480.7 sec / 8 min, produced that day):

- Pexels was blocked by a Cloudflare CAPTCHA (the stored CAPTCHA preference is "ask"), so the run downloaded clips from Mixkit instead: 22 downloaded, 21 clean clips used across 22 segments after one clip was rejected on manual frame review.
- The run log flags those clips explicitly as Mixkit Restricted License (non-commercial) and records: monetisation risk, needs a user decision. No such decision appears in the 2026-10-11 conversation, and the video was left waiting for upload approval with a planned schedule of Monday, 2026-10-12 19:00 WIB - today.

Implication: publishing a monetisation-track video built on non-commercial-licensed footage puts that channel's YPP application at risk on exactly the dimension yesterday's Letter cared about (original / rights-clean content), and the risk was incurred as a fallback when the usual source was blocked, not as a chosen strategy. Before that video is published or kept on a monetisation path, someone needs a user decision: replace the restricted clips, hold the video, or accept the risk knowingly. What must not happen is the fallback quietly becoming the default for the other religious channels the next time Pexels is blocked.

## Session incident and the standing login rule (already covered with the user, recorded here for continuity)

- The 20:00 WIB watchdog on 2026-10-11 triggered a Google alert ("trying to change YouTube settings", Windows / California - the browser server). The user pressed "Bukan, jangan izinkan" and changed the password of the main Google account at 20:38 WIB; the browser session died completely and that watchdog run ultimately failed (ended 23:21 WIB, second consecutive failure).
- Re-login was completed the same evening, 20:47 WIB, with the new password stored via the secure card and 2FA approved by the user on their phone. The channel picker then showed 20 entries, one more than the "19 channels" figure used everywhere - the extra entry is consistent with the "Info Loker Terkini" YouTube channel that was created on 2026-10-11 and kept, unused, at the user's direction, plus named entries already known. A clean channel-count audit is still owed; do not treat "19 production channels" and "20 accounts in the picker" as a contradiction until that audit runs.
- On 2026-10-11 at 23:05 WIB the user ordered the login session to be saved/persisted so logins are not repeatedly requested. On 2026-10-12 in the early morning the main agent confirmed to the user that the session was still alive (Studio opens directly, no login prompt), and explained the only forced re-login is a password change, which Google itself uses to kill all sessions.
- On 2026-10-12 at about 02:16 WIB the user ordered all approved queued videos uploaded; a manual watchdog run was triggered against 42 queue files (largest groups: Strange Tales 6, Weird World 6+, Horror EN 5, Kisah Alkitab 5, History EN 4, Jejak Buddha 4, Kisah Dharma 4, Lima Misteri 2). The outcome of that run was not yet verified when the dated log was written. The expectation already given to the user: verified channels should get through, unverified ones will likely stay queued on the daily limit.

## Measurement gap - still no baseline, two instruments land this week

- There is still no per-channel subscriber / views / watch-hours baseline for this goal. The prior note flagged that `hidden_files/scoreboard.md` (referenced by BANK-VIDEO.md) did not exist and that the Day-1 baseline had not been pulled. Nothing in the 2026-10-11 evidence closes that gap; the highest subscriber figure on record remains 49 (@ceritarakyat862, from the 2026-10-10 audit).
- Two scheduled instruments are due inside this window: `yt-seo-refresh-mingguan`, first run Monday, 2026-10-12 09:11 WIB (no run recorded yet as of 07:11 WIB), and `audit-channel-3harian`, next run Tuesday, 2026-10-13 (date verified: 2026-10-13 is a Tuesday in Asia/Jakarta). Until at least one of them reports, any claim about progress toward 1,000 subscribers / 4,000 hours / 10M Shorts views is ungrounded - production counts are not progress counts.

## Already Covered in Main Chat
- User approved all 19 voice-clone bumper clips, then cancelled the Dola avatar: bumper is voice-only, inserted mid-video at a natural break, never at second 0 (2026-10-11 07:52-07:54 WIB).
- Agent gave the honest math against monetising all 19 channels in one month (19,000 new subscribers needed from a top of 49) and suggested focusing on 3 leaders; user explicitly rejected that: focus all 19 channels (2026-10-11 07:57-08:01 WIB).
- The missing @MacamMacamID production cron was found and created the same morning; 19 of 19 production crons active; user was told publishing speed stays limited until phone verification, with failures going to the video bank.
- @MacamMacamID premiere: user had deleted their phone copy; agent confirmed the master file is stored in the workspace and queued it.
- Phone verification done live with the user: @StrangeTales-g6n and @LimaMisteri verified (4 of 19 total); user will send another number when available; next priority named as Weird World, then Kisah Alkitab.
- Second number agreed for @BizarreWorldDaily + @KisahAlkitab-k9j, then throttled by YouTube; user was told the number is safe and the retry would be that night or the next morning (2026-10-11 11:18-11:20 WIB).
- Blog traffic Q&A, the TikTok loker pivot, and the link-bio work - separate goals, not this one.
- @CosmosUnknownTV manual re-upload attempt failed on the daily limit; user was told it stays queued and is a verification candidate.
- Google settings-change alert: user ordered "kalo mau login bilang!!!"; agent confirmed the 20:00 WIB watchdog was the source, user pressed "not me", changed the password, re-login was completed with the new password and phone 2FA the same evening.
- User ordered all 42 approved queued videos uploaded (2026-10-12 about 02:16 WIB); agent set the expectation that verified channels should pass and unverified ones will likely remain queued.
- @LimaMisteri pattern change agreed: no more alternating - 1 long + 3 Shorts every day, scheduled for the next day at 19:00 WIB; user also ordered #foryou on every YouTube video (last hashtag in Shorts titles, in long-video description hashtags), applied to the protocol and all 19 production crons, with the caveat that the 42 already-queued videos keep their locked old metadata.
- @KisahAlkitab-k9j 3 Shorts, @KisahPOV long, and @KisahDharma's banked long were each reported to the user, including the Kisah Horor AI-disclosure fix.
- User ordered the login session saved/persisted; agent confirmed on 2026-10-12 morning that the session is still alive and only a password change would kill it.

## What to watch / unresolved for the next pass

- Verification retry for @BizarreWorldDaily + @KisahAlkitab-k9j is due today (2026-10-12) and, under the user's own rule, must be announced before any login/settings touch.
- Decision owed on the Jejak Islami Mixkit video before its planned 2026-10-12 19:00 WIB schedule: replace restricted clips, hold, or knowingly accept the risk. Also check whether any other 2026-10-11 religious-channel production used the same fallback.
- Comments-off: verify the upload pipeline default, count how many currently-live newest videos have comments disabled, and fix at pipeline level rather than per video.
- Outcome of the manual 42-video watchdog run ordered on 2026-10-12 about 02:16 WIB - unverified at log time.
- First `yt-seo-refresh-mingguan` result (2026-10-12 09:11 WIB) and the 3-day channel audit (2026-10-13) - the first real baseline for this goal.
- Channel-count audit: 19 production channels vs 20 entries in the Studio picker.

## Research Trajectory
- *External sources viewed*: None opened this pass. The two centre findings are first-party operational evidence from the user's own runs (dated logs and scheduler state), and yesterday's Letter already established the official YPP rules (YouTube Help, https://support.google.com/youtube/answer/72851 and https://support.google.com/youtube/answer/1311392, both read 2026-10-11); no external claim is introduced today that would need a new source.
- *Prior trajectories reviewed*: Study note 2026-10-11 for this goal (workspace/goals/monetisasi-channel-youtube-dalam-3-bulan/agent_notes/2026-10-11/monetisasi-channel-youtube-dalam-3-bulan.md) - YPP target correction, inauthentic-content verification, bumper/retry status as of that morning; and the Letter it produced, "The Real Monetization Target" (2026-10-11 00:47 UTC), read in full text form - its centre is solely the corrected 1,000 / 4,000-hour / 10M-Shorts bar.
- *Scaffolds and support tactics*: Assigned task plan (teach/novice) reviewed and set aside as scheduler metadata, consistent with the prior pass: outcome goal, no learning scaffold preserved, no learning-style matching used.
- *Connected user data*: `user_goal.get` for goal_40cb6c5afd04 (metadata, timeline, one briefing on record); `muse.context_fetch` conversation and scheduler categories for the window 2026-10-11T00:08Z to 2026-10-12T00:11Z (verification flow, all-19 decision, session incident, Lima Misteri / #foryou changes, 42-video upload order, session-persistence order); dated logs memory/2026-10-11.md and memory/2026-10-12.md read in full (retry runs 13:55 and 15:55-17:07 WIB, comment runs 09:14 and 21:19 WIB, Jejak Islami production entry, production bottleneck entries, watchdog 20:00 WIB failure, re-login 20:47 WIB). Weekday check run with `date -d` in Asia/Jakarta: 2026-10-12 is a Monday, 2026-10-13 is a Tuesday.
- *Image references checked*: None - no image bears on this goal's findings this pass; screenshots in the conversation were the user's own Google/TikTok alerts, already described in the dated logs.
- *User context and memory*: MEMORY.md standing entries on verification status (4 of 19, second number throttled, retry due 2026-10-12), the login-announce-first rule and its 2026-10-11 incident, session persistence (2026-10-12), Lima Misteri's new pattern and the #foryou rule (both dated 2026-10-12); `muse.memory_search` for verification throttle, Lima Misteri pattern, and 2026-10-11 production failures - corroborated the dated logs above. GOAL.md and STUDYING.md read for the goal's stored description and study state.
- *Searches skipped or unavailable*: `muse.learnings_search` was called with three goal-specific queries (portfolio upload-limit/verification bottleneck, systemic same-day production failures, Shorts vs long-form YPP paths) and returned fleet_learning_consumption_disabled with zero lessons - a normal outcome; the study proceeded on local evidence. No web search was run: no fast-moving external fact was needed, and no phone number, SMS code, or credential encountered in the conversation is reproduced in this note. Repetition search (required before ruling): keyword variants "verifikasi HP", "verification throttle", "komentar mati commentsDisabled", "Mixkit restricted license monetisasi", "ffmpeg queue OOM", "20 channel", "Lima Misteri pola", "#foryou", and "bank video 42" were grepped over this goal's prior agent_notes/ and briefs/ including filenames; the only hit was the prior note's passing flywheel/verification mention (2 channels verified at that time), and none of the variants hit the prior Letter - today's centre findings (comments-off relapse, Mixkit restricted-license footage) appear in neither prior notes nor prior briefs and in no main-chat message.
