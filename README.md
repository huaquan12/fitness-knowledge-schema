# Fitness Knowledge Schema

> 健身行业 Agent 元数据约束与结构规范。本仓库是 Schema 的**唯一事实来源**（Single Source of Truth），所有版本变更、数据加工日志和迭代记录均通过 GitHub 管理。

## 项目结构

```
fitness-knowledge-schema/
├── SKILL.md                         # Schema 主文档（Agent 元数据约束与结构规范 v0.2.0）
├── data/                            # 知识库数据文件
│   ├── knowhow-upgraded.json        # 升级后的知识库（Schema 2.0 格式，428 条）
│   ├── knowhow-raw-metadata.json    # 原始提取元数据
│   └── knowhow-extraction-summary.md # 提取过程摘要
├── dashboards/                      # 可视化仪表盘
│   ├── knowhow-upgraded-dashboard.html   # 主仪表盘（18 主题聚类 + 因果角色 + 置信度）
│   ├── knowhow-bias-audit-dashboard.html # 偏见审计仪表盘
│   └── knowhow-clustering-dashboard.html # 聚类分析仪表盘
├── docs/
│   └── processing-logs/             # 每次对话加工的日志
│       ├── 2026-06-26-initial-extraction.md
│       ├── 2026-06-29-schema-upgrade-and-clustering.md
│       └── 2026-06-30-skill-sync-to-v0.2.0.md
├── scripts/
│   └── sync-skill.sh                # 同步 SKILL.md 到 CatPaw Skill 目录
├── CHANGELOG.md                     # 变更日志
└── .gitignore
```

## Schema 版本

| 版本 | 日期 | 关键变更 |
|------|------|----------|
| 0.2.0 | 2026-06-30 | Schema 2.0 结构定义、18 主题聚类、统一置信度体系、knowledge_domain 三分类 |
| 0.1.0 | 2026-06-30 | 初始版本：整合三套 Schema + 学城分析约束 + 触发规则 + 迭代机制 |

## 数据概览

- **总条目数**: 428
- **知识领域分布**: industry_intrinsic (316) / platform_perspective (85) / interviewer_artifact (27)
- **主题聚类**: 18 个（13 核心 + 5 补充），覆盖 99.7% 的 industry_intrinsic 条目
- **因果角色**: drives (72) / enables (0, 待验证) / vetoes (10) / constrains (6) / null (340)
- **置信度体系**: disputed → adopted → falsified

## 迭代管理规则

1. **所有 Schema 变更必须通过 GitHub PR 进行**——禁止 Agent 直接修改已发布的 Schema 结构
2. **每次对话加工后须在 `docs/processing-logs/` 新增日志文件**，格式为 `YYYY-MM-DD-简要描述.md`
3. **版本号遵循 Semantic Versioning**：Major（结构破坏性变更）/ Minor（新增字段或维度）/ Patch（描述修正）
4. **SKILL.md 是唯一事实来源**——修改后运行 `scripts/sync-skill.sh` 同步到 CatPaw Skill 部署目录
5. **CHANGELOG.md 记录所有版本变更**，与 SKILL.md §14.6 保持同步

## 部署同步

修改 SKILL.md 后，同步到 CatPaw Skill 目录：

```bash
bash scripts/sync-skill.sh
```

这会将仓库中的 `SKILL.md` 复制到 `~/.catpaw/skills/fitness-knowledge-schema/SKILL.md`（全局）或 `{workspace}/.catpaw/skills/fitness-knowledge-schema/SKILL.md`（项目级）。

## 相关 Skill

- **gym-business-analyzer**: 健身房经营模型诊断与战略分析，消费本 Schema 的知识库
- **coach-agent**: 教练 AI 陪跑 Agent，使用 judgment event 结构采集决策点
