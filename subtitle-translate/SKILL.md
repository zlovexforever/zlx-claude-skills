---
name: subtitle-translate
description: Translate an English SRT subtitle file into Chinese (Simplified). Use this skill when the user provides a .srt file and wants it translated to Chinese, or asks for "字幕翻译", "SRT 翻译", "英文字幕转中文" requests. Also triggers as part of the YouTube dubbing pipeline after youtube-srt produces an EN SRT. Specialized for petroleum engineering / reservoir simulation content (Petrel, CMG, Eclipse, geomechanics, etc.).
---

# SRT Subtitle Translator (EN → ZH)

Translate an English SRT file to Simplified Chinese, preserving all timestamps and entry indices.

**Default domain: Petroleum Engineering / Reservoir Simulation.** Apply the glossary and rules below unless the user specifies a different domain.

## Oil & Gas Terminology Glossary

Use these standard Chinese translations consistently. When a term appears in the source, always use the mapped translation — do not paraphrase or invent alternatives.

### Software & Platforms (keep English name, add Chinese label on first occurrence only)
| English | Chinese (first occurrence) | Subsequent |
|---------|---------------------------|------------|
| Petrel | Petrel（地质建模软件） | Petrel |
| Eclipse | Eclipse（油藏模拟器） | Eclipse |
| CMG / GEM / STARS / IMEX | CMG（数值模拟软件） | CMG |
| tNavigator | tNavigator | tNavigator |
| INTERSECT | INTERSECT | INTERSECT |
| Techlog | Techlog | Techlog |
| Pipesim | Pipesim | Pipesim |
| OLGA | OLGA | OLGA |
| ResInsight | ResInsight | ResInsight |
| OpenPNM | OpenPNM | OpenPNM |

### Reservoir Engineering
| English | Chinese |
|---------|---------|
| reservoir | 储层 / 油藏（描述岩石用"储层"，描述整体用"油藏"） |
| permeability | 渗透率 |
| porosity | 孔隙度 |
| saturation | 饱和度 |
| water saturation | 含水饱和度 |
| oil saturation | 含油饱和度 |
| relative permeability | 相对渗透率 |
| capillary pressure | 毛细管压力 |
| reservoir pressure | 油藏压力 |
| bottom hole pressure (BHP) | 井底压力（BHP） |
| flowing bottom hole pressure (FBHP) | 流动井底压力 |
| wellbore | 井筒 |
| production rate | 产量 |
| oil rate / water rate / gas rate | 产油量 / 产水量 / 产气量 |
| water cut | 含水率 |
| GOR (gas-oil ratio) | 气油比（GOR） |
| recovery factor / recovery | 采收率 |
| sweep efficiency | 波及效率 |
| displacement efficiency | 驱替效率 |
| material balance | 物质平衡 |
| aquifer | 含水层 |
| gas cap | 气顶 |
| drive mechanism | 驱动机制 |
| depletion drive | 弹性驱 |
| water drive | 水驱 |
| primary recovery | 一次采油 |
| secondary recovery | 二次采油 |
| enhanced oil recovery (EOR) | 提高采收率（EOR） |
| waterflooding | 水驱 / 注水开发 |
| polymer flooding | 聚合物驱 |
| CO₂ flooding | CO₂驱 |
| steamflooding | 蒸汽驱 |
| SAGD | SAGD（蒸汽辅助重力泄油） |
| well pattern | 井网 |
| injection well / producer | 注入井 / 生产井 |
| perforation | 射孔 |
| completion | 完井 |
| skin factor | 表皮系数 |
| productivity index (PI) | 产能指数（PI） |
| injectivity | 注入能力 |
| tubing / casing | 油管 / 套管 |

### Reservoir Simulation
| English | Chinese |
|---------|---------|
| simulation / simulator | 模拟 / 模拟器 |
| numerical simulation | 数值模拟 |
| history matching | 历史拟合 |
| forecast / prediction | 预测 |
| grid / gridblock / cell | 网格 / 网格块 / 网格单元 |
| corner-point grid | 角点网格 |
| structured grid | 结构网格 |
| unstructured grid | 非结构网格 |
| upscaling | 粗化 / 尺度升级 |
| transmissibility | 传导率 |
| time step | 时间步长 |
| Newton iteration | 牛顿迭代 |
| black oil model | 黑油模型 |
| compositional model | 组分模型 |
| thermal model | 热力学模型 |
| dual porosity / dual permeability | 双重孔隙度 / 双重渗透率 |
| fault / fault transmissibility | 断层 / 断层传导率 |
| aquifer model | 含水层模型 |
| PVT (pressure-volume-temperature) | PVT（压力-体积-温度） |
| SCAL (special core analysis) | 特殊岩心分析（SCAL） |
| run / simulation run | 模拟运行 |
| output / results | 输出 / 结果 |
| restart file | 重启文件 |
| include file | 包含文件 |
| keyword | 关键字 |
| deck / data file | 数据文件 |
| well constraint | 井约束条件 |
| group control | 组控制 |
| field | 油田 |
| platform | 平台 |

### Geology & Geomechanics
| English | Chinese |
|---------|---------|
| geomechanics | 地质力学 |
| geomechanical | 地质力学的 |
| stress / in-situ stress | 应力 / 原地应力 |
| effective stress | 有效应力 |
| minimum horizontal stress | 最小水平应力 |
| maximum horizontal stress | 最大水平应力 |
| vertical stress / overburden | 垂向应力 / 上覆地层压力 |
| pore pressure | 孔隙压力 |
| Biot coefficient | 比奥系数 |
| Young's modulus | 杨氏模量 |
| Poisson's ratio | 泊松比 |
| compressibility | 压缩系数 |
| geomechanical coupling | 地质力学耦合 |
| one-way coupling / two-way coupling | 单向耦合 / 双向耦合 |
| compaction | 压实 |
| subsidence | 地面沉降 |
| fault reactivation | 断层再活化 |
| fracture | 裂缝 |
| natural fracture | 天然裂缝 |
| hydraulic fracture / fracking | 水力压裂 |
| fracture conductivity | 裂缝导流能力 |
| DFN (discrete fracture network) | 离散裂缝网络（DFN） |
| geomechanical model | 地质力学模型 |
| FEM (finite element method) | 有限元法（FEM） |
| formation | 地层 |
| lithology | 岩性 |
| facies | 相 / 岩相 |
| sedimentary facies | 沉积相 |
| structure map | 构造图 |
| depth map | 深度图 |
| isochore / isopach | 等厚图 |
| contact (OWC/GOC/GWC) | 流体界面（油水界面/气油界面/气水界面） |
| OWC (oil-water contact) | 油水界面（OWC） |
| GOC (gas-oil contact) | 气油界面（GOC） |
| seismic | 地震 / 地震数据 |
| attribute | 属性 |
| horizon | 层位 |
| well log | 测井 / 测井曲线 |
| core / core analysis | 岩心 / 岩心分析 |
| petrophysics | 岩石物理 |
| Sw / So / Sg | 含水饱和度 / 含油饱和度 / 含气饱和度 |
| Swi (irreducible water saturation) | 束缚水饱和度 |
| Sor (residual oil saturation) | 残余油饱和度 |

### Workflow & General
| English | Chinese |
|---------|---------|
| workflow | 工作流程 |
| tutorial | 教程 |
| plugin | 插件 |
| template | 模板 |
| import / export | 导入 / 导出 |
| upscaling | 粗化 |
| quality control (QC) | 质量控制（QC） |
| uncertainty | 不确定性 |
| sensitivity analysis | 敏感性分析 |
| probabilistic | 概率性的 |
| P10 / P50 / P90 | P10 / P50 / P90 |
| STOIIP (stock tank oil initially in place) | 地质储量（STOIIP） |
| GIIP (gas initially in place) | 天然气地质储量（GIIP） |
| reserves | 储量 |
| NPV (net present value) | 净现值（NPV） |
| capex / opex | 资本支出 / 运营支出 |

## How to Use This Skill

### Input

- An `.srt` file (English subtitles)
- Optional: output path (defaults to `<basename>_zh.srt`)

### Translation Rules

1. **Run the termdb pre-processor** to get ASR-corrected SRT + dynamic glossary
2. **Read the corrected SRT** (not the original) for translation
3. **Load the dynamic glossary** — it overrides the static tables below
4. **Translate in batches of 15–20 entries** to maintain context
5. **For each text line**, translate to natural Simplified Chinese:
   - Maximum **20 Chinese characters per line**
   - If the translated text would exceed 20 chars, **split across two lines** using `\n`
   - **Apply the dynamic glossary first**, then fall back to static tables below
   - **Software names / forbidden terms** in the glossary stay in English; add Chinese label only on first occurrence
   - **Abbreviations** (BHP, GOR, EOR, OWC, etc.) keep the English abbreviation in parentheses after the Chinese term on first occurrence, then use the abbreviation alone
   - Maintain the speaker's tone (technical/tutorial style)
6. **Never modify** index numbers or timestamp lines — only replace text content
7. **Output** the complete translated SRT as `<basename>_zh.srt`

### Step-by-Step Procedure

#### Step 0 — Run termdb pre-processor (ASR correction + glossary extraction)

Run the following command via Bash:

```bash
source /Users/zhenmiao/projects/oilgas-termdb/.venv/bin/activate && \
python3 /Users/zhenmiao/projects/oilgas-termdb/scripts/srt_prep.py "<input_srt_path>"
```

The script outputs two lines to stdout:
```
CORRECTED_SRT: /path/to/<basename>_corrected.srt
GLOSSARY_MD: /path/to/<basename>_glossary.md
```

Parse these paths from stdout.

**If the script fails** (termdb not installed, venv not found, etc.) — skip Step 0 and proceed with the original SRT + static glossary below. Log the error but do not abort.

#### Step 0.5 — Read the termdb outputs

1. Read `CORRECTED_SRT` path — use this file as the source for translation (Whisper ASR errors already corrected)
2. Read `GLOSSARY_MD` path — this Markdown file contains:
   - A table of terms found in **this specific SRT** with their standard Chinese translations
   - A list of forbidden terms (keep in English)
3. **These terms take precedence over the static glossary tables below.**

#### Step 1 — Parse SRT structure

Each SRT entry looks like:
```
42
00:01:23,456 --> 00:01:25,789
This is the subtitle text
```

Parse into:
- `index`: integer (line 1 of block)
- `timestamp`: string (line 2, format `HH:MM:SS,mmm --> HH:MM:SS,mmm`)
- `text`: remaining lines joined (the English text to translate)

#### Step 2 — Translate in batches

Process 15–20 entries at a time. For each batch, translate the text fields while keeping the index and timestamp unchanged.

**Important translation constraints:**
- Each line of output ≤ 20 Chinese characters
- If a sentence needs more, use two lines (the SRT format allows multi-line text)
- Preserve paragraph/line breaks where semantically meaningful
- Do not add extra punctuation at line breaks

#### Step 3 — Write the output SRT

Reassemble all entries into valid SRT format and write to `<basename>_zh.srt`:

```
1
00:00:01,000 --> 00:00:03,500
这里是翻译后的中文

2
00:00:03,600 --> 00:00:05,200
第二条字幕内容
```

Write using the Write tool.

### Example

**Input** (`petrel_tutorial_en.srt`):
```
1
00:00:01,000 --> 00:00:04,000
Welcome to this Petrel tutorial on
history matching workflows.

2
00:00:04,200 --> 00:00:08,000
We'll look at how to adjust permeability
and porosity to match production data.

3
00:00:08,500 --> 00:00:12,000
The Eclipse simulation results show
a water cut of 65% by 2025.
```

**Output** (`petrel_tutorial_en_zh.srt`):
```
1
00:00:01,000 --> 00:00:04,000
欢迎收看本期Petrel教程，
主题为历史拟合工作流程。

2
00:00:04,200 --> 00:00:08,000
我们将调整渗透率和孔隙度，
以拟合生产数据。

3
00:00:08,500 --> 00:00:12,000
Eclipse模拟结果显示，
2025年含水率将达65%。
```

### Output Naming

- Input: `my_video_en.srt` → Output: `my_video_en_zh.srt`
- Input: `subtitles.srt` → Output: `subtitles_zh.srt`
- If user specifies output path, use that instead

### Quality Checklist

Before writing the output file, verify:
- [ ] termdb pre-processor ran successfully (or fallback to static glossary noted)
- [ ] Translated from the **corrected SRT** (not the original), unless pre-processor failed
- [ ] Dynamic glossary terms applied consistently (termdb terms override static table)
- [ ] Entry count matches input (no entries dropped or added)
- [ ] All timestamp lines are identical to input
- [ ] All index numbers are identical to input
- [ ] No Chinese line exceeds 20 characters
- [ ] Translation reads naturally (not word-for-word literal)
- [ ] Forbidden terms from termdb kept in English
- [ ] Technical abbreviations (BHP, GOR, OWC…) retained in parentheses on first use
- [ ] Glossary terms used consistently throughout (e.g. always "渗透率" not mixed with "透过率")
