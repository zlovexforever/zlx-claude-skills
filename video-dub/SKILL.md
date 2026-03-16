---
name: video-dub
description: Download a YouTube video (or use a local file), replace the original audio with a Chinese TTS WAV track, and produce 3 output files: original video, ZH dubbed without subtitles, ZH dubbed with hard-burned subtitles. Use this skill when the user wants to create a Chinese-dubbed video, or asks for "视频配音", "中文配音", "替换音轨", "烧入字幕" requests. Also triggers as the final step of the YouTube dubbing pipeline after tts-gen produces a ZH WAV.
---

# Video Dubbing Tool → 3 Outputs

Given a YouTube URL (or local video), a ZH TTS WAV, and a ZH SRT, produce:

| File | Contents |
|------|----------|
| `<prefix>_original.mp4` | Best quality, original audio (reference copy) |
| `<prefix>_zh_nosub.mp4` | Best quality, ZH TTS audio, no subtitles |
| `<prefix>_zh.mp4` | Best quality, ZH TTS audio, hard-burned ZH subtitles |

For YouTube sources, the default `prefix` should be a filesystem-safe `title_slug__video_id`, not just the raw video ID. That keeps outputs readable without losing a stable identity.

## Dependencies

```bash
pip install yt-dlp Pillow
brew install ffmpeg        # macOS (no libass needed — uses Pillow overlay)
```

## How to Use This Skill

### Inputs
- **Video source**: YouTube URL *or* local video file path
- **ZH TTS audio**: WAV from `tts-gen`
- **ZH subtitles**: SRT from `subtitle-translate`
- **Output directory**: folder to save all 3 files

### Step 1 — Check dependencies

```bash
yt-dlp --version 2>/dev/null || pip install yt-dlp
python3 -c "import PIL" 2>/dev/null || pip3 install Pillow --break-system-packages
ffmpeg -version 2>/dev/null | head -1
```

### Step 2 — Write the script

Write the following to `/tmp/video_dub.py`:

```python
#!/usr/bin/env python3
"""
video_dub.py — Full Chinese dubbing pipeline. Produces 3 output files:
  <prefix>_original.mp4   — original video, best quality, original audio
  <prefix>_zh_nosub.mp4   — best quality video + ZH TTS audio, no subtitles
  <prefix>_zh.mp4         — best quality video + ZH TTS audio + hard-burned ZH subtitles

Subtitle burning: Pillow renders each entry as transparent RGBA PNG,
ffmpeg overlay chain composites them frame-accurately (no libass needed).
"""
import subprocess, sys, os, argparse, re, tempfile, json, unicodedata
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

def find_cjk_font():
    return next((f for f in FONT_CANDIDATES if os.path.exists(f)), None)

def parse_srt(path):
    entries = []
    for block in re.split(r'\n\s*\n', Path(path).read_text(encoding='utf-8').strip()):
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0])
        except ValueError:
            continue
        m = re.match(
            r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})',
            lines[1])
        if not m:
            continue
        g = m.groups()
        def ms(h, mi, s, ms_): return int(h)*3600000+int(mi)*60000+int(s)*1000+int(ms_)
        entries.append({'index': idx, 'start_ms': ms(*g[:4]),
                        'end_ms': ms(*g[4:]), 'text': ' '.join(lines[2:])})
    return entries

def get_video_info(path):
    r = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json',
                        '-show_streams', path], capture_output=True, text=True)
    for s in json.loads(r.stdout).get('streams', []):
        if s.get('codec_type') == 'video':
            w, h = s.get('width', 1280), s.get('height', 720)
            num, den = s.get('r_frame_rate', '25/1').split('/')
            return w, h, float(num) / float(den)
    return 1280, 720, 25.0

def render_subtitle_png(text, video_w, video_h, font_path, out_path,
                         font_size=32, y_offset=55):
    lines = text.split('\n') if '\n' in text else [text]
    img = Image.new('RGBA', (video_w, video_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, font_size, index=0)
    except Exception:
        font = ImageFont.load_default()
    line_h = font_size + 6
    y_start = video_h - line_h * len(lines) - y_offset
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (video_w - text_w) // 2
        y = y_start + i * line_h
        for dx in [-2, -1, 1, 2]:
            for dy in [-2, -1, 1, 2]:
                draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0, 230))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    img.save(out_path, 'PNG')

def burn_subtitles_pillow(input_mp4, srt_path, output_mp4, work_dir):
    if not HAS_PILLOW:
        print("  Pillow not available"); return False
    font_path = find_cjk_font()
    if not font_path:
        print("  No CJK font found"); return False
    print(f"  Font: {Path(font_path).name}")
    entries = parse_srt(srt_path)
    if not entries:
        return False
    w, h, fps = get_video_info(input_mp4)
    print(f"  Video: {w}x{h} @ {fps:.2f}fps, {len(entries)} subtitles")
    png_dir = os.path.join(work_dir, 'sub_pngs')
    os.makedirs(png_dir, exist_ok=True)
    png_paths = []
    for i, e in enumerate(entries):
        p = os.path.join(png_dir, f'sub_{i:04d}.png')
        render_subtitle_png(e['text'], w, h, font_path, p, font_size=32)
        png_paths.append(p)
    print(f"  Rendered {len(png_paths)} subtitle PNGs")
    inputs = ['-i', input_mp4]
    for p in png_paths:
        inputs += ['-i', p]
    filter_parts = []
    for i, e in enumerate(entries):
        in_v  = f"[v{i-1}]" if i > 0 else "[0:v]"
        out_v = f"[v{i}]"
        t0, t1 = e['start_ms']/1000, e['end_ms']/1000
        filter_parts.append(
            f"{in_v}[{i+1}:v]overlay=0:0:enable='between(t,{t0:.3f},{t1:.3f})'{out_v}"
        )
    print(f"  Running ffmpeg overlay chain ({len(entries)} nodes)...")
    result = subprocess.run(
        ['ffmpeg', '-y'] + inputs + [
            '-filter_complex', ';'.join(filter_parts),
            '-map', f"[v{len(entries)-1}]",
            '-map', '0:a:0',
            '-c:v', 'libx264', '-crf', '18', '-preset', 'fast',
            '-c:a', 'copy',
            output_mp4
        ], capture_output=True, text=True, timeout=1800)
    if result.returncode != 0:
        print(f"  overlay error:\n{result.stderr[-800:]}"); return False
    print(f"  Hard-burned → {Path(output_mp4).name}")
    return True

def embed_subtitles_soft(input_mp4, srt_path, output_mp4):
    print("  Fallback: soft subtitle track (mov_text)...")
    r = subprocess.run([
        'ffmpeg', '-y', '-i', input_mp4, '-i', srt_path,
        '-c:v', 'copy', '-c:a', 'copy', '-c:s', 'mov_text',
        '-metadata:s:s:0', 'language=zho', '-metadata:s:s:0', 'title=Chinese',
        output_mp4
    ], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  Error:\n{r.stderr[-1000:]}"); sys.exit(1)
    print(f"  Soft subtitles → {Path(output_mp4).name}")

def extract_video_id(url):
    m = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else 'video'

def slugify_title(title, fallback):
    normalized = unicodedata.normalize('NFKD', title).strip().lower()
    ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '-', ascii_text).strip('-')
    slug = re.sub(r'-+', '-', slug)
    if not slug:
        slug = fallback
    return slug[:80].rstrip('-')

def fetch_video_title(url):
    r = subprocess.run([
        'yt-dlp', '--no-playlist', '--print', '%(title)s', url
    ], capture_output=True, text=True, timeout=60)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return r.stdout.strip().splitlines()[0].strip()

def download_original(url, output_path):
    print(f"  Downloading original (bestvideo+bestaudio)...")
    r = subprocess.run([
        'yt-dlp', '-f', 'bestvideo+bestaudio/best',
        '--merge-output-format', 'mp4',
        '--no-playlist', '-o', output_path, url
    ], capture_output=True, text=True, timeout=1200)
    if r.returncode != 0:
        print(f"  yt-dlp error:\n{r.stderr}"); sys.exit(1)
    probe = subprocess.run([
        'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name,width,height',
        '-of', 'default=noprint_wrappers=1', output_path
    ], capture_output=True, text=True)
    print(f"  → {Path(output_path).name}")
    for line in probe.stdout.strip().splitlines():
        print(f"    {line}")

def merge_zh_audio(original_mp4, audio_wav, output_path):
    r = subprocess.run([
        'ffmpeg', '-y',
        '-i', original_mp4, '-i', audio_wav,
        '-map', '0:v:0', '-map', '1:a:0',
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
        '-shortest', output_path
    ], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  ffmpeg error:\n{r.stderr[-2000:]}"); sys.exit(1)
    print(f"  → {Path(output_path).name}")

def main():
    ap = argparse.ArgumentParser(
        description='YouTube → 3 outputs: original / ZH nosub / ZH with hard-burned subtitles')
    ap.add_argument('source', help='YouTube URL or local video file')
    ap.add_argument('--audio',     required=True, help='ZH TTS WAV (from tts-gen)')
    ap.add_argument('--srt',       required=True, help='ZH SRT subtitle file')
    ap.add_argument('--outdir',    default='.', help='Output directory')
    ap.add_argument('--prefix',    help='Filename prefix (default: title_slug__video_id for YouTube)')
    ap.add_argument('--soft-subs', action='store_true', help='Force soft subtitle track')
    ap.add_argument('--keep-temp', action='store_true')
    args = ap.parse_args()

    for cmd in ['yt-dlp', 'ffmpeg']:
        try: subprocess.run([cmd, '--version'], capture_output=True, timeout=10)
        except FileNotFoundError:
            print(f"Error: {cmd} not found"); sys.exit(1)
    for p, lbl in [(args.audio, 'WAV'), (args.srt, 'SRT')]:
        if not os.path.exists(p):
            print(f"Error: {lbl} not found: {p}"); sys.exit(1)

    is_url = args.source.startswith('http')
    vid    = extract_video_id(args.source) if is_url else Path(args.source).stem
    if args.prefix:
        prefix = args.prefix
    elif is_url:
        title = fetch_video_title(args.source)
        prefix = f"{slugify_title(title or vid, vid)}__{vid}"
    else:
        prefix = Path(args.source).stem
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    out_original = os.path.join(outdir, f"{prefix}_original.mp4")
    out_nosub    = os.path.join(outdir, f"{prefix}_zh_nosub.mp4")
    out_subbed   = os.path.join(outdir, f"{prefix}_zh.mp4")

    print(f"\nSource : {args.source}")
    print(f"Audio  : {args.audio}")
    print(f"SRT    : {args.srt}")
    print(f"Outdir : {outdir}")
    print(f"\nOutputs:")
    print(f"  {Path(out_original).name}  ← original video + original audio")
    print(f"  {Path(out_nosub).name}  ← ZH audio, no subtitles")
    print(f"  {Path(out_subbed).name}        ← ZH audio + hard-burned subtitles\n")

    work_ctx = None if args.keep_temp else tempfile.TemporaryDirectory(prefix='vdub_')
    work_dir = '/tmp/vdub_debug' if args.keep_temp else work_ctx.name
    if args.keep_temp: os.makedirs(work_dir, exist_ok=True)

    try:
        print("Step 1/3: Original video (best quality, original audio)...")
        if is_url:
            download_original(args.source, out_original)
        else:
            import shutil
            shutil.copy2(args.source, out_original)
            print(f"  Copied → {Path(out_original).name}")

        print("\nStep 2/3: ZH dubbed, no subtitles...")
        merge_zh_audio(out_original, args.audio, out_nosub)

        print("\nStep 3/3: Burning subtitles...")
        if args.soft_subs:
            embed_subtitles_soft(out_nosub, args.srt, out_subbed)
        else:
            if not burn_subtitles_pillow(out_nosub, args.srt, out_subbed, work_dir):
                print("  Pillow failed → soft subtitle fallback")
                embed_subtitles_soft(out_nosub, args.srt, out_subbed)
    finally:
        if work_ctx: work_ctx.cleanup()

    print("\n── Done ─────────────────────────────────────────────────────────")
    for p in [out_original, out_nosub, out_subbed]:
        mb = os.path.getsize(p) / 1024 / 1024
        print(f"  {Path(p).name:45s} {mb:6.1f} MB")

if __name__ == '__main__':
    main()
```

### Step 3 — Run

```bash
python3 /tmp/video_dub.py "<YouTube_URL>" \
    --audio <zh_tts.wav> \
    --srt   <zh_subtitles.srt> \
    --outdir <output_folder> \
    [--prefix <name>]
```

## Full Pipeline Example

```bash
# 1. Download EN subtitles (default behavior already prefers English)
python3 /tmp/youtube_srt.py "https://youtu.be/VIDEO_ID"

# 2. Translate (subtitle-translate skill → produces VIDEO_ID_en_zh.srt)

# 3. Generate TTS audio
python3 /tmp/tts_gen.py MY-TITLE__VIDEO_ID_zh.srt -o MY-TITLE__VIDEO_ID_zh_tts.wav

# 4. Full dubbing pipeline → 3 outputs in output folder
mkdir -p ~/Desktop/MY-TITLE__VIDEO_ID_zh
python3 /tmp/video_dub.py "https://youtu.be/VIDEO_ID" \
    --audio MY-TITLE__VIDEO_ID_zh_tts.wav \
    --srt   MY-TITLE__VIDEO_ID_zh.srt \
    --outdir ~/Desktop/MY-TITLE__VIDEO_ID_zh
```

## Output Files

| File | Description |
|------|-------------|
| `<prefix>_original.mp4` | Original YouTube video, best quality, original audio |
| `<prefix>_zh_nosub.mp4` | ZH dubbed, no subtitles (clean for re-editing) |
| `<prefix>_zh.mp4` | ZH dubbed + hard-burned Chinese subtitles (final delivery) |

## Subtitle Burning — Technical Notes

- **No libass required** — uses Pillow (Python) to render each subtitle entry as a transparent RGBA PNG
- Each PNG is overlaid onto the video at its exact time window via ffmpeg `overlay=enable='between(t,...)'`
- Font: `STHeiti Medium.ttc` (macOS) → fallbacks for Linux (Noto CJK, WQY Zenhei)
- Video is re-encoded with `libx264 -crf 18` only for the subtitled version; original and nosub use stream copy

## Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `source` | — | YouTube URL or local video path |
| `--audio` | — | ZH TTS WAV file |
| `--srt` | — | ZH SRT subtitle file |
| `--outdir` | `.` | Output directory |
| `--prefix` | `<title_slug>__<video_id>` for YouTube, local stem for local file | Output filename prefix |
| `--soft-subs` | off | Force soft subtitle track (skip Pillow burn) |
| `--keep-temp` | off | Keep temp PNG files for debugging |
