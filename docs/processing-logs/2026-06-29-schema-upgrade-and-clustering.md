# 加工日志：Schema 升级与主题聚类

> **日期**: 2026-06-29
> **Schema 版本**: 0.1.0 → 0.2.0 (升级中)
> **对话概述**: Schema 2.0 结构设计、主题聚类分析、"其他"桶两轮消解

## 工作内容

### 1. Schema 2.0 结构设计

在分析原始数据后，发现 Schema 1.0 的字段不足以描述知识的实际结构，设计了 Schema 2.0：

**新增字段**：
- `claim`: 核心论断（自然语言陈述）
- `layer`: fact / rule / exclusion / causal（替代旧的 6-type）
- `knowledge_domain`: industry_intrinsic / platform_perspective / interviewer_artifact
- `causal_role`: drives / enables / vetoes / constrains / null
- `evidence`: 包含 source 和 confidence
- `context`: 门店类型、商户名称等上下文

**核心创新——"去掉测试"**：
判断一条知识属于哪个 domain 的方法：如果去掉所有平台相关内容，这条知识是否仍然成立？
- 成立 → industry_intrinsic（行业固有知识）
- 不成立 → platform_perspective（平台视角知识）
- 仅为访谈框架产物 → interviewer_artifact（访谈者产物）

### 2. 数据升级

将原始元数据升级为 Schema 2.0 格式：
- 总条目：428 条
- knowledge_domain 分布：industry_intrinsic (316) / platform_perspective (85) / interviewer_artifact (27)
- causal_role 分布：drives (72) / enables (0) / vetoes (10) / constrains (6) / null (340)

输出文件：`data/knowhow-upgraded.json`

### 3. 主题聚类分析

**第一轮聚类**：将原始 13 个理论主题与实际数据对比，发现"其他"桶有 83 条。
- 通过关键词扩展和语义分析，将 83 条消解到 42 条
- 新增 5 个补充主题：运营成本与投入、业务边界与排除策略、班型与容量管理、企业/B端服务、数据获取限制

**第二轮聚类**：对剩余 42 条进一步分析
- 通过更精细的关键词匹配和逐条审阅，将 42 条消解到 1 条
- 最终"其他"桶仅剩 1 条无法归类的条目

**最终主题列表（18 个）**：
1. 门店选址与扩张策略
2. 教练管理与排班
3. 会员获取与转化
4. 定价与盈利模型
5. 课程产品与课包设计
6. 租金与场地成本
7. 竞争与市场格局
8. 运营效率与流程
9. 用户留存与复购
10. 品牌与差异化定位
11. 财务模型与现金流
12. 合规与风险管理
13. 数字化与工具选型
14. 运营成本与投入（补充）
15. 业务边界与排除策略（补充）
16. 班型与容量管理（补充）
17. 企业/B端服务（补充）
18. 数据获取限制（补充）

### 4. 仪表盘构建

- `knowhow-upgraded-dashboard.html`: 主仪表盘，展示 18 主题、因果角色分布、置信度分布
- `knowhow-bias-audit-dashboard.html`: 偏见审计仪表盘
- `knowhow-clustering-dashboard.html`: 聚类分析仪表盘

## 产出文件

| 文件 | 说明 |
|------|------|
| `data/knowhow-upgraded.json` | Schema 2.0 格式知识库（428 条） |
| `dashboards/knowhow-upgraded-dashboard.html` | 主仪表盘 |
| `dashboards/knowhow-bias-audit-dashboard.html` | 偏见审计仪表盘 |
| `dashboards/knowhow-clustering-dashboard.html` | 聚类分析仪表盘 |

## 数据验证

- industry_intrinsic (316) + platform_perspective (85) + interviewer_artifact (27) = 428 ✓
- drives (72) + enables (0) + vetoes (10) + constrains (6) + null (340) = 428 ✓
- 18 主题覆盖 315/316 条 industry_intrinsic = 99.7% ✓
