#!/usr/bin/env python3
import argparse
import dataclasses
import datetime as dt
import hashlib
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
    raise ValueError("Parentheses are not balanced")


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
    raise ValueError(f"CREATE TABLE for '{table_name}' was not found")


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
        raise ValueError("No CREATE TABLE statement found")
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


def snake_to_pascal(name: str) -> str:
    return "".join(part[:1].upper() + part[1:].lower() for part in re.split(r"[_\-\s]+", name) if part)


def snake_to_camel(name: str) -> str:
    pascal = snake_to_pascal(name)
    return pascal[:1].lower() + pascal[1:] if pascal else name


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
        raise ValueError(f"Base package is ambiguous. Choose one of: {options}")
    if business_module:
        module_name = business_module.split("/")[-1]
        base = re.sub(r"-(face|impl)$", "", module_name)
        return f"com.capte.nobe.{kebab_to_camel(base)}"
    raise ValueError("Unable to infer base package; pass --base-package")


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
            raise ValueError(f"Business module '{business_module}' is ambiguous. Choose one of: {names}")
        for _, face_module, impl_module in pairs:
            face_src = face_module / "src/main/java"
            impl_src = impl_module / "src/main/java"
            layouts.append(ModuleLayout(face_src, impl_src, base_package or infer_base_package(face_src, impl_src, business_module, table_name)))
    if len(layouts) == 1:
        return layouts[0]
    if len(layouts) > 1:
        names = ", ".join(str(layout.face_src.parent.parent.parent.name) for layout in layouts)
        raise ValueError(f"Business module '{business_module}' is ambiguous. Choose a specific module: {names}")
    raise ValueError(f"Unable to resolve face/impl modules for business module '{business_module}'")


def field_name_from_column(column_name: str) -> str:
    if column_name == "u_id":
        return "uid"
    if column_name.startswith("is_") and len(column_name) > 3:
        result = snake_to_camel(column_name[3:])
    else:
        result = snake_to_camel(column_name)
    if result in RESERVED:
        return result + "Value"
    return result


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
        raise ValueError(f"Unable to parse SQL type from: {rest}")
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
        column.java_name = field_name_from_column(column.name)
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


def words_from_identifier(value: str) -> str:
    value = re.sub(r"^t_", "", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    words = [word for word in value.split() if word]
    return " ".join(words) if words else value


def human_name(name: str) -> str:
    words = words_from_identifier(name)
    return words[:1].upper() + words[1:] if words else name


def lower_human_name(name: str) -> str:
    words = words_from_identifier(name)
    return words.lower() if words else name


def class_desc(name: str) -> str:
    return human_name(name)


def table_desc(table: Table, name: str) -> str:
    return table.comment.strip() if table.comment and table.comment.strip() else class_desc(name)


def field_desc(column: Column) -> str:
    return column.comment.strip() if column.comment and column.comment.strip() else human_name(column.java_name or column.name)


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
    lines.append(f" * {table_desc(table, name)} entity.")
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
            lines.append(java_doc(column.comment.strip() + ".", "    ").rstrip())
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
 * {comment} Mapper.
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
    lines.append(f" * {table_desc(table, name)} DTO.")
    lines.append(" *")
    lines.append(f" * @author {author}")
    lines.append(f" * @date {today}")
    lines.append(" */")
    lines.extend(["@Data", f"public class {name}DTO {{", ""])
    for column in table.columns:
        description = column.comment.strip() if column.comment and column.comment.strip() else ""
        if description:
            lines.append(java_doc(description + ".", "    ").rstrip())
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
    lines.extend(["", "/**", f" * {table_desc(table, name)} {kind.lower()} request.", " *", f" * @author {author}", f" * @date {today}", " */", "@Data", f"public class {class_name} {{", ""])
    for column in columns:
        description = column.comment.strip() if column.comment and column.comment.strip() else ""
        if description:
            lines.append(java_doc(description + ".", "    ").rstrip())
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
    lines.extend(["", "/**", f" * {table_desc(table, name)} query.", " *", f" * @author {author}", f" * @date {today}", " */", "@Data", f"public class {name}Query {{", ""])
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


def render_converter(base_package: str, name: str, author: str) -> str:
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
 * {name} Converter.
 *
 * @author {author}
 * @date {today}
 */
@Mapper
public interface {name}Converter {{

    {name}Converter INSTANCE = Mappers.getMapper({name}Converter.class);

    /**
     * Convert DTO to {name} entity.
     *
     * @param dto source DTO
     * @return converted entity
     */
    {name} convertToEntity({name}DTO dto);

    /**
     * Convert create request to {name} entity.
     *
     * @param request create request
     * @return converted entity
     */
    {name} convertToEntity(Create{name}Request request);

    /**
     * Convert update request to {name} entity.
     *
     * @param request update request
     * @return converted entity
     */
    {name} convertToEntity(Update{name}Request request);

    /**
     * Convert {name} entity to DTO.
     *
     * @param entity source entity
     * @return converted DTO
     */
    {name}DTO convertToDTO({name} entity);

    /**
     * Convert {name} entity list to DTO list.
     *
     * @param entities source entity list
     * @return converted DTO list
     */
    List<{name}DTO> convertToDTOList(List<{name}> entities);
}}
"""


def render_service(base_package: str, table: Table, name: str, author: str) -> str:
    desc = class_desc(name)
    lower_desc = lower_human_name(name)
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
 * {desc} service.
 *
 * @author {author}
 * @date {today}
 */
public interface {name}Service {{

    /**
     * Create {lower_desc}.
     *
     * @param request create request
     * @return {lower_desc} ID
     */
    Long create{name}(@NonNull Create{name}Request request);

    /**
     * Update {lower_desc}.
     *
     * @param request update request
     */
    void update{name}(@NonNull Update{name}Request request);

    /**
     * Delete {lower_desc} by ID.
     *
     * @param id {lower_desc} ID
     */
    default void delete{name}ById(@NonNull Long id) {{
        delete{name}ByIds(id);
    }}

    /**
     * Delete {lower_desc} by IDs.
     *
     * @param ids {lower_desc} IDs
     */
    void delete{name}ByIds(@NonNull Long... ids);

    /**
     * Query {lower_desc} by ID.
     *
     * @param id {lower_desc} ID
     * @return {name}DTO
     */
    {name}DTO query{name}ById(@NonNull Long id);

    /**
     * Query {lower_desc} page.
     *
     * @param query query condition
     * @param options query options
     * @return {lower_desc} page result
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
    var = name[:1].lower() + name[1:]
    desc = class_desc(name)
    lower_desc = lower_human_name(name)
    today = dt.date.today().isoformat()
    deleted = next((c for c in table.columns if c.column_annotation and "isLogicDelete" in c.column_annotation), None)
    deleted_check = ""
    if deleted:
        getter = "get" + deleted.java_name[:1].upper() + deleted.java_name[1:] + "()"
        deleted_check = f'\n        AssertUtils.isFalse(Boolean.TRUE.equals(result.{getter}), "{desc} does not exist or has been deleted");'
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
 * {desc} service implementation.
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
     * Create {lower_desc}.
     *
     * @param request create request
     * @return {lower_desc} ID
     */
    @Override
    public Long create{name}(@NonNull Create{name}Request request) {{
        AssertUtils.notNull(request, "argument request must not null");
        {name} entity = {name}Converter.INSTANCE.convertToEntity(request);
        AssertUtils.isTrue({var}Mapper.insertSelective(entity) > 0, "Failed to create {lower_desc}");
        return entity.getId();
    }}

    /**
     * Update {lower_desc}.
     *
     * @param request update request
     */
    @Override
    public void update{name}(@NonNull Update{name}Request request) {{
        AssertUtils.notNull(request, "argument request must not null");
        find{name}(request.getId());
        {name} entity = {name}Converter.INSTANCE.convertToEntity(request);
        AssertUtils.isTrue({var}Mapper.update(entity) == 1, "Failed to update {lower_desc}");
    }}

    /**
     * Delete {lower_desc} by IDs.
     *
     * @param ids {lower_desc} IDs
     */
    @Override
    public void delete{name}ByIds(@NonNull Long... ids) {{
        AssertUtils.notEmpty(ids, "argument ids must not empty");
        int total = {var}Mapper.deleteBatchByIds(Arrays.asList(ids));
        AssertUtils.isTrue(total == ids.length, "Failed to delete {lower_desc}");
    }}

    /**
     * Query {lower_desc} by ID.
     *
     * @param id {lower_desc} ID
     * @return {name}DTO
     */
    @Override
    public {name}DTO query{name}ById(@NonNull Long id) {{
        AssertUtils.notNull(id, "argument id must not null");
        return {name}Converter.INSTANCE.convertToDTO(find{name}(id));
    }}

    /**
     * Query {lower_desc} page.
     *
     * @param query query condition
     * @param options query options
     * @return {lower_desc} page result
     */
    @Override
    @NonNull
    public WindPagination<{name}DTO> query{name}s(@NonNull {name}Query query, @NonNull WindQuery<? extends QueryOrderField> options) {{
        AssertUtils.notNull(query, "argument query must not null");
        AssertUtils.notNull(options, "argument options must not null");
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
     * Find {lower_desc} entity by ID.
     *
     * @param id {lower_desc} ID
     * @return {name} entity
     */
    private {name} find{name}(@NonNull Long id) {{
        AssertUtils.notNull(id, "argument id must not null");
        {name} result = {var}Mapper.selectOneById(id);
        AssertUtils.notNull(result, "{desc} does not exist");{deleted_check}
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
    parser = argparse.ArgumentParser(description="Generate Nobe Java scaffold from CREATE TABLE DDL")
    parser.add_argument("--ddl-file", help="DDL file path. Reads stdin when omitted.")
    parser.add_argument("--schema-file", help="Schema file containing multiple CREATE TABLE statements")
    parser.add_argument("--table-name", help="Table name to extract from --schema-file")
    parser.add_argument("--business-module", help="Business module path/name, for example user-domain or user-domain/user-face")
    parser.add_argument("--repo-root", default=".", help="Repository root used with --business-module")
    parser.add_argument("--base-package", help="Base package, for example com.capte.nobe.kyc")
    parser.add_argument("--author", default=os.environ.get("USER", "codex"))
    parser.add_argument("--class-name")
    parser.add_argument("--output-dir", help="Review output directory. Used when face-src/impl-src are omitted.")
    parser.add_argument("--face-src", help="Face module src/main/java root")
    parser.add_argument("--impl-src", help="Impl module src/main/java root")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.schema_file:
        if not args.table_name:
            parser.error("--table-name is required with --schema-file")
        ddl = extract_create_table(Path(args.schema_file).read_text(encoding="utf-8"), args.table_name)
    elif args.ddl_file:
        ddl = Path(args.ddl_file).read_text(encoding="utf-8")
    else:
        ddl = sys.stdin.read()
    table = parse_ddl(ddl)
    name = prepare(table, args.class_name)

    if bool(args.face_src) != bool(args.impl_src):
        parser.error("--face-src and --impl-src must be supplied together")
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
            parser.error("--base-package is required when module roots cannot be inferred")

    files = [
        (package_path(impl_root, f"{base_package}.dal.entities") / f"{name}.java", render_entity(base_package, table, name, args.author)),
        (package_path(impl_root, f"{base_package}.dal.mapper") / f"{name}Mapper.java", render_mapper(base_package, table, name, args.author)),
        (package_path(impl_root, f"{base_package}.services.mapstruct") / f"{name}Converter.java", render_converter(base_package, name, args.author)),
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
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
