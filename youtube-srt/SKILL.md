---
name: youtube-srt
description: Download YouTube subtitles for a single target video and convert them into clean, non-overlapping SRT files with proper sentence segmentation. Use this skill whenever the user provides a YouTube URL and wants subtitles extracted as SRT, especially when the URL may contain playlist/query parameters and you need to avoid downloading the wrong video. Also triggers for "字幕下载", "YouTube 字幕", "视频字幕转 SRT" requests.
---

# YouTube Subtitle -> SRT Converter

Download subtitles for one specific YouTube video and convert them into a clean SRT.

The important part is not just "download some subtitles" - it is downloading subtitles for the exact requested video, even when the user pastes a playlist URL such as `watch?v=...&list=...`.

For the Chinese-video workflow, the default should be English subtitles first. Chinese subtitles are still available when explicitly requested, but the default path should feed `subtitle-translate` instead of relying on YouTube's auto-translated Chinese captions.

## Use This Skill When

- The user gives a YouTube URL and wants subtitles or captions.
- The URL may include `list=`, `index=`, `si=`, or other extra query parameters.
- The deliverable should be a local `.srt` file.

## Dependency Check

```bash
yt-dlp --version 2>/dev/null || pip install yt-dlp
```

## Implementation

Write the following script to `/tmp/youtube_srt.py` and run it.

```python
#!/usr/bin/env python3

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class Word:
    text: str
    start_ms: int
    end_ms: int


@dataclass
class SrtEntry:
    index: int
    start_ms: int
    end_ms: int
    text: str

    def to_srt(self) -> str:
        return (
            f"{self.index}\n"
            f"{ms_to_srt_time(self.start_ms)} --> {ms_to_srt_time(self.end_ms)}\n"
            f"{self.text}\n"
        )


def ms_to_srt_time(ms: int) -> str:
    ms = max(0, int(ms))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def check_yt_dlp() -> bool:
    try:
        return subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=10).returncode == 0
    except Exception:
        return False


def is_cjk_char(char: str) -> bool:
    cp = ord(char)
    return (
        0x4E00 <= cp <= 0x9FFF
        or 0x3040 <= cp <= 0x30FF
        or 0xAC00 <= cp <= 0xD7AF
        or 0x3400 <= cp <= 0x4DBF
        or 0x20000 <= cp <= 0x2A6DF
        or 0xFF00 <= cp <= 0xFFEF
    )


def display_width(text: str) -> int:
    return sum(2 if is_cjk_char(c) else 1 for c in text)


def is_sentence_end(text: str) -> bool:
    stripped = text.rstrip()
    return bool(stripped) and stripped[-1] in ".!?。！？…"


def clean_text(text: str, collapse_newlines: bool = False) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    if collapse_newlines:
        text = re.sub(r" {2,}", " ", text.replace("\n", " "))
    else:
        lines = [re.sub(r" {2,}", " ", line).strip() for line in text.split("\n")]
        text = "\n".join(line for line in lines if line)
    return text.strip()


def slugify_title(title: str, fallback: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).strip().lower()
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        slug = fallback
    return slug[:80].rstrip("-")


def fetch_video_title(url: str) -> str:
    result = subprocess.run(
        ["yt-dlp", "--no-playlist", "--print", "%(title)s", url],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    title = result.stdout.strip().splitlines()[0].strip()
    if not title:
        raise RuntimeError("Could not fetch video title.")
    return title


def list_available_subs(url: str) -> None:
    subprocess.run(["yt-dlp", "--list-subs", "--no-playlist", url], timeout=60)


def cleanup_json3(output_dir: str) -> None:
    for path in Path(output_dir).glob("*.json3"):
        path.unlink(missing_ok=True)


def download_subtitles(url: str, language: str, output_dir: str, expected_video_id: Optional[str]) -> Optional[Tuple[str, str]]:
    cleanup_json3(output_dir)
    output_template = os.path.join(output_dir, "%(id)s")
    base_cmd = [
        "yt-dlp",
        "--skip-download",
        "--no-playlist",
        "--sub-lang",
        language,
        "--sub-format",
        "json3",
        "--output",
        output_template,
    ]

    for flags, label in ((["--write-subs"], "manual"), (["--write-auto-subs"], "auto-generated")):
        print(f"Trying {label} subtitles for exact video...")
        try:
            result = subprocess.run(base_cmd + flags + [url], capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            print("Timed out.")
            continue
        files = sorted(Path(output_dir).glob("*.json3"))
        if not files:
            if result.stderr:
                print(result.stderr.strip().splitlines()[-1])
            continue
        chosen = files[0]
        parts = chosen.name.split(".")
        actual_video_id = parts[0]
        actual_language = parts[1] if len(parts) > 2 else language
        if expected_video_id and actual_video_id != expected_video_id:
            cleanup_json3(output_dir)
            raise RuntimeError(
                f"Downloaded subtitles for {actual_video_id}, but expected {expected_video_id}. "
                "Use the exact watch URL and keep --no-playlist enabled."
            )
        return str(chosen), actual_language
    return None


def resolve_language_candidates(explicit_language: Optional[str]) -> List[str]:
    if explicit_language:
        return [explicit_language]
    return ["en-orig", "en", "en-US", "en-GB"]


def parse_json3_to_words(filepath: str) -> List[Word]:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_words: List[Word] = []
    prev_seg_texts: List[str] = []
    for event in data.get("events", []):
        start_ms = event.get("tStartMs", 0)
        dur_ms = event.get("dDurationMs", 0)
        end_ms = start_ms + dur_ms
        segs = event.get("segs", [])
        if not segs:
            continue

        event_text = "".join(seg.get("utf8", "") for seg in segs)
        if not event_text.replace("\n", "").strip():
            prev_seg_texts = []
            continue

        has_word_timing = any("tOffsetMs" in seg for seg in segs if seg.get("utf8", "").strip())
        seg_entries: List[Tuple[str, int, int]] = []

        if has_word_timing:
            timed = [
                (seg.get("utf8", ""), start_ms + seg.get("tOffsetMs", 0))
                for seg in segs
                if seg.get("utf8", "") and seg.get("utf8", "") != "\n"
            ]
            for i, (text, word_start) in enumerate(timed):
                word_end = timed[i + 1][1] if i + 1 < len(timed) else end_ms
                seg_entries.append((text, word_start, word_end))
        else:
            cleaned = clean_text("".join(seg.get("utf8", "") for seg in segs), collapse_newlines=False)
            if cleaned:
                seg_entries.append((cleaned, start_ms, end_ms))

        current_seg_texts = [text for text, _, _ in seg_entries]
        skip = 0
        if prev_seg_texts and has_word_timing:
            for overlap in range(min(len(prev_seg_texts), len(current_seg_texts)), 0, -1):
                if prev_seg_texts[-overlap:] == current_seg_texts[:overlap]:
                    skip = overlap
                    break

        for text, seg_start, seg_end in seg_entries[skip:]:
            cleaned = clean_text(text, collapse_newlines=has_word_timing)
            if cleaned:
                all_words.append(Word(cleaned, seg_start, seg_end))

        prev_seg_texts = current_seg_texts
    return all_words


def words_to_srt_entries(words: List[Word], max_display_width: int = 40, max_duration_ms: int = 7000, min_pause_ms: int = 400) -> List[SrtEntry]:
    entries: List[SrtEntry] = []
    group: List[Word] = []
    group_start: Optional[int] = None

    def flush() -> None:
        nonlocal group_start
        if group:
            text = "".join(word.text for word in group).strip()
            if text:
                entries.append(SrtEntry(len(entries) + 1, group_start, group[-1].end_ms, text))
        group.clear()
        group_start = None

    for word in words:
        if not group:
            group_start = word.start_ms
            group.append(word)
            continue
        current = "".join(w.text for w in group)
        pause = word.start_ms - group[-1].end_ms
        duration = group[-1].end_ms - group_start
        should_split = (
            is_sentence_end(current)
            or pause >= min_pause_ms
            or display_width((current + word.text).strip()) > max_display_width
            or duration >= max_duration_ms
        )
        if should_split:
            flush()
            group_start = word.start_ms
        group.append(word)
    flush()
    return entries


def ensure_no_overlap(entries: List[SrtEntry], gap_ms: int = 40) -> List[SrtEntry]:
    fixed = list(entries)
    for i in range(len(fixed) - 1):
        if fixed[i].end_ms >= fixed[i + 1].start_ms:
            fixed[i] = SrtEntry(
                fixed[i].index,
                fixed[i].start_ms,
                max(fixed[i].start_ms + 1, fixed[i + 1].start_ms - gap_ms),
                fixed[i].text,
            )
    return fixed


def write_srt(entries: List[SrtEntry], output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(entry.to_srt())
            f.write("\n")
    print(f"Written: {output_path} ({len(entries)} entries)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download subtitles for one exact YouTube video and convert to clean SRT")
    parser.add_argument("url")
    parser.add_argument("-l", "--language", default=None)
    parser.add_argument("-o", "--output")
    parser.add_argument("--max-chars", type=int, default=40)
    parser.add_argument("--max-duration", type=int, default=7000)
    parser.add_argument("--min-pause", type=int, default=400)
    parser.add_argument("--list-subs", action="store_true")
    args = parser.parse_args()

    if not check_yt_dlp():
        print("yt-dlp not found. Install it first.")
        sys.exit(1)

    if args.list_subs:
        list_available_subs(args.url)
        return

    expected_video_id = extract_video_id(args.url)
    if not expected_video_id:
        print("Could not extract video ID from the YouTube URL.")
        sys.exit(1)

    try:
        title = fetch_video_title(args.url)
    except Exception as exc:
        print(f"Failed to fetch video title: {exc}")
        sys.exit(1)

    title_slug = slugify_title(title, expected_video_id)

    with tempfile.TemporaryDirectory(prefix="yt_srt_") as work_dir:
        json3_file = None
        actual_language = None
        for candidate in resolve_language_candidates(args.language):
            result = download_subtitles(args.url, candidate, work_dir, expected_video_id)
            if result:
                json3_file, actual_language = result
                break
        if not json3_file:
            wanted = args.language or "preferred English subtitles"
            print(f"No subtitles found for '{wanted}'.")
            sys.exit(1)
        words = parse_json3_to_words(json3_file)
        if not words:
            print("Subtitle file is empty after parsing.")
            sys.exit(1)
        entries = words_to_srt_entries(words, args.max_chars, args.max_duration, args.min_pause)
        entries = ensure_no_overlap(entries)
        output_path = args.output or f"{title_slug}__{expected_video_id}_{actual_language}.srt"
        write_srt(entries, output_path)


if __name__ == "__main__":
    main()
```

## Run

```bash
python3 /tmp/youtube_srt.py "https://www.youtube.com/watch?v=VIDEO_ID&list=SOME_PLAYLIST"
```

## Why This Version Is Safer

- It always uses `--no-playlist` so a playlist URL does not silently jump to a different video.
- It extracts the requested video ID from the URL and verifies the downloaded subtitle file matches it.
- It fetches the video title and builds a filesystem-safe `title_slug__video_id` output name.
- It prefers English subtitles by default so downstream translation is consistent and glossary-driven.
- It clears stale `json3` temp files before each attempt, so previous runs do not contaminate results.
- It still keeps the useful parts of the old workflow: rolling-caption deduplication, sentence grouping, CJK-aware width, and overlap trimming.

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `-l` / `--language` | preferred English | Subtitle language code. If omitted, tries `en-orig`, `en`, `en-US`, `en-GB` in order |
| `-o` / `--output` | `<title_slug>__<video_id>_<lang>.srt` | Output path |
| `--max-chars` | `40` | Max display width per subtitle |
| `--max-duration` | `7000` | Max subtitle duration in ms |
| `--min-pause` | `400` | Silence threshold for forced split |
| `--list-subs` | off | List available subtitle languages |

## Common Invocations

```bash
# Default behavior: prefer English subtitles for one exact video
python3 /tmp/youtube_srt.py "https://www.youtube.com/watch?v=xm5uooQJL-Y&list=PL..."

# Explicit Simplified Chinese subtitles if the target video provides them
python3 /tmp/youtube_srt.py "https://youtu.be/xm5uooQJL-Y" -l zh-Hans -o my-video__xm5uooQJL-Y_zh-Hans.srt

# Inspect available subtitle languages first
python3 /tmp/youtube_srt.py "https://www.youtube.com/watch?v=xm5uooQJL-Y" --list-subs
```

## Output Expectations

- The output `.srt` should belong to the requested video ID.
- The default filename should contain both a human-readable title slug and the exact video ID.
- Adjacent subtitles must not overlap.
- Auto-generated rolling captions should be deduplicated rather than repeated line by line.
