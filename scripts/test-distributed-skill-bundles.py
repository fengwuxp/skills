#!/usr/bin/env python3
"""验证代表性 Skill 暂存包的入口、显式资源和离线脚本。

输入仅为本仓库指定包；输出为 unittest 结果，失败返回非零。
仅写临时目录，不联网、不安装、不调用模型；不证明操作系统隔离或模型加载。
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "wise-agent/scripts/check-runtime-bundle.py"

SPEC = importlib.util.spec_from_file_location("runtime_bundle", RUNTIME_PATH)
RUNTIME = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(RUNTIME)


class DistributedSkillBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="distributed-skill-bundle-", dir="/tmp")
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.skills_root = self.root / "codex-home" / "skills"
        self.skills_root.mkdir(parents=True)

    def stage(self, skill: str) -> Path:
        source = ROOT / skill
        target = self.skills_root / skill
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        return target

    def runtime_command(self, resources: list[str]) -> list[str]:
        command = [
            str(self.skills_root / "wise-agent/scripts/check-runtime-bundle.py"),
            "--skills-root",
            str(self.skills_root),
            "--skill",
            "wise-agent",
        ]
        for resource in resources:
            command.extend(["--resource", resource])
        return command

    def run_command(self, command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
        environment["CODEX_HOME"] = str(self.root / "codex-home")
        return subprocess.run(
            [sys.executable, "-I", "-B", *command],
            cwd=cwd,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_resource_contract_rejects_outside_and_unselected_paths(self) -> None:
        self.stage("wise-agent")
        outside = self.root / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        (self.skills_root / "wise-agent" / "references" / "escape.md").symlink_to(outside)

        bundle = RUNTIME.resolve_bundle(self.skills_root, ["wise-agent"])
        for resource in (
            "/tmp/outside.md",
            "wise-agent/../outside.md",
            "unknown-skill/references/runtime-boundaries.md",
            "wise-agent/references",
            "wise-agent/references/escape.md",
        ):
            with self.subTest(resource=resource):
                with self.assertRaises(RUNTIME.BundleError):
                    RUNTIME.validate_resources(self.skills_root, bundle, [resource])

    def test_bundle_rejects_missing_entry_or_staged_reference(self) -> None:
        self.stage("wise-agent")
        (self.skills_root / "wise-agent/SKILL.md").unlink()
        with self.assertRaises(RUNTIME.BundleError):
            RUNTIME.resolve_bundle(self.skills_root, ["wise-agent"])

        self.stage("wind-coding-conventions")
        (self.skills_root / "wind-coding-conventions/references/code-style.md").unlink()
        with self.assertRaises(RUNTIME.BundleError):
            RUNTIME.validate_resources(
                self.skills_root,
                RUNTIME.resolve_bundle(self.skills_root, ["wind-coding-conventions"]),
                ["wind-coding-conventions/references/code-style.md"],
            )

    def test_architecture_bundle_requires_staged_wind_dependency(self) -> None:
        self.stage("senior-software-architect")

        with self.assertRaises(RUNTIME.BundleError):
            RUNTIME.resolve_bundle(self.skills_root, ["senior-software-architect"])

    def test_staged_wise_agent_reference_reader_from_consumer_directory(self) -> None:
        self.stage("wise-agent")
        consumer = self.root / "consumer"
        consumer.mkdir()
        resources = [
            "wise-agent/references/runtime-boundaries.md",
            "wise-agent/references/capability-routing.md",
            "wise-agent/scripts/read-reference-sections.py",
        ]
        result = self.run_command(self.runtime_command(resources), cwd=consumer)
        self.assertEqual(0, result.returncode, result.stderr)
        reader = self.run_command(
            [
                str(self.skills_root / "wise-agent/scripts/read-reference-sections.py"),
                str(self.skills_root / "wise-agent/references/runtime-boundaries.md"),
                "--query",
                "验证边界",
            ],
            cwd=consumer,
        )
        self.assertEqual(0, reader.returncode, reader.stderr)
        package = json.loads(reader.stdout)
        self.assertEqual("ready", package["status"])
        self.assertEqual(
            str(self.skills_root / "wise-agent/references/runtime-boundaries.md"),
            package["source"],
        )
        self.assertIn("验证边界", package["content"])
        (self.skills_root / "wise-agent/references/runtime-boundaries.md").unlink()
        self.assertTrue((ROOT / "wise-agent/references/runtime-boundaries.md").is_file())
        missing = self.run_command(self.runtime_command(resources), cwd=consumer)
        self.assertEqual(1, missing.returncode)

    def test_staged_architecture_and_wind_chain_runs_selected_guards(self) -> None:
        self.stage("senior-software-architect")
        self.stage("wind-coding-conventions")
        tools = self.root / "tools"
        tools.mkdir()
        shutil.copy2(RUNTIME_PATH, tools / "check-runtime-bundle.py")
        consumer = self.root / "consumer"
        consumer.mkdir()
        resources = [
            "senior-software-architect/references/workflow.md",
            "senior-software-architect/references/project-governance-service-api-modeling.md",
            "senior-software-architect/scripts/check_architecture_deliverable.py",
            "wind-coding-conventions/references/code-style.md",
            "wind-coding-conventions/references/java-coding-conventions.md",
            "wind-coding-conventions/references/wind-coding-conventions.md",
            "wind-coding-conventions/scripts/check_wind_conventions.py",
        ]
        command = [
            str(tools / "check-runtime-bundle.py"),
            "--skills-root",
            str(self.skills_root),
            "--skill",
            "senior-software-architect",
            "--skill",
            "wind-coding-conventions",
        ]
        for resource in resources:
            command.extend(["--resource", resource])
        result = self.run_command(command, cwd=consumer)
        self.assertEqual(0, result.returncode, result.stderr)
        review = consumer / "review.md"
        review.write_text("发现 P2。风险：边界遗漏。证据：文件与行号。建议修复。验证：测试。\n", encoding="utf-8")
        guard = self.run_command(
            [
                str(self.skills_root / "senior-software-architect/scripts/check_architecture_deliverable.py"),
                "--kind",
                "code-review",
                "--file",
                str(review),
            ],
            cwd=consumer,
        )
        self.assertEqual(0, guard.returncode, guard.stderr)
        review.write_text("发现 P2。\n", encoding="utf-8")
        failed_guard = self.run_command(
            [
                str(self.skills_root / "senior-software-architect/scripts/check_architecture_deliverable.py"),
                "--kind",
                "code-review",
                "--file",
                str(review),
            ],
            cwd=consumer,
        )
        self.assertEqual(1, failed_guard.returncode)
        wind = self.run_command(
            [str(self.skills_root / "wind-coding-conventions/scripts/check_wind_conventions.py"), "--self-test"],
            cwd=consumer,
        )
        self.assertEqual(0, wind.returncode, wind.stderr)


if __name__ == "__main__":
    unittest.main()
