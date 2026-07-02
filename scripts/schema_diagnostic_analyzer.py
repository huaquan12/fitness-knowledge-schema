#!/usr/bin/env python3
"""
schema_diagnostic_analyzer.py
基于 Schema 2.0 对结构化知识库执行诊断分析运算。

分析维度：
1. 跨文档因果链分析 — 识别反复出现的因果模式
2. 知识领域过滤诊断 — 仅用 industry_intrinsic 做行业规律提取
3. 经营模型谱系分析 — 按 business_model 聚类，提取模式差异
4. 置信度审计 — 标注 adopted 高置信结论 vs disputed 待验证
5. 排除策略对比 — 各商户"不做什么"的差异分析
6. 因果角色矩阵 — drives/vetoes/constrains 的分布与含义

输出：analysis/schema-diagnostic-report.json + analysis/schema-diagnostic-report.md
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import date

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
STRUCTURED_PATH = os.path.join(DATA_DIR, "structured", "knowhow-upgraded.json")
RAW_SUMMARY_PATH = os.path.join(DATA_DIR, "raw", "knowhow-extraction-summary.md")
OUTPUT_DIR = os.path.join(DATA_DIR, "analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_structured():
    with open(STRUCTURED_PATH, encoding="utf-8") as f:
        return json.load(f)


def load_raw_summary():
    with open(RAW_SUMMARY_PATH, encoding="utf-8") as f:
        return f.read()


# ─── Analysis Functions ───

def analyze_causal_chains(documents):
    """跨文档因果链分析：提取所有 causal 条目，按因果模式聚类"""
    causal_entries = []
    for doc in documents:
        for entry in doc.get("entries", []):
            if entry["layer"] == "causal":
                causal_entries.append({
                    "merchant": doc["merchant_name"],
                    "category": doc["category"],
                    "claim": entry["claim"],
                    "causal_role": entry["causal_role"],
                    "confidence": entry["evidence"]["confidence"],
                    "domain": entry["knowledge_domain"],
                })
    
    # 方式1: 精确短语匹配（→ 分隔的完整短语）
    node_counter = Counter()
    node_merchants = defaultdict(set)
    for ce in causal_entries:
        parts = re.split(r'→', ce["claim"])
        for part in parts:
            part = part.strip()
            if len(part) > 2:
                node_counter[part] += 1
                node_merchants[part].add(ce["merchant"])
    
    cross_doc_nodes = []
    for node, count in node_counter.most_common(50):
        merchants = node_merchants[node]
        if len(merchants) >= 3:
            cross_doc_nodes.append({
                "node": node,
                "mention_count": count,
                "merchant_count": len(merchants),
                "merchants": sorted(merchants),
            })
    
    # 方式2: 语义关键词匹配（业务术语）
    KEY_TERMS = re.compile(
        r'(按次付费|预付费|月卡|年卡|私教|团课|小面积|大面积|社区|商圈|高端|低价|'
        r'教练|口碑|社群|标准化|坪效|翻台|租金|现金流|获客|留存|复购|转化|扩张|规模化|'
        r'品牌|课程|体验|定价|营销|裂变|平台|佣金|SaaS|差异化|壁垒|私域|抖音|美团|点评|'
        r'品类|精品|性价比|客单价|会员|选址|稀缺|供给|需求|低门槛|高成本)'
    )
    keyword_merchants = defaultdict(set)
    keyword_count = Counter()
    for ce in causal_entries:
        terms = KEY_TERMS.findall(ce["claim"])
        for term in terms:
            keyword_merchants[term].add(ce["merchant"])
            keyword_count[term] += 1
    
    cross_doc_keywords = []
    for term, count in keyword_count.most_common(30):
        merchants = keyword_merchants[term]
        if len(merchants) >= 3:
            cross_doc_keywords.append({
                "keyword": term,
                "mention_count": count,
                "merchant_count": len(merchants),
                "merchants": sorted(merchants),
            })
    
    return {
        "total_causal_entries": len(causal_entries),
        "cross_document_patterns": cross_doc_nodes,
        "cross_document_keywords": cross_doc_keywords,
        "all_causal_entries": causal_entries,
    }


def analyze_by_business_model(documents):
    """按经营模型聚类，提取每个模型的特征模式"""
    model_groups = defaultdict(lambda: {"merchants": [], "entries": [], "exclusions": [], "causal": []})
    
    for doc in documents:
        profile = doc.get("store_profile", {})
        model = profile.get("business_model", doc.get("category", "未知"))
        model_groups[model]["merchants"].append(doc["merchant_name"])
        
        for entry in doc.get("entries", []):
            if entry["knowledge_domain"] == "industry_intrinsic":
                model_groups[model]["entries"].append({
                    "merchant": doc["merchant_name"],
                    "layer": entry["layer"],
                    "claim": entry["claim"],
                    "causal_role": entry["causal_role"],
                    "confidence": entry["evidence"]["confidence"],
                })
                if entry["layer"] == "exclusion":
                    model_groups[model]["exclusions"].append(entry["claim"])
                elif entry["layer"] == "causal":
                    model_groups[model]["causal"].append(entry["claim"])
    
    model_profiles = []
    for model, data in model_groups.items():
        if len(data["merchants"]) == 0:
            continue
        # 提取该模型下所有因果链的关键词
        causal_keywords = []
        for c in data["causal"]:
            causal_keywords.extend([p.strip() for p in re.split(r'→', c)])
        keyword_freq = Counter(causal_keywords).most_common(5)
        
        model_profiles.append({
            "business_model": model,
            "merchant_count": len(data["merchants"]),
            "merchants": data["merchants"],
            "total_entries": len(data["entries"]),
            "exclusion_count": len(data["exclusions"]),
            "causal_count": len(data["causal"]),
            "top_causal_keywords": keyword_freq,
            "exclusions": data["exclusions"],
            "causal_chains": data["causal"],
        })
    
    return sorted(model_profiles, key=lambda x: x["merchant_count"], reverse=True)


def analyze_confidence_audit(documents):
    """置信度审计：区分已验证结论与待验证假设"""
    adopted = []
    disputed = []
    falsified = []
    
    for doc in documents:
        for entry in doc.get("entries", []):
            record = {
                "merchant": doc["merchant_name"],
                "category": doc["category"],
                "claim": entry["claim"],
                "layer": entry["layer"],
                "domain": entry["knowledge_domain"],
                "causal_role": entry["causal_role"],
            }
            conf = entry["evidence"]["confidence"]
            if conf == "adopted":
                adopted.append(record)
            elif conf == "disputed":
                disputed.append(record)
            elif conf == "falsified":
                falsified.append(record)
    
    return {
        "adopted_count": len(adopted),
        "disputed_count": len(disputed),
        "falsified_count": len(falsified),
        "adopted_rate": f"{len(adopted)/(len(adopted)+len(disputed)+len(falsified))*100:.1f}%",
        "adopted_entries": adopted,
        "disputed_entries": disputed,
    }


def analyze_exclusion_strategy(documents):
    """排除策略对比：各商户'不做什么'的差异"""
    exclusions_by_merchant = {}
    all_exclusion_phrases = []
    
    for doc in documents:
        merchant = doc["merchant_name"]
        exclusions = []
        for entry in doc.get("entries", []):
            if entry["layer"] == "exclusion" and entry["knowledge_domain"] == "industry_intrinsic":
                exclusions.append(entry["claim"])
                all_exclusion_phrases.append(entry["claim"])
        if exclusions:
            exclusions_by_merchant[merchant] = exclusions
    
    # 提取排除策略中的关键动词模式
    verb_patterns = Counter()
    for phrase in all_exclusion_phrases:
        # 提取 "不..." 开头的模式
        if phrase.startswith("不"):
            # 取前4个字作为模式
            pattern = phrase[:4]
            verb_patterns[pattern] += 1
    
    return {
        "total_exclusions": len(all_exclusion_phrases),
        "merchants_with_exclusions": len(exclusions_by_merchant),
        "exclusion_by_merchant": exclusions_by_merchant,
        "common_exclusion_patterns": verb_patterns.most_common(10),
    }


def analyze_causal_role_matrix(documents):
    """因果角色矩阵：drives/vetoes/constrains 的分布与含义"""
    role_entries = defaultdict(list)
    
    for doc in documents:
        for entry in doc.get("entries", []):
            role = entry["causal_role"]
            if role != "null":
                role_entries[role].append({
                    "merchant": doc["merchant_name"],
                    "category": doc["category"],
                    "claim": entry["claim"],
                    "domain": entry["knowledge_domain"],
                    "confidence": entry["evidence"]["confidence"],
                })
    
    # 按 role 分析特征
    role_analysis = {}
    for role, entries in role_entries.items():
        # 提取因果链的起点（→ 前的内容）
        start_points = []
        for e in entries:
            parts = re.split(r'→', e["claim"])
            if parts:
                start_points.append(parts[0].strip())
        
        role_analysis[role] = {
            "count": len(entries),
            "merchants": sorted(set(e["merchant"] for e in entries)),
            "merchant_count": len(set(e["merchant"] for e in entries)),
            "top_start_points": Counter(start_points).most_common(5),
            "sample_claims": [e["claim"] for e in entries[:5]],
        }
    
    # null 的统计
    null_count = sum(1 for doc in documents for e in doc.get("entries", []) if e["causal_role"] == "null")
    
    return {
        "role_distribution": {role: len(entries) for role, entries in role_entries.items()},
        "null_count": null_count,
        "role_analysis": role_analysis,
    }


def derive_schema_conclusions(causal_analysis, model_analysis, confidence_audit, exclusion_analysis, role_matrix):
    """基于 Schema 运算结果，推导诊断结论"""
    conclusions = []
    
    # 1. 从跨文档语义关键词推导
    for kw in causal_analysis.get("cross_document_keywords", [])[:8]:
        if kw["merchant_count"] >= 4:
            conclusions.append({
                "conclusion": f"跨文档因果关键词（{kw['merchant_count']}个商户）：{kw['keyword']}",
                "evidence_type": "cross_document_causal_keyword",
                "merchants": kw["merchants"],
                "confidence": "high（多文档交叉验证）",
                "schema_basis": f"causal entries中'{kw['keyword']}'出现{kw['mention_count']}次, 覆盖{kw['merchant_count']}个商户",
            })
    
    # 2. 从经营模型聚类推导
    for model in model_analysis[:5]:
        if model["causal_count"] >= 3:
            top_chain = model["causal_chains"][0] if model["causal_chains"] else ""
            conclusions.append({
                "conclusion": f"经营模型「{model['business_model']}」核心因果：{top_chain}",
                "evidence_type": "model_cluster_causal",
                "merchants": model["merchants"],
                "confidence": "medium（模型内验证）",
                "schema_basis": f"business_model={model['business_model']}, causal_count={model['causal_count']}",
            })
    
    # 3. 从排除策略推导
    common = exclusion_analysis["common_exclusion_patterns"]
    if common:
        top_pattern = common[0]
        conclusions.append({
            "conclusion": f"行业共识性排除策略：{top_pattern[0]}（{top_pattern[1]}个商户明确排除）",
            "evidence_type": "exclusion_consensus",
            "merchants": list(exclusion_analysis["exclusion_by_merchant"].keys()),
            "confidence": "medium（多商户排除一致）",
            "schema_basis": f"layer=exclusion, pattern='{top_pattern[0]}', count={top_pattern[1]}",
        })
    
    # 4. 从因果角色推导
    if "vetoes" in role_matrix["role_analysis"]:
        veto_data = role_matrix["role_analysis"]["vetoes"]
        conclusions.append({
            "conclusion": f"行业否定性因果（vetoes）：{veto_data['sample_claims'][0]}",
            "evidence_type": "causal_veto",
            "merchants": veto_data["merchants"],
            "confidence": "medium（否定性约束）",
            "schema_basis": f"causal_role=vetoes, count={veto_data['count']}",
        })
    
    if "constrains" in role_matrix["role_analysis"]:
        constrain_data = role_matrix["role_analysis"]["constrains"]
        conclusions.append({
            "conclusion": f"行业约束性因果（constrains）：{constrain_data['sample_claims'][0]}",
            "evidence_type": "causal_constrain",
            "merchants": constrain_data["merchants"],
            "confidence": "medium（约束性限制）",
            "schema_basis": f"causal_role=constrains, count={constrain_data['count']}",
        })
    
    # 5. 从置信度审计推导
    adopted = confidence_audit["adopted_entries"]
    if adopted:
        # 按 domain 分组
        adopted_by_domain = defaultdict(list)
        for a in adopted:
            adopted_by_domain[a["domain"]].append(a)
        
        for domain, entries in adopted_by_domain.items():
            if len(entries) >= 3:
                conclusions.append({
                    "conclusion": f"已验证结论（{domain}）：{entries[0]['claim']}",
                    "evidence_type": "adopted_confidence",
                    "merchants": sorted(set(e["merchant"] for e in entries)),
                    "confidence": "high（confidence=adopted）",
                    "schema_basis": f"confidence=adopted, domain={domain}, count={len(entries)}",
                })
    
    return conclusions


def main():
    data = load_structured()
    documents = data["documents"]
    
    print("=== Schema 诊断分析开始 ===")
    print(f"总文档数: {len(documents)}")
    print(f"总条目数: {data['stats']['total_entries']}")
    print()
    
    # 执行各维度分析
    causal_analysis = analyze_causal_chains(documents)
    print(f"✓ 因果链分析: {causal_analysis['total_causal_entries']} 条因果条目, {len(causal_analysis['cross_document_keywords'])} 个跨文档语义关键词")
    
    model_analysis = analyze_by_business_model(documents)
    print(f"✓ 经营模型聚类: {len(model_analysis)} 个模型分组")
    
    confidence_audit = analyze_confidence_audit(documents)
    print(f"✓ 置信度审计: adopted={confidence_audit['adopted_count']}, disputed={confidence_audit['disputed_count']}, rate={confidence_audit['adopted_rate']}")
    
    exclusion_analysis = analyze_exclusion_strategy(documents)
    print(f"✓ 排除策略分析: {exclusion_analysis['total_exclusions']} 条排除, {exclusion_analysis['merchants_with_exclusions']} 个商户")
    
    role_matrix = analyze_causal_role_matrix(documents)
    print(f"✓ 因果角色矩阵: {role_matrix['role_distribution']}, null={role_matrix['null_count']}")
    
    # 推导诊断结论
    schema_conclusions = derive_schema_conclusions(
        causal_analysis, model_analysis, confidence_audit, exclusion_analysis, role_matrix
    )
    print(f"\n✓ Schema 推导结论: {len(schema_conclusions)} 条")
    
    # 输出 JSON
    report = {
        "analysis_date": str(date.today()),
        "schema_version": data["schema_version"],
        "data_source": "structured/knowhow-upgraded.json",
        "summary": {
            "total_documents": len(documents),
            "total_entries": data["stats"]["total_entries"],
            "analysis_dimensions": 5,
            "derived_conclusions": len(schema_conclusions),
        },
        "causal_chain_analysis": causal_analysis,
        "business_model_analysis": model_analysis,
        "confidence_audit": confidence_audit,
        "exclusion_strategy_analysis": exclusion_analysis,
        "causal_role_matrix": role_matrix,
        "schema_derived_conclusions": schema_conclusions,
    }
    
    json_path = os.path.join(OUTPUT_DIR, "schema-diagnostic-report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📄 JSON 报告: {json_path}")
    
    return report


if __name__ == "__main__":
    main()
