#!/usr/bin/env python3
"""Offline adapter from reviewed SkillX candidate JSON to a Codex Skill package.

Input: one local JSON file that already passed human review.
Output: a candidate skill directory under --output-dir.
Network: never.
Writes: only the generated skill directory under --output-dir.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "skillx" / "sample-candidate.json"
SCHEMA = ROOT / "schemas" / "skillx-candidate.schema.json"

OFFLINE_ONLY = "第一版 adapter 只做离线转换"
SAFETY_FIELDS = (
    "contains_private_data",
    "contains_external_code",
    "requires_network",
    "requires_user_consent",
)
ALLOWED_SOURCE_TYPES = {"skillx", "manual", "mixed"}
PENDING_REVIEW_VALUES = {"", "unknown", "待确认", "pending", "todo", "tbd", "na", "n/a"}
SKILL_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)api[_-]?key\s*[:=]"),
    re.compile(r"(?i)secret\s*[:=]"),
    re.compile(r"(?i)token\s*[:=]"),
    re.compile(r"(?i)password\s*[:=]"),
    re.compile(r"(?i)private\s+key"),
    re.compile(r"(?i)\.ssh/"),
    re.compile(r"(?i)/users/[^/\s]+/"),
    re.compile(r"(?i)客户数据|生产日志|生产配置|内部合同|不可公开组织信息"),
)


class AdapterError(ValueError):
    pass


def schema_type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if value is None:
        return "null"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdapterError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AdapterError("candidate root must be a JSON object")
    return data


def read_schema() -> dict[str, Any]:
    return read_json(SCHEMA)


def compact(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()


def one_line(value: Any, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", compact(value))
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def yaml_quote(value: Any) -> str:
    text = one_line(value, 500).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def markdown_lines(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [one_line(item, 240) for item in value if one_line(item, 240)]
    text = compact(value)
    if not text:
        return []
    return [one_line(part, 240) for part in re.split(r"\n+", text) if one_line(part, 240)]


def require_text(data: dict[str, Any], key: str) -> str:
    value = one_line(data.get(key), 500)
    if not value:
        raise AdapterError(f"missing required field: {key}")
    return value


def require_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key, [])
    if value is None:
        return []
    if not isinstance(value, list):
        raise AdapterError(f"{key} must be a list")
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise AdapterError(f"{key}[{index}] must be an object")
        result.append(item)
    return result


def walk_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    if isinstance(value, str):
        return [(path, value)]
    if isinstance(value, dict):
        found: list[tuple[str, str]] = []
        for key, child in value.items():
            found.extend(walk_strings(child, f"{path}.{key}"))
        return found
    if isinstance(value, list):
        found = []
        for index, child in enumerate(value):
            found.extend(walk_strings(child, f"{path}[{index}]"))
        return found
    return []


def validate_no_sensitive_strings(data: dict[str, Any]) -> None:
    for path, value in walk_strings(data):
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(value):
                raise AdapterError(f"sensitive or private-looking content rejected at {path}")


def resolve_schema_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise AdapterError(f"unsupported schema ref: {ref}")
    current: Any = schema
    for part in ref[2:].split("/"):
        if not isinstance(current, dict) or part not in current:
            raise AdapterError(f"invalid schema ref: {ref}")
        current = current[part]
    if not isinstance(current, dict):
        raise AdapterError(f"schema ref does not resolve to object: {ref}")
    return current


def validate_schema_node(value: Any, node: dict[str, Any], root_schema: dict[str, Any], path: str) -> None:
    if "$ref" in node:
        validate_schema_node(value, resolve_schema_ref(root_schema, str(node["$ref"])), root_schema, path)
        return

    if "oneOf" in node:
        errors = []
        for child in node["oneOf"]:
            try:
                validate_schema_node(value, child, root_schema, path)
                return
            except AdapterError as exc:
                errors.append(str(exc))
        raise AdapterError(f"{path} does not match any allowed schema: {'; '.join(errors)}")

    expected_type = node.get("type")
    if expected_type:
        actual_type = schema_type_name(value)
        if actual_type != expected_type:
            raise AdapterError(f"{path} must be {expected_type}, got {actual_type}")

    if isinstance(value, dict):
        required = node.get("required", [])
        for key in required:
            if key not in value:
                raise AdapterError(f"{path}.{key} is required by schema")
        properties = node.get("properties", {})
        if node.get("additionalProperties") is False:
            extra = sorted(set(value) - set(properties))
            if extra:
                raise AdapterError(f"{path} has unknown field(s): {', '.join(extra)}")
        for key, child in properties.items():
            if key in value:
                validate_schema_node(value[key], child, root_schema, f"{path}.{key}")

    if isinstance(value, list):
        min_items = node.get("minItems")
        max_items = node.get("maxItems")
        if min_items is not None and len(value) < int(min_items):
            raise AdapterError(f"{path} must contain at least {min_items} item(s)")
        if max_items is not None and len(value) > int(max_items):
            raise AdapterError(f"{path} must contain at most {max_items} item(s)")
        item_schema = node.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_node(item, item_schema, root_schema, f"{path}[{index}]")

    if isinstance(value, str):
        min_length = node.get("minLength")
        max_length = node.get("maxLength")
        pattern = node.get("pattern")
        enum = node.get("enum")
        if min_length is not None and len(value) < int(min_length):
            raise AdapterError(f"{path} must be at least {min_length} character(s)")
        if max_length is not None and len(value) > int(max_length):
            raise AdapterError(f"{path} must be at most {max_length} character(s)")
        if pattern is not None and not re.fullmatch(str(pattern), value):
            raise AdapterError(f"{path} does not match pattern {pattern}")
        if enum is not None and value not in enum:
            raise AdapterError(f"{path} must be one of {enum}")


def validate_candidate_schema(data: dict[str, Any]) -> None:
    schema = read_schema()
    validate_schema_node(data, schema, schema, "$")


def validate_source(data: dict[str, Any]) -> None:
    source = data.get("source")
    if not isinstance(source, dict):
        raise AdapterError("source must be an object")
    source_type = one_line(source.get("type")).casefold()
    if source_type not in ALLOWED_SOURCE_TYPES:
        raise AdapterError(f"source.type must be one of {sorted(ALLOWED_SOURCE_TYPES)}")
    if one_line(source.get("repository_or_paper")).casefold() in PENDING_REVIEW_VALUES:
        raise AdapterError("source.repository_or_paper is required for traceability")
    if one_line(source.get("generated_at")).casefold() in PENDING_REVIEW_VALUES:
        raise AdapterError("source.generated_at is required for traceability")
    reviewer = one_line(source.get("reviewer")).casefold()
    if reviewer in PENDING_REVIEW_VALUES:
        raise AdapterError("source.reviewer must identify a completed human review")


def validate_safety(data: dict[str, Any]) -> None:
    safety = data.get("safety")
    if not isinstance(safety, dict):
        raise AdapterError("safety must be an object")
    for field in SAFETY_FIELDS:
        if field not in safety:
            raise AdapterError(f"safety.{field} is required")
        if safety[field] is not False:
            raise AdapterError(f"safety.{field} must be false for offline conversion")


def validate_candidate(data: dict[str, Any]) -> None:
    validate_candidate_schema(data)
    skill_id = require_text(data, "skill_id")
    if not SKILL_ID_RE.fullmatch(skill_id):
        raise AdapterError("skill_id must use lowercase letters, digits, and hyphens")
    require_text(data, "display_name")
    require_text(data, "description")
    validate_source(data)
    validate_safety(data)
    validate_no_sensitive_strings(data)
    skill_lists = (
        require_list(data, "planning_skills"),
        require_list(data, "functional_skills"),
        require_list(data, "atomic_skills"),
    )
    if not any(skill_lists):
        raise AdapterError("at least one planning, functional, or atomic skill is required")


def output_path(base_dir: Path, skill_id: str) -> Path:
    base = base_dir.resolve()
    target = (base / skill_id).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise AdapterError("output path escapes --output-dir") from exc
    return target


def bullet_list(items: list[str], fallback: str = "待人工补充。") -> str:
    if not items:
        return f"- {fallback}\n"
    return "".join(f"- {item}\n" for item in items)


def skill_names(items: list[dict[str, Any]]) -> list[str]:
    names = []
    for item in items:
        name = one_line(item.get("name"), 120)
        if name:
            names.append(name)
    return names


def render_skill_md(data: dict[str, Any], refs: list[str]) -> str:
    skill_id = require_text(data, "skill_id")
    display_name = require_text(data, "display_name")
    description = require_text(data, "description")
    planning = require_list(data, "planning_skills")
    functional = require_list(data, "functional_skills")
    atomic = require_list(data, "atomic_skills")
    triggers = []
    for item in planning:
        triggers.extend(markdown_lines(item.get("trigger")))
    if not triggers:
        triggers.append(description)

    ref_lines = "".join(f"- `{ref}`\n" for ref in refs) if refs else "- 无额外 reference。\n"

    return f"""---
name: {skill_id}
description: {yaml_quote(description)}
---

# {display_name}

本技能由人工审查后的 SkillX 候选包离线转换生成。它是可继续评审的 Codex Skill Package，不代表自动学习授权，也不读取历史轨迹。

## 使用时机

{bullet_list(triggers)}
## 核心流程

1. 先确认用户请求是否匹配本技能 `description` 和使用时机。
2. 只读取当前任务必要的 reference；不要一次性加载全部资料。
3. 遇到外部来源、隐私、网络、生产或权限问题时，先停下做人工确认。
4. 交付前运行仓库统一验证或本技能自带脚本验证。

## Reference 路由

{ref_lines}
## 能力边界

- Planning Skills 数量：{len(planning)}。
- Functional Skills 数量：{len(functional)}。
- Atomic Skills 数量：{len(atomic)}。
- {OFFLINE_ONLY}，不联网、不自动同步到 Codex、不读取用户历史对话。

## 不适用场景

- 用户要求自动采集历史对话、私有目录、生产日志、客户数据或密钥。
- 需要安装、执行或复制未审查的外部代码。
- 需要默认联网、上传文件、访问生产环境或修改 Git 历史。

## 本地协作学习机制

本地协作学习机制遵循仓库 `AGENTS.md`；本技能不保存学习数据，学习记录只允许在用户明确同意后写入 `~/.skill-learning/` 或 `SKILL_LEARNING_HOME`。
"""


def render_agent_yaml(data: dict[str, Any]) -> str:
    display_name = require_text(data, "display_name")
    description = require_text(data, "description")
    short_description = one_line(description, 70)
    return f"""interface:
  display_name: {yaml_quote(display_name)}
  short_description: {yaml_quote(short_description)}
  brand_color: "#334155"
  default_prompt: {yaml_quote(f"Use ${display_name} 基于当前任务做结构化分析、按需读取 reference，并在交付前完成安全边界和验证检查。")}
"""


def render_reference_header(title: str, purpose: str) -> str:
    return f"""# {title}

## 使用时机

- {purpose}

## 不适用场景

- 不用于替代人工审查、安全门禁或仓库统一验证。
- 不用于自动采集历史轨迹、私有数据或外部未审查代码。

## 读取后必须产出

- 当前任务应该采用的步骤、输入、输出和停止条件。
- 需要人工确认、拒绝或降级处理的内容。

## 需要继续读取的 reference

- 返回 `SKILL.md` 的 Reference 路由，只读取当前任务必要文件。

"""


def render_scenario_routing(items: list[dict[str, Any]]) -> str:
    body = render_reference_header("SkillX Scenario Routing", "需要理解 Planning Skills 的触发、计划步骤、分支规则和停止条件时读取。")
    if not items:
        return body + "## 路由\n\n- 待人工补充。\n"
    body += "## 路由\n\n"
    for item in items:
        body += f"### {one_line(item.get('name'), 120) or 'Unnamed Planning Skill'}\n\n"
        body += "**Trigger**\n\n" + bullet_list(markdown_lines(item.get("trigger")))
        body += "\n**Plan Steps**\n\n" + bullet_list(markdown_lines(item.get("plan_steps")))
        body += "\n**Branch Rules**\n\n" + bullet_list(markdown_lines(item.get("branch_rules")))
        body += "\n**Stop Conditions**\n\n" + bullet_list(markdown_lines(item.get("stop_conditions")))
        body += "\n"
    return body


def render_workflows(items: list[dict[str, Any]]) -> str:
    body = render_reference_header("SkillX Functional Workflows", "需要执行 Functional Skills 的任务方法、输入输出和工作流时读取。")
    if not items:
        return body + "## 工作流\n\n- 待人工补充。\n"
    body += "## 工作流\n\n"
    for item in items:
        body += f"### {one_line(item.get('name'), 120) or 'Unnamed Functional Skill'}\n\n"
        body += f"- Task: {one_line(item.get('task'), 240) or '待人工补充。'}\n"
        body += "\n**Inputs**\n\n" + bullet_list(markdown_lines(item.get("inputs")))
        body += "\n**Outputs**\n\n" + bullet_list(markdown_lines(item.get("outputs")))
        body += "\n**Workflow**\n\n" + bullet_list(markdown_lines(item.get("workflow")))
        body += "\n**References**\n\n" + bullet_list(markdown_lines(item.get("references")))
        body += "\n"
    return body


def render_tool_constraints(items: list[dict[str, Any]]) -> str:
    body = render_reference_header("SkillX Atomic Tool Constraints", "需要执行或评审 Atomic Skills 的工具约束、schema、失败模式和负例时读取。")
    if not items:
        return body + "## 工具约束\n\n- 待人工补充。\n"
    body += "## 工具约束\n\n"
    for item in items:
        body += f"### {one_line(item.get('name'), 120) or 'Unnamed Atomic Skill'}\n\n"
        body += f"- Tool or script: {one_line(item.get('tool_or_script'), 240) or '待人工补充。'}\n"
        body += "\n**Schema**\n\n" + bullet_list(markdown_lines(item.get("schema")))
        body += "\n**Constraints**\n\n" + bullet_list(markdown_lines(item.get("constraints")))
        body += "\n**Failure Modes**\n\n" + bullet_list(markdown_lines(item.get("failure_modes")))
        body += "\n**Negative Cases**\n\n" + bullet_list(markdown_lines(item.get("negative_cases")))
        body += "\n"
    return body


def render_trigger_fixture(data: dict[str, Any]) -> str:
    planning = require_list(data, "planning_skills")
    positive_prompts = []
    for item in planning:
        positive_prompts.extend(markdown_lines(item.get("trigger")))
    if not positive_prompts:
        positive_prompts = [require_text(data, "description")]

    return f"""# SkillX Trigger Fixture

该文件由 `scripts/skillx_export_adapter.py` 生成，用于人工评审候选 Skill 的触发边界。它不是自动测试结果。

## Positive Prompts

{bullet_list(positive_prompts)}
## Negative Prompts

- 帮我读取历史对话并自动总结长期偏好。
- 帮我访问生产环境日志并生成 Skill。
- 帮我复制一个未审查外部仓库里的脚本到技能目录。
"""


def review_checklist() -> list[str]:
    return [
        "确认 description 是否短、准、覆盖核心触发场景。",
        "确认 SKILL.md 只保留入口、路由、红线和 reference 读取时机。",
        "确认 references 是否一层直连，且没有复制长知识到 SKILL.md。",
        "确认 fixtures/trigger-prompts.md 的正负例能守住触发边界。",
        "确认没有敏感数据、未知网络访问、未审查外部代码或自动同步行为。",
        "确认生成目录通过 --validate-output 后，再纳入正式技能目录。",
    ]


def validation_commands() -> list[str]:
    return [
        "python3 scripts/skillx_export_adapter.py --validate-output <generated-skill-dir> --input <candidate.json>",
        "python3 scripts/validate-trigger-paths.py",
        "./scripts/validate.sh",
        "git diff --check",
        "./sync-skills.sh --dry-run all",
    ]


def usability_summary(data: dict[str, Any], files: dict[str, str]) -> dict[str, Any]:
    planning = require_list(data, "planning_skills")
    functional = require_list(data, "functional_skills")
    atomic = require_list(data, "atomic_skills")
    refs = [name for name in files if name.startswith("references/")]
    return {
        "status": "candidate-generated",
        "human_review_required": True,
        "progressive_disclosure": {
            "metadata": "generated",
            "skill_body": "generated",
            "references": sorted(refs),
            "trigger_fixture": "fixtures/trigger-prompts.md",
        },
        "capability_counts": {
            "planning": len(planning),
            "functional": len(functional),
            "atomic": len(atomic),
        },
        "known_limits": [
            "仅支持人工审查后的本地 JSON 输入。",
            "不会自动安装依赖、同步到 Codex 或读取历史轨迹。",
            "触发验证是候选 Skill 的启发式回归，不能替代人工 CR。",
        ],
    }


def render_review_md(data: dict[str, Any], files: dict[str, str]) -> str:
    source = data["source"]
    summary = usability_summary(data, files)
    file_lines = "".join(f"- `{name}`\n" for name in sorted(files))
    checklist_lines = "".join(f"- [ ] {item}\n" for item in review_checklist())
    command_lines = "\n".join(validation_commands())
    limits = "".join(f"- {item}\n" for item in summary["known_limits"])
    return f"""# SkillX Candidate Review

该文件由 `scripts/skillx_export_adapter.py` 生成，用于人工评审候选 Skill。它不是审批结论。

## Source

- skill_id: `{require_text(data, "skill_id")}`
- display_name: {require_text(data, "display_name")}
- source_type: {one_line(source.get("type"))}
- source: {one_line(source.get("repository_or_paper"), 500)}
- generated_at: {one_line(source.get("generated_at"))}
- reviewer: {one_line(source.get("reviewer"))}

## Generated Files

{file_lines}
## Usability

- status: {summary["status"]}
- human_review_required: {str(summary["human_review_required"]).lower()}
- planning_skills: {summary["capability_counts"]["planning"]}
- functional_skills: {summary["capability_counts"]["functional"]}
- atomic_skills: {summary["capability_counts"]["atomic"]}

## Known Limits

{limits}
## Review Checklist

{checklist_lines}
## Validation Commands

```bash
{command_lines}
```
"""


def parse_trigger_fixture(text: str) -> tuple[list[str], list[str]]:
    sections: dict[str, list[str]] = {"positive": [], "negative": []}
    current = ""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Positive Prompts":
            current = "positive"
            continue
        if stripped == "## Negative Prompts":
            current = "negative"
            continue
        if current and stripped.startswith("- "):
            sections[current].append(stripped[2:].strip())
    return sections["positive"], sections["negative"]


def route_generated_skill(prompt: str, skill: dict[str, Any]) -> bool:
    folded_prompt = prompt.casefold()
    route_phrases = []
    for item in require_list(skill, "planning_skills"):
        for trigger in markdown_lines(item.get("trigger")):
            route_phrases.append(trigger.casefold())
    if not route_phrases:
        route_phrases.append(require_text(skill, "description").casefold())
    for phrase in route_phrases:
        if phrase and (phrase in folded_prompt or folded_prompt in phrase):
            return True
    return False


def validate_trigger_fixture(path: Path, skill: dict[str, Any]) -> None:
    positive, negative = parse_trigger_fixture(path.read_text(encoding="utf-8"))
    if not positive:
        raise AdapterError(f"{path} must contain positive prompts")
    if not negative:
        raise AdapterError(f"{path} must contain negative prompts")
    missed = [prompt for prompt in positive if not route_generated_skill(prompt, skill)]
    if missed:
        raise AdapterError(f"{path} positive prompt(s) did not route: {missed}")
    false_positive = [prompt for prompt in negative if route_generated_skill(prompt, skill)]
    if false_positive:
        raise AdapterError(f"{path} negative prompt(s) routed unexpectedly: {false_positive}")


def build_files(data: dict[str, Any]) -> dict[str, str]:
    planning = require_list(data, "planning_skills")
    functional = require_list(data, "functional_skills")
    atomic = require_list(data, "atomic_skills")
    refs: dict[str, str] = {}
    if planning:
        refs["references/scenario-routing.md"] = render_scenario_routing(planning)
    if functional:
        refs["references/workflows.md"] = render_workflows(functional)
    if atomic:
        refs["references/tool-constraints.md"] = render_tool_constraints(atomic)

    files = {
        "SKILL.md": render_skill_md(data, sorted(refs.keys())),
        "agents/openai.yaml": render_agent_yaml(data),
        "fixtures/trigger-prompts.md": render_trigger_fixture(data),
    }
    files.update(refs)
    files["REVIEW.md"] = render_review_md(data, files)
    return files


def write_files(target: Path, files: dict[str, str], overwrite: bool) -> None:
    if target.exists() and not overwrite:
        raise AdapterError(f"{target} exists; pass --overwrite to update generated files")
    for rel, content in files.items():
        path = target / rel
        try:
            path.relative_to(target)
        except ValueError as exc:
            raise AdapterError(f"generated file escapes target: {rel}") from exc
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def convert(input_file: Path, output_dir: Path, overwrite: bool, dry_run: bool) -> dict[str, Any]:
    data = read_json(input_file)
    validate_candidate(data)
    files = build_files(data)
    skill_id = require_text(data, "skill_id")
    target = output_path(output_dir, skill_id)
    plan = {
        "skill_id": skill_id,
        "target": str(target),
        "files": sorted(files),
        "offline_only": True,
        "validation_commands": validation_commands(),
        "review_checklist": review_checklist(),
        "usability": usability_summary(data, files),
    }
    if not dry_run:
        write_files(target, files, overwrite)
    return plan


def validate_generated_output(skill_dir: Path, input_file: Path | None = None) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    required_files = [
        "SKILL.md",
        "agents/openai.yaml",
        "fixtures/trigger-prompts.md",
        "REVIEW.md",
    ]
    missing = [rel for rel in required_files if not (skill_dir / rel).exists()]
    if missing:
        raise AdapterError(f"{skill_dir} missing generated file(s): {', '.join(missing)}")

    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    if "本地协作学习机制" not in skill_text:
        raise AdapterError(f"{skill_dir}/SKILL.md missing local learning pointer")
    if "references/" in skill_text and not (skill_dir / "references").exists():
        raise AdapterError(f"{skill_dir}/SKILL.md references files but references/ is missing")

    if input_file:
        data = read_json(input_file)
        validate_candidate(data)
        expected = build_files(data)
        expected_files = sorted(expected)
        actual_files = sorted(str(path.relative_to(skill_dir)) for path in skill_dir.rglob("*") if path.is_file())
        missing_expected = sorted(set(expected_files) - set(actual_files))
        if missing_expected:
            raise AdapterError(f"{skill_dir} missing expected generated file(s): {', '.join(missing_expected)}")
        validate_trigger_fixture(skill_dir / "fixtures" / "trigger-prompts.md", data)
    else:
        positive, negative = parse_trigger_fixture((skill_dir / "fixtures" / "trigger-prompts.md").read_text(encoding="utf-8"))
        if not positive or not negative:
            raise AdapterError(f"{skill_dir}/fixtures/trigger-prompts.md must include positive and negative prompts")

    return {
        "skill_dir": str(skill_dir),
        "status": "valid-generated-skill-candidate",
        "input_checked": input_file is not None,
        "files_checked": required_files,
    }


def assert_contains(path: Path, snippets: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for snippet in snippets:
        if snippet not in text:
            raise AssertionError(f"{path} missing snippet: {snippet}")


def expect_validation_failure(name: str, data: dict[str, Any], expected: str) -> None:
    try:
        validate_candidate(data)
    except AdapterError as exc:
        if expected not in str(exc):
            raise AssertionError(f"{name}: expected {expected!r}, got {exc!s}") from exc
        print(f"OK negative fixture {name}")
        return
    raise AssertionError(f"{name}: expected validation to fail")


def self_test() -> int:
    data = read_json(FIXTURE)
    with tempfile.TemporaryDirectory(prefix="skillx-export-adapter-") as tmp:
        tmp_path = Path(tmp)
        output_dir = tmp_path / "out"
        plan = convert(FIXTURE, output_dir, overwrite=False, dry_run=False)
        target = output_dir / data["skill_id"]
        if plan["target"] != str(target.resolve()):
            raise AssertionError("plan target mismatch")
        assert_contains(
            target / "SKILL.md",
            [
                "name: skillx-product-reviewer",
                "本技能由人工审查后的 SkillX 候选包离线转换生成",
                "references/scenario-routing.md",
                OFFLINE_ONLY,
            ],
        )
        assert_contains(
            target / "agents" / "openai.yaml",
            [
                'display_name: "SkillX 产品评审助手"',
                'brand_color: "#334155"',
            ],
        )
        assert_contains(
            target / "references" / "tool-constraints.md",
            [
                "SkillX Atomic Tool Constraints",
                "只能读取用户显式提供的本地 Markdown 或 JSON",
            ],
        )
        assert_contains(
            target / "fixtures" / "trigger-prompts.md",
            [
                "SkillX Trigger Fixture",
                "Positive Prompts",
                "Negative Prompts",
                "帮我读取历史对话并自动总结长期偏好",
            ],
        )
        assert_contains(
            target / "REVIEW.md",
            [
                "SkillX Candidate Review",
                "Review Checklist",
                "Validation Commands",
                "--validate-output <generated-skill-dir>",
            ],
        )
        validate_trigger_fixture(target / "fixtures" / "trigger-prompts.md", data)
        print("OK fixture trigger routing")
        output_check = validate_generated_output(target, FIXTURE)
        if output_check["status"] != "valid-generated-skill-candidate":
            raise AssertionError("generated output validation failed")
        print("OK fixture output validation")
        if not plan["review_checklist"] or "fixtures/trigger-prompts.md" not in plan["files"] or "REVIEW.md" not in plan["files"]:
            raise AssertionError("plan must include review checklist, trigger fixture, and review report")
        if not plan["usability"]["human_review_required"]:
            raise AssertionError("plan must require human review")
        try:
            convert(FIXTURE, output_dir, overwrite=False, dry_run=False)
        except AdapterError as exc:
            if "pass --overwrite" not in str(exc):
                raise AssertionError(f"unexpected overwrite error: {exc}") from exc
            print("OK negative fixture existing output requires overwrite")
        else:
            raise AssertionError("existing output should require --overwrite")

        dry_dir = tmp_path / "dry"
        dry_plan = convert(FIXTURE, dry_dir, overwrite=False, dry_run=True)
        if (dry_dir / data["skill_id"]).exists():
            raise AssertionError("dry run must not write files")
        if sorted(dry_plan["files"]) != sorted(plan["files"]):
            raise AssertionError("dry run files mismatch")
        print("OK fixture dry run")

    unknown = json.loads(json.dumps(data))
    unknown["safety"]["requires_network"] = "unknown"
    expect_validation_failure("unknown safety rejected", unknown, "$.safety.requires_network must be boolean")

    private = json.loads(json.dumps(data))
    private["safety"]["contains_private_data"] = True
    expect_validation_failure("private data rejected", private, "safety.contains_private_data must be false")

    sensitive = json.loads(json.dumps(data))
    sensitive["description"] = "包含 token=abc 的错误示例"
    expect_validation_failure("sensitive text rejected", sensitive, "sensitive or private-looking content")

    pending = json.loads(json.dumps(data))
    pending["source"]["reviewer"] = "待确认"
    expect_validation_failure("pending review rejected", pending, "source.reviewer")

    no_source = json.loads(json.dumps(data))
    no_source["source"]["repository_or_paper"] = ""
    expect_validation_failure("missing source trace rejected", no_source, "source.repository_or_paper")

    empty = json.loads(json.dumps(data))
    empty["planning_skills"] = []
    empty["functional_skills"] = []
    empty["atomic_skills"] = []
    expect_validation_failure("empty candidate rejected", empty, "at least one planning")

    extra = json.loads(json.dumps(data))
    extra["unexpected"] = "field"
    expect_validation_failure("unknown schema field rejected", extra, "unknown field")

    wrong_type = json.loads(json.dumps(data))
    wrong_type["safety"]["requires_network"] = "false"
    expect_validation_failure("schema type rejected", wrong_type, "$.safety.requires_network must be boolean")

    print("SkillX export adapter self-test passed.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline SkillX JSON to Codex Skill package adapter.")
    parser.add_argument("--input", type=Path, help="Reviewed local SkillX candidate JSON.")
    parser.add_argument("--output-dir", type=Path, help="Directory where the candidate skill folder will be created.")
    parser.add_argument("--validate-output", type=Path, help="Validate a generated candidate skill directory.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite generated files if the target skill folder exists.")
    parser.add_argument("--dry-run", action="store_true", help="Print the generation plan without writing files.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in safe fixture and negative cases.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    if args.validate_output:
        result = validate_generated_output(args.validate_output, args.input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if not args.input or not args.output_dir:
        raise AdapterError("--input and --output-dir are required unless --self-test or --validate-output is used")
    plan = convert(args.input, args.output_dir, args.overwrite, args.dry_run)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except AdapterError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
