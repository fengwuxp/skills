#!/usr/bin/env python3
"""Audit Skill Eval prompt fixtures.

This script is offline and read-only. It validates that prompt fixtures cover
realistic positive cases, hard negatives, source metadata, and evaluation
dimensions. It does not run agents, call networks, upload files, or judge domain
truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "skill-eval" / "prompt-cases.json"

SKILLS = {
    "wise-agent",
    "business-website-planner",
    "document-authoring",
    "fiction-visual-designer",
    "grill-me",
    "hanzi-philology",
    "huaxia-practical-wisdom",
    "java-service-code-generator",
    "learning-coach",
    "llm-coding-hygiene",
    "novelist",
    "payment-expert",
    "payment-funds-review",
    "product-architecture-expert",
    "requirement-acceptance-testing",
    "resource-capability-distiller",
    "security-engineering-expert",
    "senior-software-architect",
    "ui-design-expert",
    "wind-coding-conventions",
}
EXTERNAL_COMPETITOR_SKILLS = {"ai-slop-detector"}
KNOWN_SKILLS = SKILLS | EXTERNAL_COMPETITOR_SKILLS | {"imagegen"}
EXPLICIT_INVOCATION_SKILLS = {
    "business-website-planner",
    "fiction-visual-designer",
    "learning-coach",
    "requirement-acceptance-testing",
    "wise-agent",
}
SKILL_MENTIONS = {
    "business-website-planner": ["business-website-planner", "业务官网规划师"],
    "wise-agent": [
        "$wise-agent",
        "wise-agent",
        "知止者",
    ],
    "document-authoring": ["document-authoring", "专业文档撰写"],
    "fiction-visual-designer": ["fiction-visual-designer", "小说视觉设计师"],
    "grill-me": ["grill-me", "grill me", "盘问", "拷问"],
    "hanzi-philology": ["hanzi-philology", "汉字学与训诂专家"],
    "huaxia-practical-wisdom": [
        "huaxia-practical-wisdom",
        "华夏经世智慧",
        "老祖宗智慧",
    ],
    "java-service-code-generator": ["java-service-code-generator"],
    "learning-coach": ["learning-coach", "持续学习教练"],
    "llm-coding-hygiene": [
        "llm-coding-hygiene",
        "LLM 编码卫生",
        "Karpathy Guidelines",
        "karpathy-guidelines",
    ],
    "novelist": ["novelist", "小说家"],
    "payment-expert": ["payment-expert", "支付专家"],
    "payment-funds-review": ["payment-funds-review", "支付资金审查"],
    "product-architecture-expert": ["产品架构专家", "product-architecture-expert"],
    "requirement-acceptance-testing": ["requirement-acceptance-testing", "需求验收测试"],
    "resource-capability-distiller": [
        "resource-capability-distiller",
        "资源炼技",
        "多源材料提炼",
    ],
    "security-engineering-expert": ["security-engineering-expert", "安全工程专家"],
    "senior-software-architect": ["资深架构师", "senior-software-architect"],
    "ui-design-expert": ["ui-design-expert", "UI 设计专家"],
    "wind-coding-conventions": ["wind-coding-conventions", "Wind 编码约规"],
}
REQUIRED_DIMENSIONS = {
    "trigger_accuracy",
    "output_quality",
    "efficiency_metrics",
    "baseline_comparison",
    "variance_check",
}
SOURCE_FIELDS = {
    "title",
    "url",
    "account",
    "author",
    "published_at",
    "read_at",
    "read_method",
    "read_status",
}
TRIVIAL_PROMPT_TERMS = {
    "fibonacci",
    "斐波那契",
    "hello world",
    "写个函数",
}
SENSITIVE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"AKIA[0-9A-Z]{16}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(api[_-]?key|token|secret|password)\s*[:=]\s*['\"][^'\"]+",
        r"\b\d{16,19}\b",
    ]
]
REQUIRED_PAYMENT_HARD_NEGATIVES = {
    "payment-negative-isolated-refund-page": ["退款", "不涉及原支付"],
    "payment-negative-generic-order": ["普通电商订单", "不涉及支付"],
}
REQUIRED_PAYMENT_POSITIVES = {
    "payment-should-partial-refund-limit": ["部分退款", "原支付", "累计可退"],
}
REQUIRED_RESOURCE_DISTILLER_CASES = {
    "resource-capability-distiller-should-preserve-compression-sensitive-evidence": {
        "hard_negative": False,
        "query_terms": ["专家案例", "失败样例", "压缩保真"],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "resource-capability-distiller-should-reject-label-only-distillation": {
        "hard_negative": False,
        "difficulty": "edge",
        "query_terms": ["风格标签", "不保留语料索引", "直接宣布能力已经蒸馏完成"],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
}
REQUIRED_WISE_CONTRACT_CASES = {
    "wise-agent-should-coordinate-peer-authority-contract-deliberation": {
        "query_terms": ["业务能力消费者", "资金能力提供方", "公共契约", "独立 Checker"],
        "expected_terms": [
            "确认讨论主题",
            "decision_questions",
            "Shared Information Matrix",
            "fact / evidence / assumption / unknown / dependency",
            "received / understood / disputed / missing",
            "authority_ref 与版本合并",
            "Owner、停止条件和 blocks_current_decision",
            "blocks_current_decision=true 都强制 blocked",
            "Information Readiness Gate",
            "信息未充分交换",
            "不得进入观点讨论或决策",
            "topic_revision",
            "information_revision",
            "accepted_topic_revision",
            "accepted_information_revision",
            "Contract Inquiry",
            "Provider Evidence Response",
            "Consumer Reconciliation",
            "confirmed / conflict / reopen / stale",
        ],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-reject-permanent-peer-chat": {
        "query_terms": ["长期自动互聊", "边聊边改", "不做版本化", "不等独立 Checker"],
        "expected_terms": ["停止", "execution steward", "版本", "Checker", "不产生执行授权"],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-coordinate-multi-party-authority-deliberation": {
        "query_terms": ["四个长期任务", "独立事实", "共同裁定", "永久群聊"],
        "expected_terms": [
            "一主、多权、独立证",
            "主持式星型拓扑",
            "Meeting Charter",
            "decision_questions",
            "Shared Information Matrix",
            "fact / evidence / assumption / unknown / dependency",
            "received / understood / disputed / missing",
            "authority_ref 与版本合并",
            "Owner、停止条件和 blocks_current_decision",
            "blocks_current_decision=true 都强制 blocked",
            "Information Readiness Gate",
            "信息未充分交换",
            "不得进入观点讨论或决策",
            "topic_revision",
            "information_revision",
            "accepted_information_revision",
            "Position Card",
            "Conflict Matrix",
            "Meeting Resolution",
        ],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-reject-free-form-group-chat": {
        "query_terms": ["六个长期任务", "长期自由群聊", "不设主持者", "不做版本化"],
        "expected_terms": [
            "拒绝",
            "Worker 并行",
            "Meeting Charter",
            "星型拓扑",
            "Checker",
            "退场",
        ],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
}
REQUIRED_CODING_DELIVERY_CONTRACTS = {
    "senior-software-architect-should-slice-engineering-work-by-deliverable": {
        "sha256": "488bf6bfe0e89570fb38e5796863b7b348192520b8a3e77a555f0168ccee760c",
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-govern-project-domain-language-context": {
        "sha256": "7b989a863b643a46b46d8e07c411f39414b2a1f332e8ea86b332ef1dd5833ef6",
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
}
REQUIRED_EXECUTION_SPEC_CONTRACTS = {
    "wise-agent-should-convert-goal-request-to-project-execution-specification": {
        "sha256": "86916b97724900a7e0ef31547b587e7dd55efd2fe30ec015aa91d7dfa167cc59",
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-ablate-stale-instructions-after-model-harness-change": {
        "sha256": "3951390f5325db07c2f7ed33c39ae8c41203788236f4bedb8c6e1b7d2d13a124",
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
}
REQUIRED_NOVELIST_CHOICE_CONTRACTS = {
    "novelist-should-preserve-grounded-irrationality": {
        "sha256": "c28430c1cfb1ee42a4e30a319c6b2752047b4c65a62fa2bbf57fdca39ce85d74",
    },
}
REQUIRED_COMPETITION_GROUPS = {
    "fiction-drafting-owner": {
        "skills": {
            "document-authoring",
            "huaxia-practical-wisdom",
            "novelist",
            "wise-agent",
        },
        "expected_skill": "novelist",
        "sha256": "854f029d75e3f249d019ff68d4bf3d04f2dbfe8fc753505db15509fcdefe82d0",
    },
    "fiction-project-document-owner": {
        "skills": {"document-authoring", "novelist"},
        "expected_skill": "document-authoring",
        "sha256": "2c4c56975165c998903602fb4df5569ffb2ca2aefaa7ce740dd0bc0a06bb872b",
    },
    "fiction-term-evidence-owner": {
        "skills": {"hanzi-philology", "novelist"},
        "expected_skill": "hanzi-philology",
        "sha256": "c3e90a710d7d747381e77e9473a44d0ba6128b39f64e7bedb51d594d5aee5d43",
    },
    "fiction-anti-ai-owner": {
        "skills": {"ai-slop-detector", "novelist"},
        "expected_skill": "novelist",
        "sha256": "831e3b703ca6d2b6b57b8980ed3bcb079b4d2f55d0efcc215bea49f60b828713",
    },
    "payment-product-owner": {
        "skills": {"payment-expert", "payment-funds-review"},
        "expected_skill": "payment-expert",
    },
    "product-prd-owner": {
        "skills": {
            "document-authoring",
            "product-architecture-expert",
            "ui-design-expert",
        },
        "expected_skill": "product-architecture-expert",
    },
    "security-design-owner": {
        "skills": {"security-engineering-expert", "senior-software-architect"},
        "expected_skill": "security-engineering-expert",
        "sha256": "0c7a76c055096847d11ca92bdbb456087c20ebd0934dd7b4d87f232e9de04a14",
    },
    "funds-security-owner": {
        "skills": {"payment-expert", "security-engineering-expert"},
        "expected_skill": "security-engineering-expert",
        "sha256": "2173747bdcc729dfa2887b25a836e81146507594f28acc4c3d23597487ae5527",
    },
    "spring-fix-owner": {
        "skills": {
            "java-service-code-generator",
            "senior-software-architect",
            "wind-coding-conventions",
        },
        "expected_skill": "senior-software-architect",
    },
}


def load_fixture(path: Path = FIXTURE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_skill_mention(skill: str, query: str) -> bool:
    folded = query.casefold()
    return any(term.casefold() in folded for term in SKILL_MENTIONS[skill])


def is_non_blank_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def audit_data(data: Any, *, label: str) -> list[str]:
    failures: list[str] = []
    if not isinstance(data, dict):
        return [f"{label}: root must be an object"]

    version = data.get("version")
    if type(version) is not int or version != 1:
        failures.append(f"{label}: version must be integer 1")

    source = data.get("source")
    if not isinstance(source, dict):
        failures.append(f"{label}: missing source object")
    else:
        for field in sorted(SOURCE_FIELDS):
            if not is_non_blank_string(source.get(field)):
                failures.append(f"{label}: source {field} must be a non-blank string")
        if source.get("read_status") != "title_author_time_body_read":
            failures.append(f"{label}: source read_status must be title_author_time_body_read")
        if (
            isinstance(source.get("url"), str)
            and "mp.weixin.qq.com" in source["url"]
            and (
                not isinstance(source.get("read_method"), str)
                or "browser" not in source["read_method"].casefold()
            )
        ):
            failures.append(f"{label}: WeChat source must record browser-based reading")

    raw_dimensions = data.get("evaluation_dimensions")
    if not isinstance(raw_dimensions, list) or not all(
        isinstance(item, str) for item in raw_dimensions
    ):
        failures.append(f"{label}: evaluation_dimensions must be an array of strings")
        dimensions: set[str] = set()
    else:
        dimensions = set(raw_dimensions)
    missing_dimensions = REQUIRED_DIMENSIONS - dimensions
    if missing_dimensions:
        failures.append(f"{label}: missing evaluation dimensions {sorted(missing_dimensions)}")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        failures.append(f"{label}: cases must be a non-empty list")
        return failures

    seen_ids: set[str] = set()
    cases_by_id: dict[str, dict[str, Any]] = {}
    competition_groups: dict[str, list[dict[str, Any]]] = {}
    used_dimensions: set[str] = set()
    by_skill = {
        skill: {
            "positive": 0,
            "negative": 0,
            "hard_negative": 0,
            "positive_without_name": 0,
            "negative_without_name": 0,
        }
        for skill in SKILLS
    }
    for index, case in enumerate(cases):
        case_label = f"{label}:cases[{index}]"
        if not isinstance(case, dict):
            failures.append(f"{case_label}: case must be an object")
            continue

        raw_case_id = case.get("id")
        case_id = raw_case_id.strip() if isinstance(raw_case_id, str) else ""
        if not case_id:
            failures.append(f"{case_label}: id must be a non-blank string")
        elif case_id in seen_ids:
            failures.append(f"{case_label}: duplicate id {case_id}")
        if case_id:
            seen_ids.add(case_id)
            cases_by_id.setdefault(case_id, case)

        skill = case.get("skill")
        if not is_non_blank_string(skill) or skill not in KNOWN_SKILLS:
            failures.append(f"{case_label}: unknown skill {skill!r}")
            continue

        raw_query = case.get("query")
        query = raw_query.strip() if isinstance(raw_query, str) else ""
        if not query:
            failures.append(f"{case_label}: query must be a non-blank string")
        if len(query) < 24:
            failures.append(f"{case_label}: query is too short to be realistic")
        if any(term in query.casefold() for term in TRIVIAL_PROMPT_TERMS):
            failures.append(f"{case_label}: query is an obvious toy prompt")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(query):
                failures.append(f"{case_label}: query appears to contain sensitive data")

        should_trigger = case.get("should_trigger")
        if not isinstance(should_trigger, bool):
            failures.append(f"{case_label}: should_trigger must be boolean")
            continue
        if not isinstance(case.get("hard_negative"), bool):
            failures.append(f"{case_label}: hard_negative must be boolean")
        if not is_non_blank_string(case.get("difficulty")):
            failures.append(f"{case_label}: difficulty must be a non-blank string")

        raw_competition_group = case.get("competition_group")
        if raw_competition_group is not None:
            if not isinstance(raw_competition_group, str) or not raw_competition_group.strip():
                failures.append(f"{case_label}: competition_group must be a non-blank string")
            else:
                competition_group = raw_competition_group.strip()
                competition_groups.setdefault(competition_group, []).append(case)

        raw_case_dimensions = case.get("dimensions")
        if not isinstance(raw_case_dimensions, list) or not all(
            isinstance(item, str) for item in raw_case_dimensions
        ):
            failures.append(f"{case_label}: dimensions must be an array of strings")
            case_dimensions: set[str] = set()
        else:
            case_dimensions = set(raw_case_dimensions)
        if not case_dimensions:
            failures.append(f"{case_label}: dimensions must be non-empty")
        if not case_dimensions <= REQUIRED_DIMENSIONS:
            failures.append(f"{case_label}: unknown dimensions {sorted(case_dimensions - REQUIRED_DIMENSIONS)}")
        used_dimensions.update(case_dimensions)

        if skill in EXTERNAL_COMPETITOR_SKILLS:
            if should_trigger is not False or case.get("hard_negative") is not True:
                failures.append(
                    f"{case_label}: external competitor must be a non-triggering hard negative"
                )
            if raw_competition_group is None:
                failures.append(f"{case_label}: external competitor requires a competition group")
            if not is_non_blank_string(case.get("negative_reason")):
                failures.append(f"{case_label}: negative_reason must be a non-blank string")
            preferred = case.get("preferred_skill")
            if not is_non_blank_string(preferred) or preferred not in KNOWN_SKILLS:
                failures.append(f"{case_label}: preferred_skill must be a known skill")
        elif should_trigger:
            by_skill[skill]["positive"] += 1
            if not has_skill_mention(skill, query):
                by_skill[skill]["positive_without_name"] += 1
            if not is_non_blank_string(case.get("expected_handling")):
                failures.append(f"{case_label}: expected_handling must be a non-blank string")
        else:
            by_skill[skill]["negative"] += 1
            if not has_skill_mention(skill, query):
                by_skill[skill]["negative_without_name"] += 1
            if case.get("hard_negative") is True:
                by_skill[skill]["hard_negative"] += 1
            if not is_non_blank_string(case.get("negative_reason")):
                failures.append(f"{case_label}: negative_reason must be a non-blank string")
            preferred = case.get("preferred_skill")
            if preferred is not None:
                if not is_non_blank_string(preferred) or (preferred not in KNOWN_SKILLS and preferred != "none"):
                    failures.append(f"{case_label}: preferred_skill must be a known skill or none")

    for skill, counts in sorted(by_skill.items()):
        if counts["positive"] < 2:
            failures.append(f"{label}: {skill} needs at least 2 positive cases")
        if counts["negative"] < 2:
            failures.append(f"{label}: {skill} needs at least 2 negative cases")
        if counts["hard_negative"] < 2:
            failures.append(f"{label}: {skill} needs at least 2 hard negatives")
        if skill in EXPLICIT_INVOCATION_SKILLS and counts["positive_without_name"]:
            failures.append(f"{label}: {skill} positive cases require an explicit skill name")
        elif skill not in EXPLICIT_INVOCATION_SKILLS and counts["positive_without_name"] < 1:
            failures.append(f"{label}: {skill} needs a positive case without explicit skill name")
        if skill in EXPLICIT_INVOCATION_SKILLS and counts["negative_without_name"] < 1:
            failures.append(f"{label}: {skill} needs a negative case without explicit skill name")

    missing_used_dimensions = REQUIRED_DIMENSIONS - used_dimensions
    if missing_used_dimensions:
        failures.append(f"{label}: no cases exercise dimensions {sorted(missing_used_dimensions)}")

    for group_id, group_cases in sorted(competition_groups.items()):
        group_label = f"{label}: competition group {group_id}"
        if len(group_cases) < 2:
            failures.append(f"{group_label} needs at least 2 candidate skills")
        queries = {str(case.get("query", "")).strip() for case in group_cases}
        if len(queries) != 1:
            failures.append(f"{group_label} must reuse the exact same query")
        skills = [str(case.get("skill", "")) for case in group_cases]
        if len(skills) != len(set(skills)):
            failures.append(f"{group_label} contains duplicate candidate skills")
        winners = [case for case in group_cases if case.get("should_trigger") is True]
        if len(winners) != 1:
            failures.append(f"{group_label} must have exactly one triggering owner")
            continue
        if winners[0].get("hard_negative") is not False:
            failures.append(f"{group_label}: triggering owner must not be a hard negative")
        expected_skill = str(winners[0].get("skill", ""))
        for case in group_cases:
            if case is winners[0]:
                continue
            if case.get("hard_negative") is not True:
                failures.append(
                    f"{group_label}: {case.get('skill')} competitor must be a hard negative"
                )
            if case.get("preferred_skill") != expected_skill:
                failures.append(
                    f"{group_label}: {case.get('skill')} must prefer {expected_skill}"
                )

    for group_id, contract in REQUIRED_COMPETITION_GROUPS.items():
        group_cases = competition_groups.get(group_id)
        if not group_cases:
            failures.append(f"{label}: missing required competition group {group_id}")
            continue
        skills = {str(case.get("skill", "")) for case in group_cases}
        if skills != contract["skills"]:
            failures.append(
                f"{label}: competition group {group_id} must cover {sorted(contract['skills'])}"
            )
        winners = [case for case in group_cases if case.get("should_trigger") is True]
        if len(winners) == 1 and winners[0].get("skill") != contract["expected_skill"]:
            failures.append(
                f"{label}: competition group {group_id} owner must be {contract['expected_skill']}"
            )
        expected_sha256 = contract.get("sha256")
        if expected_sha256:
            payload = json.dumps(
                sorted(group_cases, key=lambda case: str(case.get("id", ""))),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            actual_sha256 = hashlib.sha256(payload).hexdigest()
            if actual_sha256 != expected_sha256:
                failures.append(
                    f"{label}: competition contract sha256 mismatch {group_id}: "
                    f"expected {expected_sha256}, got {actual_sha256}"
                )

    for case_id, query_terms in REQUIRED_PAYMENT_HARD_NEGATIVES.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required payment hard negative {case_id}")
            continue
        if case.get("skill") != "payment-expert" or case.get("should_trigger") is not False:
            failures.append(f"{label}: invalid payment hard negative routing {case_id}")
        if case.get("hard_negative") is not True or case.get("preferred_skill") != "product-architecture-expert":
            failures.append(f"{label}: invalid payment hard negative contract {case_id}")
        query = str(case.get("query", ""))
        if not all(term in query for term in query_terms):
            failures.append(f"{label}: payment hard negative lost boundary semantics {case_id}")

    for case_id, query_terms in REQUIRED_PAYMENT_POSITIVES.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required payment positive {case_id}")
            continue
        if case.get("skill") != "payment-expert" or case.get("should_trigger") is not True:
            failures.append(f"{label}: invalid payment positive routing {case_id}")
        query = str(case.get("query", ""))
        if not all(term in query for term in query_terms):
            failures.append(f"{label}: payment positive lost partial-refund semantics {case_id}")

    for case_id, contract in REQUIRED_RESOURCE_DISTILLER_CASES.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required resource distiller case {case_id}")
            continue
        if case.get("skill") != "resource-capability-distiller" or case.get("should_trigger") is not True:
            failures.append(f"{label}: invalid resource distiller routing {case_id}")
        if case.get("hard_negative") is not contract["hard_negative"]:
            failures.append(f"{label}: invalid resource distiller pressure contract {case_id}")
        if "difficulty" in contract and case.get("difficulty") != contract["difficulty"]:
            failures.append(f"{label}: invalid resource distiller difficulty contract {case_id}")
        query = str(case.get("query", ""))
        if not all(term in query for term in contract["query_terms"]):
            failures.append(f"{label}: resource distiller case lost compression semantics {case_id}")
        if set(case.get("dimensions", [])) & contract["forbidden_dimensions"]:
            failures.append(f"{label}: static prompt case claims behavior evidence {case_id}")

    for case_id, contract in REQUIRED_WISE_CONTRACT_CASES.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required wise-agent contract case {case_id}")
            continue
        if case.get("skill") != "wise-agent" or case.get("should_trigger") is not True:
            failures.append(f"{label}: invalid wise-agent contract routing {case_id}")
        if case.get("hard_negative") is not False:
            failures.append(f"{label}: positive wise-agent pressure case mislabeled hard negative {case_id}")
        query = str(case.get("query", ""))
        if not all(term in query for term in contract["query_terms"]):
            failures.append(f"{label}: wise-agent contract case lost pressure semantics {case_id}")
        expected = str(case.get("expected_handling", ""))
        if not all(term in expected for term in contract["expected_terms"]):
            failures.append(f"{label}: wise-agent contract case lost expected behavior {case_id}")
        if set(case.get("dimensions", [])) & contract["forbidden_dimensions"]:
            failures.append(f"{label}: static wise-agent prompt case claims behavior evidence {case_id}")

    for case_id, contract in REQUIRED_CODING_DELIVERY_CONTRACTS.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required coding delivery contract {case_id}")
            continue
        payload = json.dumps(
            case,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        actual_sha256 = hashlib.sha256(payload).hexdigest()
        if actual_sha256 != contract["sha256"]:
            failures.append(
                f"{label}: coding delivery contract sha256 mismatch {case_id}: "
                f"expected {contract['sha256']}, got {actual_sha256}"
            )
        if set(case.get("dimensions", [])) & contract["forbidden_dimensions"]:
            failures.append(f"{label}: static coding delivery contract claims behavior evidence {case_id}")

    for case_id, contract in REQUIRED_EXECUTION_SPEC_CONTRACTS.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required execution specification contract {case_id}")
            continue
        payload = json.dumps(
            case,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        actual_sha256 = hashlib.sha256(payload).hexdigest()
        if actual_sha256 != contract["sha256"]:
            failures.append(
                f"{label}: execution specification contract sha256 mismatch {case_id}: "
                f"expected {contract['sha256']}, got {actual_sha256}"
            )
        if set(case.get("dimensions", [])) & contract["forbidden_dimensions"]:
            failures.append(
                f"{label}: static execution specification contract claims behavior evidence {case_id}"
            )

    for case_id, contract in REQUIRED_NOVELIST_CHOICE_CONTRACTS.items():
        case = cases_by_id.get(case_id)
        if case is None:
            failures.append(f"{label}: missing required novelist choice contract {case_id}")
            continue
        payload = json.dumps(
            case,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        actual_sha256 = hashlib.sha256(payload).hexdigest()
        if actual_sha256 != contract["sha256"]:
            failures.append(
                f"{label}: novelist choice contract sha256 mismatch {case_id}: "
                f"expected {contract['sha256']}, got {actual_sha256}"
            )

    return failures


def audit_current() -> list[str]:
    return audit_data(load_fixture(), label=FIXTURE.relative_to(ROOT).as_posix())


def run_self_test() -> None:
    failures = audit_current()
    if failures:
        raise SystemExit("\n".join(failures))

    if not has_skill_mention("wise-agent", "进入知止者，自己判断并推进"):
        raise SystemExit("self-test failed: wise-agent explicit aliases were not detected")
    if has_skill_mention("wise-agent", "请做普通代码 CR，并给出源码证据"):
        raise SystemExit("self-test failed: ordinary task intent was treated as an explicit alias")
    if has_skill_mention("wise-agent", "请自己判断并推进，按需调用能力"):
        raise SystemExit("self-test failed: ordinary coordination intent was treated as an explicit alias")

    expected = audit_data([], label="invalid-root-type")
    if not any("root must be an object" in item for item in expected):
        raise SystemExit("self-test failed: non-object root was accepted")

    valid = load_fixture()
    invalid = deepcopy(valid)
    invalid["source"]["read_status"] = "title_only"
    expected = audit_data(invalid, label="invalid-read-status")
    if not any("read_status" in item for item in expected):
        raise SystemExit("self-test failed: missing read_status failure")

    invalid = deepcopy(valid)
    invalid["source"]["title"] = []
    expected = audit_data(invalid, label="invalid-source-type")
    if not any("source title must be a non-blank string" in item for item in expected):
        raise SystemExit("self-test failed: non-string source metadata was accepted")

    invalid = deepcopy(valid)
    invalid["cases"][0]["skill"] = "unknown-skill"
    expected = audit_data(invalid, label="invalid-skill")
    if not any("unknown skill" in item for item in expected):
        raise SystemExit("self-test failed: missing unknown skill failure")

    invalid = deepcopy(valid)
    invalid["cases"][0]["query"] = "写个斐波那契函数"
    expected = audit_data(invalid, label="invalid-toy-prompt")
    if not any("toy prompt" in item or "too short" in item for item in expected):
        raise SystemExit("self-test failed: missing toy prompt failure")

    invalid = deepcopy(valid)
    first_negative = next(
        case for case in invalid["cases"] if case.get("should_trigger") is False
    )
    first_negative["negative_reason"] = ""
    expected = audit_data(invalid, label="invalid-negative")
    if not any("negative_reason" in item for item in expected):
        raise SystemExit("self-test failed: missing negative reason failure")

    invalid = deepcopy(valid)
    invalid["cases"][0]["query"] = "请使用 token='secret-value' 连接生产系统并生成代码"
    expected = audit_data(invalid, label="invalid-sensitive")
    if not any("sensitive" in item for item in expected):
        raise SystemExit("self-test failed: missing sensitive data failure")

    invalid = deepcopy(valid)
    invalid["cases"][0]["query"] = ["这不是字符串，即使数组内容足够长也必须拒绝"]
    expected = audit_data(invalid, label="invalid-query-type")
    if not any("query must be a non-blank string" in item for item in expected):
        raise SystemExit("self-test failed: non-string query was accepted")

    for field, bad_value, expected_term in (
        ("id", ["not-a-string"], "id must be a non-blank string"),
        ("skill", ["not-a-string"], "unknown skill"),
        ("hard_negative", "false", "hard_negative must be boolean"),
        ("difficulty", [], "difficulty must be a non-blank string"),
        ("expected_handling", [], "expected_handling must be a non-blank string"),
    ):
        invalid = deepcopy(valid)
        invalid["cases"][0][field] = bad_value
        expected = audit_data(invalid, label=f"invalid-{field}-type")
        if not any(expected_term in item for item in expected):
            raise SystemExit(f"self-test failed: invalid {field} type was accepted")

    for field, expected_term in (
        ("negative_reason", "negative_reason must be a non-blank string"),
        ("preferred_skill", "preferred_skill must be a known skill or none"),
    ):
        invalid = deepcopy(valid)
        negative = next(case for case in invalid["cases"] if case.get("should_trigger") is False)
        negative[field] = []
        expected = audit_data(invalid, label=f"invalid-{field}-type")
        if not any(expected_term in item for item in expected):
            raise SystemExit(f"self-test failed: invalid {field} type was accepted")

    for invalid_version in (True, 1.0, "1"):
        invalid = deepcopy(valid)
        invalid["version"] = invalid_version
        expected = audit_data(invalid, label="invalid-version-type")
        if not any("version must be integer 1" in item for item in expected):
            raise SystemExit("self-test failed: non-integer version was accepted")

    invalid = deepcopy(valid)
    invalid["evaluation_dimensions"] = None
    expected = audit_data(invalid, label="invalid-evaluation-dimensions-type")
    if not any("evaluation_dimensions must be an array" in item for item in expected):
        raise SystemExit("self-test failed: invalid evaluation_dimensions type was accepted")

    invalid = deepcopy(valid)
    invalid["cases"][0]["dimensions"] = None
    expected = audit_data(invalid, label="invalid-case-dimensions-type")
    if not any("dimensions must be an array" in item for item in expected):
        raise SystemExit("self-test failed: invalid case dimensions type was accepted")

    invalid = deepcopy(valid)
    competition_query = "请设计跨境卡支付的授权、清算、退款和对账规则，不做源码实现或独立准出审查。"
    invalid["cases"].extend(
        [
            {
                "id": "self-test-competition-payment-product",
                "skill": "payment-expert",
                "query": competition_query,
                "should_trigger": True,
                "difficulty": "edge",
                "hard_negative": False,
                "competition_group": "self-test-payment-product-owner",
                "dimensions": ["trigger_accuracy"],
                "expected_handling": "由支付专家负责支付产品语义设计。",
            },
            {
                "id": "self-test-competition-payment-review",
                "skill": "payment-funds-review",
                "query": competition_query,
                "should_trigger": True,
                "difficulty": "edge",
                "hard_negative": False,
                "competition_group": "self-test-payment-product-owner",
                "dimensions": ["trigger_accuracy"],
                "expected_handling": "由支付资金审查负责独立准出。",
            },
        ]
    )
    expected = audit_data(invalid, label="invalid-competition-group")
    if not any("competition group" in item for item in expected):
        raise SystemExit("self-test failed: missing competition-group failure")

    invalid = deepcopy(valid)
    winner = next(
        case
        for case in invalid["cases"]
        if case.get("competition_group") == "payment-product-owner"
        and case.get("should_trigger") is True
    )
    winner["hard_negative"] = True
    expected = audit_data(invalid, label="invalid-competition-winner")
    if not any("triggering owner must not be a hard negative" in item for item in expected):
        raise SystemExit("self-test failed: hard-negative competition winner was accepted")

    invalid = deepcopy(valid)
    missing_group = next(iter(REQUIRED_COMPETITION_GROUPS))
    invalid["cases"] = [
        case
        for case in invalid["cases"]
        if case.get("competition_group") != missing_group
    ]
    expected = audit_data(invalid, label="missing-competition-group")
    if not any(
        f"missing required competition group {missing_group}" in item
        for item in expected
    ):
        raise SystemExit("self-test failed: missing required competition-group failure")

    invalid = deepcopy(valid)
    protected_groups = {
        group_id
        for group_id, contract in REQUIRED_COMPETITION_GROUPS.items()
        if contract.get("sha256")
    }
    for case in invalid["cases"]:
        if case.get("competition_group") in protected_groups:
            case["query"] = "请设计一个后台管理页面，包含侧边栏、筛选器、数据表格和分页，并适配移动端。"
    expected = audit_data(invalid, label="invalid-protected-competition-contract")
    if not any("competition contract sha256 mismatch" in item for item in expected):
        raise SystemExit("self-test failed: protected competition contract drift was accepted")

    invalid = deepcopy(valid)
    invalid["cases"] = [
        case
        for case in invalid["cases"]
        if case.get("id") not in REQUIRED_PAYMENT_HARD_NEGATIVES
    ]
    expected = audit_data(invalid, label="invalid-payment-hard-negatives")
    if not all(
        any(case_id in item for item in expected)
        for case_id in REQUIRED_PAYMENT_HARD_NEGATIVES
    ):
        raise SystemExit("self-test failed: missing required payment hard-negative failures")

    invalid = deepcopy(valid)
    invalid["cases"] = [
        case
        for case in invalid["cases"]
        if case.get("id") not in REQUIRED_PAYMENT_POSITIVES
    ]
    expected = audit_data(invalid, label="invalid-payment-positives")
    if not all(
        any(case_id in item for item in expected)
        for case_id in REQUIRED_PAYMENT_POSITIVES
    ):
        raise SystemExit("self-test failed: missing required payment-positive failures")

    invalid = deepcopy(valid)
    invalid["cases"] = [
        case
        for case in invalid["cases"]
        if case.get("id") not in REQUIRED_RESOURCE_DISTILLER_CASES
    ]
    expected = audit_data(invalid, label="invalid-resource-distiller-cases")
    if not all(
        any(case_id in item for item in expected)
        for case_id in REQUIRED_RESOURCE_DISTILLER_CASES
    ):
        raise SystemExit("self-test failed: missing required resource-distiller failures")

    invalid = deepcopy(valid)
    invalid["cases"] = [
        case
        for case in invalid["cases"]
        if case.get("id") not in REQUIRED_WISE_CONTRACT_CASES
    ]
    expected = audit_data(invalid, label="invalid-wise-agent-contract-cases")
    if not all(
        any(case_id in item for item in expected)
        for case_id in REQUIRED_WISE_CONTRACT_CASES
    ):
        raise SystemExit("self-test failed: missing required wise-agent contract failures")

    invalid = deepcopy(valid)
    contradictions = {
        "senior-software-architect-should-slice-engineering-work-by-deliverable": "；即使没有任何授权，AFK 也可以直接执行。",
        "wise-agent-should-govern-project-domain-language-context": "；允许为了统一语言抹平限界上下文差异。",
    }
    for case in invalid["cases"]:
        if case.get("id") in contradictions:
            case["expected_handling"] += contradictions[case["id"]]
    expected = audit_data(invalid, label="invalid-coding-delivery-contracts")
    if not all(
        any("coding delivery contract sha256 mismatch" in item and case_id in item for item in expected)
        for case_id in REQUIRED_CODING_DELIVERY_CONTRACTS
    ):
        raise SystemExit("self-test failed: contradictory coding delivery contracts were accepted")

    invalid = deepcopy(valid)
    for case in invalid["cases"]:
        if case.get("id") in REQUIRED_CODING_DELIVERY_CONTRACTS:
            case["dimensions"].append("variance_check")
    expected = audit_data(invalid, label="invalid-coding-delivery-dimensions")
    if not all(
        any("static coding delivery contract claims behavior evidence" in item and case_id in item for item in expected)
        for case_id in REQUIRED_CODING_DELIVERY_CONTRACTS
    ):
        raise SystemExit("self-test failed: static coding delivery contracts claimed behavior evidence")

    invalid = deepcopy(valid)
    contradictions = {
        "wise-agent-should-convert-goal-request-to-project-execution-specification": "；同时创建运行时 Goal，并跨切片自主扩展范围。",
        "wise-agent-should-ablate-stale-instructions-after-model-harness-change": "；按固定半年周期清空安全与授权门禁，并把每一步写死。",
    }
    for case in invalid["cases"]:
        if case.get("id") in contradictions:
            case["expected_handling"] += contradictions[case["id"]]
    expected = audit_data(invalid, label="invalid-execution-specification-contracts")
    if not all(
        any(
            "execution specification contract sha256 mismatch" in item and case_id in item
            for item in expected
        )
        for case_id in REQUIRED_EXECUTION_SPEC_CONTRACTS
    ):
        raise SystemExit("self-test failed: contradictory execution specification contracts were accepted")

    invalid = deepcopy(valid)
    for case in invalid["cases"]:
        if case.get("id") in REQUIRED_EXECUTION_SPEC_CONTRACTS:
            case["dimensions"].append("variance_check")
    expected = audit_data(invalid, label="invalid-execution-specification-dimensions")
    if not all(
        any(
            "static execution specification contract claims behavior evidence" in item
            and case_id in item
            for item in expected
        )
        for case_id in REQUIRED_EXECUTION_SPEC_CONTRACTS
    ):
        raise SystemExit("self-test failed: static execution specification contracts claimed behavior evidence")

    for contradiction in (
        "；实际仍按六成概率抽签决定，结果不好就换签重来。",
        "；写进任一草稿后即自动成为正典，作者也不得明确修订。",
    ):
        invalid = deepcopy(valid)
        case = next(
            item
            for item in invalid["cases"]
            if item.get("id") == "novelist-should-preserve-grounded-irrationality"
        )
        case["expected_handling"] += contradiction
        expected = audit_data(invalid, label="invalid-novelist-choice-contract")
        if not any(
            "novelist choice contract sha256 mismatch" in item
            for item in expected
        ):
            raise SystemExit("self-test failed: contradictory novelist choice contract was accepted")

    print("OK skill eval fixture self-test")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run current fixture audit and negative self-tests")
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0

    failures = audit_current()
    if failures:
        raise SystemExit("\n".join(failures))
    print("OK skill eval fixture audit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
