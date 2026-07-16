#!/usr/bin/env python3
"""Check explicit background and color formatting in document artifacts.

The checker reads one local Markdown, HTML, text, or DOCX file. It does not
modify the input, access the network, or inspect PDF pixels. Self-test mode
writes temporary files only and removes them on exit.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree


TEXT_SUFFIXES = {".md", ".markdown", ".html", ".htm", ".txt"}
STYLE_ATTRIBUTE = re.compile(r"\bstyle\s*=\s*(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
BACKGROUND_PROPERTY = re.compile(r"(?:^|[;{])\s*background(?:-[a-z-]+)?\s*:", re.IGNORECASE)
COLOR_PROPERTY = re.compile(r"(?:^|[;{])\s*color\s*:", re.IGNORECASE)
BGCOLOR_ATTRIBUTE = re.compile(r"\bbgcolor\s*=", re.IGNORECASE)
FONT_COLOR_ATTRIBUTE = re.compile(r"<font\b[^>]*\bcolor\s*=", re.IGNORECASE)
MARK_TAG = re.compile(r"</?mark\b", re.IGNORECASE)
FENCED_CODE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]+`")

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
STORY_PART = re.compile(r"word/(?:document|header\d+|footer\d+|footnotes|endnotes|comments)\.xml$")
NO_FILL = {"", "auto", "nil", "none"}
DEFAULT_TEXT_COLORS = {"", "auto", "000", "000000"}


def strip_code(text: str) -> str:
    return INLINE_CODE.sub("", FENCED_CODE.sub("", text))


def text_style_violations(text: str) -> list[str]:
    visible = strip_code(text)
    violations: set[str] = set()
    style_fragments = [match.group(2) for match in STYLE_ATTRIBUTE.finditer(visible)]
    style_fragments.extend(match.group(1) for match in STYLE_BLOCK.finditer(visible))
    for style in style_fragments:
        if BACKGROUND_PROPERTY.search(style):
            violations.add("background_style")
        if COLOR_PROPERTY.search(style):
            violations.add("foreground_color")
    if BGCOLOR_ATTRIBUTE.search(visible):
        violations.add("background_attribute")
    if FONT_COLOR_ATTRIBUTE.search(visible):
        violations.add("foreground_color")
    if MARK_TAG.search(visible):
        violations.add("highlight_tag")
    return sorted(violations)


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def attribute(element: ElementTree.Element, name: str) -> str:
    for key, value in element.attrib.items():
        if local_name(key) == name:
            return value
    return ""


def xml_style_violations(root: ElementTree.Element) -> set[str]:
    violations: set[str] = set()
    for element in root.iter():
        name = local_name(element.tag)
        if name == "shd":
            fill = attribute(element, "fill").casefold()
            pattern = attribute(element, "val").casefold()
            if fill not in NO_FILL or pattern not in {"", "clear", "nil", "none"}:
                violations.add("docx_shading")
        elif name == "highlight" and attribute(element, "val").casefold() not in {"", "none"}:
            violations.add("docx_highlight")
        elif name == "color":
            value = attribute(element, "val").casefold()
            if value not in DEFAULT_TEXT_COLORS or attribute(element, "themeColor"):
                violations.add("docx_foreground_color")
        elif name == "solidFill":
            violations.add("docx_solid_fill")
        if attribute(element, "fillcolor").casefold() not in NO_FILL:
            violations.add("docx_shape_fill")
    return violations


def docx_style_violations(path: Path) -> list[str]:
    with zipfile.ZipFile(path) as package:
        story_roots: list[ElementTree.Element] = []
        used_styles: set[str] = set()
        violations: set[str] = set()
        for name in package.namelist():
            if not STORY_PART.fullmatch(name):
                continue
            root = ElementTree.fromstring(package.read(name))
            story_roots.append(root)
            violations.update(xml_style_violations(root))
            for element in root.iter():
                if local_name(element.tag) in {"pStyle", "rStyle", "tblStyle"}:
                    style_id = attribute(element, "val")
                    if style_id:
                        used_styles.add(style_id)

        if "word/styles.xml" in package.namelist():
            styles_root = ElementTree.fromstring(package.read("word/styles.xml"))
            for defaults in styles_root.findall(f".//{W_NS}docDefaults"):
                violations.update(xml_style_violations(defaults))
            styles = {
                attribute(style, "styleId"): style
                for style in styles_root.findall(f"{W_NS}style")
                if attribute(style, "styleId")
            }
            pending = list(used_styles)
            checked: set[str] = set()
            while pending:
                style_id = pending.pop()
                if style_id in checked or style_id not in styles:
                    continue
                checked.add(style_id)
                style = styles[style_id]
                violations.update(xml_style_violations(style))
                based_on = style.find(f"{W_NS}basedOn")
                if based_on is not None and attribute(based_on, "val"):
                    pending.append(attribute(based_on, "val"))
        if not story_roots:
            raise ValueError("DOCX has no readable document story")
    return sorted(violations)


def style_violations(path: Path) -> list[str]:
    suffix = path.suffix.casefold()
    if suffix in TEXT_SUFFIXES:
        return text_style_violations(path.read_text(encoding="utf-8"))
    if suffix == ".docx":
        return docx_style_violations(path)
    raise ValueError(f"unsupported format {suffix or '<none>'}; render inspection is required")


def write_test_docx(path: Path, run_properties: str = "", styles: str = "") -> None:
    document = (
        f'<w:document xmlns:w="{W_NS[1:-1]}"><w:body><w:p><w:r><w:rPr>{run_properties}</w:rPr>'
        '<w:t>Sample</w:t></w:r></w:p></w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("word/document.xml", document)
        if styles:
            package.writestr("word/styles.xml", styles)


def run_self_test() -> int:
    failures: list[str] = []
    if text_style_violations("# Title\n**Important concept**"):
        failures.append("clean Markdown was rejected")
    if text_style_violations("```css\nmark { background: yellow; }\n```"):
        failures.append("code sample was treated as document formatting")
    expected_text = {"background_style", "foreground_color", "highlight_tag"}
    actual_text = set(text_style_violations('<mark style="background-color: yellow; color: red">x</mark>'))
    if not expected_text.issubset(actual_text):
        failures.append("HTML background or color formatting was not detected")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        clean = root / "clean.docx"
        shaded = root / "shaded.docx"
        write_test_docx(clean, "<w:b/>")
        write_test_docx(shaded, '<w:shd w:val="clear" w:fill="FFFF00"/><w:highlight w:val="yellow"/>')
        if docx_style_violations(clean):
            failures.append("clean DOCX was rejected")
        expected_docx = {"docx_shading", "docx_highlight"}
        if not expected_docx.issubset(docx_style_violations(shaded)):
            failures.append("DOCX shading or highlight was not detected")

    if failures:
        print("FAIL document style self-test", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("OK document style self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="检查文档产物中的显式背景色、高亮和文字颜色")
    parser.add_argument("--file", help="待检查的 Markdown、HTML、文本或 DOCX 文件")
    parser.add_argument("--self-test", action="store_true", help="运行内置正反例自测")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if not args.file:
        parser.error("--file is required unless --self-test is used")

    path = Path(args.file)
    try:
        violations = style_violations(path)
    except (FileNotFoundError, UnicodeDecodeError, ValueError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        print(f"ERROR document style check: {error}", file=sys.stderr)
        return 2
    if violations:
        print("FAIL document style check: " + ", ".join(violations), file=sys.stderr)
        return 1
    print(f"OK document style check: file={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
