#!/usr/bin/env python3
"""Behavior tests for the offline UI style evidence gallery."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "ui-design-expert" / "scripts" / "style_gallery.py"
CATALOG = ROOT / "ui-design-expert" / "assets" / "style-gallery" / "catalog.json"
RELEVANCE = ROOT / "ui-design-expert" / "assets" / "style-gallery" / "relevance-cases.json"
SPEC = importlib.util.spec_from_file_location("style_gallery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


class StyleGalleryTests(unittest.TestCase):
    def test_committed_gallery_is_current_and_local_only(self) -> None:
        catalog = MODULE.read_catalog(CATALOG)
        relevance = json.loads(RELEVANCE.read_text(encoding="utf-8"))
        report = MODULE.check_gallery(catalog, CATALOG, CATALOG.parent, relevance)

        self.assertEqual("passed", report["status"])
        self.assertEqual(24, report["specimens"])
        self.assertEqual(3, report["comparison_groups"])
        self.assertEqual("local-visual-evidence-only", report["proof_limit"])
        self.assertEqual("passed", report["relevance"]["status"])

    def test_search_is_deterministic_bounded_and_type_aware(self) -> None:
        catalog = MODULE.read_catalog(CATALOG)
        first = MODULE.search_catalog(catalog, "实时 监控 dashboard", "data-task", 3)
        second = MODULE.search_catalog(catalog, "实时 监控 dashboard", "data-task", 3)

        self.assertEqual(first, second)
        self.assertLessEqual(len(first), 3)
        self.assertGreater(len(first), 0)
        self.assertTrue(all(item["type"] == "data-task" for item in first))
        self.assertEqual("real-time-monitoring", first[0]["id"])

    def test_build_is_byte_stable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "gallery"
            catalog = MODULE.read_catalog(CATALOG)

            MODULE.build_gallery(catalog, output)
            first_digest = tree_digest(output)
            MODULE.build_gallery(catalog, output)

            self.assertEqual(first_digest, tree_digest(output))
            self.assertEqual(24, len(list((output / "styles").glob("*.html"))))

    def test_duplicate_and_deprecated_entries_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            catalog_path = Path(temp_dir) / "catalog.json"
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            duplicate = dict(catalog["styles"][0])
            duplicate["upstream_status"] = "deprecated"
            catalog["styles"].append(duplicate)
            catalog_path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            errors = MODULE.validate_catalog(catalog, catalog_path)

            self.assertIn("duplicate style id", " ".join(errors))
            self.assertIn("deprecated", " ".join(errors))

    def test_tampered_generated_html_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "gallery"
            catalog = MODULE.read_catalog(CATALOG)
            MODULE.build_gallery(catalog, output)
            target = output / "styles" / "glassmorphism.html"
            target.write_text(
                target.read_text(encoding="utf-8")
                + '\n<script src="https://example.test/tracker.js"></script>\n',
                encoding="utf-8",
            )

            report = MODULE.check_gallery(catalog, CATALOG, output)

            errors = " ".join(report["errors"])
            self.assertIn("generated file differs", errors)
            self.assertIn("external URL", errors)

    def test_relevance_gate_passes_and_detects_regression(self) -> None:
        catalog = MODULE.read_catalog(CATALOG)
        relevance = json.loads(RELEVANCE.read_text(encoding="utf-8"))

        passed = MODULE.evaluate_relevance(catalog, relevance)
        regressed = deepcopy(relevance)
        regressed["cases"][0]["expected_first"] = "cyberpunk-ui"
        failed = MODULE.evaluate_relevance(catalog, regressed)

        self.assertEqual("passed", passed["status"])
        self.assertEqual(20, passed["passed"])
        self.assertEqual("failed", failed["status"])
        self.assertIn("professional-grid-workspace", failed["failed_case_ids"])


if __name__ == "__main__":
    unittest.main()
