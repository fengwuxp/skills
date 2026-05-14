#!/usr/bin/env python3
"""
Generate small API SDKs from OpenAPI 3 documents without requiring Java.

This script intentionally implements a conservative subset:
- OpenAPI 3.x JSON, and YAML when PyYAML is available.
- Java Retrofit interfaces + POJO models.
- TypeScript fetch-style functions + interfaces/types.

It is a built-in fallback generator for the api-sdk-codegen-expert skill. Prefer a
project's existing generator when it is available and trusted, but do not require it.
"""

from __future__ import annotations

import argparse
import json
import keyword
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.request import urlopen


HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}
JAVA_RESERVED = {
    "abstract",
    "assert",
    "boolean",
    "break",
    "byte",
    "case",
    "catch",
    "char",
    "class",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extends",
    "final",
    "finally",
    "float",
    "for",
    "goto",
    "if",
    "implements",
    "import",
    "instanceof",
    "int",
    "interface",
    "long",
    "native",
    "new",
    "package",
    "private",
    "protected",
    "public",
    "return",
    "short",
    "static",
    "strictfp",
    "super",
    "switch",
    "synchronized",
    "this",
    "throw",
    "throws",
    "transient",
    "try",
    "void",
    "volatile",
    "while",
}
TS_RESERVED = {
    "break",
    "case",
    "catch",
    "class",
    "const",
    "continue",
    "debugger",
    "default",
    "delete",
    "do",
    "else",
    "enum",
    "export",
    "extends",
    "finally",
    "for",
    "function",
    "if",
    "import",
    "in",
    "instanceof",
    "new",
    "return",
    "super",
    "switch",
    "this",
    "throw",
    "try",
    "typeof",
    "var",
    "void",
    "while",
    "with",
    "yield",
}


@dataclass
class GeneratorOptions:
    input_path: str
    output_dir: Path
    language: str
    provider: str
    base_package: str
    package_name: str
    target_jdk: int
    validation_namespace: str
    clean: bool
    unwrap_response: str | None
    response_data_field: str
    template_style: str
    return_style: str
    query_object_strategy: str
    pagination_strategy: str
    package_map: dict[str, str]
    model_package_map: dict[str, str]
    client_suffix: str
    query_object_share_class_name: str | None
    query_object_share_dependencies: list[str]
    shared_pagination_type: str | None
    shared_pagination_import: str | None
    client_segment_map: dict[str, str]
    client_name_map: dict[str, str]
    exclude_tags: set[str]
    exclude_operation_ids: set[str]
    ignore_schema_names: set[str]
    ignore_parameter_schema_names: set[str]


@dataclass
class Parameter:
    name: str
    location: str
    required: bool
    schema: dict[str, Any]
    query_object: bool = False


@dataclass
class Operation:
    method: str
    path: str
    operation_id: str
    tag: str
    summary: str
    parameters: list[Parameter] = field(default_factory=list)
    request_schema: dict[str, Any] | None = None
    request_content_type: str | None = None
    response_schema: dict[str, Any] | None = None
    response_content_type: str | None = None
    deprecated: bool = False
    query_object_schema: dict[str, Any] | None = None
    query_object_param_name: str | None = None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate API SDK from OpenAPI 3")
    parser.add_argument("--config", help="Neutral SDK codegen config JSON/YAML")
    parser.add_argument("--target", help="Target name from --config")
    parser.add_argument("--input", help="OpenAPI JSON/YAML file or URL")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--language", choices=["java", "typescript"])
    parser.add_argument(
        "--provider",
        choices=["retrofit", "typescript-fetch"],
        help="Target provider",
    )
    parser.add_argument("--base-package", help="Java base package")
    parser.add_argument("--package-name", help="TypeScript package name")
    parser.add_argument("--target-jdk", type=int, help="Java target JDK")
    parser.add_argument(
        "--validation-namespace",
        choices=["javax.validation", "jakarta.validation", "none"],
    )
    parser.add_argument("--clean", action="store_true", help="Delete output directory before generation")
    parser.add_argument(
        "--unwrap-response",
        help="Schema name to unwrap, for example ApiResp. Only the configured data field is returned.",
    )
    parser.add_argument("--response-data-field")
    args = parser.parse_args()

    options = build_options(args)
    if options.language == "java" and options.provider != "retrofit":
        fail("Java generation currently supports provider=retrofit")
    if options.language == "typescript" and options.provider != "typescript-fetch":
        fail("TypeScript generation currently supports provider=typescript-fetch")

    spec = load_openapi(options.input_path)
    validate_openapi(spec)
    if options.clean and options.output_dir.exists():
        shutil.rmtree(options.output_dir)
    options.output_dir.mkdir(parents=True, exist_ok=True)

    schemas = deref_schemas(spec)
    operations = collect_operations(spec)
    operations = filter_operations(operations, options)
    if options.unwrap_response:
        unwrap_response_schemas(spec, operations, options.unwrap_response, options.response_data_field)
    prepare_operations_for_options(operations, options)

    if options.language == "java":
        files = JavaRetrofitGenerator(options, schemas, operations).generate()
    else:
        files = TypeScriptFetchGenerator(options, schemas, operations).generate()

    print(json.dumps({"generated_files": len(files), "files": [str(p) for p in files]}, ensure_ascii=False, indent=2))
    return 0


def build_options(args: argparse.Namespace) -> GeneratorOptions:
    config = load_config(args.config) if args.config else {}
    target = select_target(config, args.target)
    sdk_codegen = config.get("sdk_codegen", config) if isinstance(config, dict) else {}
    source = sdk_codegen.get("source", {}) if isinstance(sdk_codegen, dict) else {}
    contract = sdk_codegen.get("contract", {}) if isinstance(sdk_codegen, dict) else {}

    language = args.language or normalize_language(target.get("language"))
    if not language:
        fail("language is required. Pass --language or configure targets[].language")

    provider = args.provider or normalize_provider(target.get("provider"), language)
    if not provider:
        provider = "retrofit" if language == "java" else "typescript-fetch"

    validate_config_capabilities(sdk_codegen, target, args.clean)

    input_path = (
        args.input
        or nested_get(target, "openapi.path_or_url")
        or nested_get(source, "openapi.path_or_url")
        or target.get("input")
        or source.get("path_or_url")
    )
    if not input_path:
        fail("input is required. Pass --input or configure source.openapi.path_or_url")

    output = args.output or target.get("output_path")
    if not output:
        fail("output is required. Pass --output or configure targets[].output_path")

    java_runtime = target.get("java_runtime", {}) if isinstance(target.get("java_runtime"), dict) else {}
    response_wrapper = contract.get("response_wrapper", {}) if isinstance(contract.get("response_wrapper"), dict) else {}
    unwrap_response = args.unwrap_response
    response_data_field = args.response_data_field or response_wrapper.get("data_field") or "data"
    if not unwrap_response and response_wrapper.get("unwrap_success_data"):
        source_name = response_wrapper.get("source")
        if isinstance(source_name, str) and source_name:
            unwrap_response = source_name.rsplit(".", 1)[-1]

    class_name_transformers = (
        target.get("class_name_transformers") if isinstance(target.get("class_name_transformers"), dict) else {}
    )
    return GeneratorOptions(
        input_path=str(input_path),
        output_dir=Path(str(output)),
        language=language,
        provider=provider,
        base_package=args.base_package or target.get("base_package") or "com.example.api",
        package_name=args.package_name or target.get("package_name") or "api-sdk",
        target_jdk=args.target_jdk or int(java_runtime.get("target_jdk") or 8),
        validation_namespace=args.validation_namespace or java_runtime.get("validation_namespace") or "javax.validation",
        clean=bool(args.clean),
        unwrap_response=unwrap_response,
        response_data_field=str(response_data_field),
        template_style=str(target.get("template_style") or ("plain_retrofit" if language == "java" else "typescript_fetch")),
        return_style=str(target.get("return_style") or "retrofit_call"),
        query_object_strategy=str(target.get("query_object_strategy") or "expanded_query"),
        pagination_strategy=str(target.get("pagination_strategy") or "generated_schema"),
        package_map=target.get("package_map") if isinstance(target.get("package_map"), dict) else {},
        model_package_map=target.get("model_package_map") if isinstance(target.get("model_package_map"), dict) else {},
        client_suffix=str(class_name_transformers.get("controller_suffix") or "ApiClient"),
        query_object_share_class_name=nested_get(target, "shared_variables.queryObjectShareClassName"),
        query_object_share_dependencies=list(nested_get(target, "shared_variables.queryObjectShareDependencies") or []),
        shared_pagination_type=target.get("shared_pagination_type"),
        shared_pagination_import=target.get("shared_pagination_import"),
        client_segment_map=target.get("client_segment_map") if isinstance(target.get("client_segment_map"), dict) else {},
        client_name_map=coerce_string_map(target.get("client_name_map") or class_name_transformers.get("client_names")),
        exclude_tags=set(list_of_strings(target.get("exclude_tags"))),
        exclude_operation_ids=set(list_of_strings(target.get("exclude_operation_ids"))),
        ignore_schema_names=set(list_of_strings(target.get("ignore_schema_names"))),
        ignore_parameter_schema_names=set(list_of_strings(target.get("ignore_parameter_schema_names"))),
    )


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_config(path: str) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        fail(f"Config file not found: {path}")
    text = config_path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit("YAML config requires PyYAML. Use JSON or install PyYAML.") from exc
    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        fail("Config root must be an object")
    return loaded


def select_target(config: dict[str, Any], target_name: str | None) -> dict[str, Any]:
    if not config:
        return {}
    sdk_codegen = config.get("sdk_codegen", config)
    if not isinstance(sdk_codegen, dict):
        fail("Config sdk_codegen must be an object")
    targets = sdk_codegen.get("targets", [])
    if not isinstance(targets, list) or not targets:
        return {}
    if not target_name:
        if len(targets) == 1 and isinstance(targets[0], dict):
            return targets[0]
        names = [str(item.get("name")) for item in targets if isinstance(item, dict) and item.get("name")]
        fail(f"--target is required when config has multiple targets: {', '.join(names)}")
    for target in targets:
        if isinstance(target, dict) and target.get("name") == target_name:
            return target
    fail(f"Target not found in config: {target_name}")


def normalize_language(value: Any) -> str | None:
    if not value:
        return None
    normalized = str(value).strip().lower()
    aliases = {"java": "java", "typescript": "typescript", "ts": "typescript"}
    return aliases.get(normalized, normalized)


def normalize_provider(value: Any, language: str) -> str | None:
    if not value:
        return None
    normalized = str(value).strip().lower().replace("_", "-")
    aliases = {
        "retrofit": "retrofit",
        "typescript-fetch": "typescript-fetch",
        "fetch": "typescript-fetch",
    }
    if normalized in aliases:
        return aliases[normalized]
    if language == "java":
        return normalized
    if language == "typescript":
        return normalized
    return normalized


def nested_get(value: dict[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def coerce_string_map(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items() if item is not None}


def list_of_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return []


def validate_config_capabilities(sdk_codegen: dict[str, Any], target: dict[str, Any], clean: bool) -> None:
    template_style = str(target.get("template_style") or "").strip().lower()
    if template_style and template_style not in {"plain_retrofit", "typescript_fetch", "loong_wind_retrofit"}:
        fail(
            "Built-in generator cannot reproduce template_style="
            f"{target.get('template_style')}. Use the project generator or implement an adapter."
        )
    unsupported = {
        "post_processors": "post processors",
    }
    for key, label in unsupported.items():
        if target.get(key):
            fail(f"Built-in generator does not support {label} from config yet. Use the project generator or adapter.")
    if target.get("pagination_strategy") not in {None, "", "generated_schema", "shared_immutable_pagination", "wind_immutable_pagination"}:
        fail("Built-in generator does not support shared pagination strategies yet.")
    if target.get("delete_output_directory") and not clean:
        fail("Config requests delete_output_directory=true. Pass --clean only after confirming the output directory is safe.")

    baseline = sdk_codegen.get("generator_baseline", {}) if isinstance(sdk_codegen, dict) else {}
    if isinstance(baseline, dict) and baseline.get("compatibility_target"):
        target_name = str(baseline["compatibility_target"])
        if target_name not in {"plain_retrofit", "typescript_fetch", "loong_wind_retrofit"} and not target.get("allow_fallback_generation"):
            fail(
                "Config declares compatibility_target="
                f"{target_name}. Built-in generation is only a fallback unless allow_fallback_generation=true."
            )


def load_openapi(input_path: str) -> dict[str, Any]:
    if re.match(r"^https?://", input_path):
        with urlopen(input_path) as response:  # nosec - user-provided URL is explicit input.
            text = response.read().decode("utf-8")
    else:
        text = Path(input_path).read_text(encoding="utf-8")

    stripped = text.lstrip()
    if stripped.startswith("{"):
        return json.loads(text)

    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit("YAML input requires PyYAML. Use JSON or install PyYAML.") from exc
    return yaml.safe_load(text)


def validate_openapi(spec: dict[str, Any]) -> None:
    version = str(spec.get("openapi", ""))
    if not version.startswith("3."):
        fail("Only OpenAPI 3.x is supported by the built-in generator MVP")
    if not isinstance(spec.get("paths"), dict):
        fail("OpenAPI document must contain paths")


def deref_schemas(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = spec.get("components", {}).get("schemas", {})
    if not isinstance(raw, dict):
        return {}
    return {name: annotate_local_refs(resolve_schema(schema, spec)) for name, schema in raw.items()}


def annotate_local_refs(value: Any) -> Any:
    if isinstance(value, list):
        return [annotate_local_refs(item) for item in value]
    if not isinstance(value, dict):
        return value
    if "$ref" in value:
        ref = value["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/"):
            fail(f"External $ref is not supported yet: {ref}")
        result = {key: annotate_local_refs(item) for key, item in value.items() if key != "$ref"}
        result["x-schema-name"] = ref.rsplit("/", 1)[-1]
        return result
    return {key: annotate_local_refs(item) for key, item in value.items()}


def collect_operations(spec: dict[str, Any]) -> list[Operation]:
    operations: list[Operation] = []
    for path, path_item in spec["paths"].items():
        if not isinstance(path_item, dict):
            continue
        path_parameters = [parse_parameter(p, spec) for p in path_item.get("parameters", [])]
        for method, operation_obj in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation_obj, dict):
                continue
            parameters = list(path_parameters)
            parameters.extend(parse_parameter(p, spec) for p in operation_obj.get("parameters", []))
            request_schema, request_content_type = extract_request_body(operation_obj, spec)
            response_schema, response_content_type = extract_success_response(operation_obj, spec)
            tag = first(operation_obj.get("tags")) or "default"
            operation_id = operation_obj.get("operationId") or infer_operation_id(method, path, tag)
            operations.append(
                Operation(
                    method=method.upper(),
                    path=path,
                    operation_id=safe_name(str(operation_id), lower_first=True),
                    tag=str(tag),
                    summary=str(operation_obj.get("summary") or operation_obj.get("description") or ""),
                    parameters=parameters,
                    request_schema=request_schema,
                    request_content_type=request_content_type,
                    response_schema=response_schema,
                    response_content_type=response_content_type,
                    deprecated=bool(operation_obj.get("deprecated")),
                )
            )
    return operations


def parse_parameter(parameter: dict[str, Any], spec: dict[str, Any]) -> Parameter:
    parameter = resolve_schema(parameter, spec)
    return Parameter(
        name=parameter["name"],
        location=parameter.get("in", "query"),
        required=bool(parameter.get("required")),
        schema=resolve_schema(parameter.get("schema", {"type": "string"}), spec),
        query_object=bool(parameter.get("x-java-query-object") or parameter.get("x-query-object")),
    )


def extract_request_body(operation_obj: dict[str, Any], spec: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    body = operation_obj.get("requestBody")
    if not isinstance(body, dict):
        return None, None
    body = resolve_schema(body, spec)
    content = body.get("content", {})
    if not isinstance(content, dict):
        return None, None
    content_type = choose_content_type(content)
    if content_type is None:
        return None, None
    media = content[content_type]
    return resolve_schema(media.get("schema", {}), spec), content_type


def extract_success_response(operation_obj: dict[str, Any], spec: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    responses = operation_obj.get("responses", {})
    if not isinstance(responses, dict):
        return None, None
    for status in ("200", "201", "202", "204", "default"):
        if status not in responses:
            continue
        response = resolve_schema(responses[status], spec)
        content = response.get("content", {})
        if not isinstance(content, dict) or not content:
            return {"type": "void"}, None
        content_type = choose_content_type(content)
        if content_type is None:
            return None, None
        media = content[content_type]
        return resolve_schema(media.get("schema", {}), spec), content_type
    return None, None


def choose_content_type(content: dict[str, Any]) -> str | None:
    for content_type in ("application/json", "multipart/form-data", "application/x-www-form-urlencoded"):
        if content_type in content:
            return content_type
    return next(iter(content.keys()), None)


def resolve_schema(value: Any, spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    if "$ref" in value:
        target = ref_target(value["$ref"], spec)
        merged = dict(target)
        for key, item in value.items():
            if key != "$ref":
                merged[key] = item
        return resolve_schema(merged, spec)
    if "allOf" in value:
        return merge_all_of(value, spec)
    return {key: resolve_value(item, spec) for key, item in value.items()}


def resolve_value(value: Any, spec: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return resolve_schema(value, spec)
    if isinstance(value, list):
        return [resolve_value(item, spec) for item in value]
    return value


def ref_target(ref: str, spec: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        fail(f"External $ref is not supported yet: {ref}")
    current: Any = spec
    for part in ref[2:].split("/"):
        current = current[part.replace("~1", "/").replace("~0", "~")]
    if isinstance(current, dict):
        result = dict(current)
        result["x-schema-name"] = ref.rsplit("/", 1)[-1]
        return result
    fail(f"Invalid $ref target: {ref}")


def merge_all_of(value: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
    for item in value.get("allOf", []):
        schema = resolve_schema(item, spec)
        merged["properties"].update(schema.get("properties", {}))
        merged["required"].extend(schema.get("required", []))
    for key, item in value.items():
        if key != "allOf":
            merged[key] = item
    return merged


def unwrap_response_schemas(spec: dict[str, Any], operations: list[Operation], wrapper_name: str, data_field: str) -> None:
    for operation in operations:
        schema = operation.response_schema
        if not schema:
            continue
        if schema.get("x-schema-name") == wrapper_name:
            properties = schema.get("properties", {})
            if data_field in properties:
                operation.response_schema = resolve_schema(properties[data_field], spec)


def filter_operations(operations: list[Operation], options: GeneratorOptions) -> list[Operation]:
    if not options.exclude_tags and not options.exclude_operation_ids:
        return operations
    return [
        operation
        for operation in operations
        if operation.tag not in options.exclude_tags and operation.operation_id not in options.exclude_operation_ids
    ]


def prepare_operations_for_options(operations: list[Operation], options: GeneratorOptions) -> None:
    for operation in operations:
        operation.parameters = [
            parameter
            for parameter in operation.parameters
            if parameter_schema_name(parameter) not in options.ignore_parameter_schema_names
        ]
    if options.query_object_strategy != "query_map":
        return
    for operation in operations:
        query_params = [parameter for parameter in operation.parameters if parameter.location == "query"]
        query_object_params = [parameter for parameter in query_params if parameter.query_object]
        if len(query_object_params) == 1:
            parameter = query_object_params[0]
            operation.query_object_schema = resolve_inline_schema(parameter.schema)
            operation.query_object_param_name = java_identifier(parameter.name)
            continue
        if len(query_params) != 1:
            continue
        query_schema = resolve_inline_schema(query_params[0].schema)
        if query_schema.get("x-schema-name") or query_schema.get("properties"):
            query_params[0].query_object = True
            operation.query_object_schema = query_schema
            operation.query_object_param_name = java_identifier(query_params[0].name)


def parameter_schema_name(parameter: Parameter) -> str | None:
    schema = resolve_inline_schema(parameter.schema)
    schema_name = schema.get("x-schema-name")
    return str(schema_name) if schema_name else None


class JavaRetrofitGenerator:
    def __init__(self, options: GeneratorOptions, schemas: dict[str, dict[str, Any]], operations: list[Operation]) -> None:
        self.options = options
        self.schemas = schemas
        self.operations = operations
        self.base_dir = options.output_dir / Path(*options.base_package.split("."))
        self.files: list[Path] = []

    def generate(self) -> list[Path]:
        self.generate_models()
        self.generate_clients()
        return self.files

    def generate_models(self) -> None:
        for name, schema in self.reachable_schemas().items():
            if self.options.shared_pagination_type and name.startswith("PaginationOf"):
                continue
            if "enum" in schema or self.is_java_enum_schema(name, schema):
                self.write_enum(name, schema)
            elif schema.get("type") == "object" or "properties" in schema:
                self.write_model(name, schema)

    def reachable_schemas(self) -> dict[str, dict[str, Any]]:
        reachable: set[str] = set()
        for operation in self.operations:
            self.collect_schema_names(operation.response_schema, reachable)
            for parameter in operation.parameters:
                self.collect_schema_names(parameter.schema, reachable)
            self.collect_schema_names(operation.request_schema, reachable)
        queue = list(reachable)
        while queue:
            name = queue.pop()
            schema = self.schemas.get(name)
            if not schema:
                continue
            nested: set[str] = set()
            self.collect_schema_names(schema, nested)
            for item in nested:
                if item not in reachable:
                    reachable.add(item)
                    queue.append(item)
        return {name: self.schemas[name] for name in sorted(reachable) if name in self.schemas}

    def collect_schema_names(self, schema: Any, names: set[str]) -> None:
        if isinstance(schema, list):
            for item in schema:
                self.collect_schema_names(item, names)
            return
        if not isinstance(schema, dict):
            return
        schema_name = schema.get("x-schema-name")
        if isinstance(schema_name, str):
            if schema_name in self.options.ignore_schema_names:
                return
            names.add(schema_name)
        for item in schema.values():
            self.collect_schema_names(item, names)

    def generate_clients(self) -> None:
        grouped: dict[str, list[Operation]] = {}
        for operation in self.operations:
            grouped.setdefault(operation.tag, []).append(operation)
        for tag, operations in grouped.items():
            class_name = self.client_class_name(tag)
            package = self.client_package(tag)
            body_lines: list[str] = [f"package {package};", "", "import retrofit2.http.*;"]
            if self.options.return_style not in {"bare_unwrapped", "bare"}:
                body_lines.append("import retrofit2.Call;")
            extra_imports = self.collect_operation_imports(operations)
            for item in sorted(extra_imports):
                body_lines.append(f"import {item};")
            body_lines.extend(["", f"public interface {class_name} {{"])
            for operation in operations:
                body_lines.extend(self.render_operation(operation))
            body_lines.append("}")
            self.write_file(package_to_dir(self.options.output_dir, package) / f"{class_name}.java", "\n".join(body_lines) + "\n")

    def write_model(self, name: str, schema: dict[str, Any]) -> None:
        package = self.model_package(name)
        required = set(schema.get("required", []))
        properties = schema.get("properties", {})
        imports = {
            item
            for item in self.collect_model_imports(properties, required)
            if item != f"{package}.{to_pascal(name)}"
        }
        lines = [f"package {package};", ""]
        for item in sorted(imports):
            lines.append(f"import {item};")
        if imports:
            lines.append("")
        class_name = to_pascal(name)
        extends_clause = ""
        if self.options.query_object_strategy == "query_map" and class_name.endswith("Query"):
            for dependency in self.options.query_object_share_dependencies:
                lines.append(f"import {dependency};")
            if self.options.query_object_share_dependencies:
                lines.append("")
            if self.options.query_object_share_class_name:
                extends_clause = f" extends {self.options.query_object_share_class_name}"
        lines.append(f"public class {class_name}{extends_clause} {{")
        fields: list[tuple[str, str, dict[str, Any]]] = []
        for raw_name, property_schema in properties.items():
            prop = resolve_inline_schema(property_schema)
            java_name = java_identifier(raw_name)
            java_type = self.java_type(prop)
            fields.append((java_name, java_type, prop))
            if extends_clause:
                continue
            if raw_name in required and self.options.validation_namespace != "none":
                lines.append("    @NotNull")
            lines.append(f"    private {java_type} {java_name};")
            lines.append("")
        for java_name, java_type, _ in fields:
            suffix = java_name[0].upper() + java_name[1:]
            if extends_clause:
                lines.append(f"    public {java_type} get{suffix}() {{")
                lines.append(f"        return ({java_type}) get(\"{java_name}\");")
                lines.append("    }")
                lines.append("")
                lines.append(f"    public {class_name} set{suffix}({java_type} {java_name}) {{")
                lines.append(f"        put(\"{java_name}\", {java_name});")
                lines.append("        return this;")
                lines.append("    }")
                lines.append("")
            else:
                lines.append(f"    public {java_type} get{suffix}() {{")
                lines.append(f"        return {java_name};")
                lines.append("    }")
                lines.append("")
                lines.append(f"    public void set{suffix}({java_type} {java_name}) {{")
                lines.append(f"        this.{java_name} = {java_name};")
                lines.append("    }")
                lines.append("")
        lines.append("}")
        self.write_file(package_to_dir(self.options.output_dir, package) / f"{class_name}.java", "\n".join(lines) + "\n")

    def write_enum(self, name: str, schema: dict[str, Any]) -> None:
        package = self.model_package(name)
        constants = [to_enum_constant(str(item)) for item in schema.get("enum", [])] or ["UNKNOWN"]
        lines = [f"package {package};", "", f"public enum {to_pascal(name)} {{", f"    {', '.join(constants)}", "}"]
        self.write_file(package_to_dir(self.options.output_dir, package) / f"{to_pascal(name)}.java", "\n".join(lines) + "\n")

    def is_java_enum_schema(self, name: str, schema: dict[str, Any]) -> bool:
        return (
            schema.get("type") == "string"
            and not schema.get("properties")
            and (
                name.endswith(("Enum", "Type", "State", "Code", "Category"))
                or ".enums." in str(schema.get("x-java-full-name") or "")
                or ".core." in str(schema.get("x-java-full-name") or "")
            )
        )

    def render_operation(self, operation: Operation) -> list[str]:
        lines = ["", "    /**"]
        if operation.summary:
            lines.append(f"     * {operation.summary}")
        if operation.deprecated:
            lines.append("     * @deprecated")
        lines.append("     */")
        if operation.deprecated:
            lines.append("    @Deprecated")
        lines.append(f"    @{operation.method}(\"{operation.path}\")")
        response_type = self.java_type(operation.response_schema or {"type": "void"})
        return_type = response_type if self.options.return_style in {"bare_unwrapped", "bare"} else f"Call<{response_type}>"
        params: list[str] = []
        for parameter in operation.parameters:
            if parameter.location == "query" and parameter.query_object and operation.query_object_schema:
                params.append(
                    f"@QueryMap() {self.java_type(operation.query_object_schema)} "
                    f"{operation.query_object_param_name or java_identifier(parameter.name)}"
                )
                continue
            annotation = {
                "path": "Path",
                "query": "Query",
                "header": "Header",
                "cookie": "Header",
            }.get(parameter.location, "Query")
            params.append(f"@{annotation}(\"{parameter.name}\") {self.java_type(parameter.schema)} {java_identifier(parameter.name)}")
        if operation.request_schema and operation.request_schema.get("type") != "void":
            params.append(f"@Body {self.java_type(operation.request_schema)} request")
        rendered_params = ", ".join(params)
        lines.append(f"    {return_type} {java_identifier(operation.operation_id)}({rendered_params});")
        return lines

    def collect_model_imports(self, properties: dict[str, Any], required: set[str]) -> set[str]:
        imports: set[str] = set()
        for property_schema in properties.values():
            self.add_java_type_imports(resolve_inline_schema(property_schema), imports)
        if required and self.options.validation_namespace != "none":
            imports.add(f"{self.options.validation_namespace}.constraints.NotNull")
        return imports

    def collect_operation_imports(self, operations: Iterable[Operation]) -> set[str]:
        imports: set[str] = set()
        for operation in operations:
            self.add_java_type_imports(operation.response_schema or {"type": "void"}, imports)
            for parameter in operation.parameters:
                if parameter.location == "query" and parameter.query_object and operation.query_object_schema:
                    self.add_java_type_imports(operation.query_object_schema, imports)
                else:
                    self.add_java_type_imports(parameter.schema, imports)
            if operation.request_schema:
                self.add_java_type_imports(operation.request_schema, imports)
        return imports

    def add_java_type_imports(self, schema: dict[str, Any], imports: set[str]) -> None:
        schema = resolve_inline_schema(schema)
        schema_name = schema.get("x-schema-name")
        if schema_name:
            if self.options.shared_pagination_type and str(schema_name).startswith("PaginationOf"):
                if self.options.shared_pagination_import:
                    imports.add(self.options.shared_pagination_import)
                item_name = str(schema_name).removeprefix("PaginationOf")
                imports.add(f"{self.model_package(item_name)}.{to_pascal(item_name)}")
                return
            imports.add(f"{self.model_package(str(schema_name))}.{to_pascal(schema_name)}")
            return
        if schema.get("type") == "array":
            imports.add("java.util.List")
            self.add_java_type_imports(schema.get("items", {}), imports)
        if schema.get("type") == "object" and "additionalProperties" in schema:
            imports.add("java.util.Map")
        fmt = schema.get("format")
        if schema.get("type") == "string" and fmt == "binary":
            imports.add("okhttp3.RequestBody")
        elif fmt == "date-time" and schema.get("x-java-type") == "LocalDateTime":
            imports.add("java.time.LocalDateTime")
        elif fmt == "date-time":
            imports.add("java.time.OffsetDateTime")
        elif fmt == "date":
            imports.add("java.time.LocalDate")
        elif schema.get("type") == "number":
            imports.add("java.math.BigDecimal")

    def java_type(self, schema: dict[str, Any]) -> str:
        schema = resolve_inline_schema(schema)
        if schema.get("x-schema-name"):
            schema_name = str(schema["x-schema-name"])
            if self.options.shared_pagination_type and schema_name.startswith("PaginationOf"):
                item_name = schema_name.removeprefix("PaginationOf")
                return f"{self.options.shared_pagination_type}<{to_pascal(item_name)}>"
            return to_pascal(schema_name)
        if "enum" in schema:
            return "String"
        typ = schema.get("type")
        fmt = schema.get("format")
        if typ == "void":
            return "Void"
        if typ == "string":
            if fmt == "date-time" and schema.get("x-java-type") == "LocalDateTime":
                return "LocalDateTime"
            if fmt == "date-time":
                return "OffsetDateTime"
            if fmt == "date":
                return "LocalDate"
            if fmt == "binary":
                return "okhttp3.RequestBody"
            return "String"
        if typ == "integer":
            return "Long" if fmt == "int64" else "Integer"
        if typ == "number":
            return "BigDecimal"
        if typ == "boolean":
            return "Boolean"
        if typ == "array":
            return f"List<{self.java_type(schema.get('items', {}))}>"
        if typ == "object":
            if "additionalProperties" in schema:
                return f"Map<String, {self.java_type(schema['additionalProperties'])}>"
            return "Map<String, Object>"
        return "Object"

    def client_class_name(self, tag: str) -> str:
        class_name = to_pascal(tag)
        mapped = self.options.client_name_map.get(tag) or self.options.client_name_map.get(class_name)
        if mapped:
            return mapped if mapped.endswith(self.options.client_suffix) else f"{mapped}{self.options.client_suffix}"
        for suffix in ("Controller", "Operation"):
            if class_name.endswith(suffix):
                class_name = class_name[: -len(suffix)]
        if class_name.endswith(self.options.client_suffix):
            return class_name
        return f"{class_name}{self.options.client_suffix}"

    def client_package(self, tag: str) -> str:
        override = self.options.package_map.get("clients")
        if override:
            base = package_value(self.options.base_package, override)
        else:
            base = f"{self.options.base_package}.clients"
        if self.options.template_style == "loong_wind_retrofit":
            segment = client_segment(tag)
            segment = self.options.client_segment_map.get(to_pascal(tag), self.options.client_segment_map.get(segment, segment))
            if segment:
                return f"{base}.{segment}"
        return base

    def model_package(self, name: str) -> str:
        schema = self.schemas.get(name, {})
        java_package = str(schema.get("x-java-package") or "")
        if java_package:
            package_override = self.mapped_package_from_java_package(java_package)
            if package_override:
                return package_override
        if name.endswith("Query") and "query" in self.options.model_package_map:
            return package_value(self.options.base_package, self.options.model_package_map["query"])
        if name.endswith("Request") and "request" in self.options.model_package_map:
            return package_value(self.options.base_package, self.options.model_package_map["request"])
        if "dto" in self.options.model_package_map and (name.endswith("DTO") or name.endswith("Dto")):
            return package_value(self.options.base_package, self.options.model_package_map["dto"])
        if "enum" in self.options.model_package_map and (name.endswith("Enum") or name.endswith("Type") or name.endswith("Code")):
            return package_value(self.options.base_package, self.options.model_package_map["enum"])
        return package_value(self.options.base_package, self.options.model_package_map.get("default", "model"))

    def mapped_package_from_java_package(self, java_package: str) -> str | None:
        package_patterns = {key: value for key, value in self.options.package_map.items() if key != "clients"}
        for pattern, target in package_patterns.items():
            if package_matches(pattern, java_package):
                return package_value(self.options.base_package, target)
        return None

    def write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.files.append(path)


class TypeScriptFetchGenerator:
    def __init__(self, options: GeneratorOptions, schemas: dict[str, dict[str, Any]], operations: list[Operation]) -> None:
        self.options = options
        self.schemas = schemas
        self.operations = operations
        self.files: list[Path] = []

    def generate(self) -> list[Path]:
        self.write_models()
        self.write_client()
        self.write_index()
        return self.files

    def write_models(self) -> None:
        lines: list[str] = []
        for name, schema in self.schemas.items():
            if schema.get("type") == "object" or "properties" in schema:
                lines.extend(self.render_interface(name, schema))
            elif "enum" in schema:
                values = " | ".join(json.dumps(item) for item in schema.get("enum", [])) or "string"
                lines.append(f"export type {to_pascal(name)} = {values};")
                lines.append("")
        self.write_file(self.options.output_dir / "models.ts", "\n".join(lines))

    def render_interface(self, name: str, schema: dict[str, Any]) -> list[str]:
        required = set(schema.get("required", []))
        lines = [f"export interface {to_pascal(name)} {{"]
        for raw_name, property_schema in schema.get("properties", {}).items():
            optional = "" if raw_name in required else "?"
            lines.append(
                f"  {ts_property_name(raw_name)}{optional}: "
                f"{self.ts_type(resolve_inline_schema(property_schema), model_namespace=False)};"
            )
        lines.append("}")
        lines.append("")
        return lines

    def write_client(self) -> None:
        lines = [
            "import * as Models from './models';",
            "",
            "export interface RequestOptions {",
            "  baseUrl?: string;",
            "  headers?: Record<string, string>;",
            "  fetch?: typeof fetch;",
            "}",
            "",
            "async function sendRequest<T>(method: string, path: string, body: unknown, options: RequestOptions = {}): Promise<T> {",
            "  const fetcher = options.fetch ?? fetch;",
            "  const response = await fetcher(`${options.baseUrl ?? ''}${path}`, {",
            "    method,",
            "    headers: { 'content-type': 'application/json', ...(options.headers ?? {}) },",
            "    body: body === undefined ? undefined : JSON.stringify(body),",
            "  });",
            "  if (!response.ok) {",
            "    throw new Error(`HTTP ${response.status}`);",
            "  }",
            "  if (response.status === 204) {",
            "    return undefined as T;",
            "  }",
            "  return await response.json() as T;",
            "}",
            "",
        ]
        used_names: set[str] = set()
        for operation in self.operations:
            lines.extend(self.render_function(operation, used_names))
        self.write_file(self.options.output_dir / "client.ts", "\n".join(lines))

    def render_function(self, operation: Operation, used_names: set[str]) -> list[str]:
        path_params = [p for p in operation.parameters if p.location == "path"]
        query_params = [p for p in operation.parameters if p.location == "query"]
        header_params = [p for p in operation.parameters if p.location == "header"]
        params: list[str] = []
        function_name = unique_name(ts_identifier(operation.operation_id), used_names)

        required_params = [p for p in query_params + header_params if p.required]
        optional_params = [p for p in query_params + header_params if not p.required]
        for parameter in path_params + required_params:
            optional = "" if parameter.required else "?"
            params.append(f"{ts_identifier(parameter.name)}{optional}: {self.ts_type(parameter.schema)}")
        body_arg = "body"
        if operation.request_schema and operation.request_schema.get("type") != "void":
            params.append(f"{body_arg}: {self.ts_type(operation.request_schema)}")
        for parameter in optional_params:
            params.append(f"{ts_identifier(parameter.name)}?: {self.ts_type(parameter.schema)}")
        params.append("options?: RequestOptions")

        lines = []
        if operation.summary:
            lines.append(f"/** {operation.summary} */")
        return_type = self.ts_type(operation.response_schema or {"type": "void"})
        lines.append(f"export async function {function_name}({', '.join(params)}): Promise<{return_type}> {{")
        lines.append(f"  let path = `{ts_template_path(operation.path)}`;")
        if query_params:
            lines.append("  const query = new URLSearchParams();")
            for parameter in query_params:
                name = ts_identifier(parameter.name)
                lines.append(f"  if ({name} !== undefined) query.append('{parameter.name}', String({name}));")
            lines.append("  const queryString = query.toString();")
            lines.append("  if (queryString) path += `?${queryString}`;")
        if header_params:
            lines.append("  options = { ...(options ?? {}), headers: { ...((options ?? {}).headers ?? {}) } };")
            for parameter in header_params:
                name = ts_identifier(parameter.name)
                lines.append(f"  if ({name} !== undefined) options.headers!['{parameter.name}'] = String({name});")
        rendered_body_arg = body_arg if operation.request_schema and operation.request_schema.get("type") != "void" else "undefined"
        lines.append(f"  return sendRequest<{return_type}>('{operation.method}', path, {rendered_body_arg}, options);")
        lines.append("}")
        lines.append("")
        return lines

    def write_index(self) -> None:
        self.write_file(self.options.output_dir / "index.ts", "export * from './models';\nexport * from './client';\n")

    def ts_type(self, schema: dict[str, Any], model_namespace: bool = True) -> str:
        schema = resolve_inline_schema(schema)
        if schema.get("x-schema-name"):
            model_name = to_pascal(str(schema["x-schema-name"]))
            return f"Models.{model_name}" if model_namespace else model_name
        if "enum" in schema:
            return " | ".join(json.dumps(item) for item in schema.get("enum", [])) or "string"
        typ = schema.get("type")
        if typ == "void":
            return "void"
        if typ == "string":
            return "string"
        if typ in {"integer", "number"}:
            return "number"
        if typ == "boolean":
            return "boolean"
        if typ == "array":
            return f"Array<{self.ts_type(schema.get('items', {}), model_namespace=model_namespace)}>"
        if typ == "object":
            if "additionalProperties" in schema:
                return (
                    "Record<string, "
                    f"{self.ts_type(schema['additionalProperties'], model_namespace=model_namespace)}>"
                )
            return "Record<string, unknown>"
        return "unknown"

    def write_file(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.files.append(path)


def resolve_inline_schema(schema: Any) -> dict[str, Any]:
    if isinstance(schema, dict):
        return schema
    return {}


def infer_operation_id(method: str, path: str, tag: str) -> str:
    parts = [tag, method]
    parts.extend(part for part in path.split("/") if part and not part.startswith("{"))
    return "_".join(parts)


def first(value: Any) -> Any:
    if isinstance(value, list) and value:
        return value[0]
    return None


def safe_name(value: str, lower_first: bool = False) -> str:
    words = split_words(value)
    if not words:
        return "unnamed"
    first_word = words[0].lower() if lower_first else capitalize_word(words[0])
    rest = [capitalize_word(word) for word in words[1:]]
    return first_word + "".join(rest)


def split_words(value: str) -> list[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", value)
    return re.findall(r"[A-Za-z0-9]+", value)


def capitalize_word(value: str) -> str:
    if not value:
        return value
    if value.isupper() and len(value) > 1:
        return value
    return value[0].upper() + value[1:]


def to_pascal(value: str) -> str:
    result = safe_name(value, lower_first=False)
    return result[0].upper() + result[1:]


def java_identifier(value: str) -> str:
    result = safe_name(value, lower_first=True)
    if result in JAVA_RESERVED or keyword.iskeyword(result):
        return result + "_"
    return result


def ts_identifier(value: str) -> str:
    result = safe_name(value, lower_first=True)
    if result in TS_RESERVED:
        return result + "_"
    return result


def unique_name(base: str, used: set[str]) -> str:
    candidate = base
    index = 2
    while candidate in used:
        candidate = f"{base}{index}"
        index += 1
    used.add(candidate)
    return candidate


def package_to_dir(output_dir: Path, package: str) -> Path:
    return output_dir / Path(*package.split("."))


def package_value(base_package: str, value: str) -> str:
    if not value:
        return base_package
    if value.startswith(base_package):
        return value
    if value.startswith("."):
        return f"{base_package}{value}"
    return f"{base_package}.{value}"


def package_matches(pattern: str, java_package: str) -> bool:
    if pattern == java_package:
        return True
    regex = re.escape(pattern)
    regex = regex.replace(r"\*\*", r"(?:[\w]+\.)*[\w]*")
    regex = regex.replace(r"\*", r"[\w]+")
    return re.fullmatch(regex, java_package) is not None


def client_segment(tag: str) -> str:
    normalized = re.sub(r"ApiClient$", "", to_pascal(tag))
    normalized = re.sub(r"Controller$", "", normalized)
    normalized = re.sub(r"Operation$", "", normalized)
    words = split_words(normalized)
    if not words:
        return ""
    first_word = words[0].lower()
    if first_word in {"web", "hook", "example", "default"}:
        return ""
    return first_word


def ts_property_name(value: str) -> str:
    if re.match(r"^[A-Za-z_$][A-Za-z0-9_$]*$", value) and value not in TS_RESERVED:
        return value
    return json.dumps(value)


def ts_template_path(path: str) -> str:
    return re.sub(
        r"\{([^}]+)\}",
        lambda m: "${encodeURIComponent(String(" + ts_identifier(m.group(1)) + "))}",
        path,
    )


def to_enum_constant(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()
    if not result or result[0].isdigit():
        result = "_" + result
    return result


if __name__ == "__main__":
    raise SystemExit(main())
