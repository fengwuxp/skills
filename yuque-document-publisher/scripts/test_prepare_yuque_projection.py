#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_yuque_projection.py"
SPEC = importlib.util.spec_from_file_location("prepare_yuque_projection", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load Yuque projection script")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class YuqueProjectionTests(unittest.TestCase):
    def test_preserves_inline_code_and_escaped_resource_syntax(self) -> None:
        content = (
            '`![图](x.png)` 与 ``[文](a.md) `样例` ![图][img]``\n'
            r'\![图](https://example.com/x.png) 与 \[文](a.md)' + '\n'
            '[img]: x.png\n'
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / 'source.md'
            source_path.write_text(content, encoding='utf-8')
            projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
            self.assertIn(content, projection)
            self.assertEqual([], manifest['images'])
            self.assertEqual([], manifest['unresolved_local_links'])

    def test_image_titles_are_not_part_of_the_local_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'x.png').write_bytes(b'fixture')
            for title in ('"标题"', "'标题'", '(标题)', '"使用 `foo`"', '"单个 ` 字符"'):
                with self.subTest(title=title):
                    source_path = root / 'source.md'
                    source_path.write_text(f'![图](x.png {title})\n', encoding='utf-8')
                    projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
                    self.assertIn('【待插图：图】', projection)
                    self.assertEqual([{'alt': '图', 'path': 'x.png'}], manifest['images'])
                    self.assertEqual([], manifest['missing_images'])

    def test_reference_resources_use_definitions_and_report_missing_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'x.png').write_bytes(b'fixture')
            source_path = root / 'source.md'
            definitions = '[IMG]: <x.png> "标题"\n[缺图]: missing.png\n[本地文档]: a.md "文档标题"\n'
            source_path.write_text(
                '![图][img] ![缺图][] ![缺图] [文档][本地文档]\n\n' + definitions,
                encoding='utf-8',
            )
            projection, manifest = MODULE.prepare_projection(
                source_path, 'v1', {'a.md': 'https://example.yuque.com/doc'}
            )
            self.assertEqual(3, len(manifest['images']))
            self.assertEqual(2, len(manifest['missing_images']))
            self.assertEqual('x.png', manifest['images'][0]['path'])
            self.assertIn('[文档](https://example.yuque.com/doc "文档标题")', projection)
            self.assertIn(definitions, projection)

    def test_rejects_unsupported_resource_syntax_before_writing(self) -> None:
        for content in ('![图](folder(x)/x.png)', '![图][missing]', '[img]:\n  x.png\n![图][img]', '![图[例]](x.png)'):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temp_dir:
                source_path = Path(temp_dir) / 'source.md'
                source_path.write_text(content, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, '不支持|未定义'):
                    MODULE.prepare_projection(source_path, 'v1', {})

    def test_preserves_plain_nested_brackets(self) -> None:
        content = '矩阵 [[1,2],[3,4]] 可以逐项阅读。数组 a[i][j] 中的值。\n'
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / 'source.md'
            source_path.write_text(content, encoding='utf-8')
            projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
            self.assertIn(content, projection)
            self.assertEqual([], manifest['images'])
            self.assertEqual([], manifest['unresolved_local_links'])

    def test_maps_local_link_with_code_in_its_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / 'source.md'
            source_path.write_text('请阅读 [`foo`](api.md)。\n', encoding='utf-8')
            projection, manifest = MODULE.prepare_projection(
                source_path, 'v1', {'api.md': 'https://example.yuque.com/api'}
            )
            self.assertIn('[`foo`](https://example.yuque.com/api)', projection)
            self.assertEqual(
                [{'label': '`foo`', 'source': 'api.md', 'target': 'https://example.yuque.com/api'}],
                manifest['mapped_local_links'],
            )
            projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
            self.assertIn('请阅读 `foo`。', projection)
            self.assertEqual(
                [{'label': '`foo`', 'target': 'api.md'}], manifest['unresolved_local_links']
            )

    def test_reference_title_with_backticks_keeps_the_resource_intact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'x.png').write_bytes(b'fixture')
            source_path = root / 'source.md'
            source_path.write_text(
                '![图][img]\n[img]: x.png "使用 `foo`"\n', encoding='utf-8'
            )
            projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
            self.assertIn('【待插图：图】', projection)
            self.assertEqual([{'alt': '图', 'path': 'x.png'}], manifest['images'])
            self.assertEqual([], manifest['missing_images'])

    def test_source_sha256_uses_original_bytes_for_lf_and_crlf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / 'source.md'
            for source in (b'# Test\n\nBody\n', b'# Test\r\n\r\nBody\r\n'):
                with self.subTest(source=source):
                    source_path.write_bytes(source)
                    projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
                    expected = hashlib.sha256(source).hexdigest()
                    self.assertEqual(expected, manifest['source_sha256'])
                    self.assertIn(f'SourceSHA256={expected}', projection)

    def test_angle_and_escaped_paths_and_external_reference_remain_usable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / 'image (1).png').write_bytes(b'fixture')
            (root / 'image(2).png').write_bytes(b'fixture')
            source_path = root / 'source.md'
            source_path.write_text(
                '![一]( <image (1).png> "标题" )\n'
                r'![二](image\(2\).png)' + '\n'
                '![外图][ext]\n[ext]: https://example.com/image.png "外部标题"\n',
                encoding='utf-8',
            )
            projection, manifest = MODULE.prepare_projection(source_path, 'v1', {})
            self.assertEqual(['image (1).png', 'image(2).png'], [item['path'] for item in manifest['images']])
            self.assertEqual([], manifest['missing_images'])
            self.assertIn('![外图][ext]', projection)
            self.assertIn('[ext]: https://example.com/image.png "外部标题"', projection)

    def test_code_does_not_supply_reference_definitions(self) -> None:
        for content in (
            '```md\n[img]: x.png\n```\n![图][img]\n',
            '`示例`[img]: x.png\n![图][img]\n',
        ):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temp_dir:
                source_path = Path(temp_dir) / 'source.md'
                source_path.write_text(content, encoding='utf-8')
                with self.assertRaisesRegex(ValueError, '未定义'):
                    MODULE.prepare_projection(source_path, 'v1', {})

    def assert_cli_rejects_collision(
        self, source_path: Path, output_dir: Path, link_map: Path | None = None
    ) -> None:
        argv = [
            str(SCRIPT),
            "--source",
            str(source_path),
            "--source-version",
            "v1.2",
            "--output-dir",
            str(output_dir),
        ]
        if link_map is not None:
            argv.extend(["--link-map", str(link_map)])
        stderr = io.StringIO()
        with (
            patch.object(sys, "argv", argv),
            redirect_stdout(io.StringIO()),
            redirect_stderr(stderr),
        ):
            result = MODULE.main()
        self.assertEqual(1, result)
        self.assertIn("output path", stderr.getvalue())

    def test_preserves_markdown_syntax_inside_fenced_code_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "source.md"
            source_path.write_text(
                "```md\n![literal](inside.png)\n[x](inside.md)\n```\n"
                "~~~markdown\n![other](other.png)\n[y](other.md)\n~~~\n",
                encoding="utf-8",
            )

            projection, manifest = MODULE.prepare_projection(
                source_path, "v1.2", {}
            )

            self.assertIn(
                "```md\n![literal](inside.png)\n[x](inside.md)\n```",
                projection,
            )
            self.assertIn(
                "~~~markdown\n![other](other.png)\n[y](other.md)\n~~~",
                projection,
            )
            self.assertEqual([], manifest["images"])
            self.assertEqual([], manifest["unresolved_local_links"])

    def test_preserves_mermaid_and_builds_asset_and_link_manifest(self) -> None:
        source_path = ROOT / "fixtures" / "source.md"
        source = source_path.read_text(encoding="utf-8")
        link_map = json.loads((ROOT / "fixtures" / "link-map.json").read_text(encoding="utf-8"))

        projection, manifest = MODULE.prepare_projection(source_path, "v1.2", link_map)

        self.assertIn("```mermaid\nflowchart TD\n    A[开始] --> B[完成]\n```", projection)
        self.assertIn("【待插图：产品架构】", projection)
        self.assertNotIn("![产品架构]", projection)
        self.assertIn("[相关产品](https://example.yuque.com/team/book/related)", projection)
        self.assertIn("未映射产品", projection)
        self.assertNotIn("(missing.md)", projection)
        self.assertIn("[外部资料](https://example.com/reference)", projection)
        self.assertIn("SourceVersion=v1.2", projection)
        self.assertEqual(
            hashlib.sha256(source.encode("utf-8")).hexdigest(),
            manifest["source_sha256"],
        )
        self.assertEqual(1, manifest["mermaid_blocks"])
        self.assertEqual(
            [{"alt": "产品架构", "path": "images/architecture.svg"}],
            manifest["images"],
        )
        self.assertEqual(
            [{"alt": "产品架构", "path": "images/architecture.svg"}],
            manifest["missing_images"],
        )
        self.assertEqual(
            [{"label": "未映射产品", "target": "missing.md"}],
            manifest["unresolved_local_links"],
        )

    def test_preserves_externally_hosted_images(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "source.md"
            source_path.write_text(
                "# 示例\n\n![外部图片](https://cdn.example.com/architecture.svg)\n",
                encoding="utf-8",
            )

            projection, manifest = MODULE.prepare_projection(source_path, "v1.2", {})

            self.assertIn(
                "![外部图片](https://cdn.example.com/architecture.svg)", projection
            )
            self.assertEqual([], manifest["images"])
            self.assertEqual([], manifest["missing_images"])

    def test_cli_writes_projection_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            argv = [
                str(SCRIPT),
                "--source",
                str(ROOT / "fixtures" / "source.md"),
                "--source-version",
                "v1.2",
                "--link-map",
                str(ROOT / "fixtures" / "link-map.json"),
                "--output-dir",
                str(output_dir),
            ]
            with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
                result = MODULE.main()

            self.assertEqual(0, result)
            self.assertTrue((output_dir / "projection.md").is_file())
            self.assertTrue((output_dir / "manifest.json").is_file())
            manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("v1.2", manifest["source_version"])

    def test_cli_rejects_output_collisions_without_mutating_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "projection.md"
            source_path.write_text("# Source\n", encoding="utf-8")
            original_source = source_path.read_bytes()
            self.assert_cli_rejects_collision(source_path, root)
            self.assertEqual(original_source, source_path.read_bytes())
            self.assertFalse((root / "manifest.json").exists())

            source_path = root / "source.md"
            source_path.write_text("# Source\n", encoding="utf-8")
            link_map = root / "manifest.json"
            link_map.write_text("{}\n", encoding="utf-8")
            original_link_map = link_map.read_bytes()
            original_projection = (root / "projection.md").read_bytes()
            self.assert_cli_rejects_collision(source_path, root, link_map)
            self.assertEqual(original_link_map, link_map.read_bytes())
            self.assertEqual(original_projection, (root / "projection.md").read_bytes())

    def test_cli_rejects_symlink_and_hardlink_output_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "source.md"
            source_path.write_text("# Source\n", encoding="utf-8")
            original_source = source_path.read_bytes()
            projection_path = root / "projection.md"
            projection_path.symlink_to(source_path)
            self.assert_cli_rejects_collision(source_path, root)
            self.assertEqual(original_source, source_path.read_bytes())

            projection_path.unlink()
            projection_path.hardlink_to(source_path)
            self.assert_cli_rejects_collision(source_path, root)
            self.assertEqual(original_source, source_path.read_bytes())

            projection_path.unlink()
            manifest_path = root / "manifest.json"
            projection_path.write_text("linked output\n", encoding="utf-8")
            manifest_path.hardlink_to(projection_path)
            self.assert_cli_rejects_collision(source_path, root)
            self.assertEqual("linked output\n", projection_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
