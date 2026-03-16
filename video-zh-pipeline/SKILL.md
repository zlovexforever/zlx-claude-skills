---
name: video-zh-pipeline
description: Turn a YouTube video or local video into a Chinese-dubbed deliverable end to end: extract subtitles, translate them to Chinese, generate Chinese TTS audio, and mux or burn subtitles into the final video. Use this skill whenever the user gives a video URL/file and wants a full Chinese video rather than only subtitles or only audio. Especially use it for requests like "把这个视频转成中文视频", "做中文配音版", "YouTube 视频转中文".
---

# Video -> Chinese Pipeline

This skill is the orchestrator for the full pipeline. Use it when the user wants the final Chinese video artifact, not just one intermediate file.

## Goal

Produce these outputs for one exact input video:

- original reference video
- Chinese subtitle file
- Chinese TTS WAV
- Chinese dubbed video without subtitles
- Chinese dubbed video with burned subtitles

## Skills To Chain

1. `youtube-srt` for subtitle extraction from the exact target video.
2. `subtitle-translate` for EN -> ZH subtitle translation.
3. `tts-gen` for ZH SRT -> ZH WAV.
4. `video-dub` for muxing audio and burning subtitles.

## Working Rules

- Always create a dedicated work folder named with a human-readable title slug plus the exact video ID.
- If the source is a YouTube URL with playlist parameters, normalize to the exact target video and keep single-video mode.
- Keep intermediate files because they are useful for review and re-runs.
- If an upstream step fails, stop and fix that step before continuing. Do not keep pushing broken inputs downstream.
- Treat `video_id` as the internal stable identity and `title_slug` as the human-readable display name. Do not use title alone as the unique key.

## Recommended Folder Layout

```text
<workdir>/<title_slug>__<video_id>/
  <title_slug>__<video_id>_en.srt
  <title_slug>__<video_id>_en_corrected.srt
  <title_slug>__<video_id>_en_glossary.md
  <title_slug>__<video_id>_zh.srt
  <title_slug>__<video_id>_zh_tts.wav
  <title_slug>__<video_id>_original.mp4
  <title_slug>__<video_id>_zh_nosub.mp4
  <title_slug>__<video_id>_zh.mp4
```

## Execution Order

### Step 1 - Extract exact-video subtitles

- Use `youtube-srt`.
- Prefer English subtitles by default when the final deliverable is Chinese dubbing.
- If the URL contains `list=...`, still target the exact `v=` video ID.
- Let the subtitle output inherit `title_slug__video_id` naming so every downstream file naturally keeps the same prefix.

### Step 2 - Translate to Chinese

- Use `subtitle-translate`.
- Run termdb pre-processing first if available.
- Preserve timestamps and entry numbers exactly.
- Keep subtitle lines reasonably short because TTS quality depends on it.

### Step 3 - Generate Chinese TTS WAV

- Use `tts-gen`.
- Default voice: `zh-CN-XiaoxiaoNeural`.
- If lines are too long and the speech sounds rushed, revise the Chinese SRT before regenerating audio.

### Step 4 - Build deliverable videos

- Use `video-dub`.
- Produce both `*_zh_nosub.mp4` and `*_zh.mp4`.
- Keep the original reference copy as `*_original.mp4`.
- Pass explicit paths or let `video-dub` derive the same `title_slug__video_id` prefix. Do not switch back to raw `video_id` in this stage.

## Validation Checklist

Before claiming success, verify:

- the subtitle file belongs to the requested video ID
- the working directory and output filenames contain both `title_slug` and `video_id`
- the Chinese SRT exists and has the same number of entries as the translated source
- the TTS WAV exists and has plausible duration
- the dubbed MP4 exists
- final video duration is close to the source duration
- the final video has both a video stream and an audio stream

## Common Recovery Moves

- Wrong YouTube video downloaded: re-run with exact watch URL and single-video mode.
- Same title as another video: rely on the `__<video_id>` suffix, not title alone.
- Chinese subtitle timing feels fine but speech is too dense: shorten the Chinese subtitle wording, then regenerate TTS.
- Pillow subtitle burn fails: fall back to soft subtitles if the user mainly needs a playable review copy.

## Deliverable Summary Format

When finished, report:

- final dubbed video path
- no-subtitle dubbed video path
- original reference video path
- Chinese SRT path
- Chinese WAV path
- what you verified and any remaining quality caveats
