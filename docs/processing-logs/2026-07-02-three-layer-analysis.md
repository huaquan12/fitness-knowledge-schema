# 加工日志：三层数据架构与 Schema 诊断分析

> **日期**: 2026-07-02
> **Schema 版本**: 0.2.0 (未变更，应用层扩展)
> **对话概述**: 建立原始数据/结构化数据/分析运算三层架构，基于 Schema 2.0 执行诊断分析并与学城原始结论对比

## 工作内容

### 1. 三层数据架构重组

将 `data/` 目录从扁平结构重组为三层：

| 层级 | 目录 | 内容 | 文件 |
|------|------|------|------|
| 第一层：原始数据 | `data/raw/` | 学城文档直接提取结果，扁平字符串 | knowhow-raw-metadata.json, knowhow-extraction-summary.md |
| 第二层：结构化数据 | `data/structured/` | Schema 2.0 格式，每条标注 layer/domain/causal_role/confidence | knowhow-upgraded.json (428条) |
| 第三层：分析运算 | `data/analysis/` | 基于 Schema 字段的运算结果 | schema-diagnostic-report.json, schema-vs-xuecheng-comparison.md |

### 2. Schema 诊断分析脚本

新建 `scripts/schema_diagnostic_analyzer.py`，执行 5 个维度的分析运算：

- **跨文档语义因果分析**：从 89 条 causal 条目中提取业务关键词，统计跨商户频次，识别出 21 个高频因果关键词（≥3 商户）
- **经营模型聚类**：按 business_model 聚类，提取每个模型的核心因果链和排除策略
- **置信度审计**：adopted 92条(21.5%) / disputed 336条(78.5%) / falsified 0条(0%)
- **排除策略对比**：42 条排除策略按商户和模式分类
- **因果角色矩阵**：drives(72) / vetoes(10) / constrains(6) / null(340)

### 3. 对比报告：Schema 推导 vs 学城原始结论

生成 `data/analysis/schema-vs-xuecheng-comparison.md`，核心发现：

**学城 5 条结论的验证结果**：
- 4 条与 Schema 运算一致（按次付费双刃剑、教练核心壁垒、预付费vs按次付费现金流、社区vs商圈成本）
- 1 条部分修正（单品类规模化悖论——Schema 发现"技能依赖型品类"和"标准化品类"扩张路径不同）

**Schema 独有发现（6 条学城未覆盖）**：
- S1: 行业恶性循环飞轮（adopted 置信度）
- S2: 平台佣金是合作否决因素（3 商户 vetoes）
- S3: 私域成熟度决定平台合作意愿
- S4: 新老门店获客策略分化
- S5: SaaS 免费模式的市场扩张逻辑
- S6: 体验差异化是按次付费模型留存关键

**方法论差异**：Schema 运算的核心优势在于可追溯性（每条结论标注 schema_basis）和可复现性（脚本可重复执行），且通过 knowledge_domain 过滤将行业规律与平台视角知识分离。

### 4. 数据变更

| 变更类型 | 影响范围 | 说明 |
|----------|----------|------|
| 目录重组 | data/ | 从扁平重组为 raw/structured/analysis 三层 |
| 新增脚本 | scripts/ | schema_diagnostic_analyzer.py |
| 新增报告 | data/analysis/ | JSON 报告 + 对比报告 MD |

## 产出文件

| 文件 | 说明 |
|------|------|
| `data/raw/knowhow-raw-metadata.json` | 移动自 data/（内容不变） |
| `data/raw/knowhow-extraction-summary.md` | 移动自 data/（内容不变） |
| `data/structured/knowhow-upgraded.json` | 移动自 data/（内容不变） |
| `data/analysis/schema-diagnostic-report.json` | Schema 运算 JSON 报告 |
| `data/analysis/schema-vs-xuecheng-comparison.md` | 对比报告 |
| `scripts/schema_diagnostic_analyzer.py` | 分析脚本 |
