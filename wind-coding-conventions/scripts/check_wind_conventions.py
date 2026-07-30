#!/usr/bin/env python3
"""Offline structural guard for generic Java and high-signal Wind conventions."""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from functools import cache
from pathlib import Path


SKIP_DIRS = {".git", ".idea", ".gradle", "target", "build", "node_modules", "__pycache__"}
TEST_OR_DEMO_PARTS = {"test", "tests", "fixture", "fixtures", "demo", "sandbox"}
TEST_ANNOTATION = re.compile(
    r"@(?:org\.junit(?:\.jupiter\.(?:api|params))?\.)?"
    r"(?:Test|ParameterizedTest|RepeatedTest|TestFactory|TestTemplate)\b"
)
METHOD_DECLARATION = re.compile(
    r"\b(?:public\s+|protected\s+|private\s+)?(?:static\s+)?(?:final\s+)?"
    r"[\w<>,.?@\[\]]+\s+(?P<name>\w+)\s*\("
)
TEST_METHOD_NAME = re.compile(r"test[A-Z0-9]\w*")
METHOD_WITH_BODY = re.compile(
    r"(?P<annotations>(?:^[ \t]*@[A-Za-z_][\w.]*[^\n]*\n)*)"
    r"^[ \t]*(?:(?:public|protected|private|static|final|synchronized|default|native|strictfp)\s+)*"
    r"(?:<[^>{}]+>\s+)?[\w.$?@<>,\[\] ]+\s+(?P<name>\w+)\s*"
    r"\((?P<params>[^{};]*)\)\s*(?:throws\s+[^{}]+)?\{",
    re.MULTILINE,
)
NULLABLE_ANNOTATION = re.compile(r"@(?:[\w.]+\.)?Nullable\b")
NONNULL_ANNOTATION = re.compile(r"@(?:[\w.]+\.)?NonNull\b")
NULL_MARKED_ANNOTATION = re.compile(r"@(?:[\w.]+\.)?NullMarked\b")
NULL_UNMARKED_ANNOTATION = re.compile(r"@(?:[\w.]+\.)?NullUnmarked\b")
UNTRUSTED_PARAMETER_ANNOTATION = re.compile(
    r"@(?:[\w.]+\.)?(?:RequestBody|RequestParam|PathVariable|RequestHeader|CookieValue)\b"
)
SERVICE_VALIDATION_TRIGGER = re.compile(
    r"@(?:(?:jakarta|javax)\.validation\.)?Valid\b"
    r"|@(?:org\.springframework\.validation\.annotation\.)?Validated\b"
)
JAVA_NON_CODE = re.compile(
    r'""".*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/',
    re.DOTALL,
)
BEAN_VALIDATOR_TYPE = re.compile(r"\b(?:(?:jakarta|javax)\.validation\.)?Validator\s+(?P<name>[A-Za-z_]\w*)\b")
BEAN_VALIDATOR_FIELD = re.compile(
    r"\b(?:(?:jakarta|javax)\.validation\.)?Validator\s+(?P<name>[A-Za-z_]\w*)\s*(?:[;=])"
)
BEAN_VALIDATOR_IMPORT = re.compile(r"^\s*import\s+(?:jakarta|javax)\.validation\.(?:Validator|\*)\s*;", re.MULTILINE)
BEAN_VALIDATION_IMPORT = re.compile(r"^\s*import\s+(?:jakarta|javax)\.validation\.(?:Validation|\*)\s*;", re.MULTILINE)
BEAN_VALIDATOR_CHAIN = re.compile(
    r"\b(?:(?:jakarta|javax)\.validation\.)?Validation\s*\.\s*buildDefaultValidatorFactory\s*\(\s*\)"
    r"\s*\.\s*getValidator\s*\(\s*\)\s*\.\s*validate\s*\("
)
BEAN_VALIDATOR_VAR = re.compile(
    r"\bvar\s+(?P<name>[A-Za-z_]\w*)\s*=\s*"
    r"(?:(?:jakarta|javax)\.validation\.)?Validation\s*\.\s*buildDefaultValidatorFactory\s*\(\s*\)"
    r"\s*\.\s*getValidator\s*\(\s*\)"
)
BEAN_VALIDATOR_FACTORY_VAR = re.compile(
    r"\bvar\s+(?P<name>[A-Za-z_]\w*)\s*=\s*"
    r"(?:(?:jakarta|javax)\.validation\.)?Validation\s*\.\s*buildDefaultValidatorFactory\s*\(\s*\)"
)
BEAN_VALIDATOR_FROM_FACTORY = re.compile(
    r"\b(?:var|(?:(?:jakarta|javax)\.validation\.)?Validator)\s+(?P<name>[A-Za-z_]\w*)\s*=\s*"
    r"(?P<factory>[A-Za-z_]\w*)\s*\.\s*getValidator\s*\(\s*\)"
)
PRIMITIVE_TYPES = {"boolean", "byte", "short", "int", "long", "char", "float", "double"}
BUILD_FILE_NAMES = ("pom.xml", "build.gradle", "build.gradle.kts")
SPRING_DEPENDENCY = re.compile(r"\borg\.springframework\b|\bspring-(?:boot|context|beans|core|web|tx)\b")
LOMBOK_DEPENDENCY = re.compile(r"\borg\.projectlombok\b|\blombok\b")
SPRING_SOURCE_IMPORT = re.compile(r"^\s*import\s+org\.springframework\.", re.MULTILINE)
LOMBOK_SOURCE_IMPORT = re.compile(r"^\s*import\s+lombok\.", re.MULTILINE)
GRADLE_COMMENT = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
SPRING_STEREOTYPE = (
    ("Service", "org.springframework.stereotype.Service"),
    ("Component", "org.springframework.stereotype.Component"),
    ("Repository", "org.springframework.stereotype.Repository"),
    ("Controller", "org.springframework.stereotype.Controller"),
    ("RestController", "org.springframework.web.bind.annotation.RestController"),
    ("Configuration", "org.springframework.context.annotation.Configuration"),
)
SPRING_SERVICE = ("Service", "org.springframework.stereotype.Service")
SLF4J_ANNOTATION = ("Slf4j", "lombok.extern.slf4j.Slf4j")
FIELD_INJECTION_ANNOTATIONS = (
    ("Autowired", "org.springframework.beans.factory.annotation.Autowired"),
    ("Resource", "jakarta.annotation.Resource"),
    ("Resource", "javax.annotation.Resource"),
    ("Inject", "jakarta.inject.Inject"),
    ("Inject", "javax.inject.Inject"),
)
CLASS_DECLARATION = re.compile(r"\b(?P<abstract>abstract\s+)?class\s+(?P<name>[A-Za-z_]\w*)\b")
FIELD_DECLARATION = re.compile(
    r"^\s*(?:(?:public|protected|private|static|final|transient|volatile)\s+)*"
    r"[A-Za-z_][\w.$?@<>, \[\]]*\s+[A-Za-z_]\w*\s*;\s*$"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    path: Path
    line_no: int
    message: str


def is_face_path(path: Path) -> bool:
    text = path.as_posix()
    return "-face/" in text or "/face/" in text or any(part.endswith("-face") for part in path.parts)


def is_prod_path(path: Path) -> bool:
    lowered = {part.lower() for part in path.parts}
    return not lowered.intersection(TEST_OR_DEMO_PARTS)


def is_test_path(path: Path) -> bool:
    return bool({part.lower() for part in path.parts}.intersection({"test", "tests"}))


def java_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.java"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def stripped(line: str) -> str:
    return line.strip()


def java_code_only(text: str) -> str:
    return JAVA_NON_CODE.sub(lambda match: "\n" * match.group(0).count("\n"), text)


@cache
def build_dependency_markers(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.name != "pom.xml":
        return GRADLE_COMMENT.sub("", text)
    try:
        document = ET.fromstring(text)
    except ET.ParseError:
        return ""

    markers: list[str] = []

    def visit(element: ET.Element, excluded: bool = False) -> None:
        tag = element.tag.rsplit("}", 1)[-1]
        excluded = excluded or tag in {"dependencyManagement", "profiles", "build", "reporting"}
        if tag == "dependency" and not excluded:
            values = {
                child.tag.rsplit("}", 1)[-1]: (child.text or "").strip()
                for child in element
            }
            if values.get("scope") != "test":
                markers.extend(filter(None, (values.get("groupId"), values.get("artifactId"))))
            return
        for child in element:
            visit(child, excluded)

    visit(document)
    return "\n".join(markers)


def module_frameworks(path: Path, root: Path) -> tuple[bool, bool]:
    markers: list[str] = []
    current = path.parent
    while True:
        markers.extend(
            build_dependency_markers(current / name)
            for name in BUILD_FILE_NAMES
            if (current / name).is_file()
        )
        if current == root or root not in current.parents:
            break
        current = current.parent
    code = java_code_only(path.read_text(encoding="utf-8", errors="ignore"))
    dependency_text = "\n".join(markers)
    return (
        bool(SPRING_DEPENDENCY.search(dependency_text) or SPRING_SOURCE_IMPORT.search(code)),
        bool(LOMBOK_DEPENDENCY.search(dependency_text) or LOMBOK_SOURCE_IMPORT.search(code)),
    )


def has_annotation(header: str, annotation: tuple[str, str]) -> bool:
    simple_name, qualified_name = annotation
    if re.search(rf"@{re.escape(qualified_name)}\b", header):
        return True
    if not re.search(rf"@{re.escape(simple_name)}\b", header):
        return False
    package_name = qualified_name.rsplit(".", 1)[0]
    return bool(
        re.search(
            rf"^\s*import\s+(?:{re.escape(qualified_name)}|{re.escape(package_name)}\.\*)\s*;",
            header,
            re.MULTILINE,
        )
    )


def check_spring_bean_annotations(
    path: Path,
    root: Path,
    text: str,
    spring_enabled: bool,
    lombok_enabled: bool,
) -> list[Finding]:
    if not spring_enabled or not is_prod_path(path.relative_to(root)):
        return []

    code = java_code_only(text)
    declaration = CLASS_DECLARATION.search(code)
    if not declaration or declaration.group("abstract"):
        return []

    annotations = code[: declaration.start()]
    class_name = declaration.group("name")
    service_impl = class_name.endswith("ServiceImpl")
    stereotype = any(has_annotation(annotations, annotation) for annotation in SPRING_STEREOTYPE)
    line_no = code.count("\n", 0, declaration.start()) + 1
    findings: list[Finding] = []
    if service_impl and not has_annotation(annotations, SPRING_SERVICE):
        findings.append(
            Finding(
                "ERROR",
                path.relative_to(root),
                line_no,
                "Spring 业务 ServiceImpl 必须使用 @Service 注册为 Bean",
            )
        )
    if lombok_enabled and (service_impl or stereotype) and not has_annotation(annotations, SLF4J_ANNOTATION):
        findings.append(
            Finding(
                "ERROR",
                path.relative_to(root),
                line_no,
                "已启用 Lombok 的 Spring Bean 必须使用 @Slf4j",
            )
        )
    if service_impl or stereotype:
        body_lines = code[declaration.end() :].splitlines()
        for index, raw in enumerate(body_lines):
            annotation_header = annotations + "\n" + raw
            if not any(
                has_annotation(annotation_header, annotation)
                and re.search(rf"@(?:{re.escape(annotation[1])}|{re.escape(annotation[0])})\b", raw)
                for annotation in FIELD_INJECTION_ANNOTATIONS
            ):
                continue
            candidate = index + 1
            while candidate < len(body_lines) and (
                not body_lines[candidate].strip() or body_lines[candidate].lstrip().startswith("@")
            ):
                candidate += 1
            if candidate < len(body_lines) and FIELD_DECLARATION.match(body_lines[candidate]):
                findings.append(
                    Finding(
                        "ERROR",
                        path.relative_to(root),
                        line_no + index + 1,
                        "Spring Bean 禁止字段注入；必需依赖使用构造注入",
                    )
                )
    return findings


def split_parameters(parameters: str) -> list[str]:
    result: list[str] = []
    start = 0
    depth = 0
    for index, char in enumerate(parameters):
        if char in "<([":
            depth += 1
        elif char in ">)]":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            result.append(parameters[start:index].strip())
            start = index + 1
    tail = parameters[start:].strip()
    if tail:
        result.append(tail)
    return result


def method_body(text: str, opening_brace: int) -> str:
    depth = 0
    for index in range(opening_brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening_brace + 1 : index]
    return text[opening_brace + 1 :]


def last_match_start(pattern: re.Pattern[str], text: str) -> int:
    return max((match.start() for match in pattern.finditer(text)), default=-1)


def check_redundant_jspecify_checks(
    path: Path, root: Path, text: str, package_null_marked: bool = False
) -> list[Finding]:
    if not package_null_marked and "NonNull" not in text and "NullMarked" not in text:
        return []

    findings: list[Finding] = []
    for method in METHOD_WITH_BODY.finditer(text):
        annotations = method.group("annotations")
        scope = text[: method.start()] + annotations
        marked_at = last_match_start(NULL_MARKED_ANNOTATION, scope)
        unmarked_at = last_match_start(NULL_UNMARKED_ANNOTATION, scope)
        null_marked = marked_at > unmarked_at if max(marked_at, unmarked_at) >= 0 else package_null_marked
        body_start = method.end() - 1
        body = method_body(text, body_start)
        statement_ends = [match.end() for match in re.finditer(";", body)]
        leading_statements = body[: statement_ends[min(4, len(statement_ends) - 1)]] if statement_ends else body

        for parameter in split_parameters(method.group("params")):
            name_match = re.search(r"(?P<name>[A-Za-z_]\w*)\s*(?:\[\])?\s*$", parameter)
            if not name_match or NULLABLE_ANNOTATION.search(parameter):
                continue
            parameter_type = re.sub(r"@[\w.]+(?:\([^)]*\))?\s*", "", parameter[: name_match.start()])
            parameter_type = re.sub(r"\bfinal\s+", "", parameter_type).strip().removesuffix("...").strip()
            if parameter_type in PRIMITIVE_TYPES:
                continue
            if not (NONNULL_ANNOTATION.search(parameter) or null_marked):
                continue
            if UNTRUSTED_PARAMETER_ANNOTATION.search(parameter):
                continue

            name = re.escape(name_match.group("name"))
            redundant_assertion = re.search(
                rf"\b(?:Objects\.requireNonNull|(?:AssertUtils|Assert)\.notNull)\s*\(\s*{name}\b",
                leading_statements,
            )
            redundant_ternary = re.search(
                rf"\b{name}\s*==\s*null\s*\?\s*null\s*:\s*{name}\s*\.",
                body,
            )
            for match in (redundant_assertion, redundant_ternary):
                if match:
                    line_no = text.count("\n", 0, body_start + 1 + match.start()) + 1
                    findings.append(
                        Finding(
                            "WARN",
                            path.relative_to(root),
                            line_no,
                            "JSpecify 非空参数不得重复判空或断言",
                        )
                    )

    return findings


def check_test_method_names(path: Path, root: Path, text: str) -> list[Finding]:
    if not is_test_path(path.relative_to(root)):
        return []

    findings: list[Finding] = []
    annotation_line: int | None = None
    signature: list[str] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        line = stripped(raw)
        annotation = TEST_ANNOTATION.search(line)
        if annotation:
            annotation_line = idx
            signature = []
            line = line[annotation.end() :].strip()
            if not line:
                continue
        if annotation_line is None or not line or line.startswith("@"):
            continue

        signature.append(line)
        declaration = METHOD_DECLARATION.search(" ".join(signature))
        if declaration:
            method_name = declaration.group("name")
            if not TEST_METHOD_NAME.fullmatch(method_name):
                findings.append(
                    Finding(
                        "ERROR",
                        path.relative_to(root),
                        idx,
                        "测试方法必须使用 testXxx 格式",
                    )
                )
            annotation_line = None
            signature = []
        elif "{" in line or ";" in line:
            annotation_line = None
            signature = []

    return findings


def check_service_validation_boundary(path: Path, root: Path, text: str) -> list[Finding]:
    if not path.name.endswith(("Service.java", "ServiceImpl.java")):
        return []

    code = java_code_only(text)
    findings: list[Finding] = []
    for idx, raw in enumerate(code.splitlines(), start=1):
        line = stripped(raw)
        if SERVICE_VALIDATION_TRIGGER.search(line):
            findings.append(
                Finding(
                    "ERROR",
                    path.relative_to(root),
                    idx,
                    "Service / ServiceImpl 不出现 @Valid 或 @Validated",
                )
            )

    validator_imported = bool(BEAN_VALIDATOR_IMPORT.search(code))
    validation_imported = bool(BEAN_VALIDATION_IMPORT.search(code))
    validator_fields: set[str] = set()
    brace_depth = 0
    for raw in code.splitlines():
        if brace_depth == 1:
            validator_fields.update(
                match.group("name")
                for match in BEAN_VALIDATOR_FIELD.finditer(raw)
                if validator_imported or ".validation.Validator" in match.group(0)
            )
        brace_depth += raw.count("{") - raw.count("}")

    for method in METHOD_WITH_BODY.finditer(code):
        body_start = method.end() - 1
        body = method_body(code, body_start)
        declaration_scope = method.group("params") + "\n" + body
        bean_parameter_names = {
            match.group("name")
            for match in BEAN_VALIDATOR_TYPE.finditer(method.group("params"))
            if validator_imported or ".validation.Validator" in match.group(0)
        }
        parameter_names = {
            match.group("name")
            for parameter in split_parameters(method.group("params"))
            if (match := re.search(r"(?P<name>[A-Za-z_]\w*)\s*(?:\[\])?\s*$", parameter))
        }
        validator_names = validator_fields - (parameter_names - bean_parameter_names)
        validator_names.update(
            match.group("name")
            for match in BEAN_VALIDATOR_TYPE.finditer(declaration_scope)
            if validator_imported or ".validation.Validator" in match.group(0)
        )
        validator_names.update(
            match.group("name")
            for match in BEAN_VALIDATOR_VAR.finditer(body)
            if validation_imported or ".validation.Validation" in match.group(0)
        )
        factory_names = {
            match.group("name")
            for match in BEAN_VALIDATOR_FACTORY_VAR.finditer(body)
            if validation_imported or ".validation.Validation" in match.group(0)
        }
        validator_names.update(
            match.group("name")
            for match in BEAN_VALIDATOR_FROM_FACTORY.finditer(body)
            if match.group("factory") in factory_names
        )
        for name in validator_names:
            for match in re.finditer(rf"\b{re.escape(name)}\s*\.\s*validate\s*\(", body):
                findings.append(
                    Finding(
                        "ERROR",
                        path.relative_to(root),
                        code.count("\n", 0, body_start + 1 + match.start()) + 1,
                        "Service / ServiceImpl 不手工调用 Bean Validator.validate",
                    )
                )
    for match in BEAN_VALIDATOR_CHAIN.finditer(code):
        if validation_imported or ".validation.Validation" in match.group(0):
            findings.append(
                Finding(
                    "ERROR",
                    path.relative_to(root),
                    code.count("\n", 0, match.start()) + 1,
                    "Service / ServiceImpl 不手工调用 Bean Validator.validate",
                )
            )
    return findings


def check_file(
    path: Path,
    root: Path,
    profile: str = "wind",
    package_null_marked: bool = False,
    spring_enabled: bool = False,
    lombok_enabled: bool = False,
) -> list[Finding]:
    findings: list[Finding] = []
    rel = path.relative_to(root)
    text = path.read_text(encoding="utf-8", errors="ignore")
    findings.extend(check_test_method_names(path, root, text))
    findings.extend(check_redundant_jspecify_checks(path, root, text, package_null_marked))
    findings.extend(check_spring_bean_annotations(path, root, text, spring_enabled, lombok_enabled))

    if profile == "java":
        return findings

    findings.extend(check_service_validation_boundary(path, root, text))

    for idx, raw in enumerate(text.splitlines(), start=1):
        line = stripped(raw)
        if not line or line.startswith("//") or line.startswith("*"):
            continue

        if re.search(r"\bprivate\s+String\s+(currency|currencyCode|currencyIsoCode)\b", line):
            findings.append(Finding("ERROR", rel, idx, "币种字段不得使用 String，统一使用 CurrencyIsoCode"))

        if is_face_path(rel):
            leaks_import = re.search(r"^import\s+.*\.(dal\.entities|dal\.mapper|repository)\.", line)
            leaks_signature = re.search(r"\b\w*Entity\b|\b\w*Mapper\b|\b\w*Repository\b|\bPage\s*[<,)]", line)
            if leaks_import or ("(" in line and ")" in line and leaks_signature):
                findings.append(Finding("ERROR", rel, idx, "face 对外契约不得暴露 Entity、Mapper、Repository 或 MyBatis Page"))

        if path.name.endswith("Service.java") and re.search(r"\bquery[A-Z]\w*ById\s*\(", line):
            findings.append(Finding("WARN", rel, idx, "新服务 ID 查询优先使用 getXxxById / findXxxById 表达存在性"))

        if path.name.endswith("ServiceImpl.java") and re.search(r"\b\w+Mapper\.update\s*\(", line):
            findings.append(Finding("WARN", rel, idx, "写库默认使用 selective；需要全量 update 时说明业务语义"))

    if is_prod_path(rel) and re.search(r"\b(class|interface)\s+(InMemory|Fake|Mock)\w*Service\b", text):
        findings.append(Finding("ERROR", rel, 1, "生产源码路径不得新增内存版 / Fake / Mock 业务 Service"))

    return findings


def run(root: Path, profile: str = "wind") -> list[Finding]:
    if not root.exists():
        raise SystemExit(f"root not found: {root}")
    findings: list[Finding] = []
    files = java_files(root)
    null_marked_packages = {
        path.parent
        for path in files
        if path.name == "package-info.java"
        and NULL_MARKED_ANNOTATION.search(path.read_text(encoding="utf-8", errors="ignore"))
    }
    for path in files:
        spring_enabled, lombok_enabled = module_frameworks(path, root)
        findings.extend(
            check_file(
                path,
                root,
                profile,
                path.parent in null_marked_packages,
                spring_enabled,
                lombok_enabled,
            )
        )
    return findings


def print_findings(findings: list[Finding]) -> None:
    for item in findings:
        print(f"{item.severity} {item.path}:{item.line_no}: {item.message}")
    errors = sum(1 for item in findings if item.severity == "ERROR")
    warnings = sum(1 for item in findings if item.severity == "WARN")
    print(f"Wind convention guard: {errors} error(s), {warnings} warning(s)")


def self_test() -> None:
    fixture_root = Path(__file__).resolve().parents[1] / "fixtures"

    valid = run(fixture_root / "valid", profile="java")
    if valid:
        print_findings(valid)
        raise SystemExit("valid generic Java fixture should pass")

    invalid_java = run(fixture_root / "invalid", profile="java")
    invalid_test_names = [item for item in invalid_java if "testXxx" in item.message]
    if len(invalid_test_names) != 3:
        print_findings(invalid_java)
        raise SystemExit(
            f"invalid generic Java fixture expected 3 testXxx findings, got {len(invalid_test_names)}"
        )
    invalid_service_validation = [
        item for item in invalid_java if "Service / ServiceImpl 不出现 @Valid 或 @Validated" in item.message
    ]
    invalid_manual_validation = [
        item for item in invalid_java if "Service / ServiceImpl 不手工调用 Bean Validator.validate" in item.message
    ]
    if invalid_service_validation or invalid_manual_validation:
        print_findings(invalid_java)
        raise SystemExit("generic Java profile must not enforce Wind Service validation boundaries")
    invalid_spring_service_beans = [
        item for item in invalid_java if "Spring 业务 ServiceImpl 必须使用 @Service 注册为 Bean" in item.message
    ]
    invalid_spring_loggers = [
        item for item in invalid_java if "已启用 Lombok 的 Spring Bean 必须使用 @Slf4j" in item.message
    ]
    invalid_spring_field_injection = [
        item for item in invalid_java if "Spring Bean 禁止字段注入" in item.message
    ]
    if len(invalid_spring_service_beans) != 5 or len(invalid_spring_loggers) != 5:
        print_findings(invalid_java)
        raise SystemExit(
            "generic Spring fixture expected 5 missing @Service and 5 missing @Slf4j findings, "
            f"got {len(invalid_spring_service_beans)} and {len(invalid_spring_loggers)}"
        )
    if len(invalid_spring_field_injection) != 1:
        print_findings(invalid_java)
        raise SystemExit(
            "generic Spring fixture expected 1 field injection finding, "
            f"got {len(invalid_spring_field_injection)}"
        )

    valid = run(fixture_root / "valid", profile="wind")
    if valid:
        print_findings(valid)
        raise SystemExit("valid Wind fixture should pass")

    invalid = run(fixture_root / "invalid", profile="wind")
    messages = "\n".join(item.message for item in invalid)
    expected = [
        "不得使用 String",
        "不得暴露 Entity",
        "不得新增内存版",
        "getXxxById / findXxxById",
        "selective",
        "测试方法必须使用 testXxx",
        "Service / ServiceImpl 不出现 @Valid 或 @Validated",
        "Service / ServiceImpl 不手工调用 Bean Validator.validate",
    ]
    missing = [item for item in expected if item not in messages]
    if missing:
        print_findings(invalid)
        raise SystemExit("invalid fixture missing: " + ", ".join(missing))

    invalid_manual_validation = [
        item for item in invalid if "Service / ServiceImpl 不手工调用 Bean Validator.validate" in item.message
    ]
    if len(invalid_manual_validation) != 5:
        print_findings(invalid)
        raise SystemExit(
            "invalid Wind fixture expected 5 manual Bean Validator findings, "
            f"got {len(invalid_manual_validation)}"
        )

    redundant_jspecify_checks = [
        item for item in invalid if "JSpecify 非空参数不得重复判空或断言" in item.message
    ]
    if len(redundant_jspecify_checks) != 4:
        print_findings(invalid)
        raise SystemExit(
            "invalid fixture expected 4 redundant JSpecify findings, "
            f"got {len(redundant_jspecify_checks)}"
        )
    print("OK wind convention guard self-test")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Java project root to scan")
    parser.add_argument(
        "--profile",
        choices=("java", "wind"),
        default="wind",
        help="scan generic Java rules only, or generic Java plus Wind rules",
    )
    parser.add_argument("--self-test", action="store_true", help="run embedded positive and negative fixtures")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    findings = run(args.root.resolve(), profile=args.profile)
    print_findings(findings)
    return 1 if any(item.severity == "ERROR" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
