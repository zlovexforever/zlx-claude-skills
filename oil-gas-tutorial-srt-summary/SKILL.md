---
name: oil-gas-tutorial-srt-summary
description: Convert Whisper or other ASR-generated SRT subtitles from professional software tutorial videos into structured, high-quality Markdown study notes. Use whenever the user asks to summarize tutorial subtitles, turn SRT into Markdown notes, extract操作步骤 from video captions,整理 Petrel/CMG/Eclipse/PIPESIM/Prosper 等专业软件教学视频字幕, or wants a clean knowledge note from pasted subtitle text. Also use this skill for batch processing many SRT files, especially when the user needs stable output quality across large subtitle collections. This skill is especially appropriate for oil & gas exploration, reservoir engineering, geoscience, drilling, production, and technical training content.
---

# Oil & Gas Tutorial SRT Summary

Turn raw SRT subtitles into concise, structured Markdown notes for professional software tutorial videos.

This skill is optimized for:
- Whisper-generated subtitles with oral filler, repetition, and recognition noise
- Oil & gas technical software training content such as Petrel, Eclipse, CMG, PIPESIM, Prosper, Techlog, and similar tools
- Users who want reusable study notes, operation checklists, or content summaries rather than a transcript rewrite

## Core Goal

Produce a Markdown note that preserves the tutorial's real workflow, key software actions, important parameters, and domain meaning while aggressively removing spoken redundancy.

The output should read like notes written by:
- a senior oil & gas exploration/development specialist
- a technically precise software trainer
- a professional content creator who knows how to structure tutorials clearly

## Input Types

Accept any of these inputs:
- full SRT file content pasted into the prompt
- a `.srt` file path
- a subtitle excerpt that is clearly from a tutorial video
- a directory or file list containing many `.srt` files for batch processing

If the subtitle is incomplete, still summarize what is present. Do not invent missing content.

## Batch Processing First Principle

When the user provides many SRT files, do not process them all inside one growing conversational context.

The correct strategy is:
- isolate each file's reasoning
- write each file's result to disk before moving on
- carry forward only compact structured summaries, not raw subtitle text
- build any final batch overview from those compact summaries

This is essential because long batch runs otherwise degrade quality, consistency, and terminology precision.

## Mandatory Output Contract

In single-file mode, only output the final Markdown note.

In batch mode:
- write one final Markdown note per SRT file
- write batch artifacts such as manifest, sidecar summaries, and optional index files to disk
- when replying in chat, keep the response minimal and focus on completed outputs or current progress rather than dumping all generated notes inline

Do not include:
- preambles
- explanations of your method
- comments about what you omitted
- meta text such as "以下是总结" or "根据字幕整理"

The result must be valid Markdown.

## Required Markdown Structure

Always use this structure unless the input is too short to support multiple chapters:

```md
# <course name + tutorial title or inferred topic>

> 时长：<HH:MM:SS 或 MM:SS>  
> 核心要点：<1-2 句概括视频内容、软件目标、关键方法或流程>

## <章节标题>（MM:SS – MM:SS）
- **`MM:SS`** — <动作/概念释义>
- **`MM:SS`** — <动作/概念释义>

> ⚠️ 操作提示：<视频中明确强调的风险点、易错点、顺序要求或特殊习惯>

## <章节标题>（MM:SS – MM:SS）
- **`MM:SS`** — <动作/概念释义>
```

## Formatting Rules

### 1) Top Summary Block

At the top:
- Use one `#` title
- Follow with a short blockquote summary
- The blockquote must contain:
  - total video duration
  - a concise statement of the main knowledge covered

If the exact total duration is unclear, use the latest reliable timestamp visible in the subtitles and avoid pretending precision.

### 1.5) Course Name Is Mandatory In Title

The H1 title must include the course name or series name at the beginning whenever it is inferable from any reliable context.

Reliable sources include:
- explicit course/video title in the subtitle
- parent folder name
- batch/project name
- repeated series naming in neighboring files
- file name prefix or lesson naming convention

Required pattern:
- `# <课程名>：<本节主题>`

Examples:
- `# Petrel 2023 培训：Make Surface 与厚度图制作`
- `# CMG 历史拟合课程：生产数据导入与参数调整`

Rules:
- if both course name and lesson topic are known, both must appear
- do not output only the lesson topic when the course name is inferable
- in batch mode, keep the same course-name prefix across the whole batch unless a file clearly belongs to a different course
- if the exact official course name is unavailable, use the most stable, high-confidence inferred series name rather than omitting it

### 2) Chaptering

Split the note into natural sections using `##`.

Chapter boundaries should follow:
- workflow stage changes
- interface area changes
- tool or module switching
- parameter tuning stage changes
- interpretation shift from operation to theory, or from setup to execution

Each chapter title must end with a time range like:
- `## Pillar Gridding 基础设置（00:00 – 04:32）`

Do not create chapters mechanically every N minutes. Follow the actual tutorial logic.

### 3) Timestamped Bullet Format

Inside each chapter, every bullet must use this exact pattern:

```md
- **`MM:SS`** — 动作/概念释义
```

Rules:
- timestamp must be backticked
- timestamp must be bolded together with the backticks
- separator must be an em dash `—`
- description must be compressed, specific, and actionable

### 4) Warning Callouts

For mistakes, non-obvious software habits, irreversible operations, or trainer emphasis, use:

```md
> ⚠️ 操作提示：先点 Run 再点 OK，否则参数不会真正执行。
```

Use this specifically for cases like:
- "先点 Run 再点 OK"
- parameters that must be adjusted before running a process
- special Petrel habits or hidden interface behavior
- steps where wrong order causes wrong model/result
- cases where geological applicability matters

## Content Compression Rules

Transform speech into notes, not transcript prose.

### Keep
- actual software actions
- click paths and menus
- key parameters
- reasoning behind parameter choices
- geological applicability or modeling context
- output/result interpretation
- troubleshooting advice mentioned in the video

### Remove or compress
- greetings and filler
- repeated restatements
- vague encouragement
- word-by-word spoken transitions
- duplicated explanation that adds no new meaning

### Compression Standard

Each bullet should capture one of these:
- a concrete operation
- a key concept
- a parameter rule
- a result interpretation
- an expert warning

Prefer short, dense sentences over paragraph-style bullets.

## Operation Path Extraction

Whenever the subtitle implies UI navigation, rewrite it as a clear click path using `→`.

Examples:
- `Processes → Make Surface`
- `Pillar Gridding → Expert`
- `Input Pane → Fault Model → Horizon Stack`
- `Settings → Geometry → Rotation Angle`

Do this even if the original subtitle says it conversationally.

Bad:
- "然后我们点到 expert 那里去设置一下"

Good:
- `Pillar Gridding → Expert` 中调整高级网格参数。

## Parameter Extraction Standard

Do not merely list parameters. Explain:
- what the parameter controls
- how the instructor adjusts it
- why that setting is chosen
- which geological or engineering scenario it fits

For example, if the video mentions `Rotation Angle`, summarize along these lines when supported by the subtitle:
- how the angle aligns the grid or model orientation
- why it should follow structure trend / fault trend / well pattern direction
- what happens if it is set incorrectly

If the video provides a value, keep it.
If the video provides only a qualitative rule, summarize the rule.
Do not fabricate numeric values.

## Domain Interpretation Rules

Because this skill is for oil & gas technical content, always preserve domain meaning.

Pay attention to:
- structural modeling
- fault interpretation
- pillar gridding
- upscaling
- well correlation
- property modeling
- reservoir simulation setup
- production engineering workflows
- well completion and artificial lift context

When a software step has geological significance, say so briefly.

Examples:
- not just "set grid orientation"
- but "设置网格方向，使其顺应主构造走向，减少后续属性建模与井网对齐误差"

## Handling Recognition Noise

Whisper subtitles may contain:
- broken sentences
- repeated phrases
- wrong punctuation
- homophone errors
- mixed English/Chinese UI terms

Normalize them using context.

Principles:
- keep software names in their standard form
- correct obvious ASR noise when confidence is high
- preserve uncertainty instead of guessing when meaning is genuinely unclear
- if a line cannot be trusted, summarize only the reliable portion

## Title Inference

For the main title:
- prefer the explicit course/video title if present
- otherwise infer from folder/batch/neighboring-file context and combine it with the dominant lesson topic
- when a course or series name is inferable, it is mandatory to prepend it to the lesson title

Good title patterns:
- `# Petrel 2023 培训：Pillar Gridding 与断层网格设置`
- `# CMG 历史拟合教程：生产数据导入与参数调整`
- `# PIPESIM 井筒建模课程：流体参数与敏感性分析`

Avoid generic titles like:
- `# 视频总结`
- `# 字幕笔记`
- `# Make Surface`
- `# 属性操作部分`

## Quality Bar

Before finalizing, make sure the note is:
- structurally clean
- technically faithful
- compressed but complete
- focused on reusable knowledge
- valid Markdown with no broken formatting

## Output Checklist

Ensure all of the following are true:
- has one title
- has a top blockquote summary with duration and core points
- uses `##` chapters with time ranges
- uses timestamped bullets in the exact required format
- includes click paths with `→` where relevant
- includes parameters and their adjustment logic where present
- includes `> ⚠️ 操作提示：` blocks for emphasized pitfalls
- contains no irrelevant preamble or closing remarks

## Batch Mode Workflow

Use this workflow whenever the user wants many SRT files processed in one job.

### Stage 1: Build a Manifest

Create a manifest for the batch.

Track at least:
- source file path
- output markdown path
- processing status: `pending` / `completed` / `failed`
- short title or inferred topic
- optional notes for retry

This prevents duplicate work and makes interrupted runs resumable.

### Stage 2: Process One File at a Time

Never load multiple full SRT files into one summary pass.

For each file:
1. read only that single SRT
2. generate the final Markdown note for that file
3. write the Markdown note to disk immediately
4. extract a compact structured file-level summary
5. mark the manifest entry completed

Do not keep earlier files' raw subtitles in active context after they are written out.

### Stage 3: Emit a Compact Intermediate Summary

After each file is completed, preserve a short structured summary for later aggregation.

In batch mode, this compact summary must be written to disk immediately as a sidecar artifact, not kept only in temporary reasoning context.

The compact summary should contain only high-value fields such as:
- file name
- inferred title
- total duration
- main software/tool
- chapter list
- key operations
- critical parameters
- important warnings
- major domain topics

The compact summary should be short enough that dozens or hundreds of files can later be aggregated without reloading the full subtitles.

### Stage 4: Generate Batch Index Only From Summaries

If the user asks for a collection-level overview, generate it from the compact summaries rather than from all raw SRT files.

Valid batch-level outputs include:
- an index page of all generated notes
- a topic map by software or workflow
- a parameter checklist aggregated across files
- a study roadmap grouped by subject

Do not re-open every full SRT just to make the overview unless the user explicitly requests re-analysis.

## Batch Quality Protection Rules

### 1) File-Level Isolation

Treat each SRT file as an independent unit of reasoning.

This means:
- no cross-file context bleed
- no carrying over uncertain interpretations from earlier files
- no letting previous files bias chapter naming for later files unless terminology is intentionally standardized

### 2) Stable Terminology Layer

Keep terminology consistent across the batch by using a stable glossary or fixed naming convention.

Standardize:
- software product names
- module names
- oil & gas technical terms
- parameter names
- common UI paths

But do not force a term if the current file clearly uses a different official name.

### 3) Fixed Extraction Schema

Use the same extraction schema for every file before generating prose.

At minimum, extract these dimensions:
- title
- duration
- chapters
- actions
- click paths
- parameters
- warnings
- domain meaning

This keeps late-batch quality from drifting downward.

### 4) Immediate Persistence

Write results after each file instead of waiting until the whole batch is done.

This protects against:
- context loss
- partial session interruption
- repeated work after failure
- quality regression caused by delayed consolidation

### 5) Retry Failed Files Only

If part of the batch fails, retry only failed files.

Do not rerun completed files unless:
- the template changed
- the user requested a different format
- the file's original result is known to be bad

## Suggested Intermediate Summary Shape

When batch processing, it is often useful to save a compact sidecar summary per file before or alongside the final Markdown. The format can be JSON, YAML, or another structured form, but it should preserve only reusable distilled information.

Example shape:

```json
{
  "source_file": "lesson-03.srt",
  "title": "Petrel 构造建模：Pillar Gridding 与断层网格设置",
  "duration": "18:42",
  "software": ["Petrel"],
  "chapters": [
    {"title": "网格方向设置", "range": "00:00-04:32"},
    {"title": "Expert 参数调整", "range": "04:32-09:50"}
  ],
  "key_actions": [
    "Pillar Gridding → Expert",
    "Settings → Geometry → Rotation Angle"
  ],
  "parameters": [
    "Rotation Angle follows structural trend"
  ],
  "warnings": [
    "Run before OK"
  ],
  "topics": [
    "pillar gridding",
    "fault framework",
    "grid orientation"
  ]
}
```

The exact shape may vary, but the principle must stay the same: compact, structured, reusable.

## Batch Deliverable Patterns

When the user gives many files, prefer this output pattern:

1. generate one Markdown note per SRT file
2. optionally generate one batch index file
3. optionally generate one compact metadata file for recovery and later aggregation

Good naming examples:
- `lesson-01.md`
- `lesson-01.summary.json`
- `batch-index.md`
- `manifest.json`

## Long-Run Consistency Rules

For large batches, protect quality by enforcing these habits:
- do not improvise a new note style halfway through the batch
- do not let chapter title wording drift wildly unless content truly differs
- keep timestamp bullet format identical across all files
- keep warning block format identical across all files
- reuse the same standard for click-path extraction and parameter explanation

Consistency matters more in batch mode than in one-off mode.

## When to Aggregate Across Files

Cross-file aggregation is appropriate only after file-level notes are complete.

Good aggregation tasks:
- identify repeated workflows across videos
- compile the most common parameters and usage logic
- map which files belong to which software workflow
- produce a curriculum-like study order

Bad aggregation behavior:
- mixing raw subtitle fragments from many files into one live summary pass
- rewriting unfinished files from memory
- using earlier files' raw wording to fill gaps in later files

## Recovery Strategy For Very Large Batches

If the batch is very large, work in resumable chunks.

Recommended behavior:
- split the manifest into manageable subsets
- complete one subset fully before moving to the next
- update status after every file
- if interrupted, resume from the manifest instead of rescanning everything

This makes the process robust even when the overall collection is too large for one uninterrupted session.

## Example Prompt Triggers

This skill should be used for prompts like:
- "把这个 Petrel 教学视频的 SRT 整理成 markdown 笔记"
- "根据下面字幕总结操作步骤和参数逻辑"
- "把 Whisper 识别的教程字幕压缩成结构化学习笔记"
- "帮我整理这个专业软件视频字幕，突出点击路径和易错点"
- "把这段油气专业教学视频字幕转成适合 Obsidian 的 md 笔记"
- "批量把这个文件夹里的教程字幕都整理成 md"
- "我有 200 个 SRT，帮我逐个总结并做总目录"
- "批量处理这些 Petrel 教学字幕，避免后面的质量变差"
