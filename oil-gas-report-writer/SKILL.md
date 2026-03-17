---
name: oil-gas-report-writer
description: Write professional oil & gas technical reports in Chinese or English. Use this skill whenever the user asks to write, draft, or generate a drilling report (日钻报告/完钻报告), completion report (完井报告), well testing report (试井报告/测试报告), production report (生产报告), reservoir evaluation report (储层评价报告), field development plan section (开发方案), or any other formal technical document for the oil & gas industry. Also use when the user provides raw field data (drilling parameters, production numbers, test results, log data) and wants it formatted into a proper industry report. Trigger on keywords like "写报告"、"生成报告"、"钻井日报"、"完井报告"、"试井报告"、"生产报告"、"开发方案"、"储量报告"、"write a report"、"draft a report".
---

# Oil & Gas Technical Report Writer

Write professional, standards-compliant technical reports for the oil & gas industry.

This skill covers:
- Daily drilling reports (日钻报告) and end-of-well reports (完钻报告)
- Well completion reports (完井报告)
- Well test / DST reports (试井报告 / DST报告)
- Production reports (生产日报 / 月报 / 年报)
- Reservoir evaluation reports (储层评价报告)
- Field development plan sections (开发方案章节)
- Reserve estimation reports (储量计算报告)
- Workover reports (修井报告)

## Core Principle

Produce reports that read as if written by a senior petroleum engineer or reservoir geologist.

Reports must be:
- Technically precise: use correct industry terminology
- Structured according to industry convention
- Complete: cover all mandatory sections even if data is partially missing
- Actionable: include clear interpretations and recommendations

## Input Types

Accept any combination of:
- Raw numerical data pasted into the prompt (depths, pressures, rates, temperatures)
- Tabular data from Excel or CSV
- Verbal descriptions of field events
- Partial draft text that needs completion or formatting
- Reference reports for style matching

If data is incomplete, mark missing fields with `[待填写]` or `[Data Missing]` and add a note listing what is needed.

## Language Default

Default to **Chinese (Simplified)** unless the user requests English or provides English-language context.

Mixed-language reports are acceptable when English is the established convention for the field (e.g., software parameter names, reservoir simulator output columns).

---

## Report Type Routing

When the user asks for a report, identify the type and follow the corresponding template below.

---

## 1. Daily Drilling Report（日钻报告）

### Structure

```
井号：[Well ID]
日期：[YYYY-MM-DD]
钻井公司：[Company]
井位：[Block / Coordinates]
钻井液类型：[Mud Type]

一、当日主要工作
[Narrative of main activities performed that day]

二、钻进情况
- 当日钻进：[Start Depth] m → [End Depth] m，进尺 [footage] m
- 钻头型号：[Bit type]，累计使用：[hours] h
- 钻压：[WOB range] kN
- 转速：[RPM range]
- 排量：[Flow rate] L/s
- 立压：[Standpipe pressure] MPa

三、钻井液性能
| 参数         | 设计值 | 实测值 |
|------------|------|------|
| 密度 (g/cm³) |      |      |
| 黏度 (s)    |      |      |
| 失水 (mL/30min) |   |      |
| 泥饼 (mm)   |      |      |
| pH          |      |      |

四、地层情况
[Formation description: lithology, oil/gas shows, mud log highlights]

五、异常情况及处理
[List any incidents: lost circulation, kicks, stuck pipe, equipment issues — with time, description, and resolution]

六、次日工作计划
[Planned operations for tomorrow]

七、安全情况
[HSE summary: any near-misses, safety meetings, observations]
```

### Compression Rules

- Keep times in 24-hour format
- Depths always in meters (m) unless the well uses feet — then specify ft
- Pressures in MPa unless otherwise stated

---

## 2. End-of-Well Report（完钻报告）

### Structure

```
# [Well Name] 完钻报告

## 1. 基本信息
| 项目 | 内容 |
|------|------|
| 井号 | |
| 井型 | 直井 / 定向井 / 水平井 |
| 区块 | |
| 井位坐标 | X: Y: |
| 设计井深 | m |
| 完钻井深 | m |
| 完钻层位 | |
| 开钻日期 | |
| 完钻日期 | |
| 实钻天数 | d |

## 2. 钻井工程简况
[Summary of drilling events, BHA designs used, major bit runs, NPT events]

## 3. 地层对比与地质评价
[Formation tops encountered vs. prognosis, lithology description, key markers]

## 4. 油气显示
[List all shows: depth, formation, show type (oil/gas/water), intensity]

## 5. 测井成果
[Summary of log runs: tools used, key log responses, formation evaluation highlights]

## 6. 固井质量
[Cement job summary: intervals cemented, volume, returns, CBL/VDL quality]

## 7. 完井方式
[Completion method: open hole, cased hole perforated, etc.]

## 8. 存在问题与建议
[Issues encountered and recommendations for future wells or workover]
```

---

## 3. Well Test Report（试井报告）

### Structure

```
# [Well Name] 试井报告

## 1. 基本信息
| 项目 | 数值 |
|------|------|
| 测试层位 | |
| 测试井段 | m - m |
| 测试日期 | |
| 测试类型 | DST / 生产测试 / 压力恢复 / 干扰试井 |

## 2. 测试流程
[Describe flow periods: initial flow, initial shut-in, main flow, final shut-in — with times and durations]

## 3. 产量数据
| 流动期 | 时长(h) | 油产量(m³/d) | 气产量(10⁴m³/d) | 水产量(m³/d) | 油压(MPa) | 套压(MPa) |
|--------|---------|------------|--------------|------------|---------|---------|
|        |         |            |              |            |         |         |

## 4. 压力数据
| 参数 | 数值 |
|------|------|
| 原始地层压力 | MPa |
| 恢复压力 | MPa |
| 压力系数 | |
| 地温梯度 | °C/100m |

## 5. 试井解释
- 渗透率 K：[value] mD
- 表皮系数 S：[value]
- 泄油半径 re：[value] m
- 储层平均渗透率 kh：[value] mD·m
- 解释方法：[Horner / MDH / 现代试井软件]

## 6. 流体性质
[API gravity, GOR, BSW, gas composition if available]

## 7. 综合评价与建议
[Formation deliverability assessment, development recommendations, completion strategy]
```

---

## 4. Production Report（生产报告）

### Monthly/Annual Structure

```
# [Field/Well Name] [Year]年[Month]月 生产报告

## 一、生产概况
| 指标 | 本月 | 累计 |
|------|------|------|
| 产油量 (m³) | | |
| 产气量 (10⁴m³) | | |
| 产水量 (m³) | | |
| 含水率 (%) | | |
| 气油比 (m³/m³) | | |
| 注水量 (m³) | | |
| 注采比 | | |
| 采出程度 (%) | | |
| 综合含水 (%) | | |

## 二、生产动态分析
[Production performance narrative: trends, anomalies, comparison to plan]

## 三、异常井分析
[For each well with abnormal behavior: well ID, issue, cause analysis, action taken]

## 四、措施效果评价
[Results of workovers, stimulations, or other interventions performed this period]

## 五、存在问题
[Current issues: high water cut wells, declining producers, injection pressure issues]

## 六、下月工作计划
[Planned operations, workovers, infill drilling proposals]
```

---

## 5. Reservoir Evaluation Report（储层评价报告）

### Structure

```
# [Formation Name] 储层评价报告

## 1. 概况
[Area, formation name, depth range, study wells, data sources]

## 2. 地层特征
[Stratigraphy, depositional environment, lateral continuity]

## 3. 储层物性
| 参数 | 平均值 | 范围 |
|------|------|------|
| 孔隙度 (%) | | |
| 渗透率 (mD) | | |
| 含水饱和度 (%) | | |
| 有效厚度 (m) | | |

## 4. 储层分类
[Classify reservoir quality: Class I / II / III based on porosity-permeability criteria]

## 5. 流体性质
[Oil/gas/water PVT summary]

## 6. 储量计算
| 方法 | 含油面积(km²) | 平均有效厚度(m) | 孔隙度(%) | 含油饱和度(%) | 地质储量(10⁴t) |
|------|------------|-------------|---------|------------|------------|
| 容积法 | | | | | |

## 7. 开发建议
[Development strategy: well pattern, spacing, completion method, artificial lift]
```

---

## Formatting Rules

### Numbers and Units

- Depths: m (or ft if the field uses imperial — state clearly)
- Pressures: MPa
- Production rates: m³/d for oil and water; 10⁴m³/d for gas (convention used in Chinese petroleum industry reports; equivalent to 10,000 m³/d)
- Temperatures: °C
- Permeability: mD
- Porosity / saturations: % (not decimal)

### Tables

Always prefer tables over bullets for comparative data.

Use markdown tables. Align columns when data types are homogeneous.

### Missing Data

When data is not provided, never invent values.

Use `[待填写]` for Chinese reports and `[TBD]` for English reports.

At the end of the report, append a short note listing all fields marked as missing.

### Dates

Use `YYYY-MM-DD` or `YYYY年MM月DD日` consistently throughout a single report.

---

## Content Rules

### Keep

- Measured values with units
- Calculated parameters with method reference
- Significant events with timestamps
- Recommendations backed by data

### Avoid

- Vague qualitative statements without supporting data ("production is good")
- Redundant preamble ("this report aims to…")
- Placeholder filler paragraphs
- Speculative interpretations labeled as facts

### When to Add Expert Commentary

Add a short interpretive note when:
- A key parameter is outside normal range (e.g., very high skin factor)
- A formation evaluation conclusion has direct completion implications
- Production data shows a trend that calls for action
- The data provided suggests a different interpretation than stated

---

## Domain Knowledge Reminders

Apply these engineering principles automatically when interpreting data:

- Positive skin factor (S > 5) → well damage, consider stimulation
- Permeability < 1 mD → tight reservoir, may need hydraulic fracturing
- Water cut rising sharply → possible coning or channeling
- GOR rising above bubble point GOR → gas cap invasion or solution gas drive
- Injection pressure limit → check reservoir parting pressure
- For carbonate reservoirs: always note if dual porosity / fracture system is possible
- For horizontal wells: note the section length and orientation relative to maximum horizontal stress

---

## Output Checklist

Before delivering the report, verify:
- [ ] Correct report type identified and template used
- [ ] All mandatory sections populated (or marked `[待填写]`)
- [ ] All numerical values have proper units
- [ ] Tables formatted in valid Markdown
- [ ] Missing data listed at end
- [ ] No invented values
- [ ] Recommendations are data-backed
- [ ] Language consistent throughout (Chinese or English)

---

## Example Prompt Triggers

This skill should activate for prompts such as:
- "帮我写一份钻井日报，今天钻进了 50 米，从 2300 米到 2350 米"
- "把这些试井数据整理成标准试井报告"
- "根据以下生产数据写一份月度生产报告"
- "写一份 X 井的完钻总结"
- "帮我起草储层评价报告的物性分析章节"
- "Draft a well completion report for Well X-1"
- "Generate a production report from this monthly data table"
- "Write up the DST results for the Lower Cretaceous interval"
