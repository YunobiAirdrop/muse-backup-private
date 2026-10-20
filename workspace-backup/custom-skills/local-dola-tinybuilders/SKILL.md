# Dola Tiny Builders 30s Video Generation

## Scope and target

- Use this skill only to produce clips for the Tiny Builders channel (@tinybuilders-d5z, channel ID UCjy7bWJU5gULDIYjPmTg9xg).

- Treat 30 seconds as a hard floor, not a target average. Every generation block this skill hands to assembly must total at least 30 seconds of usable footage, verified with ffprobe before assembly starts.

- Produce footage only. Assembly, narration, upload and metadata follow the standard Tiny Builders pipeline in ~/workspace/youtube-otomatis/tinybuilders-dola-prompt-pack.md and the channel rules in ~/workspace/youtube-otomatis/protokol-viral.md.

## Accounts and credits

- Announce every Dola or Google login to the user before it happens and wait for explicit approval, following the standing login rule. One approval from the user can cover a named batch of accounts for one production session.

- Draw accounts from the user's Gmail pool in this order and rotate to the next account only when a generation attempt actually fails with a limit or quota message: khususstokyunobi@gmail.com, stokwebyakis@gmail.com, akunytyunobi17@gmail.com, stokakunwebyunobi@gmail.com.

- Never gate generation on the displayed credit balance. The user has verified that Dola generation succeeds even when the balance looks too small, so treat the balance as decoration and let a real generation attempt be the only test.

- Stop and report only when generation fails on every pooled account. Never buy credits or a subscription without the user's explicit approval.

## Plan a 30 second block

- Break the episode into story beats first, using one block per beat, and write one action sentence per block that a viewer can read in a single glance.

- Append the fixed style block to every prompt so all blocks look like one series: "tiny miniature construction workers, hyper-detailed diorama, macro photography, shallow depth of field, warm cinematic lighting, photorealistic".

- Keep characters, outfits, props and location identical across the blocks of one episode by repeating the same nouns in every prompt.

- Set the aspect ratio to 9:16 inside Dola before generating, never after.

## Generate in Dola web

- Open Dola web at https://dolai.video in the browser and sign in with the pooled Google account the user approved for this session.

- Look for the duration control before generating. When Dola offers a single generation of 30 seconds or longer, select it and generate the block in one pass.

- When the longest single generation is shorter than 30 seconds, chain clips to reach the floor:
  - Generate the first clip at the longest duration offered.
  - Download the clip and extract its last frame with ffmpeg through ~/workspace/youtube-otomatis/ffmpeg-queue.sh.
  - Upload that frame as the start frame or reference image for the next clip and continue the same action in the prompt, for example by adding "the same workers continue" plus the next movement.
  - Repeat until the chained clips for the block total at least 30 seconds.

- Download every finished clip immediately and rename it to tb-<episode>-b<block>.mp4, adding -s<segment> for chained segments, so assembly never guesses which file belongs where.

## Verify before assembly

- Run ffprobe on every downloaded clip and add up each block. Reject and regenerate any block under 30 seconds.

- Extract one frame per clip and look at it. Reject clips with broken frames, wrong subjects or a location that breaks continuity with the previous block.

- Compare the first frame of a chained segment with the last frame of the previous segment. Regenerate the segment when the scene visibly jumps.

- Check every clip for the DOLA AI watermark and note its position. Pass the positions to assembly for delogo treatment instead of regenerating a good clip only for the watermark.

## Hand off to assembly

- Deliver the verified blocks, the per-block prompt list and the watermark positions to the Tiny Builders assembly step.

- Keep the proven assembly treatment: remove the watermark with delogo, add English narration, real recorded SFX matched to visible actions, light film grain, a mid-video and end CTA, and the five standard hashtags ending with #butifyourcloseyoureyesmeme then #foryou.

- Verify the channel ID UCjy7bWJU5gULDIYjPmTg9xg before any upload and tick the AI altered content disclosure, following the standing channel rules.

- Delete the local video files after a successful upload, following the standing delete-after-upload rule.

## Known failure modes

- Expect Google to ask the user to confirm the sign-in on their phone for a fresh account. Pause and relay the prompt instead of retrying blindly.

- Expect the built-in video generation tool to stay region blocked. This skill exists because Dola web is the working route, so do not fall back to the blocked tool mid-episode.

- Treat a missing 30 second duration option as normal, not as a failure. The chaining method above is the standard way this skill reaches 30 seconds.

## Websites

- [Dola AI](https://dolai.video) for the web generator. Carry the approved account, the 9:16 setting and the block prompts into the browser task, check the duration options on screen, then generate directly instead of auditing balances first.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
