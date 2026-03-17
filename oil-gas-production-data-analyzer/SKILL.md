---
name: oil-gas-production-data-analyzer
description: Analyze oil & gas production data and generate performance analysis reports. Use this skill when the user provides production data (oil/water/gas rates, pressures, cumulative volumes, injection data) in any format (Excel tables, CSV, pasted numbers, or verbal descriptions) and wants performance analysis, decline curve analysis, water cut trend analysis, injection-production response evaluation, production forecast, or a written performance report. Trigger on keywords like "生产分析"、"产量递减"、"含水上升"、"注采分析"、"动态分析"、"decline curve"、"production analysis"、"water cut trend"、"production forecast"、"DCA"、"Arps decline"、"水驱曲线"、"甲型/乙型曲线"。Also use when user says "帮我分析这些生产数据" or pastes a table of monthly/daily production numbers.
---

# Oil & Gas Production Data Analyzer

Analyze production performance data and generate structured reports with trend analysis, decline curve fitting, and development recommendations.

This skill covers:
- Production rate and cumulative volume trend analysis
- Decline curve analysis (DCA) — Arps exponential, hyperbolic, harmonic
- Water cut (含水率) trend analysis and water drive curve methods (甲型/乙型/丙型水驱曲线)
- Injection-production ratio analysis (注采比)
- Single-well performance diagnosis
- Field-level production surveillance
- Production forecast generation
- Written performance reports (monthly, annual, development-stage)

## Core Principle

Turn raw production numbers into actionable insights. Always explain the engineering reasoning behind the analysis, not just the arithmetic.

## Input Types

Accept any combination of:
- Pasted tables (markdown, CSV, or free-form tabular text) with date + rate columns
- Verbal descriptions ("this well produced 50 m³/day in January, declining to 35 by June")
- Excel export pasted as text
- Single data points for quick calculations
- Prior reports or surveillance summaries

Minimum data needed for each analysis type:
| Analysis | Minimum Required |
|----------|-----------------|
| Rate trend | ≥ 3 time-rate data points |
| Decline curve | ≥ 6 time-rate points in declining phase |
| Water cut trend | Time series of oil + water rates or water cut % |
| Injection-production | Paired injection and production volumes |

If minimum data is not available, flag it and show what can still be calculated.

---

## Language Default

Default to **Chinese (Simplified)** unless the user requests English.

---

## Processing Workflow

### Step 1: Parse and Organize Data

Extract columns from the input and create a clean working table:

| Date | Oil Rate (m³/d) | Water Rate (m³/d) | Gas Rate (10⁴m³/d) | Liquid Rate (m³/d) | Water Cut (%) | THP (MPa) | BHP (MPa) | Cumulative Oil (m³) |
|------|----------------|-------------------|-------------------|--------------------|--------------|-----------|-----------|---------------------|

Identify:
- Time interval (daily / monthly / annual)
- Units (m³, bbl, tons — convert if needed, state conversion used)
- Any missing data points (interpolate linearly if gap ≤ 2 periods, flag if larger)
- Production shutdowns (zero rate periods — do not include in decline fitting)

### Step 2: Basic Statistics

Compute:
- Peak production rate and date
- Current production rate (latest data point)
- Cumulative production to date
- Average production rate over period
- Overall decline % from peak to current
- Current water cut and trend (rising / stable / falling)

### Step 3: Identify Production Stage

Classify the well or field into a production stage:

| Stage | Characteristics |
|-------|----------------|
| 上升期 / Buildup | Rate increasing, water cut low or stable |
| 稳产期 / Plateau | Rate relatively stable (< 5% annual decline) |
| 递减期 / Decline | Sustained rate decline |
| 高含水期 / High Water Cut | Water cut > 60%, rate declining |
| 低产期 / Stripper | Rate < economic limit, late life |

### Step 4: Decline Curve Analysis (Arps)

Apply only to the declining phase. Do not fit to buildup or plateau periods.

**Exponential decline (最常用 for stable reservoir behavior):**
```
q(t) = qi × e^(-Di × t)
```
Where:
- `qi` = initial rate at start of decline (m³/d)
- `Di` = nominal decline rate (1/time)
- `t` = time since start of decline

Linearize: `ln(q) = ln(qi) - Di × t`

Estimate Di from slope of ln(q) vs t regression.

**Hyperbolic decline (变递减率, most common in practice):**
```
q(t) = qi × (1 + b × Di × t)^(-1/b)
```
Where `b` = hyperbolic exponent (0 < b < 1 for most wells)

Estimate by non-linear curve fitting:
- b = 0: reduces to exponential
- b = 1: harmonic decline
- 0.3–0.7: typical for solution gas drive / water drive wells

**Report fit quality:**
- Show R² for the chosen decline model
- Flag if R² < 0.85 (poor fit, data may have multiple decline segments)

**Forecast:**
Project production to:
1. A user-specified date
2. The economic limit (if provided)
3. 1 year and 5 years from last data point

Show:
```
预测时间节点 | 预测日产量 (m³/d) | 预测累产 (m³) | 累计递减率 (%)
```

### Step 5: Water Cut Analysis

**Method 1: Time-water cut plot (含水率–时间曲线)**
- Plot water cut vs time
- Classify trend: linear rise / accelerating / stabilizing

**Method 2: Recovery vs Water Cut (甲型水驱特征曲线)**
```
ln(Wo) = a + b × Np
```
Where Wo = cumulative water production, Np = cumulative oil production.

Linearize on semi-log scale. If linear → water drive is regular.

Forecast:
```
Np_at_Fw = [(ln(Wo_limit) - a) / b]
```
Where Wo_limit corresponds to the economic water-oil ratio limit.

**Method 3: Water-Oil Ratio vs Cumulative Oil (乙型水驱特征曲线)**
```
WOR = a × e^(b × Np)
```
Semi-log plot: `ln(WOR) vs Np` should be linear if regular water drive.

Applicable conditions: relatively homogeneous reservoirs under stable water drive with consistent displacement. For highly heterogeneous or layered reservoirs, prefer 甲型 (Type A) or use both for cross-validation.

State which method was applied and why (data availability, linearity quality).

### Step 6: Injection-Production Analysis

If injection data is available:

| Metric | Formula | Typical Target |
|--------|---------|---------------|
| 注采比 (Injection-Production Ratio) | `IPR = Qi / (Qo + Qw)` | ≥ 1.0 |
| 累计注采比 | `Cumulative IPR = ΣQi / Σ(Qo + Qw)` | |
| 地下亏空 (Void Replacement) | `Voidage = Qo × Bo + Qg × Bg + Qw × Bw - Qi × Bwi` | Positive = under-injection (reservoir pressure declining) |
| 注水见效率 | Field judgment based on IPR trend vs rate response | |

If Bo and Bw are not provided, use defaults (Bo = 1.2 at initial reservoir pressure for moderate-API crude, Bw = 1.0, Bg calculated from reservoir pressure and temperature if gas data available) and state all assumptions clearly.

---

## Output Format

### Production Performance Report

```markdown
# [Well/Field Name] 生产动态分析报告

> 数据期间：[Start Date] — [End Date]  
> 数据频率：[Daily / Monthly]  
> 分析目的：[Rate trend / Decline / Water cut / Full performance]

---

## 一、生产概况

| 指标 | 数值 |
|------|------|
| 初始产量 (峰值) | m³/d（日期：） |
| 当前产量 | m³/d（日期：） |
| 累计产油量 | m³ |
| 累计产水量 | m³ |
| 当前含水率 | % |
| 生产天数 | d |
| 开采程度（如已知储量）| % |

---

## 二、产量趋势分析

[Narrative describing production trend: buildup, plateau, decline segments, anomalies]

### 生产阶段划分

| 阶段 | 时间段 | 特征 |
|------|--------|------|
| | | |

---

## 三、递减曲线分析

- 递减类型：[指数 / 双曲 / 调和]
- 拟合起始时间：[Date]
- 初始递减率 Di：[value] /月（年递减率：[value]%）
- 双曲指数 b：[value]（适用于双曲递减）
- 拟合 R²：[value]

### 产量预测

| 时间节点 | 预测日产量 (m³/d) | 预测累产量 (m³) |
|---------|----------------|--------------|
| [+1年]  |                |              |
| [+3年]  |                |              |
| [+5年]  |                |              |
| 达到经济极限 |            |              |

---

## 四、含水分析

- 当前含水率：[%]
- 含水上升趋势：[线性上升 / 加速上升 / 趋于稳定]
- 水驱特征曲线类型：[甲型 / 乙型]
- 水驱特征方程：[equation]
- 预测含水 80% 时累计产油量：[m³]
- 预测含水 95% 时累计产油量：[m³]（如有数据支撑）

---

## 五、注采分析（如有注入数据）

| 指标 | 数值 |
|------|------|
| 本期注采比 | |
| 累计注采比 | |
| 地下亏空 / 充填 | m³ |
| 注水见效评价 | |

---

## 六、问题诊断

[List observed anomalies: sudden rate drops, abnormal pressure behavior, unexpected water cut spikes, etc. — with potential causes]

| 现象 | 可能原因 | 建议措施 |
|------|---------|---------|
| | | |

---

## 七、开发建议

[Specific, data-backed recommendations: stimulation, workover, injection adjustment, infill wells, artificial lift optimization]

---

## 八、数据说明与局限性

[Note any data gaps, assumed values, or methodological limitations]
```

---

## Unit Conversions

If the user provides data in non-standard units, convert and state:

| From | To | Factor |
|------|-----|--------|
| bbl/d | m³/d | × 0.15899 |
| STB/d | m³/d | × 0.15899 |
| Mcf/d | 10⁴m³/d | × 0.02832 |
| MMcf/d | 10⁴m³/d | × 28.317 |
| ton/d (oil) | m³/d | ÷ [density in t/m³] |

Default oil density for conversion: 0.85 t/m³ (API ~35) — state if different value used.

---

## Engineering Diagnosis Rules

Apply these diagnostic principles automatically when reviewing production data:

| Observation | Likely Cause | Suggested Action |
|-------------|-------------|-----------------|
| Rapid initial decline then stabilization | Skin cleanup or drainage stabilization | Monitor; may not need intervention |
| Sudden rate drop (not planned) | Mechanical failure, scale, wax, sand | Workover, stimulation, or lifting adjustment |
| Accelerating decline | Pressure depletion, reservoir boundaries | Pressure support, infill drilling |
| Sharp water cut increase | Water breakthrough, coning, channeling | Conformance treatment, production control |
| GOR increasing beyond bubble point GOR | Gas cap invasion or solution gas drive | Reduce drawdown, consider gas cap protection |
| Injection pressure rising | Formation plugging, fracture closure | Acid treatment of injector, well test |
| Injection pressure falling | New fractures or thief zones opened | Tracer test, production logging |
| Recovery factor > 40% water drive | Good waterflood efficiency | Evaluate remaining potential |

---

## Decline Curve Selector

Use this decision guide:

```
Has the well had consistent decline for ≥ 6 months?
  No → Use trend analysis only, do not fit decline curve
  Yes →
    Is the decline rate relatively constant?
      Yes → Use exponential (b = 0)
      No →
        Is the decline rate decreasing over time?
          Yes → Use hyperbolic (0 < b < 1)
          Is b approaching 1 from fit?
            Hyperbolic b ≈ 1 → Use harmonic
```

---

## Output Checklist

Before delivering analysis, verify:
- [ ] Data table clean and units stated
- [ ] Production stage identified
- [ ] Basic statistics (peak, current, cumulative) reported
- [ ] Decline curve applied only if ≥ 6 months of decline data
- [ ] Decline model type stated with R² value
- [ ] Forecast table included
- [ ] Water cut trend described if water data provided
- [ ] Injection-production analysis included if injection data provided
- [ ] Problem diagnosis table populated
- [ ] Recommendations are data-backed
- [ ] Missing data and assumptions stated

---

## Example Prompt Triggers

This skill should activate for prompts such as:
- "这是我们井的月产量数据，帮我分析一下产量递减趋势"
- "帮我做一下这口井的递减曲线分析，预测未来3年产量"
- "含水率一直在涨，帮我分析一下水驱效果"
- "把这个生产数据表整理成标准的生产动态报告"
- "这个注水井的注采比是多少，合理吗"
- "Analyze this production data and fit an Arps decline curve"
- "Forecast production to abandonment for this well"
- "Plot the water cut trend and tell me when we'll hit 90% water cut"
- "Generate a monthly production performance report from this data"
- "用甲型水驱曲线预测这口井的最终采收率"
