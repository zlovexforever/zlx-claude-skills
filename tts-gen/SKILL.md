---
name: tts-gen
description: Generate a time-synchronized Chinese TTS audio track (WAV) from a Chinese SRT subtitle file using edge-tts. Use this skill when the user has a Chinese .srt file and wants to generate a dubbed audio track, or asks for "TTS 生成", "语音合成", "配音生成" requests. Also triggers as part of the YouTube dubbing pipeline after subtitle-translate produces a ZH SRT.
---

# TTS Audio Generator (ZH SRT → WAV)

Generate a time-synchronized Chinese speech audio track from a Chinese SRT file using Microsoft Edge TTS (free, no GPU needed).

## Dependencies

```bash
pip install edge-tts        # pydub NOT needed — uses ffmpeg directly
brew install ffmpeg          # macOS
# or: apt install ffmpeg
```

> **Note:** pydub is incompatible with Python 3.13+. This script uses ffmpeg subprocess calls instead.

## How to Use This Skill

### Input
- A Chinese `.srt` file
- Optional: voice name (default: `zh-CN-XiaoxiaoNeural`)
- Optional: output path (default: `<basename>_tts.wav`)

### Step 1 — Check / install dependencies

```bash
pip show edge-tts pydub 2>/dev/null | grep -c Name | grep -q 2 || pip install edge-tts pydub
ffmpeg -version 2>/dev/null || echo "Install ffmpeg: brew install ffmpeg"
```

### Step 2 — Write the TTS generation script

Write the following script to `/tmp/tts_gen.py`:

```python
#!/usr/bin/env python3
"""
tts_gen.py — Generate time-synchronized Chinese TTS from a ZH SRT file.

Algorithm:
  For each SRT entry [start_ms, end_ms, text]:
    1. Synthesize speech via edge-tts → tmp WAV segment
    2. Measure actual duration of synthesized audio
    3. If actual > slot duration → speed up (atempo, max 1.3x) via ffmpeg
    4. If actual < slot duration → pad with silence at end
    5. Place segment at start_ms in the output timeline
  Concatenate all placed segments → final WAV
"""
import asyncio, re, subprocess, sys, os, tempfile, argparse
from pathlib import Path
from dataclasses import dataclass
from typing import List

try:
    import edge_tts
except ImportError:
    print("edge-tts not found. Run: pip install edge-tts"); sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("pydub not found. Run: pip install pydub"); sys.exit(1)


@dataclass
class SrtEntry:
    index: int
    start_ms: int
    end_ms: int
    text: str

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms


def parse_srt(path: str) -> List[SrtEntry]:
    text = Path(path).read_text(encoding='utf-8')
    blocks = re.split(r'\n\s*\n', text.strip())
    entries = []
    for block in blocks:
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if len(lines) < 3:
            continue
        try:
            index = int(lines[0])
        except ValueError:
            continue
        ts_match = re.match(
            r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})',
            lines[1]
        )
        if not ts_match:
            continue
        def to_ms(h, m, s, ms):
            return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)
        start_ms = to_ms(*ts_match.groups()[:4])
        end_ms   = to_ms(*ts_match.groups()[4:])
        text_content = ' '.join(lines[2:])
        entries.append(SrtEntry(index=index, start_ms=start_ms, end_ms=end_ms, text=text_content))
    return entries


def get_audio_duration_ms(wav_path: str) -> int:
    audio = AudioSegment.from_wav(wav_path)
    return len(audio)


def adjust_audio_duration(input_wav: str, output_wav: str, target_ms: int, actual_ms: int) -> None:
    """Speed up (max 1.3x) or pad with silence to hit target_ms."""
    if actual_ms <= 0:
        # Generate silence
        silence = AudioSegment.silent(duration=target_ms)
        silence.export(output_wav, format='wav')
        return

    ratio = actual_ms / target_ms

    if ratio > 1.3:
        # Too long even at 1.3x — just use 1.3x, audio will overflow slightly
        ratio = 1.3

    if ratio > 1.01:
        # Speed up using ffmpeg atempo
        atempo = ratio
        # atempo only accepts 0.5–2.0 in one filter; chain if needed
        if atempo > 2.0:
            atempo_filter = f"atempo=2.0,atempo={atempo/2.0:.4f}"
        else:
            atempo_filter = f"atempo={atempo:.4f}"
        subprocess.run([
            'ffmpeg', '-y', '-i', input_wav,
            '-filter:a', atempo_filter,
            output_wav
        ], capture_output=True, check=True)
    else:
        # Pad with silence at end
        audio = AudioSegment.from_wav(input_wav)
        padding_ms = target_ms - actual_ms
        if padding_ms > 0:
            silence = AudioSegment.silent(duration=padding_ms)
            audio = audio + silence
        audio.export(output_wav, format='wav')


async def synthesize_segment(text: str, voice: str, out_path: str) -> None:
    """Use edge-tts to synthesize a single text segment."""
    communicate = edge_tts.Communicate(text, voice)
    # edge-tts outputs MP3; we'll save as mp3 then convert
    mp3_path = out_path.replace('.wav', '.mp3')
    await communicate.save(mp3_path)
    # Convert MP3 → WAV
    subprocess.run([
        'ffmpeg', '-y', '-i', mp3_path, mp3_path.replace('.mp3', '.wav')
    ], capture_output=True, check=True)
    os.remove(mp3_path)


def build_timeline(entries: List[SrtEntry], voice: str, tmp_dir: str) -> AudioSegment:
    """Synthesize each entry, adjust timing, place on timeline."""
    if not entries:
        return AudioSegment.silent(duration=0)

    total_duration_ms = max(e.end_ms for e in entries)
    # Start with silence for the full duration
    timeline = AudioSegment.silent(duration=total_duration_ms + 1000)

    for i, entry in enumerate(entries):
        print(f"  [{i+1}/{len(entries)}] #{entry.index}: {entry.text[:30]}...")

        raw_wav = os.path.join(tmp_dir, f"seg_{i:04d}_raw.wav")
        adj_wav = os.path.join(tmp_dir, f"seg_{i:04d}_adj.wav")

        # Synthesize
        try:
            asyncio.run(synthesize_segment(entry.text, voice, raw_wav))
        except Exception as e:
            print(f"    Warning: TTS failed for entry {entry.index}: {e}")
            # Insert silence for this slot
            silence = AudioSegment.silent(duration=entry.duration_ms)
            timeline = timeline.overlay(silence, position=entry.start_ms)
            continue

        actual_ms = get_audio_duration_ms(raw_wav)
        target_ms = entry.duration_ms

        # Adjust duration
        try:
            adjust_audio_duration(raw_wav, adj_wav, target_ms, actual_ms)
        except Exception as e:
            print(f"    Warning: duration adjustment failed: {e}, using raw")
            adj_wav = raw_wav

        # Overlay onto timeline at start_ms
        segment_audio = AudioSegment.from_wav(adj_wav)
        timeline = timeline.overlay(segment_audio, position=entry.start_ms)

    return timeline


def main():
    parser = argparse.ArgumentParser(description='ZH SRT → time-synchronized TTS WAV')
    parser.add_argument('srt', help='Input Chinese SRT file')
    parser.add_argument('-v', '--voice', default='zh-CN-XiaoxiaoNeural',
                        help='edge-tts voice name (default: zh-CN-XiaoxiaoNeural)')
    parser.add_argument('-o', '--output', help='Output WAV path')
    parser.add_argument('--keep-temp', action='store_true', help='Keep temp segment files')
    args = parser.parse_args()

    srt_path = args.srt
    if not os.path.exists(srt_path):
        print(f"Error: SRT file not found: {srt_path}"); sys.exit(1)

    out_path = args.output or str(Path(srt_path).with_suffix('')) + '_tts.wav'
    print(f"Input SRT : {srt_path}")
    print(f"Voice     : {args.voice}")
    print(f"Output WAV: {out_path}\n")

    # Parse SRT
    print("Step 1/3: Parsing SRT...")
    entries = parse_srt(srt_path)
    print(f"  {len(entries)} subtitle entries")
    if not entries:
        print("Error: no subtitle entries found"); sys.exit(1)

    # Generate TTS segments
    print("\nStep 2/3: Synthesizing TTS segments...")
    work_ctx = None if args.keep_temp else tempfile.TemporaryDirectory(prefix='tts_gen_')
    work_dir = '.' if args.keep_temp else work_ctx.name
    try:
        timeline = build_timeline(entries, args.voice, work_dir)
    finally:
        if work_ctx:
            work_ctx.cleanup()

    # Export final WAV
    print(f"\nStep 3/3: Exporting WAV ({len(timeline)/1000:.1f}s)...")
    timeline.export(out_path, format='wav')
    print(f"\nDone: {out_path}")


if __name__ == '__main__':
    main()
```

### Step 3 — Run

```bash
python3 /tmp/tts_gen.py <input_zh.srt> [-v <voice>] [-o <output.wav>]
```

## Available Chinese Voices

| Voice | Style |
|-------|-------|
| `zh-CN-XiaoxiaoNeural` | Female, warm (default) |
| `zh-CN-YunxiNeural` | Male, natural |
| `zh-CN-XiaoyiNeural` | Female, lively |
| `zh-CN-YunyangNeural` | Male, news anchor |
| `zh-TW-HsiaoChenNeural` | Female, Traditional Chinese |

List all available voices:
```bash
python3 -c "import asyncio, edge_tts; asyncio.run(edge_tts.list_voices())" | python3 -c "import sys,json; [print(v['ShortName']) for v in json.load(sys.stdin) if 'zh' in v['ShortName']]"
```

## Timing Algorithm Details

For each SRT entry `[start_ms, end_ms, text]`:
1. Synthesize → raw WAV segment (actual duration may differ from slot)
2. Measure actual duration vs. slot duration (`end_ms - start_ms`)
3. If `actual > slot`: speed up with `ffmpeg atempo` (cap at 1.3x)
4. If `actual < slot`: pad end with silence
5. Overlay segment at `start_ms` on the silent timeline

Result: a single WAV that is synchronized to the subtitle timestamps.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-v` / `--voice` | `zh-CN-XiaoxiaoNeural` | Edge TTS voice name |
| `-o` / `--output` | `<srt_basename>_tts.wav` | Output WAV path |
| `--keep-temp` | off | Keep per-segment temp files for debugging |

## Example

```bash
# Basic usage
python3 /tmp/tts_gen.py video_en_zh.srt

# Custom voice and output
python3 /tmp/tts_gen.py video_en_zh.srt -v zh-CN-YunxiNeural -o dubbed_audio.wav
```
