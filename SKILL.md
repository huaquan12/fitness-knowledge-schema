---
name: fitness-knowledge-schema
version: 0.2.0
description: >
  健身行业 Agent 元数据约束与结构规范。当 Agent 需要从学城文档中提取健身行业知识、
  执行门店诊断并填充结构化数据、采集教练判断事件、维护知识库条目、更新行业基准时，
  必须先加载本 Skill 以获取 Schema 约束和质量门禁。
  触发词：知识提取、Know-How、知识原子、Knowledge Atom、merchant-instance、
  门店实例、judgment event、判断事件、训练计划 diff、知识库更新、基准校准、
  置信度、decision trace、学城访谈分析、经营知识结构化、Schema 约束。
metadata:
  skillhub.creator: cuixinyue04
---

# Fitness Knowledge Schema — Agent 元数据约束与结构规范

> **定位**: 健身行业 Agent 在执行知识提取、学城文档分析、门店诊断、教练判断采集等任务时，必须遵循的数据结构规范和约束协议。
>
> **版本**: 0.2.0 | **最后更新**: 2026-06-30

---

## 〇、触发规则：什么时候使用本 Skill

### 必须触发的场景

以下场景中 Agent **必须**在开始工作前加载本 Skill：

| 场景 | 触发信号 | 需要的 Schema |
|------|---------|-------------|
| 分析学城访谈文档 | 用户提到学城、km、访谈、拜访记录 + 健身/商家/门店 | Knowledge Atom (§3) + 学城约束 (§7) |
| 门店诊断或画像填充 | 用户提到诊断某品牌/门店、填充门店数据 | Merchant Instance (§4) |
| 教练课程相关数据 | 用户提到备课、上课、复盘、判断事件、训练记录 | Judgment Events DDL (§5) |
| 知识库增删改 | 用户提到新增知识、废弃规则、更新基准 | Knowledge Atom (§3) + 质量门禁 (§11) |
| 跨模型对比分析 | 用户提到对比不同类型门店、行业基准 | 领域模型 (§6) + 统一术语 |

### 建议触发的场景

以下场景 Agent **应当**检查本 Skill 是否适用：

- 用户讨论健身行业经营概念（如坪效、满座率、教练流失率）→ 参照统一术语 (§6.4)
- 用户要求结构化输出任何健身行业数据 → 检查是否有对应 Schema
- 用户提到 decision trace、置信度、因果关系 → 参照设计哲学 (§13)

### 不触发的场景

- 纯闲聊、不涉及健身行业知识的任务
- 仅使用 gym-business-analyzer Skill 做诊断但不涉及数据结构输出（诊断 Skill 自带规则）
- coach-agent 的日常对话交互（coach-agent 有自己的数据协议，仅在需要与知识库对接时触发本 Skill）

### 与其他 Skill 的协作关系

```
fitness-knowledge-schema（本 Skill）
  │
  ├── 被引用 ← gym-business-analyzer
  │   诊断过程产出的 decision_traces 和 facts_discovered
  │   须符合 merchant-instance-schema 的 diagnostic_history 结构
  │
  ├── 被引用 ← coach-agent
  │   课中/课后产出的判断事件须符合 judgment_events 表结构
  │   从知识库调取行业通用知识时须遵循三层知识体系
  │
  └── 被引用 ← citadel Skill（学城）
      从学城文档提取知识时，输出格式须符合 Knowledge Atom
      提取约束见 §7
```

---

## 一、本 Skill 的使用场景

当 Agent 执行以下任务时，**必须先加载本 Skill** 以获取结构约束：

1. **学城访谈文档分析**：从学城文档中提取商家经营知识，输出须符合 Knowledge Atom 格式
2. **门店诊断数据填充**：诊断过程中产生的事实、判断、建议须符合 merchant-instance-schema
3. **教练判断事件采集**：训练课中/课后的判断记录须符合 judgment_events 表结构
4. **知识库维护**：新增/修改/废弃知识条目须遵循生命周期和质量门禁
5. **基准数据更新**：更新行业基准须遵循交叉验证和置信度规则

---

## 二、核心架构总览

整个知识体系分三个层级，数据从微观到宏观向上汇聚：

```
┌─────────────────────────────────────────────────────┐
│  第三层：行业知识库 (Industry Knowledge Pack)          │
│  ├── 领域模型 (fitness-domain-model/)                │
│  │   └── L0-L4 五层 + 2 横切维度                     │
│  ├── Know-How 知识原子 (know-how/)                   │
│  ├── 案例库 (case-studies/)                          │
│  └── 基准数据 (benchmarks/)                          │
├─────────────────────────────────────────────────────┤
│  第二层：门店实例 (merchant-instance-schema)           │
│  └── 一家具体门店的结构化画像 + 诊断历史              │
├─────────────────────────────────────────────────────┤
│  第一层：微观判断事件 (judgment_events DDL)            │
│  └── 教练/店长在日常场景中的具体决策记录              │
└─────────────────────────────────────────────────────┘

数据流向：
  judgment_events → 采集层 → 分析层(因果推断+置信度) → 沉淀层(知识原子)
                                                        ↓
                                              填充 merchant-instance 字段
                                                        ↓
                                              汇入 Industry Knowledge Pack
```

---

## 三、Schema 1：Knowledge Atom（知识原子）

这是知识库的最小可调用单元。当前存在两个版本：Schema 1.0（目标格式，用于成熟知识库）和 Schema 2.0（实际运行格式，用于当前知识库 `knowhow-upgraded.json`）。

### 3.1 Schema 2.0 结构（当前运行版本）

当前知识库 `knowhow-upgraded.json`（428 条条目，21 篇文档）实际使用的结构。**Agent 在读取和写入知识库时必须使用此格式。**

```yaml
claim: "纯文本断言"                    # 知识内容，一句话描述
layer: fact | rule | exclusion | causal  # 知识层级（见 §3.2）
knowledge_domain: industry_intrinsic | platform_perspective | interviewer_artifact  # 知识领域（见 §3.2a）
causal_role: drives | enables | vetoes | constrains | null  # 因果角色（见 §9）
evidence:
  source: interview                    # 数据来源
  confidence: disputed | adopted | falsified  # 置信度（见 §9.2 置信度生命周期）
context:
  store_type: "精品私教工作室"          # 门店类型
  merchant: "Z&B"                      # 商户名称
```

**示例**：

```json
{
  "claim": "纯私教模式无团课",
  "layer": "fact",
  "knowledge_domain": "industry_intrinsic",
  "causal_role": "null",
  "evidence": { "source": "interview", "confidence": "disputed" },
  "context": { "store_type": "精品私教工作室", "merchant": "Z&B" }
}
```

### 3.1a Schema 1.0 结构（目标格式）

Schema 1.0 是知识库成熟后的目标格式，在 Schema 2.0 条目经过充分验证和丰富后升级使用。当前尚无数据使用此格式。

```yaml
id: "{topic}-{sequence}"              # 如 coach-retention-003
topic: "{know-how主题}"               # 归属主题（见 §3.3 主题清单）
type: fact | benchmark | causal_rule | heuristic | anti_pattern | best_practice

# ===== 适用性标签（必填）=====
applicable_models: [A, B, C, D]       # A=预售驱动 B=体验驱动 C=效率驱动 D=教练驱动
applicable_stages: [1, 2, 3, 4]       # 1=初创 2=成长 3=成熟 4=衰退
applicable_regions: [全国 | 一线 | 新一线 | 二三线]

# ===== 内容（必填）=====
title: "简短标题"
content: |
  知识的具体内容（结构化描述）

# ===== 调用场景（至少一条）=====
trigger_conditions:
  - context: "诊断阶段2-指标评分"
    condition: "教练年流失率 > 该模型预警阈值"

# ===== 置信度与来源（必填）=====
confidence: disputed | adopted | falsified   # 统一使用 §9 置信度生命周期
sources:
  - type: case-study | industry-report | expert-interview | saas-data | xuecheng-doc
    reference: "具体来源（文档ID/URL/名称）"
    date: 2026-06

# ===== 生命周期（必填）=====
status: draft | pending-review | active | validated | challenged | deprecated
created_at: 2026-06-29
last_verified: 2026-06-29
verification_count: 0
contradiction_count: 0
```

### 3.1b Schema 1.0 与 2.0 映射关系

从 Schema 2.0 升级到 1.0 时的字段映射：

| Schema 2.0 字段 | Schema 1.0 字段 | 映射规则 |
|-----------------|-----------------|---------|
| `claim` | `title` + `content` | claim 拆分为简短标题和详细内容 |
| `layer` | `type` | 见 §3.2 类型映射表 |
| `knowledge_domain` | — | 仅 `industry_intrinsic` 的条目可升级 |
| `causal_role` | — | 映射为知识原子间的因果关系（§9） |
| `evidence.confidence` | `confidence` | 直接对应 |
| `evidence.source` | `sources[].type` | `interview` → `expert-interview` |
| `context.merchant` | — | 填入 `sources[].reference` |
| `context.store_type` | `applicable_models` | 根据类型推断适用模型 A/B/C/D |

### 3.2 知识层级（layer）与类型（type）

**Schema 2.0 的四种 layer**（当前使用）：

| layer | 含义 | 数据量 | 示例 |
|-------|------|--------|------|
| `fact` | 可验证的事实性断言 | 约 160 条 | "前期投入100万，房租4万/月" |
| `rule` | 经营规则或经验法则 | 约 110 条 | "新会员首次到店必须做体态评估" |
| `exclusion` | 明确不做的事情 | 约 50 条 | "不做线上直播课" |
| `causal` | 因果关系链条 | 约 100 条 | "严格教练筛选→课程质量稳定→口碑传播" |

**与 Schema 1.0 type 的映射**：

| Schema 2.0 layer | Schema 1.0 type | 说明 |
|------------------|-----------------|------|
| `fact` | `fact` / `benchmark` | 含数值的 fact 可升级为 benchmark |
| `rule` | `causal_rule` / `heuristic` | 有因果证据的升级为 causal_rule |
| `exclusion` | `anti_pattern` / `best_practice` | 视角取决于语境：明确的错误 vs 有意的战略选择 |
| `causal` | `causal_rule` | 直接映射 |

### 3.2a 知识领域（knowledge_domain）

Schema 2.0 引入的核心分类维度，用于区分知识的来源本质和可信度：

| 值 | 含义 | 数据量 | 判定规则 | 使用约束 |
|----|------|--------|---------|---------|
| `industry_intrinsic` | 行业本征知识 | 316 条 | "去掉测试"：如果移除所有平台，这条知识还成立吗？成立则为本征 | **仅此类知识**可进入面向商家的输出和主题聚类 |
| `platform_perspective` | 平台视角知识 | 85 条 | 从平台运营角度描述的知识，如佣金结构、招商策略 | 仅在平台内部分析时使用，不直接引用给商家 |
| `interviewer_artifact` | 调研产物 | 27 条 | 由调研方法或访谈者视角引入的内容，非行业客观知识 | 标记为噪声，不参与分析 |

**"去掉测试"判定流程**：

```
读取一条知识
    ↓
假设所有第三方平台（美团/大众点评/抖音/小红书）都不存在
    ↓
这条知识还成立吗？
    ├── 是 → industry_intrinsic
    └── 否 → 依赖平台才成立？
        ├── 是，且是平台视角的运营知识 → platform_perspective
        └── 是，且是访谈方法引入的 → interviewer_artifact
```

### 3.3 Know-How 主题清单

以下 18 个主题由数据驱动聚类产生（基于 316 条 `industry_intrinsic` 条目），覆盖率 99.7%（315/316）：

**核心经营主题（13 个）**：

| 主题 | 条目数 | 商户覆盖 | 对应的 Schema 1.0 slug |
|------|--------|---------|----------------------|
| 教练供给与管理 | 49 | 14 | `coach-retention` |
| 付费与定价模式 | 69 | 19 | `pricing-strategy` |
| 品类与课程策略 | 73 | 17 | `service-delivery` |
| 选址与空间 | 43 | 15 | `site-selection` |
| 获客与营销 | 54 | 19 | `acquisition-efficiency` |
| 用户留存与粘性 | 25 | 12 | `member-activation` + `retention-flywheel` |
| 规模化与扩张 | 36 | 16 | `standardization` |
| 组织与人力管理 | 18 | 9 | `ops-decision-making` |
| 安全与合规 | 11 | 3 | — |
| SaaS与数字化 | 33 | 10 | `data-capability` |
| 场馆与场地生态 | 35 | 6 | — |
| 用户画像与细分 | 15 | 8 | — |
| 品牌与差异化 | 24 | 12 | `brand-trust` |

**补充主题（5 个，第二轮精炼新增）**：

| 主题 | 条目数 | 商户覆盖 | 说明 |
|------|--------|---------|------|
| 运营成本与投入 | 16 | 9 | 房租、消耗品、单店投入控制 |
| 业务边界与排除策略 | 28 | 16 | "不做XX"类战略排除决策 |
| 班型与容量管理 | 13 | 6 | 小班人数、满员机制、入门课 |
| 企业/B端服务 | 2 | 2 | 企业客户差旅、B 端合作 |
| 数据获取限制 | 3 | 2 | 访谈拒绝、竞品信息不便分享 |

**注意**：一条知识可同时属于多个主题（关键词匹配机制），总分配数 > 316。Schema 1.0 的 `prepayment-risk`（预收款风控）和 `community-ops`（社群运营）两个旧主题在当前数据中已被"付费与定价模式"和"获客与营销"吸收。

### 3.4 生命周期状态机

```
draft → (≥3条支撑证据) → pending-review → (人工审核) → active
                                                          ↓
                                    (verification_count ≥ 10) → validated
                                    (contradiction_count ≥ 3) → challenged → deprecated
```

**硬性规则**：

- 只有 `active` 和 `validated` 的知识可被 Agent 在面向商家的输出中引用
- `deprecated` 的知识不可删除，须保留废弃原因和替代知识引用
- 超过 6 个月未验证 → 自动标记"待重新验证"
- 超过 12 个月 → 置信度自动降一级

---

## 四、Schema 2：Merchant Instance（门店实例）

### 4.1 核心设计原则

1. **事实优先**：只记录实体和事实，不嵌入过程性逻辑
2. **松耦合**：通过 `archetype_ref` 引用行业原型，不硬编码框架
3. **增量填充**：初始只需 `identity` + `archetype_binding`，后续逐步丰富
4. **置信度标注**：所有数值字段必须附带 `confidence`(0-1) + `source`
5. **决策痕迹**：每次诊断产生的 Agent建议 vs 用户修正 都记录在 `diagnostic_history.decision_traces`

### 4.2 结构速查

```yaml
schema_version: "0.1.0"
schema_type: "merchant-instance"

identity:              # 【最小必填】门店身份
  id, name, brand, industry, location, data_freshness

archetype_binding:     # 【必填】原型挂靠
  primary:             # 主原型 + confidence + matched_by
  secondary:           # 次原型列表（可选）
  deviations:          # 与原型的关键偏离

L0_business_essence:   # 生意本质（立场、收入核心、规模策略）
L1_financial_model:    # 财务模型（收入结构、成本结构、现金流、关键指标）
L2_business_architecture:  # 业务架构（获客/交付/留存三引擎）
L3_operational_modules:    # 运营模块（团队、指标、技术栈）
L4_data_relationships:     # 数据关系（因果链验证、本地关联发现）
cross_cutting:             # 横切维度（反人性本质、信任机制）

diagnostic_history:    # 【核心】诊断历史
  sessions:
    - facts_discovered     # 事实增量（字段路径 + 前后值 + 置信度）
    - decision_traces      # 决策痕迹（Agent建议 + 用户响应 + 修正内容 + 知识价值）
    - conclusions          # 诊断结论
  stats:                   # 累计统计（字段覆盖率、平均置信度）

tags:                  # 标签与索引
_meta:                 # 元数据（关联的 Industry Pack）
```

### 4.3 decision_traces 结构约束

每条决策痕迹必须包含：

```yaml
- topic: string                # 决策主题（如"该门店的原型归属"）
  agent_suggestion: string     # Agent 的原始建议
  owner_response: "accepted" | "modified" | "rejected"
  owner_modification: string | null   # 用户的修正内容（accepted 时为 null）
  insight_value: "high" | "medium" | "low"
```

**insight_value 判定规则**：

- `high`：修正揭示了 Agent 知识库的盲区（如模型误判、因果链缺失）
- `medium`：修正校准了数值或细化了条件
- `low`：修正属于表述偏好，无实质知识增量

### 4.4 source 枚举值

所有 `source` 字段使用统一枚举：

| 值 | 含义 | 置信度权重 |
|---|------|----------|
| `system_data` | SaaS/系统直接输出 | 最高 |
| `owner_report` | 门店主/管理者口述 | 中 |
| `diagnostic` | Agent 诊断推断 | 中 |
| `estimated` | 模型估算 | 低 |
| `xuecheng_doc` | 学城文档提取 | 中（需交叉验证） |

---

## 五、Schema 3：Judgment Events（判断事件 DDL）

### 5.1 核心表关系

```
members ←── training_sessions ──→ coaches
                    │
         ┌──────────┼──────────┐
         ↓          ↓          ↓
  training_plans  judgment_events  session_execution
         │                              │
         │          member_feedback ─────┘
         │
    agent_draft vs coach_final → diff_summary
```

### 5.2 judgment_events 表字段约束

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `trigger_signal` | TEXT NOT NULL | 必填 | 观察到什么/会员反馈什么 |
| `adjustment` | TEXT NOT NULL | 必填 | 教练做了什么调整 |
| `context` | JSONB | `{exercise_name, set_number, planned_weight_kg, planned_reps}` | 当时上下文 |
| `source` | TEXT NOT NULL | `voice_record` \| `post_session_review` \| `auto_diff` | 数据来源 |
| `raw_input` | TEXT | 可选 | 语音转文字原文 |
| `structured_data` | JSONB | 见下 | 结构化解析结果 |
| `confidence` | NUMERIC(3,2) | 0.00~1.00 | 结构化解析置信度 |

### 5.3 structured_data JSON 结构

```json
{
  "trigger_category": "fatigue|pain|form_issue|motivation|equipment|other",
  "adjustment_type": "reduce_weight|reduce_reps|swap_exercise|extend_rest|terminate|other",
  "severity": "low|medium|high",
  "body_part": "左膝"
}
```

### 5.4 training_plans 的 diff 机制

`agent_draft` 和 `coach_final` 使用完全相同的 JSON 结构，便于自动计算 diff：

```json
{
  "version": 1,
  "goal": "增肌",
  "exercises": [
    { "order": 1, "exercise_name": "杠铃深蹲", "sets": 4, "reps": 8, "weight_kg": 60, "rest_seconds": 90, "notes": "" }
  ],
  "warmup": "跑步机 5min + 动态拉伸",
  "cooldown": "泡沫轴放松 5min",
  "total_estimated_minutes": 60
}
```

`diff_summary` 自动计算：`{ "added": [...], "removed": [...], "modified": [{order, field, old, new}], "summary_text": "..." }`

### 5.5 辅助视图

- `v_session_panorama`：一跳查到会员、教练、计划、判断、反馈的完整课程上下文
- `v_low_confidence_judgments`：confidence < 0.5 的记录，用于人工复核

### 5.6 采集原则

- **不追求 100% 完整性**：每节课 3-5 条关键判断事件即可
- **追求持续性**：低负担确保教练长期坚持
- **三种来源互补**：课中语音（实时）+ 课后回顾（补充）+ 计划实际 diff（自动推断）

---

## 六、领域模型结构（fitness-domain-model/）

### 6.1 五层模型 + 两个横切维度

| 层级 | 关注点 | 核心内容 |
|------|--------|---------|
| L0 生意本质 | 商业模式分类 | 6种模式的决策树（收入核心 × 付费周期 × 规模策略） |
| L1 财务模型 | 钱怎么流 | 损益结构、现金流模式（均衡/前端集中/订阅） |
| L2 业务架构 | 如何运转 | 获客/交付/留存三引擎 + 模块间约束 |
| L3 运营模块 | 具体怎么做 | 线索、排课、生命周期管理、SaaS 格局 |
| L4 数据关系 | 指标因果 | 增长链/留存链/品质链/平台价值链 |
| 横切A | 反人性本质 | 利用派/顺应派/对抗派 |
| 横切B | 信任机制 | 消费者/商家-平台/行业内三类信任 |

### 6.2 四种经营模型

| 代号 | 名称 | 典型品牌 | 核心特征 |
|------|------|---------|---------|
| A | 预售驱动型传统俱乐部 | 威尔仕 | 年卡预售、赌用户不来 |
| B | 体验驱动型精品团课 | 超级猩猩 | 按次付费、教练IP |
| C | 效率驱动型互联网健身 | 乐刻 | 月卡、标准化、规模 |
| D | 专业驱动型私教工作室 | 独立工作室 | 教练专业度、深度服务 |

**关键约束**：不同模型有完全不同的评价标准，不可混用阈值。先定模型，再用该模型自己的标尺衡量。

### 6.3 模型健康度（当前状态）

- 覆盖度 0.45（5/10 原型已定义，缺瑜伽/CrossFit/代运营等）
- 准确度 0.3（18 条断言中 5 条充分验证）
- 时效性 0.8（数据 2024-2025Q1）
- 案例数 6 个
- 未解决矛盾 1 个（PURE 反例）

### 6.4 统一术语（ubiquitous-language）

Agent 在与商家交互、生成报告、提取知识时，必须使用 `ubiquitous-language.yaml` 中定义的术语。关键术语包括：

- 商户分类：健身中心/团课工作室/私教工作室/新型健身房/包月私教馆
- 收入模型：会籍收入/私教收入/团课收入/储值收入
- 获客术语：线索/访购率/到店转化率/CPL/获客渠道
- 用户行为：到店频次/换店行为/品类流转/会员生命周期
- 运营指标：满座率/坪效/教练流失率/核销率

---

## 七、学城文档分析约束

当 Agent 从学城访谈文档中提取知识时，必须遵循以下规则：

### 7.1 提取流程

```
读取学城文档原文
    ↓
识别文档类型：商家拜访 | 行业报告 | 用户行为分析 | 其他
    ↓
按四层结构提取（对应 Schema 2.0 的 layer）：
    ├── 事实层（fact）：可验证的数据性断言
    ├── 规则层（rule）：经营规则或经验法则
    ├── 排除项（exclusion）：明确不做的事情
    └── 因果链（causal）：因果关系链条
    ↓
标注 knowledge_domain（"去掉测试"判定，见 §3.2a）
    ↓
转为 Schema 2.0 格式（见 §3.1）
    ↓
标注 evidence.confidence = "disputed" + evidence.source = "interview"
```

### 7.2 提取约束

1. **每条知识必须可溯源**：`context.merchant` 必须填入商户名称，文档来源记录在提取摘要中
2. **区分事实与观点**：商家口述的观点需标注 `evidence.confidence: disputed`，除非有数据支撑
3. **标注知识领域**：每条知识必须判定 `knowledge_domain`（industry_intrinsic / platform_perspective / interviewer_artifact），使用"去掉测试"原则（§3.2a）
4. **识别矛盾**：如果提取内容与已有知识库条目冲突，不要覆盖，而是创建 `field-evidence` 记录并标注冲突
5. **不做推断性概括**：提取阶段只记录文档中明确表达的内容，推断和概括留给分析层

### 7.3 质量门禁

- 单一文档提取的知识初始 `status: draft`，不直接进入 `active`
- 同一事实在 ≥3 篇独立文档中被佐证 → 可升级为 `pending-review`
- 学城文档数据的权重低于 SaaS 系统数据：`xuecheng_doc` 的置信度权重为中

### 7.4 输出格式

提取结果应输出为结构化 JSON 文件，每条知识一个条目，格式符合 §3.1 Schema 2.0 结构。文件结构与 `knowhow-upgraded.json` 保持一致（按文档组织，每篇文档含 `entries` 数组）。同时输出一份提取摘要（markdown），包含：

- 文档来源列表
- 各 `knowledge_domain` 分布统计
- 各 `layer` 类型数量统计
- 发现的矛盾或存疑点
- 与已有知识库的比对结果

---

## 八、知识温度与更新机制

| 温度 | 内容 | 更新频率 | 更新方式 | 对应资产 |
|------|------|---------|---------|---------|
| 🧊 冷 | 框架结构、模型分类、层级定义 | 年度 | 人工决策 | `model-definitions.md` 结构 |
| 🌡️ 温 | 基准数据、阈值表、矛盾检测规则 | 季度 | 半自动（数据+人工审核） | `diagnostic-rules.md` 数值 |
| 🔥 热 | 案例、intervention 效果、新发现 | 实时 | 全自动捕获 + 定期提炼 | `know-how/*`、`case-studies/*` |

---

## 九、因果关系结构

### 9.1 因果角色类型

知识原子之间的因果关系使用五种标注（含 null）：

| 类型 | 含义 | 当前数据量 | 示例 |
|------|------|-----------|------|
| `drives` | A 驱动 B 提升 | 72 条 | 教练留存率 drives 会员续课率 |
| `enables` | A 是 B 的前置条件 | 0 条（已定义，待数据验证） | 数据能力 enables 精准营销 |
| `vetoes` | A 阻断 B | 10 条 | 高教练流失率 vetoes 服务标准化 |
| `constrains` | A 限制 B 的上限 | 6 条 | 场地面积 constrains 同时容纳人数 |
| `null` | 非因果条目 | 340 条 | 无因果关系的事实/规则/排除项 |

**注意**：`null` 表示该条目不描述因果关系（如纯事实 "前期投入100万"）。在 JSON 中存储为字符串 `"null"` 而非 JSON null 值。`enables` 虽已定义但当前数据中尚无实例，保留定义以备后续使用。

### 9.2 置信度生命周期

所有 Schema（1.0 和 2.0）统一使用以下置信度体系：

```
disputed（存疑）→ adopted（采信）→ falsified（证伪）
```

- `disputed`：首次发现，尚无充分证据。当前数据中大部分条目处于此状态
- `adopted`：≥3 条独立证据支撑，经过 SaaS 数据验证
- `falsified`：被新事实推翻，但不删除——保留推翻证据链作为高价值资产。当前数据中尚无实例

---

## 十、三层知识体系（教练场景）

```
┌──────────────────────────────────────┐
│ 第三层：教练个人偏好                    │  ← 随使用积累，归教练个人所有
├──────────────────────────────────────┤
│ 第二层：店铺集体经验                    │  ← 从多教练共性决策中提炼，归健身房所有
├──────────────────────────────────────┤
│ 第一层：行业通用知识 (NSCA/ACSM指南)    │  ← 公开知识，所有人共享
└──────────────────────────────────────┘

新教练入职 → 即拥有第一、二层知识
个人层数据 → 归教练所有，可携带
店铺层数据 → 归健身房所有
```

---

## 十一、防污染与质量保障

### 数据质量规则

- 单一来源数据不直接更新基准，需 ≥3 个独立来源交叉验证
- SaaS 系统数据权重 > 口述数据（置信度加权）
- 异常值自动隔离：偏离现有分布 >2 倍标准差 → 标记待验证
- 商家对 Agent 判断说"不对"时，记录为 `field-evidence/diagnostic-feedback/`，不直接修改规则

### 知识新鲜度

- 每条 `active` 知识有 `last_verified` 字段
- 超 6 个月未验证 → 自动标记"待重新验证"
- 超 12 个月 → 置信度降一级
- `benchmark` 类知识每季度如有 >20 样本须重新计算

---

## 十二、文件资产索引

Agent 执行任务时可参考的已有文件：

| 文件/目录 | 路径 | 用途 |
|-----------|------|------|
| **Know-How 知识库（Schema 2.0）** | `~/catdesk_workspace/knowhow-upgraded.json` | **当前主知识库**，428 条条目，21 篇文档，Schema 2.0 格式 |
| Know-How 仪表盘 | `~/catdesk_workspace/knowhow-upgraded-dashboard.html` | 交互式可视化：主题聚类（18 个）、跨商户共识、因果图谱、商户画像、数据质量 |
| 原始 Know-How（Schema 1.0） | `~/catdesk_workspace/knowhow-raw-metadata.json` | 升级前的原始提取数据，已被 knowhow-upgraded.json 替代 |
| 知识提取摘要 | `~/catdesk_workspace/knowhow-extraction-summary.md` | 早期 11 篇访谈的提取报告（知识库已扩展至 21 篇） |
| 门店实例 Schema | `~/catdesk_workspace/merchant-instance-schema.yaml` | 门店数据的完整字段定义 |
| 门店实例示例 | `~/catdesk_workspace/merchant-instance-example.yaml` | 超级猩猩静安寺店实例 |
| 判断事件 DDL | `~/catdesk_workspace/gym-judgment-metadata-schema.sql` | PostgreSQL 表结构 |
| Know-How 设计 | `~/catdesk_workspace/know-how-accumulation-design.md` | 知识积累系统完整设计 |
| 领域模型 | `~/catdesk_workspace/fitness-domain-model/` | L0-L4 五层模型全套 |
| 领域模型元数据 | `~/catdesk_workspace/fitness-domain-model/meta.yaml` | 版本、来源、健康度 |
| 统一术语 | `~/catdesk_workspace/fitness-domain-model/ubiquitous-language.yaml` | 必须使用的行业术语 |
| 模型健康度 | `~/catdesk_workspace/fitness-domain-model/validation/model-health.yaml` | 当前数据健康状态 |
| 经营诊断 Skill | `~/.catpaw/skills/gym-business-analyzer/` | 四模型诊断规则引擎 |

---

## 十三、设计哲学备忘

以下是贯穿整个体系的核心设计决策，Agent 在做任何结构性判断时应参照：

1. **Write Path 原则**：知识必须在决策发生的现场被捕获，不是事后回忆
2. **事实优先，过程后挂**：Schema 核心是实体和事实，过程状态是临时的
3. **先用后存**：每条知识必须有明确的"调用场景"，不存没人用的知识
4. **方案 B 路线**：底层只录入事实和规则，高层概念（战略一致性、因果结构）是 Agent 推断输出，不是人工输入
5. **模型即边界**：不同经营模型有完全不同的评价标准，不可混用阈值
6. **可证伪性**：每条断言都有 `falsifiable_by` 字段，每条知识都可能被推翻
7. **Decision Trace 是最高价值资产**：Agent 建议是 structured prior，人类修正是 judgment signal，两者的 delta 不可丢失

---

## 十四、Skill 与 Schema 的迭代机制

本 Skill 和它约束的三套 Schema 不是一成不变的。它们需要随着业务发展和数据积累持续演进。以下是迭代的触发条件、流程和保护机制。

### 14.1 什么时候应该迭代 Schema

| 触发信号 | 影响范围 | 迭代类型 | 谁来触发 |
|---------|---------|---------|--------|
| Agent 在诊断中发现字段不够用（如缺少某个维度的数据槽位） | merchant-instance-schema | 字段扩展 | Agent 记录 → 人工审核 |
| 新的经营模型出现（如 AI 私教工作室不归入 A/B/C/D 任何一类） | 领域模型 L0 + 全链路 | 模型扩展 | 人工决策 |
| 教练反馈判断事件的 structured_data 枚举值不够（如出现新的 trigger_category） | judgment_events DDL | 枚举扩展 | Agent 标记 → 季度审核 |
| 知识原子的 type 分类不能覆盖某种新发现的知识形态 | Knowledge Atom | 类型扩展 | 人工决策 |
| 同一个 Schema 变更被 ≥3 次独立的诊断/采集场景触发 | 对应 Schema | 确认迭代 | 自动触发审核 |
| 新行业接入（如从健身扩展到棋牌室） | 全体 Schema | 抽象化重构 | 人工决策（Phase 2 战略） |
| 置信度机制或生命周期规则在实际运行中产生了误判（如过早降级有效知识） | 质量门禁规则 | 规则调优 | 运行数据驱动 |

### 14.2 迭代分级

**Patch（补丁级 x.x.+1）**：不破坏现有数据的扩展。

- 新增可选字段（如 merchant-instance 增加一个 L3 下的可选指标）
- 扩展枚举值（如 structured_data.trigger_category 增加 "progression"）
- 新增知识主题（如从 18 个主题扩展到 19 个）
- 修正文档中的歧义或错误描述
- **操作**：直接修改本 SKILL.md + 对应源文件，更新 version 末位

**Minor（小版本 x.+1.0）**：结构性变化但向后兼容。

- 新增必填字段（需要回填已有数据）
- 修改因果关系类型定义
- 调整生命周期状态机的转移条件
- 新增一套 Schema（如未来增加「社群互动事件」Schema）
- **操作**：修改本 SKILL.md + 源文件 + 编写迁移说明 + 更新 version 中位

**Major（大版本 +1.0.0）**：不向后兼容的重构。

- 修改 Schema 的核心结构（如 merchant-instance 的层级重组）
- 合并或拆分 Schema
- 跨行业抽象化（Phase 2 扩展时必然触发）
- **操作**：新旧版本并行一个迭代周期 → 数据迁移 → 废弃旧版本

### 14.3 迭代流程

```
发现变更需求
    ↓
Agent 在 decision_traces 或 field-evidence 中记录
    {
      type: "schema_change_request",
      affected_schema: "merchant-instance" | "judgment_events" | "knowledge_atom",
      description: "诊断中发现缺少XX字段",
      triggered_by: "session_id / case_id",
      frequency: 1  // 被触发的次数
    }
    ↓
frequency 累积到 ≥3 → 自动标记为「待审核」
    ↓
人工审核：
    ├── 确认需要 → 判定迭代级别 (Patch/Minor/Major)
    ├── 暂不需要 → 记录为「已评估-暂缓」，保留触发记录
    └── 拒绝 → 记录拒绝原因，防止重复提议
    ↓
执行变更：
    ├── 修改本 SKILL.md 的对应章节
    ├── 同步修改源文件（.yaml / .sql / .md）
    ├── 更新 schema_version 字段
    ├── 如果是 Minor/Major → 编写迁移说明
    └── 更新本节的「变更日志」
```

### 14.4 保护机制

**禁止事项**：

- Agent 不可自行修改 Schema 结构（只能记录变更请求，由人工审核后执行）
- 不可删除已有字段（只能标记为 deprecated 并保留）
- 不可修改枚举值的语义（已有值的含义不可变，只能新增）
- 不可降低置信度门禁的标准（如把 ≥3 条证据改为 ≥1 条）

**版本追踪**：

- 本 SKILL.md 的 frontmatter 中 `version` 字段与所有源文件的 `schema_version` 保持同步
- 每次迭代须更新本文件的「最后更新」日期
- Major 变更须在记忆系统中记录（memory_write type=longterm）

### 14.5 本 Skill 文档自身的迭代

本 SKILL.md 作为约束文档，自身也需要迭代。触发条件：

- 新增了 Schema → 本文档需要新增对应章节
- 源文件的结构发生了实质性变化 → 本文档的「结构速查」需同步
- 与其他 Skill 的协作关系变化（如新增了一个 Skill 需要引用本约束）→ 更新 §0 协作关系
- 实际使用中发现触发规则不准确（漏触发或误触发）→ 调整 §0 触发条件

**自检清单**（每季度或重大迭代后执行）：

- [ ] 文件资产索引 (§12) 中的所有路径是否仍然有效
- [ ] 四种经营模型的定义是否需要更新（是否出现了新的模型类型）
- [ ] 知识主题清单 (§3.3) 是否需要扩展
- [ ] 统一术语 (§6.4) 是否与 ubiquitous-language.yaml 保持同步
- [ ] 源文件的 schema_version 是否与本文档的 version 一致
- [ ] 与 gym-business-analyzer、coach-agent 的协作描述是否准确

### 14.6 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 0.2.0 | 2026-06-30 | **Minor 升级**：新增 Schema 2.0 结构定义（§3.1），与 Schema 1.0 建立映射（§3.1b）；新增 knowledge_domain 三分类维度（§3.2a）及"去掉测试"判定流程；主题清单从 13 个理论主题替换为 18 个数据驱动聚类主题（§3.3）；统一置信度体系为 disputed/adopted/falsified（消除 §3.1 与 §9 矛盾）；因果角色补充 null 定义、标注 enables 待验证（§9.1）；学城提取流程更新为 Schema 2.0 格式（§7）；文件索引新增 knowhow-upgraded.json 和仪表盘，移除已废弃文件（§12）|
| 0.1.0 | 2026-06-30 | 初始版本：整合三套 Schema + 学城分析约束 + 触发规则 + 迭代机制 |

---

*本 Skill 由已有设计文档整合而成，源文件分布于 catdesk_workspace 工作空间。Schema 变更须遵循 §14 迭代机制，禁止 Agent 自行修改结构。*
