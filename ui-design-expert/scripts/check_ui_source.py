#!/usr/bin/env python3
"""Find a few high-confidence UI source anti-patterns.

The checker reads explicit local paths, writes nothing, and does not access the network.
It is intentionally not a parser and does not prove usability, semantics, or WCAG conformance.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


SOURCE_SUFFIXES = {".css", ".htm", ".html", ".jsx", ".less", ".sass", ".scss", ".svelte", ".tsx", ".vue"}
IGNORED_DIRS = {".git", ".next", "build", "coverage", "dist", "node_modules"}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    message: str


LINE_RULES = (
    (
        "zoom-disabled",
        re.compile(r'<meta\b(?=[^>]*\bname\s*=\s*["\']viewport["\'])[^>]*(?:user-scalable\s*=\s*(?:no|0)|maximum-scale\s*=\s*1(?:\.0+)?)', re.I),
        "Do not disable browser zoom in the viewport declaration.",
    ),
    (
        "transition-all",
        re.compile(r"\btransition-all\b|\btransition\s*:\s*all\b", re.I),
        "Transition named properties instead of every property.",
    ),
    (
        "non-semantic-click",
        re.compile(r"<(?:div|span)\b[^>]*\sonclick\s*=", re.I),
        "Use a semantic interactive element instead of a clickable div or span.",
    ),
    (
        "paste-blocked",
        re.compile(r"\sonpaste\s*=.*\bpreventdefault\s*\(", re.I),
        "Do not block paste in form controls.",
    ),
)

BLOCK_COMMENT_PATTERN = re.compile(r"/\*.*?\*/|<!--.*?-->", re.DOTALL)
LINE_COMMENT_PATTERN = re.compile(r"(?m)(?<!:)//.*$")
PROTOTYPE_ID_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
PROTOTYPE_DATA_TARGET_PATTERN = re.compile(
    r"\[(?P<name>data-[a-z0-9-]+)\s*=\s*(?P<quote>['\"])(?P<value>[A-Za-z0-9_.:-]+)(?P=quote)\]"
)


class PrototypeAnnotationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.mode: str | None = None
        self.ids: set[str] = set()
        self.id_counts: dict[str, int] = {}
        self.data_attributes: set[tuple[str, str]] = set()
        self.review_toggle = False
        self.review_toggle_names: list[tuple[str, str]] = []
        self.review_panel = False
        self.review_panel_names: list[tuple[str, str]] = []
        self.annotation_script_found = False
        self.annotation_script_parts: list[str] = []
        self._in_annotation_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.casefold(): value or "" for name, value in attrs}
        if tag.casefold() == "html":
            self.mode = values.get("data-prototype-mode")
        if element_id := values.get("id"):
            self.ids.add(element_id)
            self.id_counts[element_id] = self.id_counts.get(element_id, 0) + 1
        self.data_attributes.update(
            (name, value)
            for name, value in values.items()
            if name.startswith("data-") and value
        )
        if "data-prototype-review-toggle" in values:
            self.review_toggle = True
            self.review_toggle_names.append(
                (values.get("aria-label", ""), values.get("aria-labelledby", ""))
            )
        if values.get("id") == "prototype-review-panel":
            self.review_panel = True
            self.review_panel_names.append(
                (values.get("aria-label", ""), values.get("aria-labelledby", ""))
            )
        if (
            tag.casefold() == "script"
            and values.get("id") == "prototype-annotations"
            and values.get("type").casefold() == "application/json"
        ):
            self.annotation_script_found = True
            self._in_annotation_script = True

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "script":
            self._in_annotation_script = False

    def handle_data(self, data: str) -> None:
        if self._in_annotation_script:
            self.annotation_script_parts.append(data)


def mask_comments(text: str) -> str:
    masked = BLOCK_COMMENT_PATTERN.sub(lambda match: re.sub(r"[^\n]", " ", match.group()), text)
    return LINE_COMMENT_PATTERN.sub(lambda match: " " * len(match.group()), masked)


# ponytail: line-level matching stays dependency-free; use language parsers if false results become material.
def scan_text(text: str, path: Path = Path("<text>")) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(mask_comments(text).splitlines(), start=1):
        for rule, pattern, message in LINE_RULES:
            if pattern.search(line):
                findings.append(Finding(path, line_number, rule, message))
    return findings


def prototype_annotation_findings(text: str, path: Path = Path("<text>")) -> list[Finding]:
    parser = PrototypeAnnotationParser()
    parser.feed(text)
    findings: list[Finding] = []

    def add(rule: str, message: str) -> None:
        findings.append(Finding(path, 1, rule, message))

    def has_accessible_name(names: list[tuple[str, str]]) -> bool:
        return any(
            aria_label.strip()
            or any(parser.id_counts.get(reference) == 1 for reference in aria_labelledby.split())
            for aria_label, aria_labelledby in names
        )

    if parser.mode != "experience":
        add("prototype-default-mode", "Standalone HTML prototypes must default to experience mode.")
    if not parser.review_toggle or not has_accessible_name(parser.review_toggle_names):
        add("prototype-review-toggle", "Provide a named product-review toggle.")
    if not parser.review_panel or not has_accessible_name(parser.review_panel_names):
        add("prototype-review-panel", "Provide a named product-review panel.")
    if not parser.annotation_script_found:
        add("prototype-annotation-json", "Embed prototype annotations as application/json.")
        return findings

    try:
        payload = json.loads("".join(parser.annotation_script_parts))
    except (json.JSONDecodeError, TypeError):
        add("prototype-annotation-json", "Prototype annotation JSON is invalid.")
        return findings
    revision = payload.get("revision") if isinstance(payload, dict) else None
    if not isinstance(revision, str) or not revision.strip():
        add("prototype-annotation-revision", "Prototype annotation JSON requires a revision.")
    annotations = payload.get("annotations") if isinstance(payload, dict) else None
    if not isinstance(annotations, list) or not annotations:
        add("prototype-annotation-json", "Prototype annotation JSON requires annotations.")
        return findings

    annotation_ids = [row.get("id") for row in annotations if isinstance(row, dict)]
    if len(annotation_ids) != len(annotations) or any(
        not isinstance(value, str) or not PROTOTYPE_ID_PATTERN.fullmatch(value)
        for value in annotation_ids
    ) or len(annotation_ids) != len(set(annotation_ids)):
        add("prototype-annotation-id", "Prototype annotation IDs must be unique stable IDs.")

    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        target = annotation.get("target")
        target_resolves = False
        if isinstance(target, str) and target.startswith("#"):
            target_resolves = bool(
                PROTOTYPE_ID_PATTERN.fullmatch(target[1:])
                and parser.id_counts.get(target[1:]) == 1
            )
        elif isinstance(target, str) and (match := PROTOTYPE_DATA_TARGET_PATTERN.fullmatch(target)):
            target_resolves = (match.group("name"), match.group("value")) in parser.data_attributes
        if not target_resolves:
            add("prototype-annotation-target", "Every prototype annotation target must resolve in the HTML.")
        if not isinstance(annotation.get("content"), str) or not annotation["content"].strip():
            add("prototype-annotation-content", "Every prototype annotation requires display content.")
        if annotation.get("status") not in {"confirmed", "inferred", "pending"}:
            add("prototype-annotation-status", "Prototype annotation status is invalid.")
    return findings


def scan_file(path: Path, require_prototype_annotations: bool = False) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    findings = scan_text(text, path)
    if require_prototype_annotations and path.suffix.lower() in {".htm", ".html"}:
        findings.extend(prototype_annotation_findings(text, path))
    return findings


def iter_source_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in SOURCE_SUFFIXES:
                yield path
            continue
        for candidate in path.rglob("*"):
            if any(part in IGNORED_DIRS for part in candidate.parts):
                continue
            if candidate.is_file() and candidate.suffix.lower() in SOURCE_SUFFIXES:
                yield candidate


def self_test() -> int:
    fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    valid = scan_file(fixtures / "source-valid.tsx")
    invalid = {finding.rule for finding in scan_file(fixtures / "source-invalid.tsx")}
    expected = {"zoom-disabled", "transition-all", "non-semantic-click", "paste-blocked"}
    if valid or invalid != expected:
        print(f"FAIL UI source checker: valid={valid}, invalid={sorted(invalid)}")
        return 1
    valid_prototype_path = fixtures / "prototype-annotations-valid.html"
    valid_prototype_text = valid_prototype_path.read_text(encoding="utf-8")
    valid_prototype = scan_file(valid_prototype_path, True)
    invalid_prototype = {
        finding.rule
        for finding in scan_file(fixtures / "prototype-annotations-invalid.html", True)
    }
    expected_prototype = {
        "prototype-default-mode",
        "prototype-review-toggle",
        "prototype-review-panel",
        "prototype-annotation-revision",
        "prototype-annotation-id",
        "prototype-annotation-target",
        "prototype-annotation-content",
        "prototype-annotation-status",
    }
    if valid_prototype or invalid_prototype != expected_prototype:
        print(
            "FAIL prototype annotation checker: "
            f"valid={valid_prototype}, invalid={sorted(invalid_prototype)}"
        )
        return 1
    duplicate_dom_id = valid_prototype_text.replace(
        '<button id="claim-button" type="button">领取权益</button>',
        '<button id="claim-button" type="button">领取权益</button><span id="claim-button"></span>',
        1,
    )
    if "prototype-annotation-target" not in {
        finding.rule for finding in prototype_annotation_findings(duplicate_dom_id)
    }:
        print("FAIL duplicate DOM ID annotation target unexpectedly passed")
        return 1
    invalid_accessible_names = (
        valid_prototype_text
        .replace('aria-label="查看产品标注"', 'aria-label="   "', 1)
        .replace('aria-label="产品标注"', 'aria-labelledby="missing-label"', 1)
    )
    accessible_name_rules = {
        finding.rule for finding in prototype_annotation_findings(invalid_accessible_names)
    }
    if not {"prototype-review-toggle", "prototype-review-panel"}.issubset(
        accessible_name_rules
    ):
        print("FAIL invalid accessible names unexpectedly passed")
        return 1
    non_string_revision = valid_prototype_text.replace(
        '"revision": "r1"',
        '"revision": ["r1"]',
        1,
    )
    if "prototype-annotation-revision" not in {
        finding.rule for finding in prototype_annotation_findings(non_string_revision)
    }:
        print("FAIL non-string prototype revision unexpectedly passed")
        return 1
    single_quoted_target = valid_prototype_text.replace(
        '[data-carrier-id=\\"claim-success\\"]',
        "[data-carrier-id='claim-success']",
        1,
    )
    if single_quoted_target == valid_prototype_text:
        print("FAIL single-quoted prototype target fixture setup did not match")
        return 1
    if prototype_annotation_findings(single_quoted_target):
        print("FAIL valid single-quoted prototype target failed")
        return 1
    malformed_json = """
    <html data-prototype-mode="experience"><body>
      <button data-prototype-review-toggle aria-label="审阅" aria-controls="prototype-review-panel"></button>
      <aside id="prototype-review-panel" aria-label="产品标注"></aside>
      <script id="prototype-annotations" type="application/json">{</script>
    </body></html>
    """
    if {finding.rule for finding in prototype_annotation_findings(malformed_json)} != {
        "prototype-annotation-json"
    }:
        print("FAIL malformed prototype annotation JSON unexpectedly passed")
        return 1
    print("UI source checker self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="UI source files or directories")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--require-prototype-annotations",
        action="store_true",
        help="require the standalone HTML prototype annotation carrier",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.paths:
        parser.error("provide at least one file or directory")
    missing = [path for path in args.paths if not path.exists()]
    if missing:
        for path in missing:
            print(f"ERROR path does not exist: {path}", file=sys.stderr)
        return 2

    try:
        source_files = list(iter_source_files(args.paths))
        if args.require_prototype_annotations and not any(
            path.suffix.lower() in {".htm", ".html"} for path in source_files
        ):
            print("ERROR no HTML prototype found", file=sys.stderr)
            return 2
        findings = [
            finding
            for path in source_files
            for finding in scan_file(path, args.require_prototype_annotations)
        ]
    except (OSError, UnicodeError) as error:
        print(f"ERROR unable to read UI source: {error}", file=sys.stderr)
        return 2

    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.rule} - {finding.message}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
