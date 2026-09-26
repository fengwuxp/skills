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


IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
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


def prepare_projection(
    source_path: Path, source_version: str, link_map: dict[str, str]
) -> tuple[str, dict[str, Any]]:
    source = source_path.read_text(encoding="utf-8")
    images: list[dict[str, str]] = []
    missing_images: list[dict[str, str]] = []
    mapped_links: list[dict[str, str]] = []
    unresolved_links: list[dict[str, str]] = []

    def replace_image(match: re.Match[str]) -> str:
        alt = match.group(1).strip() or "未命名图片"
        target = match.group(2).strip()
        if target.startswith(("http://", "https://", "data:")):
            return match.group(0)
        image = {"alt": alt, "path": target}
        images.append(image)
        local_target = target.split("#", 1)[0].split("?", 1)[0]
        if not (source_path.parent / local_target).is_file():
            missing_images.append(image)
        return f"【待插图：{alt}】"

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)
        mapped = link_map.get(target) or link_map.get(target.split("#", 1)[0])
        if mapped:
            mapped_links.append({"label": label, "source": target, "target": mapped})
            return f"[{label}]({mapped})"
        unresolved_links.append({"label": label, "target": target})
        return label

    projection = transform_outside_fences(
        source,
        lambda text: LINK_PATTERN.sub(
            replace_link,
            IMAGE_PATTERN.sub(replace_image, text),
        ),
    )
    source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
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
