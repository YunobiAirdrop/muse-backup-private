# Free AI Voice Cloning Options — Research Report (as of 10 Oct 2026)

## Summary
- **ElevenLabs free tier does NOT include voice cloning — mission premise confirmed** by multiple Oct 2026 pricing checks. Instant Voice Cloning starts at Starter $6/mo. ElevenLabs is out at $0 budget.
- **No major commercial service offers unlimited free voice cloning.** The genuinely free paths are: (1) free tiers with real cloning but tight limits (Speechify; Resemble AI trial/PAYG; Vidnoz; Typecast 5 min/mo), (2) no-signup free tools (CloneMyVoice.ai's Qwen3-TTS tool), and (3) open-source models run free on hosted GPUs (HuggingFace Spaces / Colab) — XTTS-v2, F5-TTS, Chatterbox, or the new benchmark leader Fish Audio S2 (Apache 2.0).
- **For the use case (1–3 min Indonesian sample → 9 x ~50-char English clips ≈ 450 chars total)**: the workload is tiny, so even small free quotas suffice. Best free bets: **Speechify** (free cloning from 10–30s sample), **Resemble AI** (10-sec sample, 149+ languages — strongest cross-lingual coverage), and **open-source XTTS-v2/Fish Audio S2 on free hosted GPU** ($0, no limits, good cross-lingual).
- **CPU-only local inference (2 cores, 8 GB RAM) is not practical** for quality cloning; community evidence assumes GPUs. Realistic path: free HuggingFace Spaces/Colab GPU.
- **Cross-lingual Indonesian→English**: supported by XTTS-v2, CosyVoice, Chatterbox (23 langs), Fish Audio, Confucius4-TTS (14 langs), and commercially by Resemble AI (149+ langs). Expect an Indonesian accent on the English output — usually the desired outcome here.
- **Research limitation**: after an initial successful search batch, all browsing tools failed (session errors; live browser unavailable), so findings are index-based (sources crawled within ~1 day of 10 Oct 2026). Gaps listed explicitly.

## Findings

### Q1. Online services: which free tiers include REAL voice cloning (2026)

| Service | Free tier | Cloning on free? | Cheapest tier with cloning | Signup needed | Verdict for $0 budget |
|---|---|---|---|---|---|
| ElevenLabs | $0, 10k credits/mo (~10 min), no commercial use | **NO** — confirmed Oct 2026 | Starter $6/mo (IVC); Creator $22/mo (PVC) | Yes | Out at $0 |
| Kits.AI | $0, 15 conversion min, 0 downloads, 0 voice slots | **NO** — official FAQ: cloning unavailable on free | Starter $10/mo | Yes | Out; singing-only, not speech TTS |
| Descript/Overdub | $0, 60 media min/mo; Overdub trial (stock voice / 1,000-word vocab) | Trial only | Hobbyist $16/mo annual | Yes | Out for custom clone; own-voice-only, needs 10–30 min English training audio |
| Resemble AI | Flex $0 subscription (pay-as-you-go); ~300 secs cited | Rapid Clone (~10s sample); 149+ languages | Clone add-ons ~$2–5/voice/mo | Yes | Possible via trial/PAYG; watermarked |
| Speechify | Free tier exists | **Yes** — "free voice cloning from a 10–30 second sample" (pexo.ai) | — | Yes (assumed) | Candidate — single-source claim |
| Play.ht | Free trial ~5,000 words/mo (older data) | Claimed yes (unverified current) | $31.20/mo unlimited | Yes | Unverified — gap |
| Murf | Free trial 10 min total, no downloads | **NO** — cloning on Pro (~$39/mo) | Pro | Yes | Out |
| LOVO | Free 20-min trial | Unverified | From $24/mo | Yes | Gap |
| Hume AI | — | — | — | — | **Gap — no data** |
| Listnr | — | — | — | — | **Gap — no data** |
| Coqui Studio | — | — | — | — | **Gap — no data** (XTTS-v2 open model is the live Coqui artifact) |
| Fish Audio | Freemium tier exists | Likely yes | — | Yes (assumed) | Candidate; exact limits unverified |
| Vidnoz | Free online cloning | **Yes** — 10–20s sample | — | Likely | Candidate; quality/watermark unverified |
| Typecast | Free 5 min download/mo | Instant cloning, very short samples | From $8.99/mo | Yes | Candidate |

Source URLs: ElevenLabs — https://thetoolsverse.com/tools/elevenlabs-ai-voice-generator-cloning (pricing checked 2026-08-15), https://dev.to/stimlau/elevenlabs-pricing-explained-free-starter-creator-and-pro-in-2026-4p6b, https://news.ssbcrack.com/best-ai-voice-cloning-tools/ (pricing checked 6 Oct 2026), https://www.coval.ai/blog/elevenlabs-review-2026-voice-cloning-and-synthesis-capabilities-explained; Kits.AI — https://www.kits.ai/pricing (official), https://news.ssbcrack.com/best-ai-voice-cloning-tools/; Descript — https://news.ssbcrack.com/best-ai-voice-cloning-tools/, https://pexo.ai/blog/best-ai-voice-cloning-tools-3735, https://pilottools.ai/blog/best-ai-voice-audio-tools-2026-elevenlabs-vs-murf-vs-descript/, https://toolnest.ai/project/overdub, https://qcall.ai/descript-overdub-review; others — https://pexo.ai/blog/best-ai-voice-cloning-tools-3735, https://www.vidnoz.com/ai-solutions/ai-voice-cloning.html, https://clonemyvoice.ai/compare/best-voice-cloning-tools/, https://github.com/ishandutta2007/Awesome-Voice-Cloner, https://scored-tools.netlify.app/blog/kits-ai-vs-murf-ai-voice-cloning-comparison/. All read 2026-10-10 (index). Confidence: index only, medium-high where 2+ sources agree.

### Q2. Community consensus (Reddit, roundups, 2026)
- A Reddit help-thread roundup (via https://www.allaboutai.com/best-ai-tools/productivity/voice-cloning/, ~2025-era): most-recommended free/open tools were **F5-TTS** (free HuggingFace demo, easy, sometimes robotic), **XTTS-v2** (praised for prosody/accent control, often paired with RVC for timbre), **Zonos/IndexTTS** (emotional expressiveness), **SparkTTS, Dia, AllTalk, CosyVoice2** (good but setup-heavy; some "need a decent GPU").
- awesomeagents.ai (Apr 2026): best open-source self-host = **F5-TTS or Spark-TTS**; best free = ElevenLabs free tier or Coqui xTTS v2 self-hosted (the ElevenLabs-free-clone claim is stale vs Oct 2026 pricing).
- 2026 shift (https://clonemyvoice.ai/compare/best-voice-cloning-tools/): **Fish Audio S1** took #1 on TTS-Arena (Oct 2025); **S2** (Mar 9, 2026) went open source (Apache 2.0) and beats ElevenLabs 60–40 in blind A/B; **Qwen3-TTS** powers a no-account free tool.
- pexo.ai: new 2026 open models **Confucius4-TTS** (NetEase Youdao, June 2026, 14 languages cross-lingual zero-shot) and **Chatterbox** (Resemble AI, 23-language zero-shot).
- Consensus pick for $0: **self-hosted open-source (XTTS-v2 / F5-TTS / Fish Audio S2)**, not a commercial free tier.

### Q3. Open-source local options
- **Quality verdict (2026)**: Fish Audio S2 is the benchmark leader (#1 TTS-Arena, open Apache 2.0); XTTS-v2 remains the most battle-tested zero-shot cloner (prosody/accent control, RVC pairing); F5-TTS is easiest (free HF demo); Chatterbox adds 23-language zero-shot; CosyVoice2 strong but setup-heavy. For this use case: **XTTS-v2 or Fish Audio S2**.
- **CPU-only (2 cores, 8 GB RAM, no GPU)**: NOT recommended. Community sources assume GPU. Rough, unverified estimates: XTTS-v2-class models on 2 CPU cores would take **minutes per short sentence** (far slower than real-time); lighter models (Chatterbox Turbo-class, Spark-TTS) may be slow but usable. 8 GB RAM can hold most models, but 2 cores make generation impractical.
- **Realistic $0 path**: run models on **free hosted GPUs** — HuggingFace Spaces or Google Colab free tier. 9 x ~50-char clips is a trivial workload there.

### Q4. No-signup free browser tools
- **soundtools.io**: could NOT be verified (research tools failed before checking) — do not rely on it.
- Closest verified no-signup option: **CloneMyVoice.ai's free tool (powered by Qwen3-TTS) — "no account required"** (https://clonemyvoice.ai/compare/best-voice-cloning-tools/). Limits/quality/watermark unverified.
- **Vidnoz** offers free online cloning (10–20s sample) but is freemium/marketing-led; expect signup nudges, possible watermark, unclear data-privacy for uploaded voice samples. Typical catch for this category: lower quality, watermarks, non-commercial terms, voice samples processed on third-party servers with vague retention.
- Caution: never upload a real person's voice to a no-signup site without reading its privacy/retention terms.

### Q5. Cross-lingual: Indonesian voice sample → English voiceovers
- Capable: **XTTS-v2** (multilingual zero-shot), **CosyVoice 2/3** (strong cross-lingual reputation), **Chatterbox** (23-language zero-shot), **Fish Audio S1/S2** (multilingual), **Confucius4-TTS** (14 languages, cross-lingual zero-shot); commercially **Resemble AI Rapid Voice Clone 2.0 (149+ languages)** has broadest verified coverage.
- Expect English output with an **Indonesian accent** (timbre preserved) — normally desired when cloning a specific speaker. Short 50-char clips are forgiving.
- Descript/Overdub unsuitable (English training data, own-voice only).

### Ranked shortlist (top 3) — $0, 1–3 min Indonesian sample, 9 x ~50-char English clips

| Rank | Name | Cost | Quality verdict | Exact free limits | What you need to start |
|---|---|---|---|---|---|
| 1 | **Speechify** (free tier) | $0 | Commercial-grade; cloning from 10–30s sample per pexo.ai (single source — verify in-app) | Free tier incl. cloning (exact cap unverified) | Signup; 10–30s clean sample |
| 2 | **Resemble AI** (Rapid Voice Clone) | $0 subscription (Flex PAYG); add-ons ~$2–5/voice/mo if exceeded | Commercial quality; 149+ languages — best cross-lingual; watermarked | ~300 secs cited; trial/PAYG | Signup; ~10s clean sample |
| 3 | **Open-source: XTTS-v2 or Fish Audio S2 via free HuggingFace Spaces / Colab GPU** | $0 forever | XTTS-v2: proven zero-shot, accent control; Fish Audio S2: 2026 benchmark leader (Apache 2.0) | None | HuggingFace/Google account; 6s–3min sample; no local GPU needed |

- Fallbacks: Vidnoz (free online cloning); CloneMyVoice.ai Qwen3-TTS tool (no signup); Typecast (5 min download/mo free).
- If any budget opens: **ElevenLabs Starter $6/mo** (30k chars ≈ 30 min, IVC included) — the 9 clips need <1k chars total.

## Could not verify
- Hume AI, Listnr, Coqui Studio free tiers; Play.ht and LOVO current free-tier cloning access; Speechify exact free limits; Fish Audio freemium exact limits; Resemble AI exact free seconds; soundtools.io (works? quality? watermark? privacy?).
- OpenVoice v2's 2026 standing; 2026 head-to-head quality comparisons (Fish Audio S2 vs XTTS-v2 vs Chatterbox); CPU inference benchmarks (estimates above rough/unverified).
- Anything needing live confirmation — live browser unavailable; index tools failed after the first batch. All findings index-based (crawled within ~1 day of 2026-10-10).

## Sources
Per-source notes: notes/services-elevenlabs.md, notes/services-kits-descript.md, notes/services-others.md, notes/community-opensource.md (URLs + read dates + index flag). Key URLs inline above. No live verification was possible; confidence "index only," higher where 2+ sources agreed.
