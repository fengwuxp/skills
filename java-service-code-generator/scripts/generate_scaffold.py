#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import hashlib
import io
import os
import re
import sys
from pathlib import Path


RESERVED = {
    "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
    "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float",
    "for", "goto", "if", "implements", "import", "instanceof", "int", "interface", "long", "native",
    "new", "package", "private", "protected", "public", "return", "short", "static", "strictfp",
    "super", "switch", "synchronized", "this", "throw", "throws", "transient", "try", "void",
    "volatile", "while", "record", "var", "yield", "sealed", "permits", "non-sealed",
}

CURRENCY_ENUM = "CurrencyIsoCode"
CURRENCY_ENUM_IMPORT = "com.wind.transaction.core.enums.CurrencyIsoCode"


def avoid_reserved_identifier(name: str) -> str:
    return f"{name}Value" if name in RESERVED else name


def lower_camel_identifier(name: str) -> str:
    if not name:
        return name
    return avoid_reserved_identifier(name[:1].lower() + name[1:])


@dataclasses.dataclass
class Column:
    name: str
    sql_type: str
    nullable: bool = True
    auto_increment: bool = False
    primary: bool = False
    comment: str = ""
    default: str = ""
    java_name: str = ""
    java_type: str = ""
    column_annotation: str = ""


@dataclasses.dataclass
class Table:
    name: str
    comment: str
    columns: list[Column]
    primary_keys: list[str]


@dataclasses.dataclass
class ModuleLayout:
    face_src: Path
    impl_src: Path
    base_package: str


def split_top_level(text: str) -> list[str]:
    parts = []
    start = 0
    depth = 0
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in ("'", '"', "`"):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            part = text[start:i].strip()
            if part:
                parts.append(part)
            start = i + 1
        i += 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def strip_sql_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n\r]*(?=[\n\r]|$)", "", sql)
    return sql


def find_matching_paren(text: str, open_index: int) -> int:
    depth = 0
    quote = None
    i = open_index
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in ("'", '"', "`"):
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("SQL 括号不匹配")


def extract_create_table(schema_sql: str, table_name: str) -> str:
    sql = strip_sql_comments(schema_sql)
    create_pattern = re.compile(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>(?:`[^`]+`|\"[^\"]+\"|\[[^\]]+\]|\w+)(?:\.(?:`[^`]+`|\"[^\"]+\"|\[[^\]]+\]|\w+))?)\s*\(",
        re.IGNORECASE,
    )
    normalized_target = unquote_identifier(table_name.split(".")[-1]).lower()
    for match in create_pattern.finditer(sql):
        found = unquote_identifier(match.group("name").split(".")[-1])
        if found.lower() != normalized_target:
            continue
        close_index = find_matching_paren(sql, match.end() - 1)
        semicolon = sql.find(";", close_index)
        if semicolon == -1:
            semicolon = len(sql)
        return sql[match.start():semicolon + 1]
    raise ValueError(f"未找到表 `{table_name}` 对应的 CREATE TABLE 语句")


def unquote_identifier(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in "`\"[" and value[-1] in "`\"]":
        return value[1:-1]
    return value


def extract_comment(definition: str) -> str:
    match = re.search(r"\bCOMMENT\s*=?\s*'((?:\\'|[^'])*)'", definition, re.IGNORECASE)
    if not match:
        match = re.search(r'\bCOMMENT\s*=?\s*"((?:\\"|[^"])*)"', definition, re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).replace("\\'", "'").replace('\\"', '"')


def parse_ddl(ddl: str) -> Table:
    ddl = strip_sql_comments(ddl)
    create = re.search(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<name>(?:`[^`]+`|\"[^\"]+\"|\[[^\]]+\]|\w+)(?:\.(?:`[^`]+`|\"[^\"]+\"|\[[^\]]+\]|\w+))?)\s*\(",
        ddl,
        re.IGNORECASE,
    )
    if not create:
        raise ValueError("未找到 CREATE TABLE 语句")
    table_name = unquote_identifier(create.group("name").split(".")[-1])
    body_start = create.end()
    i = find_matching_paren(ddl, body_start - 1)
    body = ddl[body_start:i]
    suffix = ddl[i + 1 :]
    table_comment = extract_comment(suffix)

    columns: list[Column] = []
    primary_keys: list[str] = []
    for item in split_top_level(body):
        first = item.strip().split(None, 1)[0].upper().strip("`\"[]")
        if first in {"PRIMARY", "UNIQUE", "KEY", "INDEX", "CONSTRAINT", "FOREIGN", "CHECK"}:
            if first == "PRIMARY":
                primary_keys.extend(unquote_identifier(x.strip()) for x in re.findall(r"[`\"\[]?([A-Za-z_][\w$]*)[`\"\]]?", item[item.find("(") + 1 : item.rfind(")")]))
            continue
        match = re.match(r"\s*(`[^`]+`|\"[^\"]+\"|\[[^\]]+\]|\w+)\s+(.+)$", item, re.DOTALL)
        if not match:
            continue
        name = unquote_identifier(match.group(1))
        rest = match.group(2).strip()
        sql_type = extract_sql_type(rest)
        upper = rest.upper()
        column = Column(
            name=name,
            sql_type=sql_type,
            nullable=not bool(re.search(r"\bNOT\s+NULL\b", rest, re.IGNORECASE)),
            auto_increment=bool(re.search(r"\bAUTO_INCREMENT\b|\bGENERATED\b.*\bIDENTITY\b", rest, re.IGNORECASE)),
            primary=bool(re.search(r"\bPRIMARY\s+KEY\b", rest, re.IGNORECASE)),
            comment=extract_comment(rest),
            default=(re.search(r"\bDEFAULT\s+(.+?)(?:\s+COMMENT|\s+ON\s+UPDATE|$)", rest, re.IGNORECASE) or [None, ""])[1].strip(),
        )
        if "PRIMARY KEY" in upper and name not in primary_keys:
            primary_keys.append(name)
        columns.append(column)
    for column in columns:
        if column.name in primary_keys:
            column.primary = True
    return Table(table_name, table_comment, columns, primary_keys)


def extract_annotation_value(annotation: str, key: str) -> str:
    match = re.search(rf"\b{re.escape(key)}\s*=\s*\"([^\"]+)\"", annotation)
    if match:
        return match.group(1)
    if key == "value":
        match = re.search(r"\(\s*\"([^\"]+)\"", annotation)
        if match:
            return match.group(1)
    return ""


def annotation_block(text: str, index: int) -> str:
    start = text.rfind("\n\n", 0, index)
    start = 0 if start == -1 else start + 2
    return text[start:index]


def sql_type_from_java_type(java_type_name: str) -> str:
    base = java_type_name.split(".")[-1]
    if base in {"Long", "long"}:
        return "bigint"
    if base in {"Integer", "int", "Short", "short", "Byte", "byte"}:
        return "int"
    if base in {"Boolean", "boolean"}:
        return "tinyint(1)"
    if base in {"BigDecimal"}:
        return "decimal(18,2)"
    if base in {"Float", "float"}:
        return "float"
    if base in {"Double", "double"}:
        return "double"
    if base in {"LocalDateTime", "Date", "Instant", "OffsetDateTime", "ZonedDateTime"}:
        return "datetime"
    if base in {"LocalDate"}:
        return "date"
    if base in {"LocalTime"}:
        return "time"
    if base in {"byte[]", "Byte[]"}:
        return "blob"
    return "varchar(255)"


def java_annotation_indicates_auto_increment(annotations: str) -> bool:
    return bool(re.search(r"KeyType\.Auto|GeneratedValue|autoIncrement\s*=\s*true", annotations, re.IGNORECASE))


def extract_java_doc_before(text: str, index: int) -> str:
    prefix = text[:index]
    docs = list(re.finditer(r"/\*\*(.*?)\*/", prefix, re.DOTALL))
    if not docs:
        return ""
    match = docs[-1]
    between = prefix[match.end():]
    between = re.sub(r"@[\w.]+(?:\([^)]*\))?", "", between, flags=re.DOTALL).strip()
    if between:
        return ""
    lines = []
    for line in match.group(1).splitlines():
        line = re.sub(r"^\s*\*\s?", "", line).strip()
        if line and not line.startswith("@"):
            lines.append(line)
    return " ".join(lines).strip()


def parse_java_class(java_source: str, table_name: str | None = None, table_comment: str = "") -> Table:
    class_match = re.search(r"\b(?:class|record)\s+([A-Z][A-Za-z0-9_]*)\b", java_source)
    if not class_match:
        raise ValueError("未找到 Java class 或 record 定义")
    class_name = base_class_name(class_match.group(1))
    class_annotations = annotation_block(java_source, class_match.start())
    actual_table_comment = table_comment or extract_java_doc_before(java_source, class_match.start())
    annotated_table = extract_annotation_value(class_annotations, "value") or extract_annotation_value(class_annotations, "name")
    actual_table_name = table_name or annotated_table or f"t_{camel_to_snake(class_name)}"

    columns: list[Column] = []
    primary_keys: list[str] = []
    field_pattern = re.compile(
        r"(?P<annotations>(?:\s*@[\w.]+(?:\([^;{}]*\))?\s*)*)"
        r"\s*(?:private|protected|public)\s+(?:final\s+)?(?P<type>[\w.<>, ?\[\]]+)\s+(?P<name>[a-zA-Z_][\w]*)\s*(?:=[^;]*)?;",
        re.MULTILINE,
    )
    for match in field_pattern.finditer(java_source):
        field_name = match.group("name")
        if field_name in {"serialVersionUID", "TABLE_NAME"}:
            continue
        annotations = match.group("annotations") or ""
        raw_type = re.sub(r"<.*>", "", match.group("type")).strip()
        column_name = extract_annotation_value(annotations, "value") or extract_annotation_value(annotations, "name") or camel_to_snake(field_name)
        comment = extract_java_doc_before(java_source, match.start()) or extract_annotation_value(annotations, "description")
        primary = "@Id" in annotations or "@TableId" in annotations
        nullable = not any(token in annotations for token in ("@NotNull", "@NotBlank", "@NotEmpty"))
        column = Column(
            name=column_name,
            sql_type=sql_type_from_java_type(raw_type),
            nullable=nullable,
            auto_increment=primary and java_annotation_indicates_auto_increment(annotations),
            primary=primary,
            comment=comment,
        )
        column.java_name = field_name
        columns.append(column)
        if primary:
            primary_keys.append(column_name)
    if not columns:
        raise ValueError("Java 类中未识别到可生成的字段")
    return Table(actual_table_name, actual_table_comment, columns, primary_keys)


def normalize_header(value: str) -> str:
    value = value.strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    aliases = {
        "字段名": "name",
        "列名": "name",
        "column": "name",
        "columnname": "name",
        "field": "java_name",
        "fieldname": "java_name",
        "属性名": "java_name",
        "java属性名": "java_name",
        "java字段名": "java_name",
        "javaname": "java_name",
        "类型": "sql_type",
        "字段类型": "sql_type",
        "sql类型": "sql_type",
        "sqltype": "sql_type",
        "数据库类型": "sql_type",
        "javatype": "java_type",
        "java类型": "java_type",
        "说明": "comment",
        "描述": "comment",
        "备注": "comment",
        "comment": "comment",
        "description": "comment",
        "是否主键": "primary",
        "主键": "primary",
        "pk": "primary",
        "是否必填": "required",
        "必填": "required",
        "是否为空": "nullable",
        "可空": "nullable",
        "nullable": "nullable",
        "默认值": "default",
        "default": "default",
        "是否自增": "auto_increment",
        "自增": "auto_increment",
        "autoincrement": "auto_increment",
    }
    return aliases.get(value, value)


def truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "是", "是的", "主键", "必填", "非空", "自增"}


def falsy(value: str) -> bool:
    return value.strip().lower() in {"0", "false", "no", "n", "否", "不是", "可空", "空"}


def read_table_rows(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    markdown_lines = [line for line in lines if "|" in line]
    if markdown_lines:
        rows = []
        for line in markdown_lines:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
                continue
            rows.append(cells)
        if len(rows) < 2:
            raise ValueError("字段表格至少需要表头和一行字段")
        headers = [normalize_header(cell) for cell in rows[0]]
        return [dict(zip(headers, row)) for row in rows[1:]]

    sample = "\n".join(lines)
    delimiter = "\t" if "\t" in sample else ","
    reader = csv.DictReader(io.StringIO(sample), delimiter=delimiter)
    if not reader.fieldnames:
        raise ValueError("字段表格缺少表头")
    reader.fieldnames = [normalize_header(name) for name in reader.fieldnames]
    return [dict(row) for row in reader]


def parse_field_table(text: str, table_name: str | None = None, table_comment: str = "") -> Table:
    rows = read_table_rows(text)
    columns: list[Column] = []
    primary_keys: list[str] = []
    for row in rows:
        name = (row.get("name") or "").strip()
        java_name = (row.get("java_name") or "").strip()
        if not name and java_name:
            name = camel_to_snake(java_name)
        if not name:
            continue
        sql_type = (row.get("sql_type") or "").strip()
        java_type_name = (row.get("java_type") or "").strip()
        if not sql_type:
            sql_type = sql_type_from_java_type(java_type_name) if java_type_name else "varchar(255)"
        primary = truthy(row.get("primary") or "")
        required = row.get("required") or ""
        nullable_value = row.get("nullable") or ""
        nullable = False if truthy(required) else True
        if nullable_value:
            nullable = not falsy(nullable_value)
        column = Column(
            name=name,
            sql_type=sql_type,
            nullable=nullable,
            auto_increment=truthy(row.get("auto_increment") or ""),
            primary=primary,
            comment=(row.get("comment") or "").strip(),
            default=(row.get("default") or "").strip(),
        )
        column.java_name = avoid_reserved_identifier(java_name) if java_name else field_name_from_column(name)
        columns.append(column)
        if primary:
            primary_keys.append(name)
    if not columns:
        raise ValueError("字段表格中未识别到有效字段")
    if not table_name:
        raise ValueError("字段表格输入必须通过 --table-name 指定目标表名")
    return Table(table_name, table_comment, columns, primary_keys)


def render_ddl(table: Table) -> str:
    lines = [f"CREATE TABLE `{table.name}` ("]
    definitions = []
    for column in table.columns:
        definition = f"  `{column.name}` {column.sql_type}"
        definition += " NOT NULL" if column.primary or not column.nullable else " NULL"
        if column.auto_increment:
            definition += " AUTO_INCREMENT"
        if column.default:
            definition += f" DEFAULT {column.default}"
        if column.comment:
            escaped = column.comment.replace("'", "\\'")
            definition += f" COMMENT '{escaped}'"
        definitions.append(definition)
    if table.primary_keys:
        keys = ", ".join(f"`{key}`" for key in table.primary_keys)
        definitions.append(f"  PRIMARY KEY ({keys})")
    lines.append(",\n".join(definitions))
    suffix = ""
    if table.comment:
        escaped_table_comment = table.comment.replace("'", "\\'")
        suffix = f" COMMENT='{escaped_table_comment}'"
    lines.append(f"){suffix};")
    return "\n".join(lines) + "\n"


def infer_input_type(text: str, source_path: Path | None = None) -> str:
    suffix = source_path.suffix.lower() if source_path else ""
    if suffix == ".java":
        return "java"
    if suffix in {".csv", ".tsv"}:
        return "table"
    if re.search(r"\bCREATE\s+TABLE\b", text, re.IGNORECASE):
        return "ddl"
    if re.search(r"\b(?:class|record)\s+[A-Z][A-Za-z0-9_]*\b", text):
        return "java"
    if "|" in text or "\t" in text:
        return "table"
    return "ddl"


def table_from_input(text: str, input_type: str, table_name: str | None = None, table_comment: str = "") -> Table:
    if input_type == "ddl":
        return parse_ddl(text)
    if input_type == "java":
        return parse_java_class(text, table_name, table_comment)
    if input_type == "table":
        return parse_field_table(text, table_name, table_comment)
    raise ValueError(f"不支持的输入类型：{input_type}")


def snake_to_pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:].lower() for part in re.split(r"[_\-\s]+", name) if part)


def snake_to_camel(name: str) -> str:
    pascal = snake_to_pascal(name)
    return pascal[:1].lower() + pascal[1:] if pascal else name


def camel_to_snake(name: str) -> str:
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return value.replace("-", "_").lower()


def base_class_name(name: str) -> str:
    return re.sub(r"(DTO|DO|VO|PO|BO|Entity|Request|Query)$", "", name)


def class_name_from_table(table_name: str) -> str:
    raw = re.sub(r"^t_", "", table_name)
    return snake_to_pascal(raw)


def kebab_to_camel(name: str) -> str:
    return snake_to_camel(name.replace("-", "_"))


def package_counts(src_root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not src_root.exists():
        return counts
    for java_file in src_root.rglob("*.java"):
        if "target" in java_file.parts:
            continue
        text = java_file.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"^\s*package\s+([a-zA-Z_][\w.]*);", text, re.MULTILINE)
        if match:
            pkg = match.group(1)
            parts = pkg.split(".")
            if len(parts) >= 3:
                base = ".".join(parts[:4]) if len(parts) >= 4 else ".".join(parts)
                counts[base] = counts.get(base, 0) + 1
    return counts


def package_from_java_files(src_root: Path) -> str | None:
    counts = package_counts(src_root)
    if not counts:
        return None
    return max(counts.items(), key=lambda x: x[1])[0]


def infer_base_package(face_src: Path, impl_src: Path, business_module: str | None, table_name: str | None = None) -> str:
    merged: dict[str, int] = {}
    for src_root in (impl_src, face_src):
        for pkg, count in package_counts(src_root).items():
            merged[pkg] = merged.get(pkg, 0) + count
    if len(merged) == 1:
        return next(iter(merged))
    if table_name and merged:
        normalized_table = re.sub(r"^t_", "", table_name).lower()
        table_prefixes = normalized_table.split("_")
        matches = []
        for pkg in merged:
            last = pkg.split(".")[-1].lower()
            if table_prefixes and table_prefixes[0] == last:
                matches.append(pkg)
        if len(matches) == 1:
            return matches[0]
    if merged:
        options = ", ".join(sorted(merged))
        raise ValueError(f"基础包名存在歧义，请选择其中一个：{options}")
    raise ValueError("无法推断基础包名，请传入 --base-package")


def resolve_module_layout(repo_root: Path, business_module: str, base_package: str | None, table_name: str | None = None) -> ModuleLayout:
    candidates = []
    module_path = Path(business_module)
    if module_path.is_absolute():
        candidates.append(module_path)
    else:
        candidates.append((repo_root / module_path).resolve())
        candidates.extend(repo_root.glob(f"**/{business_module}"))
    roots = []
    for candidate in candidates:
        if not candidate.exists() or "target" in candidate.parts:
            continue
        if candidate.name.endswith("-face") or candidate.name.endswith("-impl"):
            roots.append(candidate.parent)
        elif any(child.name.endswith("-face") or child.name.endswith("-impl") for child in candidate.iterdir() if child.is_dir()):
            roots.append(candidate)
    seen = []
    for root in roots:
        if root not in seen:
            seen.append(root)
    requested_name = Path(business_module).name
    requested_stem = re.sub(r"-(face|impl)$", "", requested_name)
    layouts: list[ModuleLayout] = []
    for root in seen:
        face_modules = sorted([p for p in root.iterdir() if p.is_dir() and p.name.endswith("-face")])
        impl_modules = sorted([p for p in root.iterdir() if p.is_dir() and p.name.endswith("-impl")])
        pairs = []
        for face_module in face_modules:
            stem = re.sub(r"-face$", "", face_module.name)
            impl_module = root / f"{stem}-impl"
            if impl_module.exists():
                pairs.append((stem, face_module, impl_module))
        if not pairs:
            continue
        exact_pairs = [pair for pair in pairs if pair[0] == requested_stem]
        if exact_pairs:
            pairs = exact_pairs
        if len(pairs) > 1 and requested_name == root.name:
            names = ", ".join(pair[0] for pair in pairs)
            raise ValueError(f"业务模块 `{business_module}` 存在歧义，请选择其中一个：{names}")
        for _, face_module, impl_module in pairs:
            face_src = face_module / "src/main/java"
            impl_src = impl_module / "src/main/java"
            layouts.append(ModuleLayout(face_src, impl_src, base_package or infer_base_package(face_src, impl_src, business_module, table_name)))
    if len(layouts) == 1:
        return layouts[0]
    if len(layouts) > 1:
        names = ", ".join(str(layout.face_src.parent.parent.parent.name) for layout in layouts)
        raise ValueError(f"业务模块 `{business_module}` 存在歧义，请指定具体模块：{names}")
    raise ValueError(f"无法解析业务模块 `{business_module}` 对应的 face/impl 模块")


def field_name_from_column(column_name: str) -> str:
    if column_name == "u_id":
        return "uid"
    if column_name.startswith("is_") and len(column_name) > 3:
        result = snake_to_camel(column_name[3:])
    else:
        result = snake_to_camel(column_name)
    return avoid_reserved_identifier(result)


def expected_column_from_field(field_name: str) -> str:
    if field_name == "uid":
        return "u_id"
    result = []
    for ch in field_name:
        if ch.isupper():
            result.append("_")
            result.append(ch.lower())
        else:
            result.append(ch)
    return "".join(result)


def java_type(column: Column) -> str:
    if is_currency_column(column):
        return CURRENCY_ENUM
    t = column.sql_type.lower()
    base = re.sub(r"\s*\(.*\)", "", t).strip()
    if base in {"bigint", "bigserial"}:
        return "Long"
    if base in {"int", "integer", "smallint", "mediumint", "serial"}:
        return "Integer"
    if base == "tinyint":
        return "Boolean" if re.search(r"\(\s*1\s*\)", t) else "Integer"
    if base in {"bit", "boolean", "bool"}:
        return "Boolean"
    if base in {"decimal", "numeric", "number"}:
        return "BigDecimal"
    if base in {"float", "real"}:
        return "Float"
    if base in {"double"}:
        return "Double"
    if base in {"datetime", "timestamp", "timestamp without time zone", "timestamp with time zone"}:
        return "LocalDateTime"
    if base == "date":
        return "LocalDate"
    if base == "time":
        return "LocalTime"
    if base in {"blob", "binary", "varbinary", "bytea"}:
        return "byte[]"
    return "String"


def is_currency_column(column: Column) -> bool:
    name = column.name.lower()
    return name in {"currency", "currency_code", "currency_iso_code"} or column.comment.strip() == "币种"


def extract_sql_type(rest: str) -> str:
    constraints = {
        "not", "null", "default", "comment", "auto_increment", "primary", "unique", "key",
        "references", "check", "generated", "collate", "character", "charset", "on",
    }
    tokens = re.findall(r"[A-Za-z]+(?:\([^)]*\))?|\([^)]*\)|\S+", rest)
    result = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        word = re.sub(r"\(.*\)", "", token).lower()
        if word in constraints:
            break
        result.append(token)
        i += 1
    if not result:
        raise ValueError(f"无法解析 SQL 类型：{rest}")
    if len(result) >= 2 and result[0].lower() == "double" and result[1].lower() == "precision":
        return "double precision"
    if len(result) >= 2 and result[0].lower() == "timestamp" and result[1].lower() in {"with", "without"}:
        return " ".join(result[:4])
    if len(result) >= 2 and result[1].lower() == "unsigned":
        return result[0]
    return result[0]


def column_annotation(column: Column) -> str:
    comment = column.comment or ""
    physical = column.name
    field = column.java_name
    if physical == "u_id":
        return '@Column("u_id")'
    if physical == "tenant_id" or field == "tenantId":
        return "@Column(tenantId = true)"
    if physical in {"version", "lock_version"} or "乐观锁" in comment or "版本号" in comment:
        return "@Column(version = true)"
    if physical in {"is_deleted", "deleted"} or "逻辑删除" in comment:
        return f'@Column(value = "{physical}", isLogicDelete = true)'
    if physical.startswith("is_") or physical != expected_column_from_field(field):
        return f'@Column("{physical}")'
    return ""


def prepare(table: Table, class_name: str | None) -> str:
    actual_class = class_name or class_name_from_table(table.name)
    for column in table.columns:
        column.java_name = avoid_reserved_identifier(column.java_name) if column.java_name else field_name_from_column(column.name)
        column.java_type = java_type(column)
        column.column_annotation = column_annotation(column)
    return actual_class


def imports_for_types(columns: list[Column], entity: bool) -> set[str]:
    imports = set()
    types = {c.java_type for c in columns}
    if "BigDecimal" in types:
        imports.add("java.math.BigDecimal")
    if "LocalDate" in types:
        imports.add("java.time.LocalDate")
    if "LocalDateTime" in types:
        imports.add("java.time.LocalDateTime")
    if "LocalTime" in types:
        imports.add("java.time.LocalTime")
    if CURRENCY_ENUM in types:
        imports.add(CURRENCY_ENUM_IMPORT)
    if entity:
        imports.add("java.io.Serial")
        imports.add("java.io.Serializable")
    return imports


def validation_annotation(column: Column) -> str:
    if column.primary or column.nullable or column.default:
        return ""
    if column.java_type == "String":
        return "@NotBlank"
    return "@NotNull"


def java_doc(comment: str, indent: str = "    ") -> str:
    if not comment:
        return ""
    lines = [f"{indent}/**"]
    for line in comment.splitlines():
        lines.append(f"{indent} * {line}")
    lines.append(f"{indent} */")
    return "\n".join(lines) + "\n"


def zh_sentence(text: str) -> str:
    value = text.strip()
    if not value:
        return ""
    if value.endswith(("。", "！", "？", ".", "!", "?")):
        return value
    return value + "。"


def words_from_identifier(value: str) -> str:
    value = re.sub(r"^t_", "", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    words = [word for word in value.split() if word]
    return " ".join(words) if words else value


def human_name(name: str) -> str:
    words = words_from_identifier(name)
    return words[:1].upper() + words[1:] if words else name


def class_desc(name: str) -> str:
    return human_name(name)


def table_desc(table: Table, name: str) -> str:
    return table.comment.strip() if table.comment and table.comment.strip() else class_desc(name)


def render_lines(lines: list[str]) -> str:
    rendered = "\n".join(lines)
    rendered = re.sub(r"\n{3,}", "\n\n", rendered)
    return rendered.rstrip() + "\n"


def serial_uid(seed: str) -> int:
    digest = hashlib.sha256(seed.encode("utf-8")).digest()[:8]
    value = int.from_bytes(digest, "big", signed=True)
    return value if value != 0 else 1


def render_entity(base_package: str, table: Table, name: str, author: str) -> str:
    imports = {
        "com.mybatisflex.annotation.Id",
        "com.mybatisflex.annotation.Table",
        "lombok.Data",
    }
    if any(c.primary and c.auto_increment for c in table.columns):
        imports.add("com.mybatisflex.annotation.KeyType")
    if any(c.column_annotation for c in table.columns):
        imports.add("com.mybatisflex.annotation.Column")
    if any(validation_annotation(c) == "@NotBlank" for c in table.columns):
        imports.add("jakarta.validation.constraints.NotBlank")
    if any(c.primary or validation_annotation(c) == "@NotNull" for c in table.columns):
        imports.add("jakarta.validation.constraints.NotNull")
    imports |= imports_for_types(table.columns, True)

    lines = [f"package {base_package}.dal.entities;", ""]
    lines.extend(f"import {imp};" for imp in sorted(imports))
    lines.extend(["", "/**"])
    lines.append(f" * {table_desc(table, name)}实体。")
    lines.append(" *")
    lines.append(f" * @author {author}")
    lines.append(f" * @date {dt.date.today().isoformat()}")
    lines.append(" */")
    lines.extend(["@Data", f"@Table({name}.TABLE_NAME)", f"public class {name} implements Serializable {{", ""])
    lines.append(f'    public static final String TABLE_NAME = "{table.name}";')
    lines.append("")
    lines.append("    @Serial")
    lines.append(f"    private static final long serialVersionUID = {serial_uid(name + table.name)}L;")
    lines.append("")
    for column in table.columns:
        if column.comment and column.comment.strip():
            lines.append(java_doc(zh_sentence(column.comment), "    ").rstrip())
        if column.primary:
            if column.auto_increment:
                lines.append("    @Id(keyType = KeyType.Auto)")
            else:
                lines.append("    @Id")
            lines.append("    @NotNull")
        else:
            ann = validation_annotation(column)
            if ann:
                lines.append(f"    {ann}")
        if column.column_annotation:
            lines.append(f"    {column.column_annotation}")
        lines.append(f"    private {column.java_type} {column.java_name};")
        lines.append("")
    lines.append("}")
    return render_lines(lines)


def render_mapper(base_package: str, table: Table, name: str, author: str) -> str:
    comment = table_desc(table, name)
    today = dt.date.today().isoformat()
    return f"""package {base_package}.dal.mapper;

import {base_package}.dal.entities.{name};
import com.mybatisflex.core.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/**
 * {comment}Mapper。
 *
 * @author {author}
 * @date {today}
 **/
@Mapper
public interface {name}Mapper extends BaseMapper<{name}> {{
}}
"""


def render_dto(base_package: str, table: Table, name: str, author: str) -> str:
    imports = {
        "io.swagger.v3.oas.annotations.media.Schema",
        "lombok.Data",
    }
    if any(validation_annotation(c) == "@NotBlank" for c in table.columns):
        imports.add("jakarta.validation.constraints.NotBlank")
    if any(c.primary or validation_annotation(c) == "@NotNull" for c in table.columns):
        imports.add("jakarta.validation.constraints.NotNull")
    imports |= imports_for_types(table.columns, False)
    today = dt.date.today().isoformat()
    lines = [f"package {base_package}.model.dto;", ""]
    lines.extend(f"import {imp};" for imp in sorted(imports))
    lines.extend(["", "/**"])
    lines.append(f" * {table_desc(table, name)}DTO。")
    lines.append(" *")
    lines.append(f" * @author {author}")
    lines.append(f" * @date {today}")
    lines.append(" */")
    lines.extend(["@Data", f"public class {name}DTO {{", ""])
    for column in table.columns:
        description = column.comment.strip() if column.comment and column.comment.strip() else ""
        if description:
            lines.append(java_doc(zh_sentence(description), "    ").rstrip())
            lines.append(f'    @Schema(description = "{description}")')
        ann = "@NotNull" if column.primary else validation_annotation(column)
        if ann:
            lines.append(f"    {ann}")
        lines.append(f"    private {column.java_type} {column.java_name};")
        lines.append("")
    lines.append("}")
    return render_lines(lines)


def render_request(base_package: str, table: Table, name: str, author: str, kind: str) -> str:
    class_name = f"{kind}{name}Request"
    action = "创建" if kind == "Create" else "更新"
    today = dt.date.today().isoformat()
    columns = table.columns if kind == "Update" else [c for c in table.columns if not c.primary and c.name not in {"gmt_create", "gmt_modified"}]
    imports = {
        "io.swagger.v3.oas.annotations.media.Schema",
        "lombok.Data",
    }
    if kind != "Update" and any(validation_annotation(c) == "@NotBlank" for c in columns):
        imports.add("jakarta.validation.constraints.NotBlank")
    if any(c.primary for c in columns) or (kind != "Update" and any(validation_annotation(c) == "@NotNull" for c in columns)):
        imports.add("jakarta.validation.constraints.NotNull")
    imports |= imports_for_types(columns, False)
    lines = [f"package {base_package}.model.request;", ""]
    lines.extend(f"import {imp};" for imp in sorted(imports))
    lines.extend(["", "/**", f" * {table_desc(table, name)}{action}请求。", " *", f" * @author {author}", f" * @date {today}", " */", "@Data", f"public class {class_name} {{", ""])
    for column in columns:
        description = column.comment.strip() if column.comment and column.comment.strip() else ""
        if description:
            lines.append(java_doc(zh_sentence(description), "    ").rstrip())
            lines.append(f'    @Schema(description = "{description}")')
        ann = "@NotNull" if column.primary else ("" if kind == "Update" else validation_annotation(column))
        if ann:
            lines.append(f"    {ann}")
        lines.append(f"    private {column.java_type} {column.java_name};")
        lines.append("")
    lines.append("}")
    return render_lines(lines)



def render_query(base_package: str, table: Table, name: str, author: str) -> str:
    columns = [c for c in table.columns if not c.primary and c.name not in {"gmt_create", "gmt_modified"}]
    imports = {"io.swagger.v3.oas.annotations.media.Schema", "java.time.LocalDateTime", "lombok.Data"}
    imports |= imports_for_types(columns, False)
    today = dt.date.today().isoformat()
    lines = [f"package {base_package}.model.query;", ""]
    lines.extend(f"import {imp};" for imp in sorted(imports))
    lines.extend(["", "/**", f" * {table_desc(table, name)}查询条件。", " *", f" * @author {author}", f" * @date {today}", " */", "@Data", f"public class {name}Query {{", ""])
    for column in columns:
        if column.comment and column.comment.strip():
            lines.append(f'    @Schema(description = "{column.comment.strip()}")')
        lines.append(f"    private {column.java_type} {column.java_name};")
        lines.append("")
    lines.extend([
        '    @Schema(description = "查询到最小gmtCreate")',
        "    private LocalDateTime minGmtCreate;",
        "",
        '    @Schema(description = "查询到最大gmtCreate")',
        "    private LocalDateTime maxGmtCreate;",
        "",
        '    @Schema(description = "查询到最小gmtModified")',
        "    private LocalDateTime minGmtModified;",
        "",
        '    @Schema(description = "查询到最大gmtModified")',
        "    private LocalDateTime maxGmtModified;",
        "",
    ])
    lines.append("}")
    return render_lines(lines)


def render_converter(base_package: str, table: Table, name: str, author: str) -> str:
    desc = table_desc(table, name)
    today = dt.date.today().isoformat()
    return f"""package {base_package}.services.mapstruct;

import {base_package}.dal.entities.{name};
import {base_package}.model.dto.{name}DTO;
import {base_package}.model.request.Create{name}Request;
import {base_package}.model.request.Update{name}Request;
import org.mapstruct.Mapper;
import org.mapstruct.factory.Mappers;

import java.util.List;

/**
 * {desc}转换器。
 *
 * @author {author}
 * @date {today}
 */
@Mapper
public interface {name}Converter {{

    {name}Converter INSTANCE = Mappers.getMapper({name}Converter.class);

    /**
     * DTO 转换为{desc}实体。
     *
     * @param dto DTO
     * @return {desc}实体
     */
    {name} convertToEntity({name}DTO dto);

    /**
     * 创建请求转换为{desc}实体。
     *
     * @param request 创建请求
     * @return {desc}实体
     */
    {name} convertToEntity(Create{name}Request request);

    /**
     * 更新请求转换为{desc}实体。
     *
     * @param request 更新请求
     * @return {desc}实体
     */
    {name} convertToEntity(Update{name}Request request);

    /**
     * {desc}实体转换为 DTO。
     *
     * @param entity {desc}实体
     * @return {desc}DTO
     */
    {name}DTO convertToDTO({name} entity);

    /**
     * {desc}实体列表转换为 DTO 列表。
     *
     * @param entities {desc}实体列表
     * @return {desc}DTO 列表
     */
    List<{name}DTO> convertToDTOList(List<{name}> entities);
}}
"""


def render_service(base_package: str, table: Table, name: str, author: str) -> str:
    desc = table_desc(table, name)
    today = dt.date.today().isoformat()
    return f"""package {base_package}.services;

import {base_package}.model.dto.{name}DTO;
import {base_package}.model.query.{name}Query;
import {base_package}.model.request.Create{name}Request;
import {base_package}.model.request.Update{name}Request;
import com.wind.common.query.WindPagination;
import com.wind.common.query.WindQuery;
import com.wind.common.query.supports.QueryOrderField;
import org.jspecify.annotations.NonNull;

/**
 * {desc}服务。
 *
 * @author {author}
 * @date {today}
 */
public interface {name}Service {{

    /**
     * 创建{desc}。
     *
     * @param request 创建请求
     * @return {desc}ID
     */
    Long create{name}(@NonNull Create{name}Request request);

    /**
     * 更新{desc}。
     *
     * @param request 更新请求
     */
    void update{name}(@NonNull Update{name}Request request);

    /**
     * 根据 ID 删除{desc}。
     *
     * @param id {desc}ID
     */
    default void delete{name}ById(@NonNull Long id) {{
        delete{name}ByIds(id);
    }}

    /**
     * 根据 ID 批量删除{desc}。
     *
     * @param ids {desc}ID 列表
     */
    void delete{name}ByIds(@NonNull Long... ids);

    /**
     * 根据 ID 查询{desc}。
     *
     * @param id {desc}ID
     * @return {desc}DTO
     */
    @NonNull
    {name}DTO get{name}ById(@NonNull Long id);

    /**
     * 分页查询{desc}。
     *
     * @param query 查询条件
     * @param options 查询选项
     * @return {desc}分页结果
     */
    @NonNull
    WindPagination<{name}DTO> query{name}s(@NonNull {name}Query query, @NonNull WindQuery<? extends QueryOrderField> options);
}}
"""


def render_query_conditions(table: Table, var: str) -> str:
    columns = [c for c in table.columns if not c.primary and c.name not in {"gmt_create", "gmt_modified"}]
    conditions = [f"{var}.{column.java_name}.eq(query.get{column.java_name[:1].upper() + column.java_name[1:]}())" for column in columns]
    if any(c.name == "gmt_create" for c in table.columns):
        conditions.append(f"{var}.gmtCreate.ge(query.getMinGmtCreate())")
        conditions.append(f"{var}.gmtCreate.le(query.getMaxGmtCreate())")
    if any(c.name == "gmt_modified" for c in table.columns):
        conditions.append(f"{var}.gmtModified.ge(query.getMinGmtModified())")
        conditions.append(f"{var}.gmtModified.le(query.getMaxGmtModified())")
    if not conditions:
        return ""
    rendered = "\n                .where(" + conditions[0] + ")"
    for condition in conditions[1:]:
        rendered += "\n                .and(" + condition + ")"
    return rendered


def render_service_impl(base_package: str, table: Table, name: str, author: str) -> str:
    var = lower_camel_identifier(name)
    desc = table_desc(table, name)
    today = dt.date.today().isoformat()
    deleted = next((c for c in table.columns if c.column_annotation and "isLogicDelete" in c.column_annotation), None)
    deleted_check = ""
    if deleted:
        getter = "get" + deleted.java_name[:1].upper() + deleted.java_name[1:] + "()"
        deleted_check = f'\n        AssertUtils.isFalse(Boolean.TRUE.equals(result.{getter}), "{desc}不存在或已删除");'
    query_conditions = render_query_conditions(table, var)
    return f"""package {base_package}.services.impl;

import {base_package}.dal.entities.{name};
import {base_package}.dal.entities.table.{name}NameRefs;
import {base_package}.dal.mapper.{name}Mapper;
import {base_package}.model.dto.{name}DTO;
import {base_package}.model.query.{name}Query;
import {base_package}.model.request.Create{name}Request;
import {base_package}.model.request.Update{name}Request;
import {base_package}.services.{name}Service;
import {base_package}.services.mapstruct.{name}Converter;
import com.mybatisflex.core.query.QueryWrapper;
import com.wind.common.exception.AssertUtils;
import com.wind.common.query.WindPagination;
import com.wind.common.query.WindQuery;
import com.wind.common.query.supports.QueryOrderField;
import com.wind.mybatis.flex.MybatisQueryHelper;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.jspecify.annotations.NonNull;
import org.springframework.stereotype.Service;

import java.util.Arrays;

/**
 * {desc}服务实现。
 *
 * @author {author}
 * @date {today}
 */
@Service
@Slf4j
@AllArgsConstructor
public class {name}ServiceImpl implements {name}Service {{

    private final {name}Mapper {var}Mapper;

    /**
     * 创建{desc}。
     *
     * @param request 创建请求
     * @return {desc}ID
     */
    @Override
    public Long create{name}(@NonNull Create{name}Request request) {{
        {name} entity = {name}Converter.INSTANCE.convertToEntity(request);
        AssertUtils.isTrue({var}Mapper.insertSelective(entity) > 0, "创建{desc}失败");
        return entity.getId();
    }}

    /**
     * 更新{desc}。
     *
     * @param request 更新请求
     */
    @Override
    public void update{name}(@NonNull Update{name}Request request) {{
        find{name}(request.getId());
        {name} entity = {name}Converter.INSTANCE.convertToEntity(request);
        AssertUtils.isTrue({var}Mapper.updateSelective(entity) == 1, "更新{desc}失败");
    }}

    /**
     * 根据 ID 批量删除{desc}。
     *
     * @param ids {desc}ID 列表
     */
    @Override
    public void delete{name}ByIds(@NonNull Long... ids) {{
        AssertUtils.notEmpty(ids, "参数 ids 不能为空");
        int total = {var}Mapper.deleteBatchByIds(Arrays.asList(ids));
        AssertUtils.isTrue(total == ids.length, "删除{desc}失败");
    }}

    /**
     * 根据 ID 查询{desc}。
     *
     * @param id {desc}ID
     * @return {desc}DTO
     */
    @Override
    @NonNull
    public {name}DTO get{name}ById(@NonNull Long id) {{
        return {name}Converter.INSTANCE.convertToDTO(find{name}(id));
    }}

    /**
     * 分页查询{desc}。
     *
     * @param query 查询条件
     * @param options 查询选项
     * @return {desc}分页结果
     */
    @Override
    @NonNull
    public WindPagination<{name}DTO> query{name}s(@NonNull {name}Query query, @NonNull WindQuery<? extends QueryOrderField> options) {{
        {name}NameRefs {var} = {name}NameRefs.{var};
        QueryWrapper queryWrapper = MybatisQueryHelper.from(options).select()
                .from({var}){query_conditions};

        return MybatisQueryHelper.<{name}, {name}DTO>query(queryWrapper)
                .counter({var}Mapper::selectCountByQuery)
                .resultQueryFunc({var}Mapper::selectListByQuery)
                .converter({name}Converter.INSTANCE::convertToDTO)
                .query(options);
    }}

    /**
     * 根据 ID 查询{desc}实体。
     *
     * @param id {desc}ID
     * @return {desc}实体
     */
    private {name} find{name}(@NonNull Long id) {{
        {name} result = {var}Mapper.selectOneById(id);
        AssertUtils.notNull(result, "{desc}不存在");{deleted_check}
        return result;
    }}
}}
"""


def package_path(base: Path, package_name: str) -> Path:
    return base.joinpath(*package_name.split("."))


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} exists; pass --overwrite to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="根据 DDL、Java 类或字段表格生成 Wind/Nobe 风格 Java 模板代码")
    parser.add_argument("--input-file", help="输入文件路径，支持 DDL/SQL、Java 类、Markdown/CSV/TSV 字段表格")
    parser.add_argument("--input-type", choices=["auto", "ddl", "java", "table"], default="auto", help="输入类型，默认自动识别")
    parser.add_argument("--ddl-file", help="DDL 文件路径；未传入时读取标准输入")
    parser.add_argument("--schema-file", help="包含多个 CREATE TABLE 语句的 schema 文件")
    parser.add_argument("--table-name", help="目标表名；schema 输入时用于提取 CREATE TABLE，Java/字段表格输入时用于指定生成表名")
    parser.add_argument("--table-comment", default="", help="Java/字段表格输入时的表中文说明")
    parser.add_argument("--business-module", help="业务模块路径或名称，例如 user-domain 或 user-domain/user-face")
    parser.add_argument("--repo-root", default=".", help="配合 --business-module 使用的仓库根目录")
    parser.add_argument("--base-package", help="基础包名，例如 com.example.skill.codegen")
    parser.add_argument("--author", default=os.environ.get("USER", "codex"))
    parser.add_argument("--class-name")
    parser.add_argument("--output-dir", help="评审输出目录；未传入 face-src/impl-src 时使用")
    parser.add_argument("--face-src", help="Face 模块 src/main/java 根目录")
    parser.add_argument("--impl-src", help="Impl 模块 src/main/java 根目录")
    parser.add_argument("--emit-ddl", help="将 Java 类或字段表格归一后生成 DDL 草案到指定路径")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    source_path = None
    if args.schema_file:
        if not args.table_name:
            parser.error("使用 --schema-file 时必须同时传入 --table-name")
        ddl = extract_create_table(Path(args.schema_file).read_text(encoding="utf-8"), args.table_name)
        input_type = "ddl"
    elif args.input_file:
        source_path = Path(args.input_file)
        ddl = source_path.read_text(encoding="utf-8")
        input_type = infer_input_type(ddl, source_path) if args.input_type == "auto" else args.input_type
    elif args.ddl_file:
        ddl = Path(args.ddl_file).read_text(encoding="utf-8")
        input_type = "ddl" if args.input_type == "auto" else args.input_type
    else:
        ddl = sys.stdin.read()
        input_type = infer_input_type(ddl) if args.input_type == "auto" else args.input_type
    table = table_from_input(ddl, input_type, args.table_name, args.table_comment)
    name = prepare(table, args.class_name)

    if args.emit_ddl:
        write_file(Path(args.emit_ddl), render_ddl(table), args.overwrite)

    if bool(args.face_src) != bool(args.impl_src):
        parser.error("--face-src 和 --impl-src 必须同时传入")
    base_package = args.base_package
    if args.face_src:
        face_root = Path(args.face_src)
        impl_root = Path(args.impl_src)
        if not base_package:
            base_package = infer_base_package(face_root, impl_root, args.business_module, table.name)
    elif args.business_module:
        layout = resolve_module_layout(Path(args.repo_root).resolve(), args.business_module, base_package, table.name)
        face_root = layout.face_src
        impl_root = layout.impl_src
        base_package = layout.base_package
    else:
        out = Path(args.output_dir or "generated-ddl-java")
        face_root = out / "face"
        impl_root = out / "impl"
        if not base_package:
            parser.error("无法推断基础包名，请传入 --base-package")

    files = [
        (package_path(impl_root, f"{base_package}.dal.entities") / f"{name}.java", render_entity(base_package, table, name, args.author)),
        (package_path(impl_root, f"{base_package}.dal.mapper") / f"{name}Mapper.java", render_mapper(base_package, table, name, args.author)),
        (package_path(impl_root, f"{base_package}.services.mapstruct") / f"{name}Converter.java", render_converter(base_package, table, name, args.author)),
        (package_path(impl_root, f"{base_package}.services.impl") / f"{name}ServiceImpl.java", render_service_impl(base_package, table, name, args.author)),
        (package_path(face_root, f"{base_package}.model.dto") / f"{name}DTO.java", render_dto(base_package, table, name, args.author)),
        (package_path(face_root, f"{base_package}.model.request") / f"Create{name}Request.java", render_request(base_package, table, name, args.author, "Create")),
        (package_path(face_root, f"{base_package}.model.request") / f"Update{name}Request.java", render_request(base_package, table, name, args.author, "Update")),
        (package_path(face_root, f"{base_package}.model.query") / f"{name}Query.java", render_query(base_package, table, name, args.author)),
        (package_path(face_root, f"{base_package}.services") / f"{name}Service.java", render_service(base_package, table, name, args.author)),
    ]
    for path, content in files:
        write_file(path, content, args.overwrite)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
