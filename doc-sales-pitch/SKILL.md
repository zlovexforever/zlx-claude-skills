---
name: doc-sales-pitch
description: 将专业资料（PDF/PPT/Word）提炼为可售卖的销售内容。当用户提到要"卖资料"、"推介资料"、"做朋友圈文案"、"提炼卖点"、"分析文档价值"、"资料变现"、或想从某个文档生成推广文字时，必须使用此 Skill。也适用于用户提供了一个文档并想知道"这能卖给谁"、"怎么介绍这份资料"的场景。支持 PDF（优先）、PPT/PPTX、Word/DOCX。
---

# 专业资料销售内容提炼

## 你在做什么

用户提供了一份专业资料，想把它变成可售卖的产品。你的任务不是做普通摘要，而是**站在买家角度**提炼价值，并生成可以直接发布的朋友圈推介文案。

## 完整流程

按顺序执行以下步骤，**不要跳过任何一步**。

---

### Step 1：提取文档内容

根据文件类型选择提取方式：

**PDF（优先支持）：**
```bash
python /Users/zhenmiao/.claude/skills/doc-sales-pitch/scripts/extract_doc.py "<文件路径>" --output /tmp/doc_extracted.json
```

**PPT/PPTX：**
使用 `python-pptx` 提取每页标题 + 正文文本，保留层级结构。

**Word/DOCX：**
使用 `python-docx` 提取段落 + 标题，保留标题层级。

如果脚本不可用，直接用 Read 工具读取文件（PDF 用 pdf skill，PPT 用 pptx skill，Word 用 docx skill）。

**提取重点：**
- 文档标题、章节标题
- 每章节的核心论点（而非逐字）
- 数据、案例、方法论、工具清单
- 作者/出处信息（如有）

---

### Step 2：分析内容价值

阅读提取内容后，**读取并严格遵循提示词模板**：

```
/Users/zhenmiao/.claude/skills/doc-sales-pitch/prompts/analyze.md
```

按模板输出结构化分析结果，包含：
- 文档类型判断（教程/报告/方法论/工具包/案例集...）
- 核心知识点清单
- 实用价值评估
- 稀缺性/专业性评估

---

### Step 3：生成销售内容

阅读并遵循文案提示词模板：

```
/Users/zhenmiao/.claude/skills/doc-sales-pitch/prompts/copywrite.md
```

生成以下内容（**中文输出**）：

#### 3a. 精华内容摘要（2-3段）
提炼文档最有价值的知识，让潜在买家了解"买了能学到什么"。语气客观专业。

#### 3b. 核心卖点（3-5条）
每条卖点格式：`**卖点标题**：一句话说清楚这个点的价值`

#### 3c. 适合购买人群
分三层：主要人群 / 次要人群 / 不适合人群（帮买家自我筛选）

#### 3d. 朋友圈推介文案（三版）
- **短版**：≤100字，适合配截图发送，重点一句话击中痛点
- **标准版**：150-200字，平衡内容介绍和价值感，适合大部分场景
- **强销售版**：200-300字，有行动号召，适合限时推广场景

文案风格要求：**专业、自然、可信**，像朋友推荐而非广告，不用"震惊"、"必须拥有"等夸张词。

---

### Step 4：推荐展示页面并生成截图

**仅 PDF 文件执行此步骤。**

#### 4a. 确定目录页范围（必做）

从 `extract_doc.json` 的 `sections` 列表中找出所有标题包含"目录"、"contents"、"table of contents"（不区分大小写）的 section，记录其 `index`（即页码）。**目录可能跨多页，需把连续的目录页全部纳入截图列表。**

```python
# 示例：从 sections 找目录页
import json
with open('/tmp/doc_extracted.json') as f:
    data = json.load(f)
toc_pages = [s['index'] for s in data['sections']
             if any(kw in s.get('title','').lower() for kw in ['目录','contents','table of'])]
print(toc_pages)
```

#### 4b. 选取其他展示页

在目录页之外，再额外选取 3-5 页（标准：信息密度高、视觉清晰、能代表文档价值）：
- 封面页（第1页）
- 最有干货的章节首页
- 包含数据/图表的页面
- 结论/总结页

#### 4c. 生成截图

截图保存目录规则：与原文件同目录，文件夹名与原文件同名（去掉扩展名）。

例如：
- 原文件：`/Users/foo/Downloads/petrel构造建模.pdf`
- 截图目录：`/Users/foo/Downloads/petrel构造建模/`

将目录页 + 其他展示页合并去重，按页码排序后，一次性调用截图脚本：

```bash
python /Users/zhenmiao/.claude/skills/doc-sales-pitch/scripts/screenshot_pages.py \
  "<PDF文件路径>" \
  --pages "<目录页+其他页，逗号分隔，如 1,3,4,5,15,26>" \
  --output-dir "<原文件所在目录>/<原文件名不含扩展名>/" \
  --dpi 150
```

---

### Step 5：整理并输出最终结果

按以下模板输出完整结果，**不要省略任何板块**：

```
/Users/zhenmiao/.claude/skills/doc-sales-pitch/assets/output_template.md
```

告知用户截图保存位置，并明确说明每张截图适合搭配哪版文案发布。

#### 5a. 保存为 Markdown 文件（必做）

将完整输出内容保存为 Markdown 文件，路径规则：
- 文件名与原文件同名，扩展名改为 `.md`
- 保存到原文件**同一目录**下

例如：
- 原文件：`/Users/foo/Downloads/petrel构造建模.pdf`
- 输出文件：`/Users/foo/Downloads/petrel构造建模.md`

使用 Write 工具写入，内容为本次生成的完整报告（价值分析 + 精华摘要 + 核心卖点 + 适合人群 + 三版朋友圈文案 + 展示页面说明 + 定价建议），**不要只写摘要或部分内容**。

写入完成后，告知用户文件保存路径。

---

## 注意事项

- 分析时始终站在**潜在买家**的角度，而非作者角度
- 卖点要具体可验证，避免"内容丰富"、"干货满满"等空话
- 文案中不编造文档中没有的内容
- 如果文档内容较少或质量一般，诚实说明，给用户合理的定价建议
- 截图脚本依赖 `pymupdf`（fitz），如未安装先运行：`pip install pymupdf`
