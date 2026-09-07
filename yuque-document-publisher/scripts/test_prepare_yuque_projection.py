#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
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


if __name__ == "__main__":
    unittest.main()
