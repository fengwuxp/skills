#!/usr/bin/env python3
"""Tests for the novelist continuity-ledger checker."""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-novelist-continuity-ledger.py"

SPEC = importlib.util.spec_from_file_location("check_novelist_continuity_ledger", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ContinuityLedgerTests(unittest.TestCase):
    def test_accepts_unique_resolved_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "ledger.md").write_text(
                "| ID | Decision |\n| --- | --- |\n| RW-001 | Keep the promise |\n",
                encoding="utf-8",
            )
            (project / "outline.md").write_text("Depends on RW-001.\n", encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                errors = MODULE.check(project, project / "ledger.md")

            self.assertEqual([], errors)
            self.assertIn("1 definitions", output.getvalue())

    def test_rejects_duplicate_and_unresolved_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "ledger.md").write_text(
                "| ID | Decision |\n"
                "| --- | --- |\n"
                "| RW-001 | First |\n"
                "| RW-001 | Duplicate |\n",
                encoding="utf-8",
            )
            (project / "outline.md").write_text("Depends on RW-999.\n", encoding="utf-8")

            errors = MODULE.check(project, project / "ledger.md")

            self.assertTrue(any("duplicate definition RW-001" in error for error in errors))
            self.assertTrue(any("unresolved reference RW-999" in error for error in errors))

    def test_rejects_markdown_symlink_outside_project_root(self) -> None:
        with (
            tempfile.TemporaryDirectory() as project_dir,
            tempfile.TemporaryDirectory() as outside_dir,
        ):
            project = Path(project_dir)
            (project / "ledger.md").write_text(
                "| ID | Decision |\n| --- | --- |\n| RW-001 | Keep the promise |\n",
                encoding="utf-8",
            )
            outside = Path(outside_dir) / "private.md"
            outside.write_text("outside mentions RW-999\n", encoding="utf-8")
            (project / "linked.md").symlink_to(outside)

            errors = MODULE.check(project, project / "ledger.md")

            self.assertTrue(any("outside project root" in error for error in errors))
            self.assertFalse(any("RW-999" in error for error in errors))

if __name__ == "__main__":
    unittest.main()
