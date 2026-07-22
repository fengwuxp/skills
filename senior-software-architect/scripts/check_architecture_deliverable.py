#!/usr/bin/env python3
"""Check architecture deliverable completeness for high-value output types.

The script only inspects local text or an explicit local file. It does not
access the network, upload content, read secrets, or judge technical quality.
It is a deterministic completeness guard before architecture review.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class RequiredGroup(NamedTuple):
    name: str
    aliases: list[str]
    min_hits: int = 1


CHECKS: dict[str, list[RequiredGroup]] = {
    "architecture-plan": [
        RequiredGroup("background_and_goal", ["背景", "目标", "非目标", "成功标准"], 2),
        RequiredGroup("current_state", ["现状", "约束", "问题", "影响范围"], 1),
        RequiredGroup("core_decisions", ["核心决策", "选型", "职责", "边界", "取舍"], 2),
        RequiredGroup("contracts", ["接口契约", "入参", "出参", "错误码", "幂等", "兼容"], 2),
        RequiredGroup("data_and_consistency", ["数据方案", "事务边界", "一致性", "补偿", "对账"], 2),
        RequiredGroup("reliability_security", ["可靠性", "安全", "权限", "审计", "告警"], 2),
        RequiredGroup("verification", ["验证方案", "测试", "静态检查", "压测", "回归"], 2),
        RequiredGroup("release_and_risk", ["发布", "灰度", "回滚", "风险", "待确认"], 2),
    ],
    "system-design": [
        RequiredGroup("requirements", ["需求背景", "背景", "问题", "不做的风险"], 2),
        RequiredGroup("goal_and_scope", ["目标", "非目标", "定性", "范围", "系统职责", "系统边界"], 4),
        RequiredGroup("design_basis", ["设计依据", "当前事实", "产品文档", "假设", "待确认"], 2),
        RequiredGroup("overview_design", ["概要设计", "核心方案", "总体结构", "关键依赖", "关键流程", "设计取舍"], 3),
        RequiredGroup("detail_design", ["详细设计", "模块", "职责", "接口抽象", "数据设计", "状态设计"], 3),
        RequiredGroup("runtime_and_rules", ["关键流程", "业务入口", "运行时", "状态机", "业务规则", "守卫条件", "失败语义"], 3),
        RequiredGroup("contracts", ["接口抽象", "业务契约", "技术契约", "输入", "输出", "失败语义", "幂等"], 3),
        RequiredGroup("quality_and_risk", ["非功能", "性能", "容量", "可用性", "兼容性", "风险", "待确认"], 3),
        RequiredGroup("acceptance_summary", ["验收摘要", "业务结果", "系统不变量", "质量目标", "关键边界", "红线"], 2),
        RequiredGroup("execution_plan_reference", ["执行计划", "实施计划", "任务计划", "权威路径", "适用版本"], 2),
    ],
    "refactoring-design": [
        RequiredGroup("admission", ["重构准入", "独立重构设计", "为什么局部修改", "行为变化", "非目标"], 2),
        RequiredGroup("current_evidence", ["当前问题与证据", "当前结构", "调用链", "缺陷", "事故", "运行指标"], 2),
        RequiredGroup("behavior_boundaries", ["目标结构", "行为不变量", "公共契约不变量", "保留范围", "替换范围", "删除范围"], 3),
        RequiredGroup("migration_rules", ["主写方", "双写", "回填", "影子读", "灰度切流", "回滚", "共存", "下线条件"], 4),
        RequiredGroup("migration_slices", ["MIG 切片", "前置条件", "写入范围", "验证证据", "暂停", "回退"], 3),
        RequiredGroup("verification", ["特征测试", "契约测试", "回归测试", "数据校验", "监控", "告警"], 3),
        RequiredGroup("handoff", ["Engineering Handoff", "第一实施切片", "停止条件", "执行 owner", "验证 owner"], 2),
    ],
    "code-review": [
        RequiredGroup("findings", ["发现", "P0", "P1", "P2", "P3"], 2),
        RequiredGroup("risk", ["风险", "后果", "业务", "数据", "安全", "稳定性"], 1),
        RequiredGroup("evidence", ["证据", "文件", "行号", "调用链", "状态流转", "测试缺口"], 2),
        RequiredGroup("suggestion", ["建议", "修复", "整改", "替代方案"], 1),
        RequiredGroup("verification", ["验证", "测试", "检查", "回归"], 1),
    ],
    "production-change": [
        RequiredGroup("impact", ["影响范围", "用户", "模块", "数据", "外部依赖"], 2),
        RequiredGroup("release", ["灰度", "开关", "准入条件", "退出条件"], 1),
        RequiredGroup("rollback", ["回滚", "回退", "前滚修复", "恢复方式"], 1),
        RequiredGroup("observability", ["监控", "告警", "指标", "日志", "链路"], 2),
        RequiredGroup("runbook", ["Runbook", "应急", "止血", "负责人", "升级机制"], 1),
        RequiredGroup("verification", ["验证", "测试", "压测", "数据校验", "验收"], 2),
        RequiredGroup("risk", ["风险", "残余风险", "待确认", "风险等级"], 1),
    ],
    "diagram-brief": [
        RequiredGroup("diagram_goal", ["图形目标", "用途", "目标读者", "读者"], 1),
        RequiredGroup("diagram_type", ["图形类型", "架构图", "时序图", "状态机", "ER 图", "部署图"], 1),
        RequiredGroup("engineering_anchor", ["工程落点", "模块", "接口", "部署", "监控", "验证"], 2),
        RequiredGroup("semantic_nodes", ["节点", "分组", "系统", "组件", "领域"], 2),
        RequiredGroup("semantic_edges", ["箭头", "关系", "调用", "数据流", "同步", "异步"], 1),
        RequiredGroup("assumptions", ["假设", "待确认", "风险", "边界"], 1),
        RequiredGroup("output_format", ["SVG", "输出格式", "正式图形化交付"], 1),
    ],
}
PLACEHOLDER_FIELD = re.compile(r"〈[^〉\n]+〉")
HEADING_PATTERN = re.compile(r"(?m)^#{2,6}\s+(.+?)\s*$")
SYSTEM_DESIGN_SECTION_ORDER = [
    ("section_background", ("需求背景", "背景与问题")),
    ("section_goal", ("目标与边界", "目标与非目标")),
    ("section_overview", ("概要设计",)),
    ("section_detail", ("详细设计",)),
    ("section_runtime_and_rules", ("运行时场景", "关键流程", "状态与工程规则")),
    ("section_quality_and_risk", ("非功能", "风险与待确认")),
    ("section_acceptance_and_plan", ("验收摘要",)),
]
TABLE_DESIGN_MARKERS = ("表名", "字段清单")
TABLE_DESIGN_CHECKS = [
    RequiredGroup("table_identity", ["表名：", "业务用途：", "数据归属："], 3),
    RequiredGroup("table_fields", ["字段名称", "字段类型", "是否必填", "默认值", "字段说明", "业务约束"], 6),
    RequiredGroup("table_uniqueness", ["业务唯一性", "唯一索引", "业务规则"], 3),
    RequiredGroup("table_access_path", ["普通索引", "索引字段", "查询/排序场景"], 3),
    RequiredGroup("table_compatibility", ["数据约束与兼容", "历史数据迁移", "兼容", "回滚", "删除与归档"], 3),
]
WIND_TABLE_MARKERS = ("Wind 编码约规", "wind-coding-conventions", "Wind/Nobe")
WIND_SOURCE_NEGATIONS = ("不是", "不属于", "不适用", "未命中", "不使用", "未使用", "不遵循", "未明确", "待确认")
WIND_REQUIRED_FIELDS = {"id", "gmt_create", "gmt_modified"}
REQUIRED_VALUES = {"是", "[x]", "yes", "required", "not null", "强制"}
EMPTY_DEFAULT_VALUES = {"", "-", "无", "null", "none", "不适用"}
REQUEST_ID_TERMS = ("requestsn", "idempotency-key", "traceid")
REQUEST_ID_NEGATIONS = ("不使用", "不得", "不作为", "不能作为", "不是", "仅用于", "只用于")

SELF_TESTS: dict[str, tuple[str, str]] = {
    "architecture-plan": (
        "背景：订单链路慢；目标：降低延迟；非目标：不改外部协议。"
        "现状：同步调用多，约束是兼容旧接口，问题影响范围是订单链路。"
        "核心决策：按边界拆应用服务并说明取舍。"
        "接口契约：入参、出参、错误码、幂等和兼容。"
        "数据方案：事务边界、一致性、补偿和对账。"
        "可靠性：超时重试；安全：权限、审计和告警。"
        "验证方案：测试、静态检查和回归。发布：灰度、回滚、风险和待确认。",
        "背景：需要优化。",
    ),
    "system-design": (
        "## 一、需求背景\n需求背景：解决回调超时问题；背景：订单处理慢；问题：积压；不做的风险：生产延迟。\n"
        "## 二、目标与边界\n目标：降低 RT；非目标：不迁移数据库；定性：存量链路治理；范围和系统职责明确。"
        "设计依据：产品文档和当前事实已核对，假设与待确认项已分开。\n"
        "## 三、概要设计\n概要设计：核心方案说明总体结构、关键依赖、关键流程和设计取舍。\n"
        "## 四、详细设计\n详细设计：模块职责、接口抽象、数据设计和状态设计。\n"
        "## 五、运行时场景、状态与工程规则\n"
        "关键流程：业务入口为订单完成事件；运行时状态机和守卫条件明确。"
        "业务规则：失败语义可恢复。接口抽象给出业务契约、技术契约、输入、输出和幂等。\n"
        "## 六、非功能、风险与待确认\n非功能覆盖性能、容量和可用性；风险和待确认项已经列出。\n"
        "## 七、验收摘要与执行计划\n验收摘要说明业务结果、系统不变量和质量目标。"
        "执行计划：详细验收矩阵和验证命令见任务计划；权威路径及适用版本明确。",
        "需求背景：解决回调超时问题。",
    ),
    "refactoring-design": (
        "重构准入：跨模块核心链路替换需要独立重构设计；非目标是不改变结算行为。"
        "当前问题与证据：当前结构调用链过长，事故和运行指标证明风险。"
        "目标结构：行为不变量、公共契约不变量、保留范围和替换范围明确。"
        "迁移规则：主写方明确；双写失败可恢复；先回填和影子读，再灰度切流；支持回滚并限定共存期限和下线条件。"
        "MIG 切片：前置条件、写入范围、验证证据、暂停和回退方式齐全。"
        "验证：特征测试、契约测试、回归测试、数据校验、监控和告警。"
        "Engineering Handoff：第一实施切片、执行 owner、验证 owner 和停止条件明确。",
        "重构目标：整理代码。",
    ),
    "code-review": (
        "发现：[P1] service.java:10 事务内吞异常。风险：会造成业务、数据和稳定性后果。"
        "证据：文件、行号和调用链显示事务回滚缺失。建议：修复异常包装并补偿。"
        "验证：补测试和回归检查。",
        "发现：代码需要优化。",
    ),
    "production-change": (
        "影响范围：用户、模块、数据和外部依赖。灰度：白名单；开关：默认关闭；准入条件和退出条件明确。"
        "回滚：支持回退和前滚修复；恢复方式为关闭开关。"
        "监控：成功率和耗时；告警：错误率；指标、日志和链路齐全。"
        "Runbook：应急止血、负责人和升级机制。验证：测试、压测、数据校验和验收。"
        "风险：残余风险和待确认项已列出。",
        "影响范围：用户。",
    ),
    "diagram-brief": (
        "图形目标：说明订单链路；目标读者：研发和 SRE；图形类型：架构图。"
        "工程落点：模块、接口、部署、监控和验证。节点：系统、组件、领域；分组：应用层和基础设施层。"
        "箭头：同步调用；关系：数据流。假设：容量边界待确认；输出格式：SVG。",
        "图形目标：说明链路；图形类型：架构图。",
    ),
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def labeled_value(line: str, label: str) -> str | None:
    match = re.match(
        rf"^\s*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*|__|`)?\s*{re.escape(label)}\s*(?:\*\*|__|`)?\s*[：:]\s*(.*)$",
        line,
        re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def uses_wind_table_rules(text: str) -> bool:
    for line in text.splitlines():
        source = labeled_value(line, "数据库约规来源")
        if source is None:
            continue
        normalized_source = normalize(source)
        if any(marker.casefold() in normalized_source for marker in WIND_TABLE_MARKERS) and not any(
            term in normalized_source for term in WIND_SOURCE_NEGATIONS
        ):
            return True
    return False


def parse_field_tables(text: str) -> list[tuple[set[str], list[dict[str, str]]]]:
    lines = text.splitlines()
    tables: list[tuple[set[str], list[dict[str, str]]]] = []
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        headers = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "字段名称" not in headers:
            continue
        rows: list[dict[str, str]] = []
        for row_line in lines[index + 1 :]:
            if not row_line.strip().startswith("|"):
                break
            cells = [cell.strip().strip("`") for cell in row_line.strip().strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        tables.append((set(headers), rows))
    return tables


def missing_ordered_sections(text: str, sections: list[tuple[str, tuple[str, ...]]]) -> list[str]:
    headings = [match.group(1).casefold() for match in HEADING_PATTERN.finditer(text)]
    missing: list[str] = []
    positions: list[int] = []
    for name, aliases in sections:
        position = next(
            (index for index, heading in enumerate(headings) if any(alias.casefold() in heading for alias in aliases)),
            None,
        )
        if position is None:
            missing.append(name)
        else:
            positions.append(position)
    if not missing and positions != sorted(positions):
        missing.append("section_order")
    return missing


def missing_groups(kind: str, text: str) -> list[str]:
    normalized = normalize(text)
    missing: list[str] = []
    groups = CHECKS[kind]
    if kind == "system-design" and all(marker.casefold() in normalized for marker in TABLE_DESIGN_MARKERS):
        groups = [*groups, *TABLE_DESIGN_CHECKS]
    for group in groups:
        hits = sum(1 for alias in group.aliases if alias.casefold() in normalized)
        if hits < group.min_hits:
            missing.append(group.name)
    if (
        kind == "system-design"
        and all(marker.casefold() in normalized for marker in TABLE_DESIGN_MARKERS)
        and uses_wind_table_rules(text)
    ):
        field_tables = parse_field_tables(text)
        if not field_tables or any(
            not WIND_REQUIRED_FIELDS.issubset({row.get("字段名称", "").casefold() for row in rows})
            for _, rows in field_tables
        ):
            missing.append("wind_required_fields")
        default_columns = {"是否必填", "默认值", "变更类型"}
        invalid_required_default = not field_tables or any(
            not default_columns.issubset(headers)
            or any(
                "新增" in row.get("变更类型", "")
                and row.get("是否必填", "").strip().casefold() in REQUIRED_VALUES
                and row.get("默认值", "").strip().casefold() in EMPTY_DEFAULT_VALUES
                for row in rows
            )
            for headers, rows in field_tables
        )
        if invalid_required_default:
            missing.append("wind_required_field_defaults")
        for line in text.splitlines():
            uniqueness = labeled_value(line, "业务唯一性")
            if uniqueness is None:
                continue
            normalized_uniqueness = normalize(uniqueness)
            if any(term in normalized_uniqueness for term in REQUEST_ID_TERMS) and not any(
                term in normalized_uniqueness for term in REQUEST_ID_NEGATIONS
            ):
                missing.append("wind_request_id_as_business_key")
                break
    if PLACEHOLDER_FIELD.search(text):
        missing.append("placeholder_fields")
    if kind == "system-design":
        missing.extend(missing_ordered_sections(text, SYSTEM_DESIGN_SECTION_ORDER))
    return missing


def read_input(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if args.text:
        return args.text
    return sys.stdin.read()


def run_self_test() -> int:
    failures: list[str] = []
    for kind, (valid_text, invalid_text) in SELF_TESTS.items():
        valid_missing = missing_groups(kind, valid_text)
        if valid_missing:
            failures.append(f"{kind}: valid fixture missing {', '.join(valid_missing)}")
        invalid_missing = missing_groups(kind, invalid_text)
        if not invalid_missing:
            failures.append(f"{kind}: invalid fixture unexpectedly passed")
    for kind in ("system-design", "refactoring-design"):
        placeholder_text = SELF_TESTS[kind][0] + "owner：〈待填写〉"
        if "placeholder_fields" not in missing_groups(kind, placeholder_text):
            failures.append(f"{kind}: placeholder fixture unexpectedly passed")
    flat_system_design = re.sub(
        r"(?m)^#{2,6}\s+", "", SELF_TESTS["system-design"][0]
    ).replace("\n", " ")
    if not any(
        item.startswith("section_")
        for item in missing_groups("system-design", flat_system_design)
    ):
        failures.append("system-design: flat keyword fixture unexpectedly passed")
    wrong_order_system_design = (
        SELF_TESTS["system-design"][0]
        .replace("## 一、需求背景", "## __SWAP__", 1)
        .replace("## 二、目标与边界", "## 一、需求背景", 1)
        .replace("## __SWAP__", "## 二、目标与边界", 1)
    )
    if "section_order" not in missing_groups("system-design", wrong_order_system_design):
        failures.append("system-design: wrong section order unexpectedly passed")
    incomplete_table = SELF_TESTS["system-design"][0] + "表名：callback_task；字段清单：id。"
    expected_table_missing = {
        "table_identity",
        "table_fields",
        "table_uniqueness",
        "table_access_path",
        "table_compatibility",
    }
    actual_table_missing = set(missing_groups("system-design", incomplete_table))
    if not expected_table_missing.issubset(actual_table_missing):
        failures.append("system-design: incomplete table fixture unexpectedly passed")
    complete_table = (
        SELF_TESTS["system-design"][0]
        + "表名：callback_task；业务用途：记录回调；数据归属：订单。"
        "字段清单：字段名称、字段类型、是否必填、默认值、字段说明、业务约束。"
        "业务唯一性由数据库唯一索引保护并回指业务规则。"
        "普通索引列明索引字段和查询/排序场景。"
        "数据约束与兼容覆盖历史数据迁移、回滚和删除与归档。"
    )
    if expected_table_missing.intersection(missing_groups("system-design", complete_table)):
        failures.append("system-design: complete table fixture unexpectedly failed")
    invalid_wind_table = (
        complete_table
        + "\n数据库约规来源：Wind 编码约规。\n"
        "| 字段名称 | 字段类型 | 是否必填 | 默认值 | 变更类型 | 字段说明 | 业务约束 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| biz_key | varchar(50) | 是 | 无 | 新增字段 | 业务键 | 普通字段 |\n"
    )
    expected_wind_missing = {"wind_required_fields", "wind_required_field_defaults"}
    actual_wind_missing = set(missing_groups("system-design", invalid_wind_table))
    if not expected_wind_missing.issubset(actual_wind_missing):
        failures.append("system-design: invalid Wind table fixture unexpectedly passed")
    valid_wind_table = (
        complete_table
        + "\n数据库约规来源：Wind 编码约规。\n"
        "| 字段名称 | 字段类型 | 是否必填 | 默认值 | 变更类型 | 字段说明 | 业务约束 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| id | bigint(20) | 是 | 主键生成策略 | 新表字段 | 主键 | 强制 |\n"
        "| gmt_create | datetime | 是 | CURRENT_TIMESTAMP | 新表字段 | 创建时间 | 强制 |\n"
        "| gmt_modified | datetime | 是 | CURRENT_TIMESTAMP | 新表字段 | 最后更新时间 | 强制 |\n"
        "| biz_key | varchar(50) | 是 | '' | 新增字段 | 业务键 | 业务唯一 |\n"
    )
    if expected_wind_missing.intersection(missing_groups("system-design", valid_wind_table)):
        failures.append("system-design: valid Wind table fixture unexpectedly failed")
    invalid_second_wind_table = (
        valid_wind_table
        + "\n表名：callback_attempt；业务用途：记录尝试；数据归属：回调任务。\n"
        "字段清单：\n"
        "| 字段名称 | 字段类型 | 是否必填 | 默认值 | 变更类型 | 字段说明 | 业务约束 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| attempt_no | int(11) | 是 | 0 | 新增字段 | 尝试次数 | 普通字段 |\n"
    )
    if "wind_required_fields" not in missing_groups("system-design", invalid_second_wind_table):
        failures.append("system-design: invalid second Wind table fixture unexpectedly passed")
    invalid_request_uniqueness = valid_wind_table.replace(
        "业务唯一性由数据库唯一索引保护并回指业务规则。",
        "\n业务唯一性：使用外部 requestSn 作为业务身份；唯一索引对应业务规则。\n",
    )
    if "wind_request_id_as_business_key" not in missing_groups("system-design", invalid_request_uniqueness):
        failures.append("system-design: request id business key fixture unexpectedly passed")
    formatted_request_uniqueness = valid_wind_table.replace(
        "业务唯一性由数据库唯一索引保护并回指业务规则。",
        "\n- **业务唯一性**：使用外部 requestSn 作为业务身份；唯一索引对应业务规则。\n",
    )
    if "wind_request_id_as_business_key" not in missing_groups("system-design", formatted_request_uniqueness):
        failures.append("system-design: formatted request id business key fixture unexpectedly passed")
    explicit_non_wind_table = invalid_wind_table.replace(
        "数据库约规来源：Wind 编码约规。",
        "数据库约规来源：本项目明确不是 Wind/Nobe。",
    )
    if {"wind_required_fields", "wind_required_field_defaults"}.intersection(
        missing_groups("system-design", explicit_non_wind_table)
    ):
        failures.append("system-design: explicit non-Wind table unexpectedly enabled Wind rules")
    if failures:
        print("FAIL architecture deliverable self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK architecture deliverable self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查架构师交付物的结构完整性")
    parser.add_argument("--kind", choices=sorted(CHECKS), help="交付物类型")
    parser.add_argument("--file", help="待检查的本地 Markdown/文本文件")
    parser.add_argument("--text", help="直接传入待检查文本")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.kind:
        parser.error("--kind is required unless --self-test is used")

    text = read_input(args)
    if not text.strip():
        print("FAIL architecture deliverable check: empty input", file=sys.stderr)
        return 2

    missing = missing_groups(args.kind, text)
    if missing:
        print(
            f"FAIL architecture deliverable check: kind={args.kind} missing " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    print(f"OK architecture deliverable check: kind={args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
