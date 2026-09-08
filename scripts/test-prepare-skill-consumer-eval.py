#!/usr/bin/env python3
"""Offline regression checks; these do not execute a model or prove Skill loading."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare-skill-consumer-eval.py"


class SourceScopeTests(unittest.TestCase):
    def test_packaged_skills_do_not_inherit_source_repository_policy(self):
        for skill in ("senior-software-architect", "product-architecture-expert"):
            with self.subTest(skill=skill):
                body = (ROOT / skill / "SKILL.md").read_text()
                self.assertNotIn("继承仓库 `AGENTS.md`", body)


class ConsumerPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("consumer_eval", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.cases = cls.module.load_cases()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="consumer-eval-test-", dir="/tmp")
        self.addCleanup(self.temporary.cleanup)
        self.output = Path(self.temporary.name) / "bundle"

    def test_valid_contract(self):
        self.module.validate_consumer_cases(self.cases)

    def test_source_injection_profiles_are_rejected(self):
        for field in ("source_profiles", "input_profile"):
            with self.subTest(field=field):
                data = deepcopy(self.cases)
                data[field] = {}
                with self.assertRaises(ValueError):
                    self.module.validate_consumer_cases(data)

    def test_unknown_host_and_unsafe_write_paths_are_rejected(self):
        for field, value in (("host_profile", "unknown"), ("write_paths", ["../escape"]),
                             ("write_paths", ["/tmp/escape"]), ("write_paths", "labels.py")):
            with self.subTest(field=field, value=value):
                data = deepcopy(self.cases)
                data["cases"][0][field] = value
                with self.assertRaises(ValueError):
                    self.module.validate_consumer_cases(data)

    def test_unknown_case_does_not_write_or_sync(self):
        with patch.object(self.module.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                self.module.prepare_case(self.cases, "unknown", self.output)
            run.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_source_and_user_destinations_are_rejected(self):
        for output in (ROOT / "consumer-output", Path.home() / ".codex" / "consumer-output"):
            with self.subTest(output=output), patch.object(self.module.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    self.module.prepare_case(self.cases, "consumer-direct-repair", output)
                run.assert_not_called()

    def test_existing_destination_is_preserved(self):
        self.output.mkdir()
        marker = self.output / "marker.txt"
        marker.write_text("keep")
        with patch.object(self.module.subprocess, "run") as run:
            with self.assertRaises(ValueError):
                self.module.prepare_case(self.cases, "consumer-direct-repair", self.output)
            run.assert_not_called()
        self.assertEqual(marker.read_text(), "keep")

    def test_current_codex_home_under_tmp_is_protected(self):
        with patch.dict(self.module.os.environ, {"CODEX_HOME": str(self.output.parent)}):
            with patch.object(self.module.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    self.module.prepare_case(self.cases, "consumer-direct-repair", self.output)
                run.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_dangling_link_and_parent_escape_are_rejected(self):
        self.output.symlink_to(self.output.parent / "missing")
        with self.assertRaises(ValueError):
            self.module.prepare_case(self.cases, "consumer-direct-repair", self.output)
        escape = self.output.parent / "escape"
        escape.symlink_to(ROOT, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.module.prepare_case(self.cases, "consumer-direct-repair", escape / "consumer-output")

    def test_minimal_bundle_contains_only_package_project_and_task(self):
        with patch.object(self.module.subprocess, "run", wraps=subprocess.run) as run:
            receipt = self.module.prepare_case(self.cases, "consumer-direct-repair", self.output)
        self.assertEqual([call.args[0] for call in run.call_args_list], [
            ["bash", str(ROOT / "sync-skills.sh"), "--dry-run", "senior-software-architect"],
            ["bash", str(ROOT / "sync-skills.sh"), "senior-software-architect"],
        ])
        for call in run.call_args_list:
            self.assertEqual(Path(call.kwargs["env"]["CODEX_HOME"]), self.output.resolve() / "codex-home")
            self.assertNotIn("shell", call.kwargs)
        project = self.output / "project"
        home = self.output / "codex-home"
        self.assertFalse((project / "AGENTS.md").exists())
        self.assertFalse((home / "AGENTS.md").exists())
        self.assertFalse((home / "agents").exists())
        self.assertEqual({entry.name for entry in (home / "skills").iterdir()
                          if not entry.name.startswith(".")}, {"senior-software-architect"})
        self.assertEqual((home / "skills/senior-software-architect/SKILL.md").read_bytes(),
                         (ROOT / "senior-software-architect/SKILL.md").read_bytes())
        self.assertEqual({entry.name for entry in project.iterdir()},
                         {"labels.py", "verify_labels.py", "facts.md"})
        case = self.cases["cases"][0]
        self.assertEqual((self.output / "task.txt").read_text(), case["prompt"] + "\n")
        self.assertEqual(receipt["execution_status"], "NOT_RUN")
        self.assertEqual(receipt["loading_status"], "NOT_VERIFIED")
        self.assertEqual(receipt["write_paths"], ["labels.py"])
        for relative, digest in receipt["files_sha256"].items():
            self.assertEqual(hashlib.sha256((self.output / relative).read_bytes()).hexdigest(), digest)
        self.assertEqual(json.loads((self.output / "receipt.json").read_text()), receipt)
        self.assertNotIn("criteria", json.dumps(receipt))

    def test_strict_host_profile_preserves_pending_authorization(self):
        receipt = self.module.prepare_case(self.cases, "consumer-host-approval", self.output)
        policy = (self.output / "project/AGENTS.md").read_text()
        self.assertEqual(policy, self.cases["consumer_setup"]["host_profiles"]["approval"])
        self.assertNotEqual(policy, (ROOT / "AGENTS.md").read_text())
        self.assertEqual((self.output / "project/approval.md").read_text(), "PENDING\n")
        self.assertEqual(receipt["write_paths"], [])

    def test_failed_sync_leaves_log_without_success_receipt(self):
        result = subprocess.CompletedProcess([], 1, "controlled failure\n")
        with patch.object(self.module.subprocess, "run", return_value=result) as run:
            with self.assertRaises(RuntimeError):
                self.module.prepare_case(self.cases, "consumer-direct-repair", self.output)
            run.assert_called_once()
        self.assertIn("controlled failure", (self.output / "setup.log").read_text())
        self.assertFalse((self.output / "receipt.json").exists())

    def test_checker_detects_fixture_bug_and_accepts_minimal_fix(self):
        fixture = ROOT / "fixtures/skill-eval/consumer-project"
        self.output.mkdir()
        for name in ("labels.py", "verify_labels.py"):
            (self.output / name).write_bytes((fixture / name).read_bytes())
        checker = [self.module.sys.executable, "-B", "verify_labels.py"]
        failed = subprocess.run(checker, cwd=self.output, capture_output=True, text=True)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("test_none", failed.stderr)
        (self.output / "labels.py").write_text(
            'def normalize_label(value):\n    return "" if value is None else value.strip()\n'
        )
        passed = subprocess.run(checker, cwd=self.output, capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stderr)


if __name__ == "__main__":
    unittest.main()
