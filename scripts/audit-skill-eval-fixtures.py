#!/usr/bin/env python3
"""Audit Skill Eval prompt fixtures.

This script is offline and read-only. It validates that prompt fixtures cover
realistic positive cases, hard negatives, source metadata, and evaluation
dimensions. It does not run agents, call networks, upload files, or judge domain
truth.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "skill-eval" / "prompt-cases.json"

SKILLS = {
    "wise-agent",
    "document-authoring",
    "grill-me",
    "hanzi-philology",
    "huaxia-practical-wisdom",
    "java-service-code-generator",
    "payment-expert",
    "payment-funds-review",
    "product-architecture-expert",
    "resource-capability-distiller",
    "senior-software-architect",
    "ui-design-expert",
    "wind-coding-conventions",
}
SKILL_MENTIONS = {
    "wise-agent": [
        "wise-agent",
        "知止者",
        "自己判断并推进",
        "按需调用能力",
    ],
    "document-authoring": ["document-authoring", "专业文档撰写"],
    "grill-me": ["grill-me", "grill me", "盘问", "拷问"],
    "hanzi-philology": ["hanzi-philology", "汉字学与训诂专家"],
    "huaxia-practical-wisdom": [
        "huaxia-practical-wisdom",
        "华夏经世智慧",
        "老祖宗智慧",
    ],
    "java-service-code-generator": ["java-service-code-generator"],
    "payment-expert": ["payment-expert", "支付专家"],
    "payment-funds-review": ["payment-funds-review", "支付资金审查"],
    "product-architecture-expert": ["产品架构专家", "product-architecture-expert"],
    "resource-capability-distiller": [
        "resource-capability-distiller",
        "资源炼技",
        "多源材料提炼",
    ],
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
            "限时会商",
            "Contract Inquiry",
            "Provider Evidence Response",
            "Consumer Reconciliation",
            "confirmed / conflict / reopen / stale",
        ],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-reject-permanent-peer-chat": {
        "query_terms": ["长期自动互聊", "边聊边改", "不做版本化", "不等独立 Checker"],
        "expected_terms": ["停止", "Goal owner", "版本", "Checker", "不产生执行授权"],
        "forbidden_dimensions": {"baseline_comparison", "variance_check"},
    },
    "wise-agent-should-coordinate-multi-party-authority-deliberation": {
        "query_terms": ["四个长期任务", "独立事实", "共同裁定", "永久群聊"],
        "expected_terms": [
            "一主、多权、独立证",
            "主持式星型拓扑",
            "Meeting Charter",
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


def load_fixture(path: Path = FIXTURE) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def has_skill_mention(skill: str, query: str) -> bool:
    folded = query.casefold()
    return any(term.casefold() in folded for term in SKILL_MENTIONS[skill])


def audit_data(data: dict[str, Any], *, label: str) -> list[str]:
    failures: list[str] = []

    if data.get("version") != 1:
        failures.append(f"{label}: version must be 1")

    source = data.get("source")
    if not isinstance(source, dict):
        failures.append(f"{label}: missing source object")
    else:
        for field in sorted(SOURCE_FIELDS):
            if not str(source.get(field, "")).strip():
                failures.append(f"{label}: source missing {field}")
        if source.get("read_status") != "title_author_time_body_read":
            failures.append(f"{label}: source read_status must be title_author_time_body_read")
        if "mp.weixin.qq.com" in str(source.get("url", "")) and "browser" not in str(source.get("read_method", "")).casefold():
            failures.append(f"{label}: WeChat source must record browser-based reading")

    dimensions = set(data.get("evaluation_dimensions", []))
    missing_dimensions = REQUIRED_DIMENSIONS - dimensions
    if missing_dimensions:
        failures.append(f"{label}: missing evaluation dimensions {sorted(missing_dimensions)}")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        failures.append(f"{label}: cases must be a non-empty list")
        return failures

    seen_ids: set[str] = set()
    cases_by_id: dict[str, dict[str, Any]] = {}
    used_dimensions: set[str] = set()
    by_skill = {
        skill: {"positive": 0, "negative": 0, "hard_negative": 0, "positive_without_name": 0}
        for skill in SKILLS
    }

    for index, case in enumerate(cases):
        case_label = f"{label}:cases[{index}]"
        if not isinstance(case, dict):
            failures.append(f"{case_label}: case must be an object")
            continue

        case_id = str(case.get("id", "")).strip()
        if not case_id:
            failures.append(f"{case_label}: missing id")
        elif case_id in seen_ids:
            failures.append(f"{case_label}: duplicate id {case_id}")
        seen_ids.add(case_id)
        if case_id:
            cases_by_id.setdefault(case_id, case)

        skill = case.get("skill")
        if skill not in SKILLS:
            failures.append(f"{case_label}: unknown skill {skill!r}")
            continue

        query = str(case.get("query", "")).strip()
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

        case_dimensions = set(case.get("dimensions", []))
        if not case_dimensions:
            failures.append(f"{case_label}: dimensions must be non-empty")
        if not case_dimensions <= REQUIRED_DIMENSIONS:
            failures.append(f"{case_label}: unknown dimensions {sorted(case_dimensions - REQUIRED_DIMENSIONS)}")
        used_dimensions.update(case_dimensions)

        if should_trigger:
            by_skill[skill]["positive"] += 1
            if not has_skill_mention(skill, query):
                by_skill[skill]["positive_without_name"] += 1
            if not str(case.get("expected_handling", "")).strip():
                failures.append(f"{case_label}: positive case missing expected_handling")
        else:
            by_skill[skill]["negative"] += 1
            if case.get("hard_negative") is True:
                by_skill[skill]["hard_negative"] += 1
            if not str(case.get("negative_reason", "")).strip():
                failures.append(f"{case_label}: negative case missing negative_reason")
            preferred = case.get("preferred_skill")
            if preferred is not None and preferred not in SKILLS and preferred != "none":
                failures.append(f"{case_label}: preferred_skill must be a known skill or none")

    for skill, counts in sorted(by_skill.items()):
        if counts["positive"] < 2:
            failures.append(f"{label}: {skill} needs at least 2 positive cases")
        if counts["negative"] < 2:
            failures.append(f"{label}: {skill} needs at least 2 negative cases")
        if counts["hard_negative"] < 2:
            failures.append(f"{label}: {skill} needs at least 2 hard negatives")
        if counts["positive_without_name"] < 1:
            failures.append(f"{label}: {skill} needs a positive case without explicit skill name")

    missing_used_dimensions = REQUIRED_DIMENSIONS - used_dimensions
    if missing_used_dimensions:
        failures.append(f"{label}: no cases exercise dimensions {sorted(missing_used_dimensions)}")

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

    valid = load_fixture()
    invalid = deepcopy(valid)
    invalid["source"]["read_status"] = "title_only"
    expected = audit_data(invalid, label="invalid-read-status")
    if not any("read_status" in item for item in expected):
        raise SystemExit("self-test failed: missing read_status failure")

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
