#!/usr/bin/env python3
"""Tests for the novelist logical-timeline checker."""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-novelist-timeline.py"

SPEC = importlib.util.spec_from_file_location("check_novelist_timeline", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


TABLE_HEADER = (
    "| Event ID | Authority | Canon Status | Record Status | Open Fields | "
    "T Anchor | Line Role | Time Relation | Depends On | Interface | State Delta | P Anchor |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)
HEADER = "Time Axis: `TEST`\n\n" + TABLE_HEADER
DURATION_TABLE_HEADER = (
    "| Event ID | Authority | Canon Status | Record Status | Open Fields | "
    "T Anchor | Line Role | Time Relation | Depends On | Interface | State Delta | "
    "P Anchor | Natural Duration |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


class TimelineTests(unittest.TestCase):
    def write_timeline(self, project: Path, rows: str, *, include_time_axis: bool = True) -> Path:
        (project / "canon.md").write_text(
            "# Canon\n\n"
            "## fight\n## approach\n## other-line\n## arrival\n## scene\n## seal\n",
            encoding="utf-8",
        )
        timeline = project / "timeline.md"
        header = HEADER if include_time_axis else TABLE_HEADER
        timeline.write_text(header + rows, encoding="utf-8")
        return timeline

    def test_accepts_parallel_scenes_and_selective_merge(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#fight | confirmed | aligned | action | "
                "T080.01.010 | main | same-window | - | - | tiger retreats | P010, P040 |\n"
                "| EV-020 | canon.md#approach | confirmed | aligned | route | "
                "T080.02.010 | side | overlap:EV-010 | - | - | pursuer approaches | P020 |\n"
                "| EV-030 | canon.md#other-line | confirmed | aligned | - | "
                "T080.03.010 | side | unknown-order | - | - | another line continues | P030 |\n"
                "| EV-040 | canon.md#arrival | confirmed | aligned | - | "
                "T090.00.010 | global | same-window | EV-010, EV-020 | movement | "
                "pursuer arrives | P050 |\n",
            )

            output = io.StringIO()
            with redirect_stdout(output):
                errors = MODULE.check(project, timeline)

            self.assertEqual([], errors)
            self.assertIn("4 events", output.getvalue())
            self.assertIn("1 cross-line interface", output.getvalue())

    def test_rejects_conflicting_identity_and_invalid_cross_line_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-020 | canon.md#source | confirmed | aligned | - | "
                "T070~090.02.010 | side | same-window | - | - | source event | P010 |\n"
                "| EV-010 | - | confirmed | conflict | - | "
                "T080.01.020 | global | same-window | EV-020 | - | moved event | P020 |\n"
                "| EV-010 | canon.md#duplicate | confirmed | aligned | - | "
                "T100.01.030 | main | same-window | - | - | duplicate event | P030 |\n",
            )

            errors = MODULE.check(project, timeline)

            self.assertTrue(any("duplicate event ID EV-010" in error for error in errors))
            self.assertTrue(any("confirmed event EV-010 has no authority" in error for error in errors))
            self.assertTrue(any("dependency EV-020 occurs after EV-010" in error for error in errors))
            self.assertTrue(any("cross-line dependency EV-020 -> EV-010 has no interface" in error for error in errors))
            self.assertTrue(any("line 01 cannot use role global" in error for error in errors))

    def test_require_ready_blocks_unaligned_or_unconfirmed_events(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | author-confirmation | confirmed | pending-writeback | route | "
                "T020~040.01.010 | main | unknown-order | - | movement | bridge pending | - |\n"
                "| EV-020 | - | candidate | aligned | action | "
                "T050.01.020 | main | same-window | EV-010 | - | candidate scene | P010 |\n"
                "| EV-030 | canon.md#scene | confirmed | aligned | blocker:travel-time | "
                "T060.01.030 | main | same-window | EV-020 | - | blocked scene | P020 |\n",
            )

            self.assertEqual([], MODULE.check(project, timeline))
            errors = MODULE.check(project, timeline, require_ready=True)

            self.assertTrue(any("EV-010 record status is pending-writeback" in error for error in errors))
            self.assertTrue(any("EV-020 canon status is candidate" in error for error in errors))
            self.assertTrue(any("EV-030 has open blocker" in error for error in errors))

    def test_rejects_missing_time_axis_and_missing_local_authority(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | missing-authority.md#event | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | event happens | P010 |\n",
                include_time_axis=False,
            )

            errors = MODULE.check(project, timeline)

            self.assertTrue(any("Time Axis" in error for error in errors))
            self.assertTrue(any("authority path does not exist" in error for error in errors))

    def test_validates_local_authority_heading_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#三-初遇与伏线 | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | event happens | P010 |\n"
                "| EV-020 | canon.md#不存在 | confirmed | aligned | - | "
                "T020.01.020 | main | same-window | EV-010 | - | next event | P020 |\n",
            )
            (project / "canon.md").write_text(
                "# Canon\n\n## 三、初遇与伏线\n",
                encoding="utf-8",
            )

            errors = MODULE.check(project, timeline)

            self.assertFalse(any("EV-010" in error for error in errors))
            self.assertTrue(
                any("authority heading does not exist for EV-020" in error for error in errors)
            )

    def test_resolves_explicit_authority_bases_without_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            planning = project / "planning"
            planning.mkdir()
            (project / "canon.md").write_text(
                "# Root Canon\n\n## root scene\n",
                encoding="utf-8",
            )
            (planning / "canon.md").write_text(
                "# Local Canon\n\n## local scene\n",
                encoding="utf-8",
            )
            timeline = planning / "timeline.md"
            timeline.write_text(
                HEADER
                + "| EV-010 | canon.md#root-scene | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | root event | P010 |\n"
                "| EV-020 | ./canon.md#local-scene | confirmed | aligned | - | "
                "T020.01.020 | main | same-window | EV-010 | - | local event | P020 |\n"
                "| EV-030 | [root](../canon.md#root-scene) | confirmed | aligned | - | "
                "T030.01.030 | main | same-window | EV-020 | - | linked event | P030 |\n",
                encoding="utf-8",
            )

            self.assertEqual([], MODULE.check(project, timeline))

    def test_rejects_absolute_authority_paths_inside_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                f"| EV-010 | {project / 'canon.md'}#scene | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | event happens | P010 |\n",
            )

            errors = MODULE.check(project, timeline)

            self.assertTrue(any("must stay under project root" in error for error in errors))

    def test_rejects_self_referential_time_relations(self) -> None:
        for relation in ("overlap:EV-010", "exact-sync:EV-010"):
            with self.subTest(relation=relation), tempfile.TemporaryDirectory() as temp_dir:
                project = Path(temp_dir)
                timeline = self.write_timeline(
                    project,
                    "| EV-010 | canon.md#scene | confirmed | aligned | - | "
                    f"T010.01.010 | main | {relation} | - | - | event happens | P010 |\n",
                )

                errors = MODULE.check(project, timeline)

                self.assertTrue(
                    any("cannot reference itself" in error for error in errors),
                    errors,
                )

    def test_counts_cross_line_overlap_interface_without_requiring_pure_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#seal | confirmed | aligned | - | "
                "T620~670.02.010 | side | overlap:EV-020 | - | environmental-change | "
                "exit becomes unavailable | P010 |\n"
                "| EV-020 | canon.md#fight | confirmed | aligned | - | "
                "T640.01.010 | main | same-window | - | - | fight continues | P020 |\n",
            )

            output = io.StringIO()
            with redirect_stdout(output):
                errors = MODULE.check(project, timeline)

            self.assertEqual([], errors)
            self.assertIn("1 parallel group", output.getvalue())
            self.assertIn("1 cross-line interface", output.getvalue())

            missing_interface = self.write_timeline(
                project,
                "| EV-010 | canon.md#seal | confirmed | aligned | - | "
                "T620~670.02.010 | side | overlap:EV-020 | - | - | "
                "exit becomes unavailable | P010 |\n"
                "| EV-020 | canon.md#fight | confirmed | aligned | - | "
                "T640.01.010 | main | same-window | - | - | fight continues | P020 |\n",
            )
            output = io.StringIO()
            with redirect_stdout(output):
                errors = MODULE.check(project, missing_interface)

            self.assertEqual([], errors)
            self.assertIn("0 cross-line interfaces", output.getvalue())

    def test_scoped_readiness_allows_non_blocking_fields_and_ignores_overlap_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#seal | confirmed | aligned | executor-count-and-names | "
                "T010~020.01.010 | main | overlap:EV-020 | - | environment | "
                "seal continues | P010 |\n"
                "| EV-020 | canon.md#fight | confirmed | aligned | blocker:combat | "
                "T015.01.020 | main | same-window | - | - | fight continues | P020 |\n",
            )

            self.assertEqual(
                [],
                MODULE.check(
                    project,
                    timeline,
                    require_ready=True,
                    ready_events=("EV-010",),
                ),
            )
            full_errors = MODULE.check(project, timeline, require_ready=True)
            self.assertTrue(any("EV-020 has open blocker" in error for error in full_errors))

    def test_scoped_readiness_checks_dependency_status_but_not_dependency_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#approach | candidate | conflict | blocker:route | "
                "T010.01.010 | main | same-window | - | - | approach pending | P010 |\n"
                "| EV-020 | canon.md#scene | confirmed | aligned | - | "
                "T020.01.020 | main | same-window | EV-010 | - | scene starts | P020 |\n",
            )

            errors = MODULE.check(
                project,
                timeline,
                require_ready=True,
                ready_events=("EV-020",),
            )

            self.assertTrue(
                any("ready dependency EV-010 canon status is candidate" in error for error in errors)
            )
            self.assertTrue(
                any("ready dependency EV-010 record status is conflict" in error for error in errors)
            )
            self.assertFalse(any("EV-010 has open blocker" in error for error in errors))

    def test_scoped_readiness_rejects_unknown_events_and_requires_ready_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#scene | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | event happens | P010 |\n",
            )

            unknown_errors = MODULE.check(
                project,
                timeline,
                require_ready=True,
                ready_events=("EV-999",),
            )
            self.assertIn("ready event EV-999 does not exist", unknown_errors)
            self.assertIn(
                "ready events require --require-ready",
                MODULE.check(project, timeline, ready_events=("EV-010",)),
            )
            self.assertIn(
                "duplicate ready event ID EV-010",
                MODULE.check(
                    project,
                    timeline,
                    require_ready=True,
                    ready_events=("EV-010", "EV-010"),
                ),
            )

    def test_scoped_readiness_does_not_hide_full_table_structural_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(
                project,
                "| EV-010 | canon.md#scene | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | selected event | P010 |\n"
                "| EV-020 | missing.md#scene | confirmed | aligned | blocker:other | "
                "T020.01.020 | main | same-window | EV-010 | - | other event | P020 |\n",
            )

            errors = MODULE.check(
                project,
                timeline,
                require_ready=True,
                ready_events=("EV-010",),
            )

            self.assertTrue(
                any("authority path does not exist for EV-020" in error for error in errors)
            )
            self.assertFalse(any("EV-020 has open blocker" in error for error in errors))

    def test_scoped_readiness_requires_non_empty_optional_natural_duration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            timeline = self.write_timeline(project, "")
            timeline.write_text(
                "Time Axis: `TEST`\n\n"
                + DURATION_TABLE_HEADER
                + "| EV-010 | canon.md#scene | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | event happens | P010 | - |\n",
                encoding="utf-8",
            )

            errors = MODULE.check(
                project,
                timeline,
                require_ready=True,
                ready_events=("EV-010",),
            )
            self.assertIn("EV-010 has empty Natural Duration", errors)

            timeline.write_text(
                "Time Axis: `TEST`\n\n"
                + DURATION_TABLE_HEADER
                + "| EV-010 | canon.md#scene | confirmed | aligned | - | "
                "T010.01.010 | main | same-window | - | - | event happens | P010 | unknown |\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                MODULE.check(
                    project,
                    timeline,
                    require_ready=True,
                    ready_events=("EV-010",),
                ),
            )


if __name__ == "__main__":
    unittest.main()
