#!/usr/bin/env python3
"""
Export a conservative OpenAPI 3 draft from Spring MVC controller source files.

This script is intentionally a lightweight source reader, not a full Java compiler.
It is useful when no OpenAPI JSON/YAML is available and the skill needs a local,
Java-runtime-free path:

  Spring controller source -> OpenAPI 3 draft -> generate_sdk.py

Unresolved symbols are preserved as object placeholders or simple strings, and
the generated description includes caveats so reviewers do not confuse the draft
with a compiled/runtime contract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


MAPPING_ANNOTATIONS = {
    "GetMapping": "get",
    "PostMapping": "post",
    "PutMapping": "put",
    "DeleteMapping": "delete",
    "PatchMapping": "patch",
}
PRIMITIVE_SCHEMAS = {
    "String": {"type": "string"},
    "CharSequence": {"type": "string"},
    "char": {"type": "string"},
    "Character": {"type": "string"},
    "boolean": {"type": "boolean"},
    "Boolean": {"type": "boolean"},
    "byte": {"type": "integer", "format": "int32"},
    "Byte": {"type": "integer", "format": "int32"},
    "short": {"type": "integer", "format": "int32"},
    "Short": {"type": "integer", "format": "int32"},
    "int": {"type": "integer", "format": "int32"},
    "Integer": {"type": "integer", "format": "int32"},
    "long": {"type": "integer", "format": "int64"},
    "Long": {"type": "integer", "format": "int64"},
    "float": {"type": "number", "format": "float"},
    "Float": {"type": "number", "format": "float"},
    "double": {"type": "number", "format": "double"},
    "Double": {"type": "number", "format": "double"},
    "BigDecimal": {"type": "number", "x-java-type": "BigDecimal"},
    "BigInteger": {"type": "integer"},
    "LocalDate": {"type": "string", "format": "date", "x-java-type": "LocalDate"},
    "Date": {"type": "string", "format": "date-time", "x-java-type": "Date"},
    "LocalDateTime": {"type": "string", "format": "date-time", "x-java-type": "LocalDateTime"},
    "OffsetDateTime": {"type": "string", "format": "date-time", "x-java-type": "OffsetDateTime"},
    "Instant": {"type": "string", "format": "date-time", "x-java-type": "Instant"},
    "UUID": {"type": "string", "format": "uuid"},
    "Void": {"type": "void"},
    "void": {"type": "void"},
}
INTERNAL_PARAM_ANNOTATIONS = {"RequestAttribute"}
CONTAINER_TYPES = {"List", "Set", "Collection", "Iterable"}


@dataclass
class JavaField:
    name: str
    type_name: str
    annotations: list[str]


@dataclass
class JavaMethod:
    name: str
    return_type: str
    params: str
    annotations: list[str]


@dataclass
class JavaClass:
    path: Path
    package: str
    name: str
    kind: str
    imports: dict[str, str]
    annotations: list[str]
    fields: list[JavaField]
    methods: list[JavaMethod]
    enum_constants: list[str]
    text: str


@dataclass
class Context:
    classes: dict[str, JavaClass]
    constants: dict[str, str]
    components: dict[str, dict[str, Any]] = field(default_factory=dict)
    building: set[str] = field(default_factory=set)
    warnings: list[str] = field(default_factory=list)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export OpenAPI 3 from Spring MVC source files")
    parser.add_argument("--source-root", action="append", required=True, help="Java source root. Repeatable.")
    parser.add_argument("--output", required=True, help="Output OpenAPI JSON file")
    parser.add_argument("--title", default="Source Generated API")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument(
        "--controller-package",
        action="append",
        default=[],
        help="Only include controllers whose package starts with this value. Repeatable.",
    )
    parser.add_argument("--unwrap-response", default="ApiResp", help="Wrapper type to unwrap, or empty to disable")
    args = parser.parse_args()

    roots = [Path(item).expanduser().resolve() for item in args.source_root]
    classes = load_classes(roots)
    constants = load_constants(classes.values())
    ctx = Context(classes=classes, constants=constants)
    paths: dict[str, dict[str, Any]] = {}

    for java_class in sorted(classes.values(), key=lambda item: str(item.path)):
        if args.controller_package and not any(
            java_class.package.startswith(prefix) for prefix in args.controller_package
        ):
            continue
        if not is_controller(java_class):
            continue
        append_controller_paths(ctx, paths, java_class, args.unwrap_response or None)

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": args.title,
            "version": args.version,
            "description": (
                "Generated from Spring source. Review unresolved symbols, inherited fields, "
                "runtime routing, validation and hidden parameters before production use."
            ),
        },
        "paths": paths,
        "components": {"schemas": dict(sorted(ctx.components.items()))},
        "x-source-generation-warnings": ctx.warnings,
    }

    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"paths": sum(len(v) for v in paths.values()), "schemas": len(ctx.components), "output": str(output)}, ensure_ascii=False))
    return 0


def load_classes(roots: Iterable[Path]) -> dict[str, JavaClass]:
    classes: dict[str, JavaClass] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.java"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            java_class = parse_class(path, text)
            if java_class:
                full_name = f"{java_class.package}.{java_class.name}" if java_class.package else java_class.name
                classes[full_name] = java_class
                classes.setdefault(java_class.name, java_class)
    return classes


def parse_class(path: Path, text: str) -> JavaClass | None:
    package_match = re.search(r"\bpackage\s+([\w.]+)\s*;", text)
    class_match = re.search(
        r"\b(?:public|protected|private|abstract|final|sealed|non-sealed|static|\s)+"
        r"(class|interface|enum|record)\s+(\w+)",
        text,
    )
    if not class_match:
        class_match = re.search(r"\b(class|interface|enum|record)\s+(\w+)", text)
    if not class_match:
        return None
    class_kind = class_match.group(1)
    class_name = class_match.group(2)
    imports = {}
    for import_match in re.finditer(r"\bimport\s+(static\s+)?([\w.*]+)\s*;", text):
        full_name = import_match.group(2)
        if full_name.endswith(".*"):
            continue
        imports[full_name.rsplit(".", 1)[-1]] = full_name
    member_text = top_level_members_text(text, class_match.start())
    return JavaClass(
        path=path,
        package=package_match.group(1) if package_match else "",
        name=class_name,
        kind=class_kind,
        imports=imports,
        annotations=extract_class_annotations(text, class_match.start()),
        fields=extract_fields(member_text),
        methods=extract_methods(text),
        enum_constants=extract_enum_constants(text, class_match.start()) if class_kind == "enum" else [],
        text=text,
    )


def top_level_members_text(text: str, class_start: int) -> str:
    body_start = text.find("{", class_start)
    if body_start == -1:
        return text
    body_end = find_matching(text, body_start, "{", "}")
    if body_end == -1:
        return text[body_start + 1 :]
    body = text[body_start + 1 : body_end]
    depth = 0
    lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if depth == 0 or stripped.startswith("@"):
            lines.append(line)
        depth = max(0, depth + brace_delta(line))
    return "\n".join(lines)


def extract_enum_constants(text: str, class_start: int) -> list[str]:
    body_start = text.find("{", class_start)
    if body_start == -1:
        return []
    body_end = find_matching(text, body_start, "{", "}")
    if body_end == -1:
        return []
    body = re.sub(r"/\*.*?\*/", "", text[body_start + 1 : body_end], flags=re.S)
    body = re.sub(r"//.*", "", body)
    constants_block = body.split(";", 1)[0]
    constants = []
    for item in split_top_level(constants_block, ","):
        item = re.sub(r"@\w+(?:\.\w+)*(?:\([^)]*\))?\s*", "", item).strip()
        match = re.match(r"\s*([A-Z][A-Z0-9_]*)\b", item)
        if match:
            constants.append(match.group(1))
    return constants


def load_constants(classes: Iterable[JavaClass]) -> dict[str, str]:
    constants: dict[str, str] = {}
    seen: set[Path] = set()
    for java_class in classes:
        if java_class.path in seen:
            continue
        seen.add(java_class.path)
        for match in re.finditer(
            r"(?:public|private|protected)?\s*static\s+final\s+String\s+(\w+)\s*=\s*\"([^\"]*)\"",
            java_class.text,
        ):
            name, value = match.group(1), match.group(2)
            constants.setdefault(name, value)
            constants.setdefault(f"{java_class.name}.{name}", value)
            if java_class.package:
                constants[f"{java_class.package}.{java_class.name}.{name}"] = value
    return constants


def extract_class_annotations(text: str, class_start: int) -> list[str]:
    return collect_annotations(text[:class_start].splitlines())


def extract_fields(text: str) -> list[JavaField]:
    fields: list[JavaField] = []
    annotations: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("@"):
            annotations.append(stripped)
            continue
        match = re.match(
            r"(?:private|protected|public)\s+(?!static\b)(?:final\s+)?([\w.<>?,\s\[\]]+)\s+(\w+)\s*(?:=.*)?;",
            stripped,
        )
        if match:
            fields.append(JavaField(name=match.group(2), type_name=normalize_type(match.group(1)), annotations=annotations))
            annotations = []
        elif not stripped.startswith("*") and not stripped.startswith("//"):
            annotations = []
    return fields


def extract_methods(text: str) -> list[JavaMethod]:
    methods: list[JavaMethod] = []
    lines = text.splitlines()
    annotations: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("@"):
            block, i = read_annotation_block(lines, i)
            annotations.append(block)
            continue
        if re.match(r"public\s+", stripped) and not re.match(r"public\s+(class|interface|enum|record)\b", stripped):
            signature_lines = [stripped]
            balance = paren_delta(stripped)
            while (balance > 0 or "{" not in " ".join(signature_lines)) and i + 1 < len(lines):
                i += 1
                nxt = lines[i].strip()
                signature_lines.append(nxt)
                balance += paren_delta(nxt)
                if "{" in nxt and balance <= 0:
                    break
            signature = " ".join(signature_lines)
            match = re.match(r"public\s+(.+?)\s+(\w+)\s*\((.*)\)\s*(?:throws\s+[\w.,\s]+)?\s*\{", signature)
            if match:
                methods.append(
                    JavaMethod(
                        name=match.group(2),
                        return_type=normalize_type(match.group(1)),
                        params=match.group(3),
                        annotations=annotations,
                    )
                )
            annotations = []
        elif stripped and not stripped.startswith("*") and not stripped.startswith("//"):
            annotations = []
        i += 1
    return methods


def collect_annotations(lines: list[str]) -> list[str]:
    result: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("@"):
            block, i = read_annotation_block(lines, i)
            result.append(block)
            continue
        i += 1
    return result


def read_annotation_block(lines: list[str], index: int) -> tuple[str, int]:
    parts = [lines[index].strip()]
    balance = paren_delta(parts[0])
    index += 1
    while balance > 0 and index < len(lines):
        part = lines[index].strip()
        parts.append(part)
        balance += paren_delta(part)
        index += 1
    return " ".join(parts), index


def append_controller_paths(ctx: Context, paths: dict[str, dict[str, Any]], java_class: JavaClass, unwrap_response: str | None) -> None:
    class_paths = mapping_paths(java_class.annotations, "RequestMapping", ctx) or [""]
    tag = strip_quotes(annotation_arg(find_annotation(java_class.annotations, "Tag"), "name") or "")
    if not tag:
        tag = java_class.name.removesuffix("Controller")
    used_operation_ids: set[str] = set()

    for method in java_class.methods:
        mapping_name = first_mapping_annotation(method.annotations)
        if not mapping_name:
            continue
        http_method = MAPPING_ANNOTATIONS.get(mapping_name)
        if mapping_name == "RequestMapping":
            http_method = request_mapping_method(find_annotation(method.annotations, "RequestMapping")) or "get"
        if not http_method:
            continue
        method_paths = mapping_paths(method.annotations, mapping_name, ctx) or [""]
        operation = build_operation(ctx, java_class, method, tag, unwrap_response)
        for index, class_path in enumerate(class_paths):
            for sub_index, method_path in enumerate(method_paths):
                full_path = normalize_path(class_path, method_path)
                op = json.loads(json.dumps(operation))
                op_id = op["operationId"]
                if index or sub_index or op_id in used_operation_ids:
                    op_id = unique_operation_id(op_id, full_path, used_operation_ids)
                used_operation_ids.add(op_id)
                op["operationId"] = op_id
                paths.setdefault(full_path, {})[http_method] = op


def build_operation(
    ctx: Context,
    java_class: JavaClass,
    method: JavaMethod,
    tag: str,
    unwrap_response: str | None,
) -> dict[str, Any]:
    operation_annotation = find_annotation(method.annotations, "Operation")
    summary = strip_quotes(annotation_arg(operation_annotation, "summary") or method.name)
    description = strip_quotes(annotation_arg(operation_annotation, "description") or "")
    parameters: list[dict[str, Any]] = []
    request_body: dict[str, Any] | None = None

    for parameter in parse_parameters(method.params):
        if has_any_annotation(parameter["annotations"], INTERNAL_PARAM_ANNOTATIONS):
            continue
        location = parameter_location(parameter["annotations"])
        schema = schema_for_type(ctx, parameter["type"], java_class, include_component=True)
        name = parameter_name(parameter, location, ctx)
        if location == "body":
            request_body = {
                "required": True,
                "content": {"application/json": {"schema": schema}},
            }
            continue
        if location == "query_object":
            query_object_schema = schema_for_type(ctx, parameter["type"], java_class, include_component=True)
            query_object_schema = dict(query_object_schema)
            query_object_schema["x-java-query-object"] = True
            parameters.append(
                {
                    "name": parameter["name"],
                    "in": "query",
                    "required": False,
                    "schema": query_object_schema,
                    "x-java-query-object": True,
                }
            )
            query_object_parameters(ctx, parameter["type"], java_class)
            continue
        parameters.append(
            {
                "name": name,
                "in": location,
                "required": location in {"path", "header"} or parameter_required(parameter["annotations"]),
                "schema": schema,
            }
        )

    response_schema = response_schema_for_type(ctx, method.return_type, java_class, unwrap_response)
    response: dict[str, Any] = {"description": "OK"}
    if response_schema.get("type") != "void":
        response["content"] = {"application/json": {"schema": response_schema}}

    operation: dict[str, Any] = {
        "tags": [tag],
        "summary": summary,
        "operationId": method.name,
        "parameters": parameters,
        "responses": {"200": response},
    }
    if description:
        operation["description"] = description
    if request_body:
        operation["requestBody"] = request_body
    return operation


def parse_parameters(params: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for raw in split_top_level(params, ","):
        raw = raw.strip()
        if not raw:
            continue
        annotations, rest = leading_annotations(raw)
        rest = rest.strip()
        match = re.match(r"(.+?)\s+(\w+)$", rest)
        if not match:
            continue
        result.append({"annotations": annotations, "type": normalize_type(match.group(1)), "name": match.group(2)})
    return result


def leading_annotations(value: str) -> tuple[list[str], str]:
    annotations: list[str] = []
    rest = value.strip()
    while rest.startswith("@"):
        name_match = re.match(r"@[\w.]+", rest)
        if not name_match:
            break
        end = name_match.end()
        if end < len(rest) and rest[end] == "(":
            close = find_matching(rest, end, "(", ")")
            if close == -1:
                break
            annotations.append(rest[: close + 1].strip())
            rest = rest[close + 1 :].strip()
        else:
            annotations.append(rest[:end].strip())
            rest = rest[end:].strip()
    return annotations, rest


def parameter_location(annotations: list[str]) -> str:
    if find_annotation(annotations, "PathVariable"):
        return "path"
    if find_annotation(annotations, "RequestHeader"):
        return "header"
    if find_annotation(annotations, "RequestBody"):
        return "body"
    if find_annotation(annotations, "RequestParam"):
        return "query"
    if find_annotation(annotations, "CookieValue"):
        return "cookie"
    if find_annotation(annotations, "RequestPart"):
        return "body"
    return "query_object"


def parameter_name(parameter: dict[str, Any], location: str, ctx: Context) -> str:
    if location == "query_object":
        return parameter["name"]
    annotation_name = {
        "path": "PathVariable",
        "query": "RequestParam",
        "header": "RequestHeader",
        "cookie": "CookieValue",
        "body": "RequestBody",
    }.get(location)
    annotation = find_annotation(parameter["annotations"], annotation_name) if annotation_name else None
    raw = annotation_arg(annotation, "name") or annotation_arg(annotation, "value") or annotation_positional(annotation)
    if raw:
        return resolve_expression(raw, ctx.constants)
    return parameter["name"]


def query_object_parameters(ctx: Context, type_name: str, owner: JavaClass) -> list[dict[str, Any]]:
    simple = simple_type(type_name)
    java_class = resolve_class(ctx, type_name, owner)
    if not java_class:
        ctx.warnings.append(f"query object not expanded: {owner.name}.{simple}")
        return []
    parameters: list[dict[str, Any]] = []
    for field in java_class.fields:
        if field_hidden(field.annotations):
            continue
        parameters.append(
            {
                "name": field.name,
                "in": "query",
                "required": parameter_required(field.annotations),
                "schema": schema_for_type(ctx, field.type_name, java_class, include_component=True),
            }
        )
    return parameters


def response_schema_for_type(ctx: Context, type_name: str, owner: JavaClass, unwrap_response: str | None) -> dict[str, Any]:
    if unwrap_response:
        outer, args = generic_parts(type_name)
        if outer == unwrap_response and args:
            return schema_for_type(ctx, args[0], owner, include_component=True)
    return schema_for_type(ctx, type_name, owner, include_component=True)


def schema_for_type(ctx: Context, type_name: str, owner: JavaClass | None, include_component: bool) -> dict[str, Any]:
    type_name = normalize_type(type_name)
    outer, args = generic_parts(type_name)
    simple = simple_type(outer)
    java_class = resolve_class(ctx, outer, owner)
    if simple in PRIMITIVE_SCHEMAS:
        return dict(PRIMITIVE_SCHEMAS[simple])
    if simple in CONTAINER_TYPES:
        item_type = args[0] if args else "Object"
        return {"type": "array", "items": schema_for_type(ctx, item_type, owner, include_component=True)}
    if simple == "Map":
        value_type = args[1] if len(args) > 1 else "Object"
        return {"type": "object", "additionalProperties": schema_for_type(ctx, value_type, owner, include_component=True)}
    if simple == "Optional" and args:
        return schema_for_type(ctx, args[0], owner, include_component=True)
    if simple == "Pagination" and args:
        component_name = f"PaginationOf{schema_name_for_type(args[0])}"
        if component_name not in ctx.components:
            ctx.components[component_name] = {
                "type": "object",
                "properties": {
                    "records": {"type": "array", "items": schema_for_type(ctx, args[0], owner, include_component=True)},
                    "total": {"type": "integer", "format": "int64"},
                },
            }
        return {"$ref": f"#/components/schemas/{component_name}"}
    if java_class and java_class.kind == "enum":
        if include_component:
            ensure_component(ctx, simple, owner)
            return {"$ref": f"#/components/schemas/{simple}"}
        return enum_schema(java_class)
    if is_probable_enum(simple, owner):
        return {"type": "string"}
    if simple == "Object":
        return {"type": "object"}
    if include_component:
        ensure_component(ctx, simple, owner)
        return {"$ref": f"#/components/schemas/{simple}"}
    return {"type": "object"}


def ensure_component(ctx: Context, name: str, owner: JavaClass | None) -> None:
    if name in ctx.components:
        return
    if name in ctx.building:
        ctx.components.setdefault(name, {"type": "object"})
        return
    java_class = resolve_class(ctx, name, owner)
    if not java_class:
        ctx.components[name] = {"type": "object", "properties": {}}
        ctx.warnings.append(f"schema placeholder generated for unresolved type: {name}")
        return
    if java_class.kind == "enum":
        ctx.components[name] = enum_schema(java_class)
        return
    ctx.building.add(name)
    required: list[str] = []
    properties: dict[str, Any] = {}
    for field in java_class.fields:
        if field_hidden(field.annotations):
            continue
        schema = schema_for_type(ctx, field.type_name, java_class, include_component=True)
        description = schema_description(field.annotations)
        if description:
            schema = dict(schema)
            schema["description"] = description
        properties[field.name] = schema
        if parameter_required(field.annotations):
            required.append(field.name)
    component: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "x-java-package": java_class.package,
        "x-java-full-name": f"{java_class.package}.{java_class.name}" if java_class.package else java_class.name,
    }
    description = schema_description(java_class.annotations)
    if description:
        component["description"] = description
    if required:
        component["required"] = required
    ctx.components[name] = component
    ctx.building.remove(name)


def resolve_class(ctx: Context, type_name: str, owner: JavaClass | None) -> JavaClass | None:
    simple = simple_type(type_name)
    if owner and simple in owner.imports:
        java_class = ctx.classes.get(owner.imports[simple])
        if java_class:
            return java_class
    return ctx.classes.get(type_name) or ctx.classes.get(simple)


def enum_schema(java_class: JavaClass) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "type": "string",
        "x-java-package": java_class.package,
        "x-java-full-name": f"{java_class.package}.{java_class.name}" if java_class.package else java_class.name,
    }
    if java_class.enum_constants:
        schema["enum"] = java_class.enum_constants
    description = schema_description(java_class.annotations)
    if description:
        schema["description"] = description
    return schema


def is_controller(java_class: JavaClass) -> bool:
    return bool(find_annotation(java_class.annotations, "RestController") or find_annotation(java_class.annotations, "Controller"))


def first_mapping_annotation(annotations: list[str]) -> str | None:
    for name in [*MAPPING_ANNOTATIONS.keys(), "RequestMapping"]:
        if find_annotation(annotations, name):
            return name
    return None


def mapping_paths(annotations: list[str], name: str, ctx: Context) -> list[str]:
    annotation = find_annotation(annotations, name)
    if not annotation:
        return []
    args = annotation_args(annotation)
    expression = annotation_arg_from_args(args, "path") or annotation_arg_from_args(args, "value") or first_positional_arg(args)
    if expression is None or expression == "":
        return [""]
    expression = expression.strip()
    if expression.startswith("{") and expression.endswith("}"):
        return [resolve_expression(item, ctx.constants) for item in split_top_level(expression[1:-1], ",")]
    return [resolve_expression(expression, ctx.constants)]


def request_mapping_method(annotation: str | None) -> str | None:
    args = annotation_args(annotation)
    method = annotation_arg_from_args(args, "method")
    if not method:
        return None
    return method.rsplit(".", 1)[-1].lower()


def normalize_path(*parts: str) -> str:
    result = "/".join(part.strip("/") for part in parts if part is not None and part != "")
    return "/" + result.strip("/") if result else "/"


def unique_operation_id(base: str, path: str, used: set[str]) -> str:
    suffix = "".join(part[:1].upper() + part[1:] for part in re.findall(r"[A-Za-z0-9]+", path))
    candidate = f"{base}{suffix}" if suffix else f"{base}Alias"
    index = 2
    while candidate in used:
        candidate = f"{base}{index}"
        index += 1
    return candidate


def find_annotation(annotations: list[str], name: str | None) -> str | None:
    if not name:
        return None
    for annotation in annotations:
        match = re.match(r"@(?:[\w.]+\.)?(\w+)\b", annotation.strip())
        if match and match.group(1) == name:
            return annotation
    return None


def has_any_annotation(annotations: list[str], names: set[str]) -> bool:
    return any(find_annotation(annotations, name) for name in names)


def annotation_args(annotation: str | None) -> str:
    if not annotation:
        return ""
    start = annotation.find("(")
    if start == -1:
        return ""
    end = find_matching(annotation, start, "(", ")")
    return annotation[start + 1 : end] if end != -1 else ""


def annotation_arg(annotation: str | None, key: str) -> str | None:
    return annotation_arg_from_args(annotation_args(annotation), key)


def annotation_arg_from_args(args: str, key: str) -> str | None:
    for part in split_top_level(args, ","):
        if "=" not in part:
            continue
        left, right = part.split("=", 1)
        if left.strip() == key:
            return right.strip()
    return None


def annotation_positional(annotation: str | None) -> str | None:
    return first_positional_arg(annotation_args(annotation))


def first_positional_arg(args: str) -> str | None:
    for part in split_top_level(args, ","):
        if "=" not in part:
            return part.strip()
    return None


def schema_description(annotations: list[str]) -> str | None:
    schema = find_annotation(annotations, "Schema")
    return strip_quotes(annotation_arg(schema, "description") or "")


def field_hidden(annotations: list[str]) -> bool:
    schema = find_annotation(annotations, "Schema")
    json_field = find_annotation(annotations, "JSONField")
    json_ignore = find_annotation(annotations, "JsonIgnore")
    return (
        ("hidden" in annotation_args(schema) and "true" in annotation_args(schema))
        or ("serialize" in annotation_args(json_field) and "false" in annotation_args(json_field))
        or json_ignore is not None
    )


def parameter_required(annotations: list[str]) -> bool:
    if has_any_annotation(annotations, {"NotNull", "NotBlank", "NotEmpty"}):
        return True
    schema = find_annotation(annotations, "Schema")
    args = annotation_args(schema)
    return "required = true" in args or "requiredMode = Schema.RequiredMode.REQUIRED" in args


def is_probable_enum(simple: str, owner: JavaClass | None) -> bool:
    if simple.endswith("Enum") or simple.endswith("Type") or simple.endswith("State") or simple.endswith("Code"):
        return True
    if owner and simple in owner.imports:
        full_name = owner.imports[simple]
        return ".enums." in full_name or full_name.endswith(".enums." + simple)
    return False


def generic_parts(type_name: str) -> tuple[str, list[str]]:
    type_name = normalize_type(type_name)
    start = type_name.find("<")
    if start == -1 or not type_name.endswith(">"):
        return type_name, []
    outer = type_name[:start].strip()
    inner = type_name[start + 1 : -1]
    return outer, [normalize_type(item) for item in split_top_level(inner, ",")]


def schema_name_for_type(type_name: str) -> str:
    outer, args = generic_parts(type_name)
    simple = simple_type(outer)
    if args:
        return simple + "Of" + "And".join(schema_name_for_type(arg) for arg in args)
    return simple


def simple_type(type_name: str) -> str:
    type_name = normalize_type(type_name)
    type_name = type_name.replace("[]", "")
    return type_name.rsplit(".", 1)[-1].split("<", 1)[0].strip()


def normalize_type(type_name: str) -> str:
    type_name = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", type_name)
    type_name = type_name.replace("? extends ", "").replace("? super ", "")
    return re.sub(r"\s+", " ", type_name).strip()


def resolve_expression(expression: str, constants: dict[str, str]) -> str:
    parts = split_top_level(expression.strip(), "+")
    resolved = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith('"') and part.endswith('"'):
            resolved.append(strip_quotes(part))
        else:
            resolved.append(constants.get(part, constants.get(part.rsplit(".", 1)[-1], part)))
    return "".join(resolved)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    return value


def split_top_level(value: str, separator: str) -> list[str]:
    parts: list[str] = []
    start = 0
    angle = paren = brace = bracket = 0
    quote: str | None = None
    i = 0
    while i < len(value):
        ch = value[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in {'"', "'"}:
            quote = ch
        elif ch == "<":
            angle += 1
        elif ch == ">":
            angle = max(0, angle - 1)
        elif ch == "(":
            paren += 1
        elif ch == ")":
            paren = max(0, paren - 1)
        elif ch == "{":
            brace += 1
        elif ch == "}":
            brace = max(0, brace - 1)
        elif ch == "[":
            bracket += 1
        elif ch == "]":
            bracket = max(0, bracket - 1)
        elif ch == separator and angle == paren == brace == bracket == 0:
            parts.append(value[start:i].strip())
            start = i + 1
        i += 1
    parts.append(value[start:].strip())
    return parts


def find_matching(value: str, start: int, opener: str, closer: str) -> int:
    depth = 0
    quote: str | None = None
    i = start
    while i < len(value):
        ch = value[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in {'"', "'"}:
            quote = ch
        elif ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def paren_delta(value: str) -> int:
    delta = 0
    quote: str | None = None
    i = 0
    while i < len(value):
        ch = value[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in {'"', "'"}:
            quote = ch
        elif ch == "(":
            delta += 1
        elif ch == ")":
            delta -= 1
        i += 1
    return delta


def brace_delta(value: str) -> int:
    delta = 0
    quote: str | None = None
    i = 0
    while i < len(value):
        ch = value[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in {'"', "'"}:
            quote = ch
        elif ch == "{":
            delta += 1
        elif ch == "}":
            delta -= 1
        i += 1
    return delta


if __name__ == "__main__":
    raise SystemExit(main())
