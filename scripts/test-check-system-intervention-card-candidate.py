#!/usr/bin/env python3
"""Behavior tests for the candidate system-intervention card checker."""

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


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "fixtures" / "skill-eval" / "candidate-tools" / "check_system_intervention_card.py"
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
        "evidence": [
            {
                "statement": "三轮 CR 均发现 source digest 口径冲突",
                "status": "fact",
                "basis": "CR-101、CR-108、CR-115",
            },
            {
                "statement": "快速恢复绿色放大了证据债",
                "status": "inference",
                "basis": "待由变更时间线复核",
            },
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
                {
                    "name": "监管趋严",
                    "condition": "地区要求独立数据驻留",
                    "early_signal": "正式咨询或监管草案出现",
                },
                {
                    "name": "规模不足",
                    "condition": "客户量未达到独立运营门槛",
                    "early_signal": "连续两季度容量利用率低于目标",
                },
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


class CandidateSystemInterventionCardTests(unittest.TestCase):
    def assert_passed(self, completed: SimpleNamespace, mode: str) -> None:
        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual("passed", report["status"])
        self.assertEqual(mode, report["mode"])
        self.assertEqual([], report["errors"])
        self.assertEqual("structure_only", report["proof_limit"])

    def test_valid_feedback_card_passes(self) -> None:
        self.assert_passed(run_checker(feedback_card()), "feedback")

    def test_feedback_card_requires_balancing_loop(self) -> None:
        card = feedback_card()
        del card["feedback_model"]["balancing_loop"]

        completed = run_checker(card)

        self.assertEqual(1, completed.returncode)
        report = json.loads(completed.stdout)
        self.assertEqual("failed", report["status"])
        self.assertIn("feedback_model.balancing_loop", report["errors"])

    def test_valid_backcasting_card_passes(self) -> None:
        self.assert_passed(run_checker(backcasting_card()), "backcasting")

    def test_backcasting_card_requires_rollback(self) -> None:
        card = backcasting_card()
        card["intervention"]["rollback"] = ""

        completed = run_checker(card)

        self.assertEqual(1, completed.returncode)
        report = json.loads(completed.stdout)
        self.assertIn("intervention.rollback", report["errors"])

    def test_valid_combined_card_passes(self) -> None:
        card = feedback_card()
        backcasting = backcasting_card()
        card["mode"] = "combined"
        card["foresight"] = copy.deepcopy(backcasting["foresight"])
        card["target"] = copy.deepcopy(backcasting["target"])

        self.assert_passed(run_checker(card), "combined")

    def test_invalid_json_is_an_input_error(self) -> None:
        completed = run_checker("{", raw=True)

        self.assertEqual(2, completed.returncode)
        report = json.loads(completed.stdout)
        self.assertEqual("input_error", report["status"])
        self.assertEqual("structure_only", report["proof_limit"])


if __name__ == "__main__":
    unittest.main()
