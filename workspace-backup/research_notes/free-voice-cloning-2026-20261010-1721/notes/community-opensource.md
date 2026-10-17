# Community consensus + open-source options — notes (read 2026-10-10, index-based)

## Community consensus (Reddit et al.)
### URLs
- https://www.allaboutai.com/best-ai-tools/productivity/voice-cloning/ (425 days old, crawled 172 days ago — summarizes a Reddit thread)
- https://awesomeagents.ai/tools/best-ai-voice-cloning-tools-2026/ (174 days ago; reflects Apr 2026)
- https://www.vidnoz.com/ai-solutions/ai-voice-reddit.html (crawled 5 days ago — Reddit roundup, marketing page)
- https://pexo.ai/blog/best-ai-voice-cloning-tools-3735 (30 days ago)
- https://clonemyvoice.ai/compare/best-voice-cloning-tools/ (crawled 2h ago)

### Reddit thread summary (via allaboutai; ~2025-era, flag as older)
Frequently recommended: F5-TTS (free on HuggingFace; easy; some found it robotic); XTTS-v2 (praised for prosody and accent control; often paired with RVC for timbre); Zonos and IndexTTS (emotional expressiveness, audiobooks); SparkTTS, Dia, AllTalk, CosyVoice2 (good results but more setup/technical). Tips: use clean recordings; some setups (RVC, AllTalk) "need a decent GPU but offer top-tier results offline."
### 2026 roundups
- awesomeagents.ai (Apr 2026): best open-source self-host = F5-TTS or Spark-TTS ("no commercial restrictions, 3-10 second clone from a sample"); best free = ElevenLabs free tier or Coqui xTTS v2 self-hosted. (ElevenLabs-free-includes-clone claim conflicts with Oct 2026 pricing sources — flag as stale.)
- pexo.ai: new 2026 open models — Confucius4-TTS (NetEase Youdao, June 2026, 14 languages, cross-lingual zero-shot); Chatterbox (Resemble AI, 23-language zero-shot cloning).
- clonemyvoice.ai: Fish Audio S1 #1 TTS-Arena (Oct 2025); S2 (Mar 9 2026) open source Apache 2.0; beats ElevenLabs 60-40 blind A/B.
- awesomeagents tested open-source models on a single A10G GPU — i.e., GPU assumed for serious use.

## Open-source options
- XTTS-v2 (Coqui): community workhorse; multilingual zero-shot; prosody/accent control; commonly paired with RVC.
- F5-TTS: frequently recommended; free HuggingFace demo; occasionally described as robotic.
- Chatterbox (Resemble AI): 23-language zero-shot cloning (per pexo).
- CosyVoice 2/3: mentioned with caveats (setup-heavy); strong cross-lingual reputation in community.
- OpenVoice v2: no 2026-specific data gathered — GAP.
- Fish Audio S2: Apache 2.0, #1 TTS-Arena — likely best 2026 zero-shot quality per benchmarks, but needs verification against community reports.
- Spark-TTS, IndexTTS, Zonos, Dia, AllTalk: community mentions; no 2026 benchmark data gathered.

## CPU-only feasibility (2 cores, 8GB RAM, no GPU) — UNVERIFIED, rough estimates
Could not verify benchmarks (search/browser down after first batch). Honest guidance:
- These models are built for GPU; community sources note "decent GPU" needed for top-tier offline results (allaboutai); roundup testing used an A10G (awesomeagents).
- Rough expectation only (low confidence): large models (XTTS-v2 class, ~hundreds of M params) on 2 CPU cores will be far slower than real-time — minutes per short sentence is plausible; small/fast models (Chatterbox Turbo-class, Spark-TTS) may approach usable speeds but still slow.
- Practical free path: run on free hosted GPU — HuggingFace Spaces demos (e.g., F5-TTS demo noted free), Google Colab free tier — $0, no local hardware needed. This is the realistic recommendation for the mission's budget.
