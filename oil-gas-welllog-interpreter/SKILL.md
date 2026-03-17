---
name: oil-gas-welllog-interpreter
description: Interpret well log data and generate formation evaluation reports. Use this skill when the user provides well log data in any format (LAS file content, tabular ASCII data, Petrel/Techlog exports, or verbal descriptions of log curves) and wants a formation evaluation, lithology interpretation, petrophysical analysis, pay zone identification, or a reservoir summary. Also use when the user asks to "解释测井"、"测井解释"、"读取测井曲线"、"识别储层"、"计算孔隙度饱和度"、"划分油水层"、"log interpretation"、"petrophysical analysis"、"identify pay zones"、"calculate Sw" or similar. This skill covers standard open-hole log suites (GR, RT, RHOB, NPHI, DT, SP, Caliper) and specialized tools (FMI, NMR, array sonic, spectroscopy logs).
---

# Oil & Gas Well Log Interpreter

Analyze well log data and produce structured formation evaluation reports with lithology, reservoir quality, and fluid content interpretation.

This skill covers:
- Open-hole log interpretation (GR, RT, RHOB, NPHI, DT, SP, Caliper)
- Quantitative petrophysical analysis (Vsh, porosity, Sw, pay identification)
- Lithology and depositional environment assessment
- Fluid contact identification (OWC, GOC, GWC)
- NMR, FMI, and array sonic interpretation where data is provided
- LAS file parsing and structured column extraction
- Formation evaluation report generation

## Core Principle

Interpret log data using standard petrophysical workflows. Always show calculation methods. Flag uncertain interpretations rather than projecting false confidence.

## Input Types

Accept any of:
- LAS 2.0 / LAS 3.0 file content pasted into the prompt
- Tabular ASCII log data (depth + curve columns)
- Petrel or Techlog exported curve tables
- A verbal description of log responses ("GR reads 90 API, RT 5 ohm·m, NPHI 25%, RHOB 2.45 g/cm³")
- A depth table of calculated reservoir parameters

---

## Processing Workflow

### Step 1: Parse Input

Identify the input format and extract:
- Depth range and depth reference (MD or TVD; KB, DF, or GL)
- Available curves and their units
- Sampling interval (e.g., 0.125 m, 0.5 ft)
- Missing curve sections

If the input is a LAS file, extract the `~Well`, `~Curve`, and `~Parameter` sections before reading data.

### Step 2: Quality Check

Before interpreting:
- Flag bad-hole intervals: Caliper > [bit size + 2 inches or bit size + 5 cm]
- Flag washout-affected curves (RHOB, NPHI, SP unreliable in washed-out sections)
- Note any curve splices or tool changes
- Identify depth shifts or obvious spikes

### Step 3: Shale Volume Calculation (Vsh)

Default method: linear GR index

```
IGR = (GR - GR_min) / (GR_max - GR_min)
Vsh = IGR  (linear)
```

If user provides a Larionov correction preference, apply it (Larionov, 1969):
- Tertiary/unconsolidated: `Vsh = 0.083 × (2^(3.7 × IGR) - 1)`
- Older consolidated rocks: `Vsh = 0.33 × (2^(2 × IGR) - 1)`

Note: Larionov corrections reduce Vsh relative to the linear GR index; choose the formula appropriate for the geological age of the formation.

State GR baseline values used:
- GR_min: clean sand baseline (typical: 15–30 API)
- GR_max: shale baseline (typical: 80–120 API in clastic systems)

Adjust baselines for carbonates: GR_min may be 5–10 API; shale GR higher.

### Step 4: Porosity Calculation

**Density porosity:**
```
PHID = (RHOB_matrix - RHOB) / (RHOB_matrix - RHOB_fluid)
```

Default matrix densities:
| Lithology | RHOB_matrix (g/cm³) |
|-----------|---------------------|
| Sandstone | 2.65 |
| Limestone | 2.71 |
| Dolomite  | 2.87 |
| Anhydrite | 2.96 |

Default fluid density: 1.0 g/cm³ (water), 1.1 g/cm³ (oil-based mud)

**Neutron-density crossplot porosity:**
```
PHIND = (NPHI + PHID) / 2   [for liquid-filled pores, average method]
```

**Gas-corrected crossplot porosity (Bateman and Konen approximation):**
```
PHIG = sqrt((NPHI² + PHID²) / 2)
```
Note: This is a simplified empirical correction suitable for moderate gas saturations. It tends to underestimate porosity in high gas saturation zones. For high-saturation gas sands, a more rigorous correction using gas PVT data is preferable.

Apply shale correction when Vsh > 0.1:
```
PHI_corrected = PHIND - (Vsh × PHI_shale)
```

### Step 5: Water Saturation Calculation

Default: Archie's equation

```
Sw = ((a × Rw) / (PHI^m × RT))^(1/n)
```

Default Archie parameters for clastics:
| Parameter | Default |
|-----------|---------|
| a (tortuosity) | 1.0 |
| m (cementation) | 2.0 |
| n (saturation) | 2.0 |

For carbonates, use m = 2.0–2.5 (vuggy) or specify if dual porosity.

**Rw estimation (if not provided):**
Use SP curve: `Rw = Rmf × 10^(-(SSP / (60 + 0.133 × T)))`
Or use the water zone: `Rw = RT_water × PHI^m × (1/a)`

If Rw is unavailable, state it clearly and request the value from the user.
Otherwise estimate from a water zone using Archie (Sw = 1 in clean water zone):
```
Rw = (RT_water × PHI^m) / a
```

### Step 6: Pay Identification

Apply cutoffs to identify net pay intervals:

| Cutoff Parameter | Typical Clastic | Typical Carbonate |
|-----------------|----------------|------------------|
| Vsh ≤ | 0.40 | 0.30 |
| PHI ≥ | 0.08 | 0.05 |
| Sw ≤ | 0.65 | 0.70 |

Flag if the user has specified different cutoffs.

Net pay = sum of intervals meeting all three cutoffs.

### Step 7: Fluid Contact Identification

Look for:
- Sharp RT increase with constant or decreasing porosity → potential OWC or GOC
- NPHI/RHOB crossover (neutron less than density in pu units) → gas signature
- SP deflection changes
- Consistent Sw transitions

State contacts as:
- Definite: clear log response + pressure confirmation or test data
- Probable: log response alone, no independent confirmation
- Possible: ambiguous response, requires additional data

---

## Output Format

### Formation Evaluation Summary Report

```markdown
# [Well Name] — 测井解释成果报告

## 1. 基本信息
| 项目 | 内容 |
|------|------|
| 井号 | |
| 解释井段 | m - m |
| 测井日期 | |
| 井眼尺寸 | mm |
| 钻井液类型 | |
| 钻井液密度 | g/cm³ |
| KB/DF 高程 | m |
| 数据来源 | |

## 2. 可用测井曲线
| 曲线 | 单位 | 井段覆盖 | 质量 |
|------|------|---------|------|
| GR   | API  |         |      |
| RT   | Ω·m  |         |      |
| RHOB | g/cm³|         |      |
| NPHI | v/v  |         |      |
| DT   | μs/ft|         |      |

## 3. 解释参数
| 参数 | 取值 | 来源 |
|------|------|------|
| GR_min (纯砂) | API | |
| GR_max (泥岩) | API | |
| 基质密度 | g/cm³ | |
| 地层水电阻率 Rw | Ω·m | |
| Archie a | | |
| Archie m | | |
| Archie n | | |

## 4. 分层解释成果表
| 层号 | 顶深(m) | 底深(m) | 厚度(m) | 岩性 | Vsh(%) | PHI(%) | Sw(%) | 解释 |
|------|---------|---------|---------|------|-------|-------|------|------|
|      |         |         |         |      |       |       |      |      |

解释符号说明：
- 油层：O
- 气层：G
- 油水同层：OW
- 气水同层：GW
- 水层：W
- 致密层/干层：D
- 泥岩：S

## 5. 储层物性汇总
| 储层 | 顶深(m) | 底深(m) | 有效厚度(m) | 平均孔隙度(%) | 平均Sw(%) | 流体类型 |
|------|---------|---------|-----------|------------|---------|---------|
|      |         |         |           |            |         |         |

## 6. 流体接触关系
| 接触面 | 推测深度(m) | 置信度 | 依据 |
|--------|-----------|--------|------|
| OWC (油水界面) | | | |
| GOC (气油界面) | | | |

## 7. 解释评价与建议
[综合评价储层质量，推荐射孔井段，提示需进一步确认的不确定点]

## 8. 数据缺口与补充建议
[列出缺少的参数、需要的化验分析、或建议加密的测井项目]
```

---

## Lithology Identification Rules

Use the following log response patterns to classify lithology:

| Lithology | GR | RHOB (g/cm³) | NPHI (%) | RT | DT (μs/ft) |
|-----------|----|--------------|-----------|----|------------|
| Clean sandstone | Low (<50 API) | 2.45–2.65 | 15–30 | High (dry), Low (wet) | 50–80 |
| Shaly sandstone | Medium (50–90) | 2.45–2.65 | 20–35 | Variable | 60–90 |
| Shale | High (>80 API) | 2.45–2.65 | 25–45 | Low (1–5) | 80–130 |
| Limestone | Low–medium | 2.65–2.71 | 0–20 | Very high (dry) | 40–60 |
| Dolomite | Low–medium | 2.71–2.87 | 0–15 | Very high | 38–50 |
| Anhydrite | Low | ~2.96 | ~0 | Very high | ~50 |
| Coal | Very high | <2.0 | High | Very low | >120 | Note: coal intervals are typically avoidance targets or seal rocks in petroleum exploration, not reservoir targets. High GR and very low density are diagnostic. |
| Salt | Low | ~2.03 | ~0 | Very high | ~67 | |

---

## Special Interpretation Notes

### Gas Effect

When NPHI < PHID (density porosity > neutron porosity — a "crossover" in standard overlay):
- Indicates gas in pores
- Apply gas correction: `PHIG = sqrt((NPHI² + PHID²) / 2)`
- RT should be high; GR should be low (clean gas sand)

### Carbonate Reservoirs

- Secondary porosity (fractures, vugs) not captured by matrix logs alone
- FMI / image logs needed to characterize fracture porosity
- Archie cementation exponent m may vary 1.8–3.0 for vuggy carbonates
- Dual porosity systems: total porosity ≠ effective porosity

### Tight / Low-Permeability Reservoirs

- Low porosity (< 8% for sandstone, < 3% for carbonate)
- RT may be elevated even in water-bearing zones due to low saturation
- NMR T2 cutoff critical for permeability estimation
- DT / sonic porosity helps cross-check

### LAS File Parsing Instructions

LAS 2.0 format sections:
```
~Version      → LAS format version
~Well         → Well name, coordinates, dates
~Curve        → Column definitions (mnemonic, units, description)
~Parameter    → Formation parameters, mud properties, Rw
~A (or ~ASCII)→ Numerical data columns
```

When parsing:
1. Extract well metadata from `~Well`
2. Map column names from `~Curve` to their positions in `~A`
3. Handle null values (default: -999.25 or -9999.0) — replace with `NaN` before calculations
4. Note depth reference: `STRT`, `STOP`, `STEP` in `~Well` section

---

## Quality Flag Table

Include a quality flag column in the output table:

| Flag | Meaning |
|------|---------|
| ✓ | Good quality, reliable interpretation |
| △ | Marginal quality, use with caution |
| ✗ | Poor quality due to washout, tool failure, or insufficient data |
| ? | Uncertain interpretation, needs additional data |

---

## Calculation Transparency

Always show:
- The formula used for each parameter
- The input values substituted
- The result with units
- The source of constants or parameters

Example:
```
Sw at 2456.5 m:
  PHI = 0.18 (from RHOB = 2.44 g/cm³, matrix = 2.65)
  RT = 8.2 Ω·m, Rw = 0.05 Ω·m
  Sw = ((1.0 × 0.05) / (0.18² × 8.2))^(1/2) = 0.41 = 41%
  → Oil pay (Sw < 65% cutoff)
```

---

## Output Checklist

Before delivering results, verify:
- [ ] All curve mnemonics identified and units stated
- [ ] Bad-hole intervals flagged
- [ ] Vsh method and baselines stated
- [ ] Porosity method stated, gas correction applied if crossover present
- [ ] Rw source stated
- [ ] Archie parameters stated
- [ ] Pay cutoffs stated
- [ ] Fluid contacts noted with confidence level
- [ ] Interpretation table populated with quality flags
- [ ] Missing data or parameter gaps listed

---

## Example Prompt Triggers

This skill should activate for prompts such as:
- "帮我解释这段测井数据，判断是油层还是水层"
- "这是LAS文件内容，帮我算孔隙度和饱和度"
- "GR 85API，密度 2.3，中子 28%，电阻率 35 欧姆米，这是什么层？"
- "从这个测井表格中识别出所有储层并计算净油层厚度"
- "Identify pay zones from this log suite"
- "Calculate Sw using Archie's equation for these intervals"
- "帮我写这口井的测井解释报告"
- "Interpret this LAS file and give me a formation evaluation"
