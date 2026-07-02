# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-06-30

### Added
- Schema 2.0 结构定义（§3.1）：`claim/layer/knowledge_domain/causal_role/evidence/context`
- Schema 1.0 ↔ 2.0 字段映射表（§3.1b）
- `knowledge_domain` 三分类维度（§3.2a）：industry_intrinsic / platform_perspective / interviewer_artifact
- "去掉测试"判定流程图（§3.2a）
- 18 个数据驱动主题聚类（§3.3）：13 核心 + 5 补充，覆盖 99.7% industry_intrinsic 条目
- 因果角色 `null` 定义（§9.1）及 `enables` 待验证标注
- 统一置信度生命周期（§9.2）：disputed → adopted → falsified
- 文件资产索引新增 knowhow-upgraded.json 和仪表盘（§12）

### Changed
- 主题清单从 13 个理论英文 slug 替换为 18 个中文数据驱动主题
- 置信度从 `high|medium|low` 统一为 `disputed|adopted|falsified`
- 学城提取流程更新为 Schema 2.0 格式（§7）
- 因果角色定义从 6-type 替换为 4-layer + 映射表

### Removed
- 废弃文件 knowhow-clustering-results.json 从文件索引中移除

## [0.1.0] - 2026-06-30

### Added
- 初始版本：整合三套 Schema（Knowledge Atom / merchant-instance / judgment event）
- 学城文档分析约束与提取流程
- 触发规则与 Skill 协作关系定义
- 迭代机制与自检清单（§14）
- 13 个理论主题定义
- 6-type 知识类型定义
- 置信度体系：high / medium / low
