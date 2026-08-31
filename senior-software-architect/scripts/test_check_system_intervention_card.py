#!/usr/bin/env python3
"""Behavior tests for the runtime system-intervention card checker."""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


TOOL = Path(__file__).with_name("check_system_intervention_card.py")
SPEC = importlib.util.spec_from_file_location("check_system_intervention_card", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def intervention() -> dict[str, str]:
    return {
        "action": "在一个 Skill 上试行单一 source closure",
        "owner": "validator owner",
        "observation_window": "连续三次变更",
        "feedback_source": "validator 输出与 CR 记录",
        "success_signal": "相同输入重复生成相同 digest",
        "failure_signal": "仍需手工选择或刷新 hash",
        "stop_condition": "出现第二权威或不可解释漂移",
        "rollback": "撤回试点生成入口并恢复原只读检查",
    }


def problem() -> dict[str, object]:
    return {
        "behavior_over_time": "规则和 guard 增长，证据口径持续分叉",
        "system_boundary": "Skill source、manifest、validator 与 CR",
        "non_negotiable_constraints": ["reference 是单一权威", "证据边界不可弱化"],
        "evidence": [
            {
                "statement": "三轮 CR 均发现 source digest 口径冲突",
                "status": "fact",
                "basis": "CR-101、CR-108、CR-115",
            }
        ],
    }


def feedback_card() -> dict[str, object]:
    return {
        "version": 1,
        "mode": "feedback",
        "problem": problem(),
        "feedback_model": {
            "reinforcing_loop": "漂移 -> 补 guard -> 状态源增多 -> 更多漂移",
            "balancing_loop": "单一生成入口 -> 差异可定位 -> 阻断手工刷新",
            "delays": ["CR 在变更合入后才暴露证据分叉"],
            "leverage_point": "收口 digest 的唯一生成责任",
        },
        "intervention": intervention(),
    }


def backcasting_card() -> dict[str, object]:
    return {
        "version": 1,
        "mode": "backcasting",
        "problem": problem(),
        "foresight": {
            "scenarios": [
                {"name": "监管趋严", "condition": "要求独立数据驻留", "early_signal": "监管草案出现"},
                {"name": "规模不足", "condition": "客户量未达门槛", "early_signal": "容量利用率持续偏低"},
            ],
            "review_condition": "任一早期信号触发或每季度复核",
        },
        "target": {
            "owner": "区域平台主管",
            "controllability": {
                "controllable": ["内部接口与数据分类"],
                "partially_controllable": ["区域团队规模"],
                "uncontrollable": ["监管最终文本"],
            },
            "forward_check": ["先验证单数据流隔离，再决定是否建设区域平台"],
        },
        "intervention": intervention(),
    }


def run_checker(payload: object, *, raw: bool = False) -> SimpleNamespace:
    content = str(payload) if raw else json.dumps(payload, ensure_ascii=False)
    stdout = io.StringIO()
    with mock.patch.object(MODULE.sys, "stdin", io.StringIO(content)), redirect_stdout(stdout):
        returncode = MODULE.main()
    return SimpleNamespace(returncode=returncode, stdout=stdout.getvalue(), stderr="")


class SystemInterventionCardTests(unittest.TestCase):
    def test_valid_modes_render_required_decision_fields(self) -> None:
        combined = feedback_card()
        backcasting = backcasting_card()
        combined["mode"] = "combined"
        combined["foresight"] = copy.deepcopy(backcasting["foresight"])
        combined["target"] = copy.deepcopy(backcasting["target"])

        expected_markers = {
            "feedback": ("### 反馈模型", "强化环：", "平衡环：", "时间延迟：", "杠杆点："),
            "backcasting": ("### 前瞻与回溯", "可控：", "部分可控：", "不可控：", "前向校验："),
            "combined": ("### 反馈模型", "### 前瞻与回溯"),
        }
        for mode, card in (("feedback", feedback_card()), ("backcasting", backcasting), ("combined", combined)):
            with self.subTest(mode=mode):
                completed = run_checker(card)
                self.assertEqual(0, completed.returncode, completed.stderr)
                report = json.loads(completed.stdout)
                self.assertEqual("passed", report["status"])
                self.assertEqual(mode, report["mode"])
                self.assertEqual("structure_only", report["proof_limit"])
                for marker in ("不可退让约束：", "Owner：", "停止条件：", "回退："):
                    self.assertIn(marker, report["rendered_markdown"])
                for marker in expected_markers[mode]:
                    self.assertIn(marker, report["rendered_markdown"])

    def test_missing_or_placeholder_constraints_fail_closed(self) -> None:
        variants = [feedback_card(), feedback_card(), feedback_card()]
        del variants[0]["problem"]["non_negotiable_constraints"]
        variants[1]["problem"]["non_negotiable_constraints"] = ["N/A"]
        variants[2]["problem"]["non_negotiable_constraints"] = ["遵守红线"]

        for card in variants:
            completed = run_checker(card)
            self.assertEqual(1, completed.returncode, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertIn("problem.non_negotiable_constraints", report["errors"])
            self.assertEqual("", report["rendered_markdown"])

    def test_missing_mode_specific_fields_fail_closed(self) -> None:
        feedback = feedback_card()
        del feedback["feedback_model"]["balancing_loop"]
        backcasting = backcasting_card()
        backcasting["intervention"]["rollback"] = ""

        for card, expected_error in (
            (feedback, "feedback_model.balancing_loop"),
            (backcasting, "intervention.rollback"),
        ):
            with self.subTest(expected_error=expected_error):
                completed = run_checker(card)
                self.assertEqual(1, completed.returncode, completed.stderr)
                report = json.loads(completed.stdout)
                self.assertIn(expected_error, report["errors"])
                self.assertEqual("", report["rendered_markdown"])

    def test_invalid_json_reports_input_error(self) -> None:
        completed = run_checker("{", raw=True)

        self.assertEqual(2, completed.returncode, completed.stderr)
        self.assertTrue(completed.stdout, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual("input_error", report["status"])
        self.assertEqual("structure_only", report["proof_limit"])


if __name__ == "__main__":
    unittest.main()
