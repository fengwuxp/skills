#!/usr/bin/env python3
"""Prepare a repository Markdown document for controlled Yuque publication."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


TARGET_PATTERN = re.compile(
    r'(?P<path><[^<>\n]+>|(?:\\[^\n]|[^\s()<>\\])+)'
    r'''(?P<title>[ \t]+(?:"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|\([^()\n]*\)))?[ \t]*'''
)
REFERENCE_PATTERN = re.compile(r"(?m)^ {0,3}\[([^\]\n]+)\]:[ \t]*([^\n]*)$")
RESOURCE_PATTERN = re.compile(
    r"(?P<definition>^ {0,3}\[[^\]\n]+\]:[^\n]*$)|"
    r"(?P<escape>\\[^\n])|(?P<code>`+)|(?P<nested>!?\[(?=[^\]\n]*\[))|"
    r"(?P<resource>!?\[[^\]\n]*\])|(?P<unsupported_image>!\[)",
    re.MULTILINE,
)
MERMAID_PATTERN = re.compile(r"(?m)^(?:```|~~~)mermaid\s*$")
FENCE_START_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def transform_outside_fences(text: str, transform: Any) -> str:
    result: list[str] = []
    plain: list[str] = []
    fence_char = ""
    fence_length = 0
    for line in text.splitlines(keepends=True):
        if not fence_char:
            opening = FENCE_START_PATTERN.match(line)
            if opening:
                if plain:
                    result.append(transform("".join(plain)))
                    plain.clear()
                marker = opening.group(1)
                fence_char = marker[0]
                fence_length = len(marker)
                result.append(line)
            else:
                plain.append(line)
            continue

        result.append(line)
        if re.fullmatch(
            rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*(?:\r?\n)?",
            line,
        ):
            fence_char = ""
            fence_length = 0
    if plain:
        result.append(transform("".join(plain)))
    return "".join(result)


def reference_key(label: str) -> str:
    return " ".join(label.split()).casefold()


def parse_target(text: str, start: int = 0) -> tuple[str, str, int]:
    while text[start:start + 1] in (" ", "\t"):
        start += 1
    match = TARGET_PATTERN.match(text, start)
    if match is None:
        raise ValueError("不支持的 Markdown 资源目标；请使用单行目标和可选 title")
    target = match.group("path")
    if target.startswith("<"):
        target = target[1:-1]
    target = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])", r"\1", target)
    return target, match.group("title") or "", match.end()


def prepare_projection(
    source_path: Path, source_version: str, link_map: dict[str, str]
) -> tuple[str, dict[str, Any]]:
    source_bytes = source_path.read_bytes()
    source = source_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    images: list[dict[str, str]] = []
    missing_images: list[dict[str, str]] = []
    mapped_links: list[dict[str, str]] = []
    unresolved_links: list[dict[str, str]] = []

    references: dict[str, tuple[str, str]] = {}

    def replace_image(label: str, target: str, original: str) -> str:
        alt = label.strip() or "未命名图片"
        if target.startswith(("http://", "https://", "data:")):
            return original
        image = {"alt": alt, "path": target}
        images.append(image)
        local_target = target.split("#", 1)[0].split("?", 1)[0]
        if not (source_path.parent / local_target).is_file():
            missing_images.append(image)
        return f"【待插图：{alt}】"

    def replace_link(label: str, target: str, title: str, original: str) -> str:
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return original
        mapped = link_map.get(target) or link_map.get(target.split("#", 1)[0])
        if mapped:
            mapped_links.append({"label": label, "source": target, "target": mapped})
            return f"[{label}]({mapped}{title})"
        unresolved_links.append({"label": label, "target": target})
        return label

    def project_text(text: str, collect_only: bool = False) -> str:
        parts: list[str] = []
        start = 0
        for match in RESOURCE_PATTERN.finditer(text):
            if match.start() < start:
                continue
            if match.lastgroup == "escape":
                continue
            if match.lastgroup == "definition":
                definition = REFERENCE_PATTERN.fullmatch(match.group())
                target, title, end = parse_target(definition.group(2))
                if end != len(definition.group(2)):
                    raise ValueError("不支持的 Markdown 引用定义；请使用单行目标和可选 title")
                references.setdefault(reference_key(definition.group(1)), (target, title))
                continue
            if match.lastgroup == "code":
                # 按原始位置跳过整段代码，不切断外层链接标签或 title。
                closing = re.search(rf"(?<!`){match.group()}(?!`)", text[match.end():])
                if closing is not None:
                    end = match.end() + closing.end()
                    parts.append(text[start:end])
                    start = end
                continue
            if match.lastgroup == "nested":
                # 普通矩阵或方括号说明不属于资源，只有资源目标才触发拒绝。
                depth = 1
                end = match.end()
                while end < len(text) and depth:
                    char = text[end]
                    if char == "\\":
                        end += 2
                        continue
                    if char == "[":
                        depth += 1
                    elif char == "]":
                        depth -= 1
                    end += 1
                has_target = text[end:end + 1] in ("(", "[")
                contains_link = re.search(r"\]\s*\(", text[match.end():end])
                if match.group().startswith("!") or has_target or contains_link:
                    raise ValueError("不支持的嵌套 Markdown 资源标签；请改为普通单行标签")
                parts.append(text[start:end])
                start = end
                continue
            if match.lastgroup != "resource":
                raise ValueError("不支持的嵌套或跨行 Markdown 资源标签；请改为普通单行标签")
            original = match.group()
            is_image = original.startswith("!")
            label = original[2:-1] if is_image else original[1:-1]
            end = match.end()
            if text[end:end + 1] == "(":
                target, title, end = parse_target(text, end + 1)
                if text[end:end + 1] != ")":
                    raise ValueError("不支持的 Markdown 资源目标；含括号的路径请用尖括号包围")
                end += 1
            else:
                reference = re.match(r"\[([^\]\n]*)\]", text[end:])
                key = reference_key((reference.group(1) or label) if reference else label)
                if reference:
                    end += reference.end()
                if collect_only or key not in references:
                    if is_image and not collect_only:
                        raise ValueError(f"Markdown 图片引用未定义：{key}")
                    parts.append(text[start:end])
                    start = end
                    continue
                target, title = references[key]
            original = text[match.start():end]
            if collect_only:
                replacement = original
            elif is_image:
                replacement = replace_image(label, target, original)
            else:
                replacement = replace_link(label, target, title, original)
            parts.extend((text[start:match.start()], replacement))
            start = end
        parts.append(text[start:])
        return "".join(parts)

    transform_outside_fences(source, lambda text: project_text(text, collect_only=True))
    projection = transform_outside_fences(source, project_text)
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    marker = (
        "> 语雀协作副本；本地源文件为权威。"
        f"SourceVersion={source_version}；SourceSHA256={source_sha256}。"
    )
    lines = projection.splitlines()
    if lines and lines[0].startswith("# "):
        lines[1:1] = ["", marker]
    else:
        lines[0:0] = [marker, ""]
    projection = "\n".join(lines) + ("\n" if source.endswith("\n") else "")

    manifest = {
        "source_path": str(source_path),
        "source_version": source_version,
        "source_sha256": source_sha256,
        "mermaid_blocks": len(MERMAID_PATTERN.findall(source)),
        "images": images,
        "missing_images": missing_images,
        "mapped_local_links": mapped_links,
        "unresolved_local_links": unresolved_links,
    }
    return projection, manifest


def load_link_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def same_file_identity(left: Path, right: Path) -> bool:
    if left.resolve() == right.resolve():
        return True
    try:
        return left.samefile(right)
    except FileNotFoundError:
        return False


def validate_output_paths(
    source_path: Path, link_map_path: Path | None, output_dir: Path
) -> tuple[Path, Path]:
    projection_path = output_dir / "projection.md"
    manifest_path = output_dir / "manifest.json"
    for output_path in (projection_path, manifest_path):
        for input_path in (source_path, link_map_path):
            if input_path is not None and same_file_identity(output_path, input_path):
                raise ValueError(
                    f"output path conflicts with input: {output_path}"
                )
    if same_file_identity(projection_path, manifest_path):
        raise ValueError("output path conflicts: projection and manifest are aliases")
    return projection_path, manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-version", required=True)
    parser.add_argument("--link-map", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        projection_path, manifest_path = validate_output_paths(
            args.source, args.link_map, args.output_dir
        )
        projection, manifest = prepare_projection(
            args.source, args.source_version, load_link_map(args.link_map)
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        projection_path.write_text(projection, encoding="utf-8")
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        print(f"FAIL output path or input: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "projection": str(projection_path),
                "manifest": str(manifest_path),
                "source_sha256": manifest["source_sha256"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
